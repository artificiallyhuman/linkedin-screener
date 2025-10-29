#!/usr/bin/env python3
"""
LinkedIn Profile Scanner - Detects fake candidate profiles using Playwright and GPT-5
"""

import os
import sys
import argparse
import json
import time
import re
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from openai import OpenAI


# Terminal color codes for better readability
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def format_markdown_for_terminal(text):
    """
    Convert markdown to terminal-friendly formatted text with colors.
    """
    lines = text.split('\n')
    formatted_lines = []

    for line in lines:
        # Headers (# HEADER)
        if line.startswith('# '):
            header = line[2:].strip()
            formatted_lines.append(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
            formatted_lines.append(f"{Colors.BOLD}{Colors.CYAN}{header}{Colors.END}")
            formatted_lines.append(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")

        # Subheaders (## SUBHEADER)
        elif line.startswith('## '):
            subheader = line[3:].strip()
            formatted_lines.append(f"\n{Colors.BOLD}{Colors.BLUE}{subheader}{Colors.END}")
            formatted_lines.append(f"{Colors.BLUE}{'-'*40}{Colors.END}")

        # Bold text (**text**)
        elif '**' in line:
            line = re.sub(r'\*\*(.*?)\*\*', f'{Colors.BOLD}\\1{Colors.END}', line)
            formatted_lines.append(line)

        # Bullet points (- item)
        elif line.strip().startswith('- '):
            bullet_text = line.strip()[2:]
            formatted_lines.append(f"  {Colors.GREEN}•{Colors.END} {bullet_text}")

        # Numbered lists (1. item)
        elif re.match(r'^\d+\.\s', line.strip()):
            formatted_lines.append(f"  {line.strip()}")

        # Risk assessment coloring
        elif 'MEDIUM' in line.upper():
            line = line.replace('Medium', f'{Colors.YELLOW}Medium{Colors.END}')
            line = line.replace('MEDIUM', f'{Colors.YELLOW}MEDIUM{Colors.END}')
            formatted_lines.append(line)
        elif 'HIGH' in line.upper():
            line = line.replace('High', f'{Colors.RED}High{Colors.END}')
            line = line.replace('HIGH', f'{Colors.RED}HIGH{Colors.END}')
            formatted_lines.append(line)
        elif 'LOW' in line.upper():
            line = line.replace('Low', f'{Colors.GREEN}Low{Colors.END}')
            line = line.replace('LOW', f'{Colors.GREEN}LOW{Colors.END}')
            formatted_lines.append(line)

        # Regular text
        else:
            formatted_lines.append(line)

    return '\n'.join(formatted_lines)


def get_session_dir():
    """Get directory for storing browser session data."""
    session_dir = Path.home() / '.linkedin_scanner' / 'browser_data'
    session_dir.mkdir(parents=True, exist_ok=True)
    return str(session_dir)


def extract_candidate_name(profile_data):
    """
    Extract the candidate's name from LinkedIn profile data.
    Tries multiple sources in order of reliability.
    """
    # Try 1: Page title (format: "Name | LinkedIn" or "Name - Title | LinkedIn")
    page_title = profile_data.get('page_title', '')
    if page_title and page_title != 'Sign Up | LinkedIn':
        # Remove " | LinkedIn" and " - LinkedIn" suffixes
        name = page_title.split(' | ')[0].split(' - ')[0].strip()
        if name and len(name) > 1 and len(name) < 100:
            return name

    # Try 2: Meta description (usually starts with name)
    meta_desc = profile_data.get('meta_description', '')
    if meta_desc:
        # Meta descriptions often start with "Name's professional profile"
        # or just "Name - Title"
        words = meta_desc.split()
        if len(words) >= 2:
            # Take first 2-4 words as potential name
            potential_name = ' '.join(words[:3])
            if len(potential_name) < 100:
                return potential_name.split(' - ')[0].strip()

    # Try 3: First line of visible text (often the name)
    visible_text = profile_data.get('visible_text', '')
    if visible_text:
        lines = visible_text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            # Name lines are usually 2-5 words, not too long
            words = line.split()
            if 2 <= len(words) <= 5 and len(line) < 100:
                # Avoid common LinkedIn UI text
                if line not in ['Sign in', 'Join now', 'LinkedIn', 'Profile', 'About']:
                    return line

    # Fallback: Try to extract from URL
    url = profile_data.get('url', '')
    if '/in/' in url:
        slug = url.split('/in/')[-1].rstrip('/').split('?')[0]
        # Convert slug to title case (e.g., "john-smith-123" -> "John Smith")
        name_parts = slug.split('-')
        # Remove numbers and take first 2-4 parts
        name_parts = [part for part in name_parts if not part.isdigit()][:4]
        if name_parts:
            return ' '.join(part.capitalize() for part in name_parts)

    return "Unknown Candidate"


def perform_login(page, email, password):
    """
    Perform LinkedIn login with 2FA support.
    Returns True if successful, False otherwise.
    """
    try:
        print("   Logging into LinkedIn...")
        page.goto('https://www.linkedin.com/login', wait_until='domcontentloaded')

        # Wait for login form
        page.wait_for_selector('#username', timeout=10000)

        # Fill in credentials
        page.fill('#username', email)
        page.fill('#password', password)

        # Click sign in button
        page.click('button[type="submit"]')

        # Wait for navigation
        time.sleep(3)

        # Handle 2FA if required
        if 'checkpoint/challenge' in page.url or 'checkpoint' in page.url:
            print("   ⚠️  Two-factor authentication required")

            # Try to find 2FA input field - LinkedIn uses various selectors
            # IMPORTANT: Exclude hidden inputs and prioritize visible, editable fields
            two_fa_selectors = [
                'input[autocomplete="one-time-code"]:not([type="hidden"])',
                'input[inputmode="numeric"]:not([type="hidden"])',
                'input[type="tel"]:not([type="hidden"])',
                '#input__phone_verification_pin:not([type="hidden"])',
                'input[id*="verification"]:not([type="hidden"]):not([id*="resend"])',
                'input[name*="pin"]:not([type="hidden"]):not([name*="resend"])',
                'input[id*="pin"]:not([type="hidden"]):not([id*="resend"])',
                'input[data-test-id*="verification"]:not([type="hidden"])'
            ]

            two_fa_input = None
            for selector in two_fa_selectors:
                try:
                    locator = page.locator(selector)
                    count = locator.count()

                    if count > 0:
                        # Additional check: make sure it's visible
                        for i in range(count):
                            try:
                                if locator.nth(i).is_visible(timeout=1000):
                                    two_fa_input = locator.nth(i)
                                    print(f"   ✓ Found visible 2FA input field")
                                    break
                            except:
                                continue

                        if two_fa_input:
                            break
                except:
                    continue

            if two_fa_input:
                # Prompt user for 2FA code
                print("\n" + "="*60)
                print("   ENTER YOUR TWO-FACTOR AUTHENTICATION CODE")
                print("="*60)
                two_fa_code = input("   Enter 2FA code: ").strip()

                if not two_fa_code:
                    print("   ✗ No code provided")
                    return False

                # Enter the 2FA code
                print(f"   Submitting 2FA code...")
                try:
                    two_fa_input.fill(two_fa_code)
                except Exception as e:
                    print(f"   ✗ Error filling 2FA code: {e}")
                    return False

                # Look for submit button
                submit_selectors = [
                    'button[type="submit"]:visible',
                    'button[data-test-id*="submit"]:visible',
                    'button:has-text("Submit"):visible',
                    'button:has-text("Verify"):visible',
                    'button:has-text("Continue"):visible'
                ]

                submitted = False
                for selector in submit_selectors:
                    try:
                        locator = page.locator(selector)
                        if locator.count() > 0:
                            locator.first.click(timeout=5000)
                            print("   ✓ 2FA code submitted")
                            submitted = True
                            break
                    except Exception as e:
                        continue

                if not submitted:
                    print("   ⚠️  Could not find submit button, trying Enter key...")
                    try:
                        two_fa_input.press('Enter')
                        print("   ✓ Pressed Enter to submit")
                    except:
                        print("   ✗ Could not submit 2FA code")

                # Wait for navigation after 2FA
                time.sleep(4)

            else:
                print("   ⚠️  Could not find 2FA input field")
                print("   Please complete verification manually in the browser")
                print("   Waiting 45 seconds...")
                time.sleep(45)

        # Check if we're logged in
        if 'feed' in page.url:
            print("   ✓ Login successful!")
            return True
        elif 'checkpoint' in page.url:
            # Still on checkpoint - might need additional verification
            print("   ⚠️  Additional verification may be needed")
            print("   Check the page for any manual actions required")
            print("   Waiting 30 seconds...")
            time.sleep(30)

            # Check again
            if 'feed' in page.url or 'mynetwork' in page.url or 'notifications' in page.url:
                print("   ✓ Login successful!")
                return True
            else:
                print("   ⚠️  Login status unclear, continuing anyway...")
                return True
        else:
            print("   ✓ Login appears successful")
            return True

    except Exception as e:
        print(f"   ✗ Login error: {e}")
        return False


def scrape_linkedin_profile(url, headless=True, use_session=True, credentials=None, retries=2):
    """
    Scrape LinkedIn profile data using Playwright with authentication support.

    Args:
        url: LinkedIn profile URL
        headless: Run browser in headless mode
        use_session: Use persistent browser context (saves cookies/login)
        credentials: Dict with 'email' and 'password' for LinkedIn login
        retries: Number of retry attempts if scraping fails
    """
    for attempt in range(retries + 1):
        try:
            if attempt > 0:
                print(f"   Retry attempt {attempt}/{retries}...")
                time.sleep(2)

            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(
                    headless=headless,
                    args=['--disable-blink-features=AutomationControlled']
                )

                # Use persistent context if requested (saves login sessions)
                if use_session:
                    context = p.chromium.launch_persistent_context(
                        get_session_dir(),
                        headless=headless,
                        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        viewport={'width': 1920, 'height': 1080},
                        args=['--disable-blink-features=AutomationControlled']
                    )
                    page = context.pages[0] if context.pages else context.new_page()
                else:
                    context = browser.new_context(
                        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        viewport={'width': 1920, 'height': 1080}
                    )
                    page = context.new_page()

                # Perform login if credentials provided and not already logged in
                if credentials and credentials.get('email') and credentials.get('password'):
                    # Check if already logged in by trying to access feed
                    page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded', timeout=10000)
                    time.sleep(2)

                    if 'login' in page.url or 'authwall' in page.url:
                        # Not logged in, perform login
                        if not perform_login(page, credentials['email'], credentials['password']):
                            print("   Warning: Login failed, continuing without authentication")

                print(f"   Loading profile page...")

                # Navigate to the profile with retry logic
                try:
                    page.goto(url, wait_until='domcontentloaded', timeout=30000)
                except PlaywrightTimeout:
                    print("   Warning: Page load timeout, continuing anyway...")

                # Wait for content to load - try multiple strategies
                time.sleep(3)  # Give page time to render

                # Try to wait for main profile content
                try:
                    # Wait for profile name or main content area
                    page.wait_for_selector('main, .scaffold-layout__main, [data-generated-suggestion-target]', timeout=10000)
                except:
                    print("   Warning: Main content selector not found, continuing...")

                # Additional wait for dynamic content
                time.sleep(2)

                # Extract page data
                profile_data = {
                    'url': url,
                    'page_title': page.title(),
                    'meta_description': '',
                    'visible_text': ''
                }

                # Get meta description
                try:
                    meta_desc = page.locator('meta[name="description"]').get_attribute('content')
                    if meta_desc:
                        profile_data['meta_description'] = meta_desc
                except:
                    pass

                # Try multiple methods to extract profile text
                extracted_text = ""

                # Method 1: Try to get main content area
                try:
                    main_content = page.locator('main').inner_text()
                    if main_content and len(main_content) > 100:
                        extracted_text = main_content
                        print(f"   ✓ Extracted {len(extracted_text)} characters from main content")
                except:
                    pass

                # Method 2: Try body text if main didn't work
                if not extracted_text:
                    try:
                        body_text = page.locator('body').inner_text()
                        if body_text and len(body_text) > 100:
                            extracted_text = body_text
                            print(f"   ✓ Extracted {len(extracted_text)} characters from body")
                    except Exception as e:
                        print(f"   Warning: Could not extract text: {e}")

                # Method 3: Last resort - get all text
                if not extracted_text:
                    try:
                        extracted_text = page.content()
                        print(f"   ⚠️  Using raw HTML content as fallback")
                    except:
                        pass

                # Clean and limit text
                profile_data['visible_text'] = ' '.join(extracted_text.split())[:10000]

                # Take screenshot on failure for debugging
                if not profile_data['visible_text'] or len(profile_data['visible_text']) < 50:
                    screenshot_path = f"debug_screenshot_{int(time.time())}.png"
                    try:
                        page.screenshot(path=screenshot_path)
                        print(f"   ⚠️  Saved debug screenshot to {screenshot_path}")
                    except:
                        pass

                    # Close and retry
                    if not use_session:
                        browser.close()
                    context.close()

                    if attempt < retries:
                        continue
                    else:
                        print("   ✗ Failed to extract meaningful content after retries")
                        return None

                # Success!
                if not use_session:
                    browser.close()
                context.close()

                return profile_data

        except Exception as e:
            print(f"   Error on attempt {attempt + 1}: {e}")
            if attempt < retries:
                continue
            else:
                print("\nNote: If you encounter issues, try:")
                print("  1. Using --show-browser to see what's happening")
                print("  2. Using --login with your LinkedIn credentials")
                print("  3. Using --text-file to provide manual input")
                return None

    return None


def analyze_profile_with_llm(profile_data, client, model="gpt-5"):
    """
    Send profile data to OpenAI GPT-5 for analysis.
    The LLM will create its own framework for detecting fake profiles.
    """

    prompt = f"""You are an expert recruiter and fraud detection specialist. Analyze this LinkedIn profile for authenticity and identify if it shows signs of being fake or fraudulent.

Consider factors like: profile completeness, timeline consistency, account age indicators, content quality, network characteristics, activity patterns, job history credibility, education markers, duplicate/template content, and other red flags.

LinkedIn Profile Data:
URL: {profile_data.get('url', 'N/A')}
Page Title: {profile_data.get('page_title', 'N/A')}
Meta Description: {profile_data.get('meta_description', 'N/A')}

Profile Content:
{profile_data.get('visible_text', 'N/A')}

Provide a concise report with these sections ONLY (no framework explanation):

# RISK ASSESSMENT
[Low/Medium/High and brief reason]

# RED FLAGS
[List specific concerning issues found, or "None identified"]

# POSITIVE SIGNALS
[List authenticity indicators found, or "None identified"]

# RECOMMENDATIONS
[Specific verification steps to take]

# CONCLUSION
[Brief overall assessment with confidence level]

Use clear markdown formatting with headers (##), bullet points (-), and bold (**text**) for emphasis."""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert at detecting fake LinkedIn profiles and fraudulent candidates. You have years of experience identifying patterns in fake profiles and can quickly spot red flags."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        error_message = str(e)

        # If GPT-5 doesn't exist, try GPT-4o as fallback
        if "does not exist" in error_message.lower() or "model_not_found" in error_message.lower():
            print(f"   Note: {model} not available, falling back to gpt-4o")
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are an expert at detecting fake LinkedIn profiles and fraudulent candidates. You have years of experience identifying patterns in fake profiles and can quickly spot red flags."},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content
            except Exception as e2:
                print(f"Error calling OpenAI API: {e2}")
                return None
        else:
            print(f"Error calling OpenAI API: {e}")
            return None


def validate_linkedin_url(url):
    """Validate that the URL is a LinkedIn profile URL."""
    parsed = urlparse(url)
    return 'linkedin.com' in parsed.netloc and '/in/' in parsed.path


def load_profile_from_file(filepath, url):
    """Load profile data from a text file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            'url': url,
            'page_title': 'Manually provided',
            'meta_description': 'Profile data loaded from file',
            'visible_text': content
        }
    except Exception as e:
        print(f"Error reading file: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Analyze LinkedIn profiles for fake candidate detection using GPT-5.\n\nNote: Automatically uses LinkedIn login if LINKEDIN_EMAIL and LINKEDIN_PASSWORD are set.',
        epilog='Examples:\n  # With auto-login (if credentials are set in env vars)\n  python linkedin_scanner.py https://www.linkedin.com/in/username\n\n  # Show browser for debugging\n  python linkedin_scanner.py https://www.linkedin.com/in/username --show-browser\n\n  # Use text file instead of scraping\n  python linkedin_scanner.py https://www.linkedin.com/in/username --text-file profile.txt',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('url', help='LinkedIn profile URL to analyze')
    parser.add_argument('--api-key', help='OpenAI API key (defaults to OPENAI_API_KEY env var)', default=None)
    parser.add_argument('--text-file', help='Text file containing profile data (bypasses scraping)', default=None)
    parser.add_argument('--show-browser', action='store_true', help='Show browser window during scraping (useful for debugging)')
    parser.add_argument('--login', action='store_true', help='Require LinkedIn login (error if credentials not set). By default, login is used automatically if LINKEDIN_EMAIL and LINKEDIN_PASSWORD are set.')
    parser.add_argument('--no-session', action='store_true', help='Don\'t use persistent browser session (login fresh each time)')
    parser.add_argument('--retries', type=int, default=2, help='Number of retry attempts for scraping (default: 2)')
    parser.add_argument('--model', help='OpenAI model to use (default: gpt-5)', default='gpt-5')

    args = parser.parse_args()

    # Validate URL
    if not validate_linkedin_url(args.url):
        print("Error: Please provide a valid LinkedIn profile URL (e.g., https://www.linkedin.com/in/username)")
        sys.exit(1)

    # Get API key
    api_key = args.api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OpenAI API key not found. Set OPENAI_API_KEY environment variable or use --api-key")
        sys.exit(1)

    # Get LinkedIn credentials - check environment variables automatically
    credentials = None
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')

    if email and password:
        credentials = {'email': email, 'password': password}
    elif args.login:
        # User explicitly requested login but credentials not found
        print("Error: LinkedIn credentials not found.")
        print("Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables:")
        print("  export LINKEDIN_EMAIL='your-email@example.com'")
        print("  export LINKEDIN_PASSWORD='your-password'")
        sys.exit(1)

    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)

    print("=" * 80)
    print("LINKEDIN PROFILE FAKE CANDIDATE DETECTOR")
    print("=" * 80)
    print(f"\nAnalyzing profile: {args.url}\n")

    # Step 1: Get profile data (either from file or scraping)
    if args.text_file:
        print(f"Step 1: Loading profile data from file: {args.text_file}...")
        profile_data = load_profile_from_file(args.text_file, args.url)
        if not profile_data:
            sys.exit(1)
        print("✓ Profile data loaded from file\n")
    else:
        print("Step 1: Scraping LinkedIn profile with Playwright...")
        if args.show_browser:
            print("   (Browser window will be visible)")
        if credentials:
            print("   (Using LinkedIn authentication)")

        profile_data = scrape_linkedin_profile(
            args.url,
            headless=not args.show_browser,
            use_session=not args.no_session,
            credentials=credentials,
            retries=args.retries
        )

        if not profile_data or not profile_data.get('visible_text'):
            print("\nWarning: Limited or no data scraped from LinkedIn.")
            print("LinkedIn may be blocking access or requiring authentication.")
            print("\nTips:")
            print("  1. Try using --login with LinkedIn credentials")
            print("  2. Use --show-browser to see what's happening")
            print("  3. Copy profile text and use: --text-file profile.txt")
            sys.exit(1)

        print("✓ Profile data collected\n")

    # Step 2: Analyze with LLM
    print(f"Step 2: Analyzing profile with {args.model}...")
    analysis = analyze_profile_with_llm(profile_data, client, model=args.model)

    if not analysis:
        print("Failed to get analysis from OpenAI")
        sys.exit(1)

    print("✓ Analysis complete\n")

    # Step 3: Display results with markdown formatting
    # Extract candidate name for header
    candidate_name = extract_candidate_name(profile_data)

    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}ANALYSIS REPORT: {candidate_name}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}\n")

    formatted_analysis = format_markdown_for_terminal(analysis)
    print(formatted_analysis)

    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}\n")


if __name__ == "__main__":
    main()
