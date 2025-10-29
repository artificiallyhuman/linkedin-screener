# LinkedIn Profile Fake Candidate Detector

A Python tool that analyzes LinkedIn profiles to detect potential fake candidates using GPT-5 and Playwright for real browser automation.

## Features

- Directly scrapes LinkedIn profile URLs using real browser automation (Playwright)
- Uses GPT-5 to create a custom framework for fake profile detection
- Provides detailed terminal-based reports with risk assessment
- Identifies specific red flags and authenticity signals
- Handles JavaScript-rendered content properly
- Optional visible browser mode for debugging

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

3. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Usage

### Method 1: Direct Scraping with Playwright (Recommended)
```bash
python linkedin_scanner.py https://www.linkedin.com/in/username
```

### Method 2: Visible Browser Mode (for debugging or login)
```bash
python linkedin_scanner.py https://www.linkedin.com/in/username --show-browser
```

This shows the browser window, useful if you need to:
- Debug what's being scraped
- Manually handle login prompts
- See why scraping might be failing

### Method 3: Manual Text Input (fallback)
If automated scraping is blocked:
1. Visit the LinkedIn profile in your browser
2. Copy all visible text from the profile
3. Save it to a text file (e.g., `profile.txt`)
4. Run the scanner:
```bash
python linkedin_scanner.py https://www.linkedin.com/in/username --text-file profile.txt
```

### Advanced Options
```bash
# Use a specific model
python linkedin_scanner.py https://www.linkedin.com/in/username --model gpt-4o

# With explicit API key
python linkedin_scanner.py https://www.linkedin.com/in/username --api-key YOUR_KEY

# Combine options
python linkedin_scanner.py https://www.linkedin.com/in/username --show-browser --model gpt-5
```

## Important Notes

### LinkedIn Access

This tool uses Playwright to access LinkedIn with a real browser. However:

- **Public Profiles**: Works best with public profiles viewable without login
- **Login Required**: If LinkedIn requires login, use `--show-browser` to manually log in
- **Rate Limiting**: LinkedIn may temporarily block if you scan too many profiles rapidly
- **Authentication**: Consider using Playwright's persistent context to save login sessions

### GPT-5 Model

The script defaults to GPT-5. If GPT-5 is not yet available in your OpenAI account:
- The script will automatically fall back to GPT-4o
- You can explicitly specify a model with `--model gpt-4o`
- Check OpenAI's documentation for the latest available models

## Output

The tool provides:
- Risk Assessment (Low/Medium/High)
- Key red flags identified
- Positive authenticity signals
- Specific concerns and recommendations
- Overall conclusion with detailed reasoning

## Requirements

- Python 3.7+
- OpenAI API key
- Internet connection
