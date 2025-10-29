# LinkedIn Fake Candidate Detector 🔍

> AI-powered LinkedIn profile analyzer that helps recruiters identify potentially fake or fraudulent candidate profiles using GPT-5 and browser automation.

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5-412991.svg)](https://openai.com/)

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
✅ **GPT-5 Powered Analysis** - Creates custom detection framework and evaluates profiles
✅ **Comprehensive Reports** - Risk assessment, red flags, authenticity signals
✅ **Multiple Input Methods** - Automated scraping, manual text input, or visible browser
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
# Analyze a LinkedIn profile
python linkedin_scanner.py https://www.linkedin.com/in/username

# Show browser window (useful for debugging/login)
python linkedin_scanner.py https://www.linkedin.com/in/username --show-browser

# Use manual text input (fallback method)
python linkedin_scanner.py https://www.linkedin.com/in/username --text-file profile.txt
```

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
   Loading page...
✓ Profile data collected

Step 2: Analyzing profile with gpt-5...
✓ Analysis complete

================================================================================
ANALYSIS REPORT
================================================================================

EVALUATION FRAMEWORK:
- Account age and creation indicators
- Profile completeness and detail quality
- Employment history timeline verification
- Education and credential validation
- Network size and engagement patterns
- Content originality vs template usage

RISK ASSESSMENT: HIGH

KEY RED FLAGS IDENTIFIED:
1. Profile created within last 30 days
2. Generic job descriptions with minimal detail
3. No recommendations or endorsements
4. Suspiciously low connection count (<50)
5. No activity history (posts, comments, likes)
6. Stock photo potentially used for profile picture

POSITIVE AUTHENTICITY SIGNALS:
- Email and phone number listed
- Education section completed

CONCERNS & RECOMMENDATIONS:
- Account age is a major concern - newly created profiles are often fake
- Request additional verification before proceeding
- Consider video interview to verify identity
- Check references independently

OVERALL CONCLUSION:
This profile exhibits multiple characteristics common to fake candidates.
The combination of new account age, generic content, and lack of engagement
suggests a high probability of fraudulent profile. Recommend thorough
verification before continuing recruitment process.

Confidence Level: 85%

================================================================================
```

---

## Command-Line Options

```
usage: linkedin_scanner.py [-h] [--api-key API_KEY] [--text-file TEXT_FILE]
                           [--show-browser] [--model MODEL]
                           url

positional arguments:
  url                   LinkedIn profile URL to analyze

options:
  -h, --help            show this help message and exit
  --api-key API_KEY     OpenAI API key (defaults to OPENAI_API_KEY env var)
  --text-file TEXT_FILE Text file containing profile data (bypasses scraping)
  --show-browser        Show browser window during scraping
  --model MODEL         OpenAI model to use (default: gpt-5)
```

### Examples

```bash
# Basic analysis
python linkedin_scanner.py https://www.linkedin.com/in/candidate

# Use specific model
python linkedin_scanner.py https://www.linkedin.com/in/candidate --model gpt-4o

# Provide API key explicitly
python linkedin_scanner.py https://www.linkedin.com/in/candidate --api-key sk-xxx

# Manual text input (if scraping fails)
python linkedin_scanner.py https://www.linkedin.com/in/candidate --text-file profile.txt

# Show browser for debugging
python linkedin_scanner.py https://www.linkedin.com/in/candidate --show-browser
```

---

## Batch Processing

To analyze multiple candidates:

```bash
# Create a file with LinkedIn URLs (one per line)
cat candidates.txt
https://www.linkedin.com/in/candidate1
https://www.linkedin.com/in/candidate2
https://www.linkedin.com/in/candidate3

# Process all profiles
while read url; do
  echo "Analyzing: $url"
  python linkedin_scanner.py "$url" >> results.txt
  sleep 5  # Avoid rate limiting
done < candidates.txt
```

---

## Important Considerations

### LinkedIn Access

- **Public Profiles**: Works best with publicly viewable profiles
- **Login Required**: Use `--show-browser` to manually log in if needed
- **Rate Limiting**: LinkedIn may block rapid requests - add delays between scans
- **Terms of Service**: Review LinkedIn's TOS before large-scale scraping

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

**Problem: LinkedIn blocking scraping**
- Use `--show-browser` flag
- Add delays between requests
- Use `--text-file` for manual input

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

⚠️ **Important Legal Notice**

This tool is for educational and legitimate recruitment purposes only. Users must:

- Comply with LinkedIn's Terms of Service
- Respect privacy laws and regulations (GDPR, CCPA, etc.)
- Obtain appropriate consent where required
- Use responsibly and ethically
- Not use for harassment, discrimination, or illegal purposes

The authors are not responsible for misuse of this tool. Fake profile detection is probabilistic - always verify findings through additional methods.

---

## Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/linkedin-fake-candidate-detector/issues)
- 💡 **Feature Requests**: Open an issue with the "enhancement" label
- 📧 **Contact**: your.email@example.com

---

## Acknowledgments

- OpenAI for GPT-5 API
- Playwright team for browser automation framework
- The open-source community

---

**Made with ❤️ to help recruiters find real talent**
