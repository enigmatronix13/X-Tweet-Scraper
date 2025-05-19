import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- CONFIG ---
USERNAME = 'your_x_username'
PASSWORD = 'your_x_password'
MAX_TWEETS = 20000
OUTPUT_CSV = 'tweets.csv'

# --- KEYWORDS ---
KEYWORDS = ["keyword1", "keyword2", "keyword3"]

def login(driver, wait):
    print("[+] Navigating to X.com...")
    driver.get("https://x.com/")
    time.sleep(3)  # Give page time to load
    
    try:
        # Find and click the login button
        login_buttons = [
            '//a[@href="/login"]',
            '//a[text()="Sign in"]',
            '//span[text()="Sign in"]/..',
            '//a[contains(@href, "signin")]'
        ]
        
        login_clicked = False
        for xpath in login_buttons:
            try:
                login_btn = driver.find_element(By.XPATH, xpath)
                login_btn.click()
                login_clicked = True
                print("[+] Clicked login button")
                break
            except:
                continue
                
        if not login_clicked:
            print("[!] Could not find login button")
            return False
            
        time.sleep(2)  # Wait for login form
        
        # Enter username
        username_field = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@autocomplete="username" or @name="text" or @type="text"]')))
        username_field.send_keys(USERNAME)
        username_field.send_keys(Keys.RETURN)
        print("[+] Entered username")
        time.sleep(3)  # Wait for password screen
        
        # Enter password - Try multiple selectors for password field
        try:
            pwd_field = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="password"]')))
        except:
            try:
                pwd_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
            except:
                pwd_field = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@autocomplete="current-password"]')))
        
        pwd_field.send_keys(PASSWORD)
        pwd_field.send_keys(Keys.RETURN)
        print("[+] Entered password")
        
        # Wait for home timeline to confirm login
        time.sleep(5)
        return True
        
    except Exception as e:
        print(f"[!] Login failed: {str(e)}")
        driver.save_screenshot("login_error.png")
        return False

def search_and_collect(driver, wait, keyword, max_tweets_per_keyword):
    tweets_collected = []
    seen_ids = set()
    
    try:
        # Navigate to explore page
        driver.get("https://x.com/explore")
        time.sleep(2)
        
        # Find and use search input
        search = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@enterkeyhint="search" or @placeholder="Search" or @aria-label="Search query"]')))
        search.clear()
        search.send_keys(keyword)
        search.send_keys(Keys.RETURN)
        time.sleep(3)  # Wait for search results
        
        # Switch to "Latest" tab for more diverse results
        try:
            latest_tab = driver.find_element(By.XPATH, '//span[text()="Latest"]/..')
            latest_tab.click()
            time.sleep(2)
        except:
            print("[!] Could not find Latest tab, continuing with default view")
        
        collected = 0
        attempts_without_new = 0
        
        # Keep scrolling until we collect enough tweets or hit too many attempts without new tweets
        while collected < max_tweets_per_keyword and attempts_without_new < 5:
            # Get tweets before scrolling
            pre_count = len(seen_ids)
            
            # Find tweets
            tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet" or @role="article"]')
            
            # Process each tweet
            for tweet in tweets:
                try:
                    user = tweet.find_element(By.XPATH, './/span[contains(text(), "@")]').text
                    
                    # Try multiple XPaths for tweet text
                    try:
                        text = tweet.find_element(By.XPATH, './/div[@lang]').text
                    except:
                        try:
                            text = tweet.find_element(By.XPATH, './/div[contains(@class, "css-")]').text
                        except:
                            continue  # Skip if we can't get the text
                            
                    try:
                        timestamp = tweet.find_element(By.XPATH, './/time').get_attribute("datetime")
                    except:
                        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S.000Z")  # Use current time if timestamp not found
                    
                    tweet_id = f"{user}_{timestamp}"
                    
                    # Skip if we've seen this tweet already
                    if tweet_id in seen_ids:
                        continue
                        
                    seen_ids.add(tweet_id)
                    
                    # Check if keyword is in tweet text (case insensitive)
                    if keyword.lower() in text.lower():
                        tweets_collected.append({
                            "keyword": keyword,
                            "user": user,
                            "text": " ".join(text.split()),  # Normalize whitespace
                            "time": timestamp
                        })
                        collected += 1
                        
                        if collected >= max_tweets_per_keyword:
                            break
                            
                except Exception as e:
                    continue  # Skip problematic tweets
            
            print(f"[+] {keyword}: Collected {collected}/{max_tweets_per_keyword}")
            
            # Scroll down to get more tweets
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1, 3))  # Random wait to appear more human-like
            
            # Check if we found any new tweets in this scroll
            if len(seen_ids) == pre_count:
                attempts_without_new += 1
            else:
                attempts_without_new = 0
                
    except Exception as e:
        print(f"[!] Error collecting tweets for '{keyword}': {str(e)}")
        
    return tweets_collected

def main():
    # Initialize variables to track progress
    all_tweets = []
    tweets_per_keyword = MAX_TWEETS // len(KEYWORDS)
    if tweets_per_keyword < 20:
        tweets_per_keyword = 20  # Minimum tweets per keyword
        
    options = webdriver.FirefoxOptions()
    # Comment out for debugging - seeing the browser helps troubleshoot
    # options.add_argument('--headless')
    
    print("[+] Starting browser...")
    driver = webdriver.Firefox(options=options)
    driver.set_window_size(1280, 900)  # Larger window size
    wait = WebDriverWait(driver, 15)
    
    try:
        # Login to Twitter/X
        if not login(driver, wait):
            print("[!] Login failed. Exiting.")
            driver.quit()
            return
            
        print("[+] Successfully logged in!")
        
        # Process keywords in batches to avoid pattern detection
        random.shuffle(KEYWORDS)  # Randomize order
        
        for i, keyword in enumerate(KEYWORDS):
            print(f"\n[{i+1}/{len(KEYWORDS)}] Processing: {keyword}")
            tweets = search_and_collect(driver, wait, keyword, tweets_per_keyword)
            all_tweets.extend(tweets)
            
            # Save progress after each keyword
            if all_tweets:
                temp_df = pd.DataFrame(all_tweets)
                temp_df.to_csv(f"tweets_progress_{i+1}.csv", index=False)
                
            # Random delay between keywords to avoid detection
            time.sleep(random.uniform(3, 8))
            
            # Check if we've collected enough total tweets
            if len(all_tweets) >= MAX_TWEETS:
                print(f"[+] Reached target of {MAX_TWEETS} tweets. Stopping.")
                break
                
        # Save final results
        if all_tweets:
            df = pd.DataFrame(all_tweets)
            df.drop_duplicates(subset=['user', 'time'], inplace=True)  # Remove any duplicates
            df.to_csv(OUTPUT_CSV, index=False)
            print(f"\n[✓] Done! Collected {len(df)} unique tweets → {OUTPUT_CSV}")
        else:
            print("[!] No tweets collected.")
            
    except Exception as e:
        print(f"[!] Unexpected error: {str(e)}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
