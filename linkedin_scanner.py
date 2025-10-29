#!/usr/bin/env python3
"""
LinkedIn Profile Scanner - Detects fake candidate profiles using Playwright and GPT-5
"""

import os
import sys
import argparse
import json
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from openai import OpenAI


def scrape_linkedin_profile(url, headless=True):
    """
    Scrape LinkedIn profile data using Playwright for better JavaScript handling.
    This uses a real browser to bypass basic anti-scraping measures.
    """
    try:
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()

            print(f"   Loading page...")

            # Navigate to the profile
            try:
                page.goto(url, wait_until='networkidle', timeout=30000)
            except PlaywrightTimeout:
                print("   Warning: Page load timeout, continuing anyway...")
                pass

            # Wait a bit for any dynamic content
            page.wait_for_timeout(2000)

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

            # Get all visible text from the page
            try:
                # Get the main content area text
                body_text = page.locator('body').inner_text()
                profile_data['visible_text'] = ' '.join(body_text.split())[:8000]  # Increased limit
            except Exception as e:
                print(f"   Warning: Could not extract text: {e}")

            browser.close()

            if not profile_data['visible_text']:
                print("   Warning: No content extracted from page")
                return None

            return profile_data

    except Exception as e:
        print(f"Error scraping profile: {e}")
        print("\nNote: If you encounter issues, you may need to:")
        print("  1. Install Playwright browsers: playwright install chromium")
        print("  2. Use --text-file option to provide manual input")
        return None


def analyze_profile_with_llm(profile_data, client, model="gpt-5"):
    """
    Send profile data to OpenAI GPT-5 for analysis.
    The LLM will create its own framework for detecting fake profiles.
    """

    prompt = f"""You are an expert recruiter and fraud detection specialist. Your task is to analyze a LinkedIn profile and determine if it shows signs of being a fake or fraudulent candidate profile.

First, develop a comprehensive framework/taxonomy for evaluating LinkedIn profiles for authenticity. Consider factors such as:
- Profile completeness and consistency
- Timeline gaps or inconsistencies
- Account age indicators (new accounts are often suspicious)
- Quality of content (descriptions, endorsements, posts)
- Network characteristics
- Photo authenticity indicators
- Activity patterns
- Job history credibility
- Education verification markers
- Duplicate or template-like content
- Any other red flags you deem relevant

Then, analyze the following LinkedIn profile data against your framework:

URL: {profile_data.get('url', 'N/A')}
Page Title: {profile_data.get('page_title', 'N/A')}
Meta Description: {profile_data.get('meta_description', 'N/A')}

Profile Content:
{profile_data.get('visible_text', 'N/A')}

Provide a detailed report with:
1. Your evaluation framework (brief overview)
2. Risk Assessment (Low/Medium/High)
3. Key red flags identified (if any)
4. Positive authenticity signals (if any)
5. Specific concerns or recommendations
6. Overall conclusion with confidence level

Format your response clearly for terminal output."""

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
        description='Analyze LinkedIn profiles for fake candidate detection using GPT-5',
        epilog='Examples:\n  python linkedin_scanner.py https://www.linkedin.com/in/username\n  python linkedin_scanner.py https://www.linkedin.com/in/username --text-file profile.txt\n  python linkedin_scanner.py https://www.linkedin.com/in/username --show-browser',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('url', help='LinkedIn profile URL to analyze')
    parser.add_argument('--api-key', help='OpenAI API key (defaults to OPENAI_API_KEY env var)', default=None)
    parser.add_argument('--text-file', help='Text file containing profile data (bypasses scraping)', default=None)
    parser.add_argument('--show-browser', action='store_true', help='Show browser window during scraping (useful for debugging)')
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
        profile_data = scrape_linkedin_profile(args.url, headless=not args.show_browser)

        if not profile_data or not profile_data.get('visible_text'):
            print("\nWarning: Limited or no data scraped from LinkedIn.")
            print("LinkedIn may be blocking access or requiring authentication.")
            print("\nTip: Copy the profile text and save to a file, then use:")
            print(f"  python linkedin_scanner.py {args.url} --text-file profile.txt")
            sys.exit(1)

        print("✓ Profile data collected\n")

    # Step 2: Analyze with LLM
    print(f"Step 2: Analyzing profile with {args.model}...")
    analysis = analyze_profile_with_llm(profile_data, client, model=args.model)

    if not analysis:
        print("Failed to get analysis from OpenAI")
        sys.exit(1)

    print("✓ Analysis complete\n")

    # Step 3: Display results
    print("=" * 80)
    print("ANALYSIS REPORT")
    print("=" * 80)
    print()
    print(analysis)
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
