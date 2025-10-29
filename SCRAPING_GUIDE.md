# LinkedIn Scraping Improvements Guide

## What's New

The scraper has been significantly enhanced with:

### 1. **LinkedIn Authentication Support**
- Login with your LinkedIn credentials for better access
- Credentials stored in environment variables (secure)
- Session persistence - login once, use many times

### 2. **Persistent Browser Sessions**
- Browser sessions saved to `~/.linkedin_scanner/browser_data/`
- Stay logged in between runs
- Faster subsequent scans

### 3. **Automatic Retry Logic**
- Retries failed scrapes automatically (default: 2 retries)
- Configurable retry attempts
- Smart waiting between retries

### 4. **Better Content Extraction**
- Multiple extraction methods (fallback if one fails)
- Targets main content area first
- Increased content limit (10,000 characters)

### 5. **Debug Features**
- Automatic screenshot on failure
- Verbose error messages
- Shows extraction progress

### 6. **Anti-Detection Features**
- Removes automation flags
- Human-like timing
- Persistent context reduces suspicion

---

## How to Use LinkedIn Authentication

### Setup (One-time)

```bash
# Set your LinkedIn credentials as environment variables
export LINKEDIN_EMAIL='your-email@example.com'
export LINKEDIN_PASSWORD='your-password'

# Add to ~/.zshrc or ~/.bash_profile to persist:
echo "export LINKEDIN_EMAIL='your-email@example.com'" >> ~/.zshrc
echo "export LINKEDIN_PASSWORD='your-password'" >> ~/.zshrc
```

### Run with Login

```bash
# First run - logs in and saves session
python linkedin_scanner.py https://www.linkedin.com/in/candidate --login

# Subsequent runs - uses saved session (no login needed)
python linkedin_scanner.py https://www.linkedin.com/in/candidate2
python linkedin_scanner.py https://www.linkedin.com/in/candidate3
```

### Two-Factor Authentication (2FA)

If your LinkedIn account has 2FA enabled, the script will:
1. Detect the 2FA prompt automatically
2. Ask you to enter your 2FA code in the terminal
3. Submit the code for you

**Example flow:**
```bash
python linkedin_scanner.py https://www.linkedin.com/in/candidate --login

# Output:
   Logging into LinkedIn...
   ⚠️  Two-factor authentication required
   ✓ Found 2FA input field

============================================================
   ENTER YOUR TWO-FACTOR AUTHENTICATION CODE
============================================================
   Enter 2FA code: 123456    # <-- You type your code here

   Submitting 2FA code...
   ✓ 2FA code submitted
   ✓ Login successful!
```

**Supports:**
- SMS codes
- Authenticator app codes (Google Authenticator, Authy, etc.)
- Email verification codes

### Other Verification Methods

If LinkedIn asks for other verification (e.g., CAPTCHA):
```bash
# Use visible browser mode to complete verification manually
python linkedin_scanner.py https://www.linkedin.com/in/candidate --login --show-browser

# Complete the verification in the browser window
```

---

## Advanced Options

### Increase Retries
```bash
# Retry up to 5 times if scraping fails
python linkedin_scanner.py https://www.linkedin.com/in/candidate --retries 5
```

### Don't Save Session
```bash
# Login fresh each time (slower but more private)
python linkedin_scanner.py https://www.linkedin.com/in/candidate --login --no-session
```

### Debug Mode
```bash
# See browser, watch what's happening
python linkedin_scanner.py https://www.linkedin.com/in/candidate --show-browser

# With login
python linkedin_scanner.py https://www.linkedin.com/in/candidate --login --show-browser
```

---

## Troubleshooting

### Problem: "Login failed"
**Solutions:**
- Check credentials are correct
- Use `--show-browser` to see the error
- LinkedIn may require verification - complete it manually
- Try waiting a few minutes and retry

### Problem: Still getting blocked
**Solutions:**
- Add delays between profile scans (5-10 seconds)
- Use `--login` for authenticated access
- Don't scan too many profiles too quickly
- LinkedIn may have rate limited your IP - wait a few hours

### Problem: "No content extracted"
**Solutions:**
- Check the debug screenshot saved to current directory
- Try `--retries 5` for more attempts
- Use `--show-browser` to see what's loading
- Profile may require login - use `--login`

### Problem: Session expired
**Solutions:**
- Clear session: `rm -rf ~/.linkedin_scanner/browser_data/`
- Run again with `--login` to re-authenticate

---

## Session Management

### Where are sessions stored?
`~/.linkedin_scanner/browser_data/`

### Clear saved session:
```bash
rm -rf ~/.linkedin_scanner/browser_data/
```

### Check if logged in:
The script automatically checks and logs in if needed.

---

## Batch Processing with Login

```bash
# Set credentials
export LINKEDIN_EMAIL='your-email@example.com'
export LINKEDIN_PASSWORD='your-password'

# First profile - logs in
python linkedin_scanner.py https://www.linkedin.com/in/candidate1 --login >> results.txt
sleep 5

# Rest use saved session (faster)
while read url; do
  echo "Analyzing: $url"
  python linkedin_scanner.py "$url" >> results.txt
  sleep 5  # Be nice to LinkedIn
done < candidates.txt
```

---

## Security Notes

⚠️ **Important:**
- Credentials stored in environment variables (not in files)
- Never commit credentials to git
- Session data is local to your machine
- Use `--no-session` for shared computers
- Consider using a dedicated recruiter account

---

## Best Practices

1. **Start with login**: `--login` on first run of the day
2. **Add delays**: 5-10 seconds between profiles
3. **Monitor for blocks**: If you get errors, slow down
4. **Use retries**: `--retries 3` for reliability
5. **Debug when needed**: `--show-browser` if something's wrong
6. **Respect limits**: Don't scan hundreds at once
