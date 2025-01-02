from shlex import quote
import requests
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from datetime import datetime
from pymongo import MongoClient
import uuid  # Import uuid for unique ID generation
import os

# Environment Variables for Credentials
LOGIN_USERNAME = os.getenv('TWITTER_USERNAME'  "unername")
LOGIN_PASSWORD = os.getenv('TWITTER_PASSWORD'  "password")
if LOGIN_USERNAME is None or LOGIN_PASSWORD is None:
    print("Error: Twitter credentials are not set in the environment variables.")
      # Exit the function or script if credentials are not provided


# Proxy and User-Agent Pool
proxy_list = [
    {'proxy': '45.32.86.6:31280', 'username': 'Maachi', 'password': '%23Machi5500'},
    #{'proxy': '35.193.45.123:80', 'username': 'username2', 'password': 'password2'},
    {'proxy': '34.60.74.134:80'},
    {'proxy': '103.105.224.181:8083'}
]
user_agent_list = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
]

service = FirefoxService(GeckoDriverManager().install())

def get_proxy(proxy_config):
    return proxy_config['proxy']

def test_proxies(proxy_list):
    print("Testing proxies...\n")
    working_proxies = []

    for proxy_config in proxy_list:
        proxy = get_proxy(proxy_config)
        username = proxy_config.get('username')
        password = proxy_config.get('password')

        encoded_username = quote(username) if username else ''
        encoded_password = quote(password) if password else ''

        proxies = {
            "http": f"http://{encoded_username}:{encoded_password}@{proxy}" if username or password else f"http://{proxy}",
            "https": f"http://{encoded_username}:{encoded_password}@{proxy}" if username or password else f"http://{proxy}",
        }

        print(f"Testing proxy: {proxies['http']}")

        try:
            response = requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=10)
            response.raise_for_status()
            ip_info = response.json()
            print(f"Proxy: {proxy} is working. Public IP: {ip_info['ip']}")
            working_proxies.append(ip_info['ip'])
        except requests.exceptions.ProxyError:
            print(f"Proxy: {proxy} failed. Proxy authorization error.")
        except Exception as e:
            print(f"Proxy: {proxy} failed. Error: {e}")

    return working_proxies

def create_driver(proxy, user_agent):
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'--proxy-server={proxy}')
    options.add_argument(f'user-agent={user_agent}')

    try:
        return webdriver.Firefox(service=service, options=options)
    except Exception as e:
        print(f"Failed to initialize WebDriver: {e}")
        raise

def scrape_trends(driver, working_proxy):
    trends_with_proxy = []

    try:
        print("Navigating to login page...")
        driver.get("https://x.com/i/flow/login")
        time.sleep(random.uniform(2, 5))

        username_input = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "text")))
        username_input.send_keys(LOGIN_USERNAME)
        time.sleep(random.uniform(2, 4))
        next_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']")))
        next_button.click()
        time.sleep(random.uniform(2, 4))
        password_input = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.NAME, "password")))
        password_input.send_keys(LOGIN_PASSWORD)
        time.sleep(random.uniform(2, 4))
        login_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button div span span")))
        login_button.click()
        print("Login successful.")
        time.sleep(random.uniform(8, 12))

        driver.get("https://twitter.com/explore/tabs/trending")
        trending_topics = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@data-testid='trend']"))
        )

        for j, topic in enumerate(trending_topics):
            trend_text = topic.text
            trends_with_proxy.append(trend_text)
            print(f"Trend {j + 1}: {trend_text}")
            if j >= 4:  # Limit to 5 trends
                break

        unique_id = str(uuid.uuid4())

        client = MongoClient('mongodb://localhost:27017/')
        db = client['Last']
        collection = db['trends']

        # Insert into MongoDB
        collection.insert_one({
            'unique_id': unique_id,
            'trend_1': trends_with_proxy[0] if len(trends_with_proxy) > 0 else None,
            'trend_2': trends_with_proxy[1] if len(trends_with_proxy) > 1 else None,
            'trend_3': trends_with_proxy[2] if len(trends_with_proxy) > 2 else None,
            'trend_4': trends_with_proxy[3] if len(trends_with_proxy) > 3 else None,
            'trend_5': trends_with_proxy[4] if len(trends_with_proxy) > 4 else None,
            'timestamp': datetime.now(),
            'proxy_ip': working_proxy
        })
        print("Data successfully saved to MongoDB.")

    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        driver.save_screenshot("error_screenshot.png")

def main():
    working_proxies = test_proxies(proxy_list)

    if not working_proxies:
        print("No working proxies found.")
        return

    selected_proxy = working_proxies[0]
    user_agent = random.choice(user_agent_list)
    driver = create_driver(selected_proxy, user_agent)

    try:
        scrape_trends(driver, selected_proxy)
    except Exception as e:
        print(f"Failed to scrape trends. Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
