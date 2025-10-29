# LinkedIn Fake Candidate Detector 🔍

> AI-powered LinkedIn profile analyzer that helps recruiters identify potentially fake or fraudulent candidate profiles using GPT-5 and browser automation.

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5-412991.svg)](https://openai.com/)

---

## ⚠️ IMPORTANT: DEMO PURPOSES ONLY

**This project is for demonstration and educational purposes only.**

**LinkedIn explicitly prohibits automated scraping and data collection from its platform.** Using this tool to scrape LinkedIn profiles violates LinkedIn's [User Agreement](https://www.linkedin.com/legal/user-agreement) and [Terms of Service](https://www.linkedin.com/legal/professional-community-policies).

This code demonstrates:
- Browser automation techniques with Playwright
- AI-powered content analysis with GPT models
- Authentication handling and session management

**DO NOT use this tool for actual LinkedIn data collection.** Doing so may result in:
- Account suspension or permanent ban
- Legal action from LinkedIn
- Violation of data protection laws (GDPR, CCPA, etc.)

If you need LinkedIn data for legitimate purposes, use [LinkedIn's official APIs](https://developer.linkedin.com/) or contact LinkedIn directly.

---

## The Problem

Recruiters face an overwhelming number of fake candidate profiles on LinkedIn. Manually reviewing thousands of profiles to identify red flags is:
- **Time-consuming**: Sorting through 2,000+ profiles before finding real talent
- **Inconsistent**: Human reviewers may miss subtle indicators
- **Tedious**: Checking account age, profile completeness, timeline gaps, etc.

## The Solution

This tool automates fake profile detection using:
1. **Real browser automation** (Playwright) to scrape LinkedIn profiles
2. **GPT-5 AI analysis** to evaluate authenticity using a custom-built framework
3. **Detailed reports** highlighting specific red flags and risk levels

---

## Features

✅ **Direct LinkedIn Scraping** - Uses Playwright to access profiles like a real browser
✅ **Auto-Login** - Automatically uses credentials from environment variables, no flags needed
✅ **LinkedIn Authentication** - Login support for reliable access to profiles
✅ **Two-Factor Authentication** - Automatic 2FA detection with interactive code entry in terminal
✅ **Persistent Sessions** - Login once, use many times (saved locally at `~/.linkedin_scanner/`)
✅ **Auto-Retry Logic** - Automatically retries failed scrapes with smart fallbacks
✅ **GPT-5 Powered Analysis** - AI creates custom detection framework and evaluates profiles
✅ **Formatted Reports** - Color-coded terminal output with candidate name in header
✅ **Comprehensive Analysis** - Risk assessment, red flags, authenticity signals, recommendations
✅ **Multiple Input Methods** - Automated scraping, manual text input, or visible browser
✅ **Debug Mode** - Screenshots on failure, verbose logging, visible browser option
✅ **Flexible Model Support** - Works with GPT-5, GPT-4o, or other OpenAI models
✅ **Terminal-Based** - Fast, scriptable, perfect for batch processing

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/linkedin-fake-candidate-detector.git
cd linkedin-fake-candidate-detector

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Set your OpenAI API key
export OPENAI_API_KEY='your-api-key-here'
```

### Basic Usage

```bash
# Set up LinkedIn credentials (one-time setup)
export LINKEDIN_EMAIL='your-email@example.com'
export LINKEDIN_PASSWORD='your-password'

# Analyze a LinkedIn profile - login happens automatically!
python linkedin_scanner.py https://www.linkedin.com/in/username

# The script will automatically prompt for your 2FA code if enabled:
#   ============================================================
#   ENTER YOUR TWO-FACTOR AUTHENTICATION CODE
#   ============================================================
#   Enter 2FA code: 123456

# Show browser window (useful for debugging)
python linkedin_scanner.py https://www.linkedin.com/in/username --show-browser

# Use manual text input (fallback method)
python linkedin_scanner.py https://www.linkedin.com/in/username --text-file profile.txt
```

**Note:** If `LINKEDIN_EMAIL` and `LINKEDIN_PASSWORD` are set, login happens automatically - no `--login` flag needed!

---

## How It Works

```
┌─────────────────┐
│ LinkedIn Profile│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Playwright    │  ← Scrapes profile with real browser
│ Browser Automation│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   GPT-5 Model   │  ← Analyzes content for authenticity
│  AI Framework   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Detailed Report │  ← Risk level + red flags + recommendations
└─────────────────┘
```

### Detection Framework

GPT-5 evaluates profiles based on:
- **Profile Completeness** - Missing sections, incomplete information
- **Timeline Consistency** - Employment gaps, overlapping positions
- **Account Age Indicators** - Recently created accounts (suspicious)
- **Content Quality** - Generic descriptions, template-like text
- **Network Characteristics** - Connection count, endorsements
- **Activity Patterns** - Posts, comments, engagement history
- **Credibility Markers** - Job history, education, skills validation

---

## Sample Output

```
================================================================================
LINKEDIN PROFILE FAKE CANDIDATE DETECTOR
================================================================================

Analyzing profile: https://www.linkedin.com/in/john-smith-dev

Step 1: Scraping LinkedIn profile with Playwright...
   (Using LinkedIn authentication)
   Loading page...
   ✓ Extracted 4,523 characters from main content
✓ Profile data collected

Step 2: Analyzing profile with gpt-5...
✓ Analysis complete

================================================================================
ANALYSIS REPORT: John Smith
================================================================================

============================================================
RISK ASSESSMENT
============================================================
High - Multiple indicators suggest this may be a fraudulent profile

----------------------------------------
RED FLAGS
----------------------------------------
  • Profile created within last 30 days
  • Generic job descriptions with minimal detail
  • No recommendations or endorsements
  • Suspiciously low connection count (<50)
  • No activity history (posts, comments, likes)
  • Stock photo potentially used for profile picture

----------------------------------------
POSITIVE SIGNALS
----------------------------------------
  • Email and phone number listed
  • Education section completed
  • Company names appear legitimate

----------------------------------------
RECOMMENDATIONS
----------------------------------------
  • Request video interview to verify identity
  • Check references independently
  • Verify employment with HR contacts at listed companies
  • Request additional documentation (LinkedIn PDF export, resume)
  • Reverse image search the profile photo

============================================================
CONCLUSION
============================================================
This profile exhibits multiple characteristics common to fake candidates.
The combination of new account age, generic content, and lack of engagement
suggests a high probability of fraudulent profile. Recommend thorough
verification before continuing recruitment process.

Confidence: 85%

================================================================================
```

**Note:** Output includes color-coding in terminal:
- Risk levels: Low (green), Medium (yellow), High (red)
- Section headers in cyan
- Bullet points in green
- Clean, easy-to-scan format

---

## Command-Line Options

```
usage: linkedin_scanner.py [-h] [--api-key API_KEY] [--text-file TEXT_FILE]
                           [--show-browser] [--login] [--no-session]
                           [--retries RETRIES] [--model MODEL]
                           url

Analyze LinkedIn profiles for fake candidate detection using GPT-5.

Note: Automatically uses LinkedIn login if LINKEDIN_EMAIL and LINKEDIN_PASSWORD are set.

positional arguments:
  url                   LinkedIn profile URL to analyze

options:
  -h, --help            show this help message and exit
  --api-key API_KEY     OpenAI API key (defaults to OPENAI_API_KEY env var)
  --text-file TEXT_FILE Text file containing profile data (bypasses scraping)
  --show-browser        Show browser window during scraping
  --login               Require LinkedIn login (error if credentials not set)
                        By default, login is automatic if credentials are set
  --no-session          Don't use persistent browser session (login fresh each time)
  --retries RETRIES     Number of retry attempts for scraping (default: 2)
  --model MODEL         OpenAI model to use (default: gpt-5)
```

### Examples

```bash
# Basic analysis (auto-login if credentials are set)
python linkedin_scanner.py https://www.linkedin.com/in/candidate

# With more retries for flaky connections
python linkedin_scanner.py https://www.linkedin.com/in/candidate --retries 5

# Use specific model
python linkedin_scanner.py https://www.linkedin.com/in/candidate --model gpt-4o

# Debug mode - see what's happening
python linkedin_scanner.py https://www.linkedin.com/in/candidate --show-browser

# Manual text input (fallback if scraping fails)
python linkedin_scanner.py https://www.linkedin.com/in/candidate --text-file profile.txt

# Don't save session (more private, slower)
python linkedin_scanner.py https://www.linkedin.com/in/candidate --no-session

# Require login (error if credentials not set)
python linkedin_scanner.py https://www.linkedin.com/in/candidate --login
```

---

## Batch Processing

To analyze multiple candidates:

```bash
# Set up credentials (one-time)
export LINKEDIN_EMAIL='your-email@example.com'
export LINKEDIN_PASSWORD='your-password'

# Create a file with LinkedIn URLs (one per line)
cat candidates.txt
https://www.linkedin.com/in/candidate1
https://www.linkedin.com/in/candidate2
https://www.linkedin.com/in/candidate3

# Process all profiles - auto-login happens on first profile
while read url; do
  echo "Analyzing: $url"
  python linkedin_scanner.py "$url" >> results.txt
  sleep 5  # Avoid rate limiting
done < candidates.txt
```

**Pro tip:** With credentials set, the first profile logs you in automatically, and subsequent profiles use the saved session - making batch processing fast and seamless!

---

## Important Considerations

### LinkedIn Access

- **Auto-Login**: Just set `LINKEDIN_EMAIL` and `LINKEDIN_PASSWORD` - login happens automatically, no flags needed!
- **Two-Factor Authentication**: Fully supported! Script will prompt for your 2FA code automatically
  - Works with SMS codes, authenticator apps (Google Authenticator, Authy), and email codes
  - Code entry happens in terminal - no need to use browser
- **Session Persistence**: Login saved to `~/.linkedin_scanner/` - login once, use many times
- **Public Profiles**: Works without login but may have limited access
- **Rate Limiting**: Add 5-10 second delays between profiles to avoid blocks
- **Terms of Service**: Review LinkedIn's TOS before large-scale scraping
- **Other Verification**: If LinkedIn asks for CAPTCHA, use `--show-browser` to complete manually

### OpenAI API

- **GPT-5 Access**: Requires OpenAI API access to GPT-5 (auto-falls back to GPT-4o)
- **Costs**: API calls incur charges based on token usage
- **Rate Limits**: Be aware of your API tier limits

### Accuracy

- This tool provides **analysis assistance**, not definitive proof
- Always combine with additional verification methods
- False positives/negatives are possible
- Use as one tool in your recruitment process

---

## Use Cases

- **Recruitment Teams**: Screen large candidate pools efficiently
- **HR Departments**: Verify profile authenticity before interviews
- **Hiring Managers**: Quick red flag detection for suspicious profiles
- **Talent Acquisition**: Prioritize reviewing genuine candidates first

---

## Requirements

- Python 3.7 or higher
- OpenAI API key with GPT-5 access (or GPT-4o)
- Internet connection
- ~200MB disk space for Playwright browser

### Dependencies

- `openai>=1.0.0` - OpenAI API client
- `playwright>=1.40.0` - Browser automation

---

## Troubleshooting

**Problem: "Module not found" errors**
```bash
pip install -r requirements.txt
```

**Problem: Playwright browser not found**
```bash
playwright install chromium
```

**Problem: LinkedIn blocking scraping or "No content extracted"**
- Set LinkedIn credentials in environment variables (most effective!)
  ```bash
  export LINKEDIN_EMAIL='your-email@example.com'
  export LINKEDIN_PASSWORD='your-password'
  ```
- Use `--show-browser` to see what's happening
- Increase retries: `--retries 5`
- Add delays between requests (5-10 seconds)
- Check debug screenshot saved to current directory
- Use `--text-file` for manual input as fallback

**Problem: Login failed**
- Verify credentials are set: `echo $LINKEDIN_EMAIL`
- Use `--show-browser` to see login process
- If 2FA is enabled, make sure to enter the code when prompted
- Complete other verification manually if LinkedIn asks
- Try again after a few minutes

**Problem: 2FA code not working**
- Make sure you're entering the code quickly (they expire in 30-60 seconds)
- Double-check you copied the entire code
- Try using `--show-browser` to see if there are additional prompts
- Some authenticator apps may have time sync issues - check your device time

**Problem: Session expired or "Not logged in"**
- Clear session: `rm -rf ~/.linkedin_scanner/browser_data/`
- Run script again - it will auto-login with your credentials

**Problem: OpenAI API errors**
- Verify API key is set: `echo $OPENAI_API_KEY`
- Check API quota and billing
- Try `--model gpt-4o` if GPT-5 unavailable

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Disclaimer

⚠️ **CRITICAL LEGAL NOTICE**

**THIS PROJECT IS FOR DEMONSTRATION AND EDUCATIONAL PURPOSES ONLY.**

**LinkedIn prohibits web scraping and automated data collection.** This tool violates LinkedIn's Terms of Service and should **NOT** be used to scrape LinkedIn profiles in any production or commercial capacity.

This code is provided solely to demonstrate:
- Technical implementation of browser automation
- AI-powered content analysis patterns
- Authentication flow handling
- Educational programming concepts

**By using this code, you acknowledge that:**

- **LinkedIn does NOT allow data scraping** from its platform
- Using this tool for actual data collection **violates LinkedIn's Terms of Service**
- You may face **account termination, legal action, and other consequences**
- The authors assume **NO responsibility or liability** for any misuse
- For legitimate LinkedIn data access, use [LinkedIn's official APIs](https://developer.linkedin.com/)

**Users must:**
- Use this ONLY for learning and demonstration in controlled environments
- NEVER deploy this against LinkedIn's production website
- Respect all applicable laws including GDPR, CCPA, and CFAA
- Understand that automated profile detection is probabilistic and not definitive

**The authors explicitly disclaim all responsibility for misuse of this tool.**

---

## Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/linkedin-fake-candidate-detector/issues)
- 💡 **Feature Requests**: Open an issue with the "enhancement" label

---

## Acknowledgments

- OpenAI for GPT-5 API
- Playwright team for browser automation framework
- The open-source community

---

**Made with ❤️ to help recruiters find real talent**
