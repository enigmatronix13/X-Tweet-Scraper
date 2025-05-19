# X Tweet Scraper

X Tweet Scraper is a scalable, keyword-based tweet scraping tool built using Python and Selenium. It automates login to X.com (formerly Twitter), searches for user-defined keywords, collects tweet data (usernames, text, timestamps), and stores the results in CSV format. The scraper supports continuous progress saving, duplicate filtering, and basic bot-detection evasion using human-like scrolling and randomized delays.

## Features

- Automates login to X.com using credentials
- Custom keyword search
- Extracts tweet text, user handle, timestamp
- Saves results incrementally and to CSV
- Redundant XPaths for UI resilience
- Randomized scrolling and delay to avoid detection

## Requirements

- Python 3.7+
- Firefox browser
- GeckoDriver (in system PATH)

Install dependencies via:

```bash
pip install -r requirements.txt
````

## Installation

```
git clone https://github.com/enigmatronix13/x-tweet-scraper.git
cd x-tweet-scraper
pip install -r requirements.txt
```

Download [GeckoDriver](https://github.com/mozilla/geckodriver/releases) and add it to your system PATH.

## Configuration

Edit the following in `main.py`:

```python
USERNAME = 'your_x_username'
PASSWORD = 'your_x_password'
MAX_TWEETS = 20000
OUTPUT_CSV = 'tweets.csv'

KEYWORDS = [
    "keyword1", "keyword2", "keyword3"
]
```

To run headless (without opening the browser):

```python
# options.add_argument('--headless')
```

## Usage

```bash
python main.py
```

It will:

1. Log in to X.com
2. Search for each keyword
3. Go to the "Latest" tab
4. Scroll and extract tweets
5. Save to CSV and progress files

## Output

Saved to `tweets.csv` with this format:

| keyword | user     | text                     | time                     |
| ------- | -------- | ------------------------ | ------------------------ |
| test    | @user123 | Example tweet text here. | 2025-05-19T13:45:00.000Z |

Progress is saved as: `tweets_progress_<index>.csv`

## Notes

* Use for research or educational purposes only.
* Avoid storing credentials in public repos.
* May require updates if X.com UI changes.

## License

Licensed under the [MIT License](LICENSE).
