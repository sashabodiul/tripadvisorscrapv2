import requests
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import time
import random
from selenium.webdriver.common.by import By

# Function to get geolocation data from IP address
def get_geolocation_from_ip(ip):
    response = requests.get(f'http://ip-api.com/json/{ip}')
    data = response.json()
    if data['status'] == 'success':
        return data['lat'], data['lon']
    else:
        raise Exception('Failed to get geolocation data for IP')

# Chrome options setup
opts = Options()

# Disable automation and extensions
opts.add_experimental_option("excludeSwitches", ["enable-automation"])
opts.add_experimental_option('useAutomationExtension', False)

# Set user agent to Chrome 126 on macOS
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
opts.add_argument(f'user-agent={user_agent}')


# Disable WebRTC to prevent IP leak
opts.add_argument("--disable-features=WebRTC-HW-Decoding,WebRTC-HW-Encoding,WebRTC-SupportMultipleTracks,WebRTC-SupportVP9")

# Proxy configuration
proxy_username = "sashabodiul07"
proxy_password = "7UMNo7iRr6"
proxy_address = "91.124.93.253"
proxy_port = "50100"
proxy_url = f"https://{proxy_username}:{proxy_password}@{proxy_address}:{proxy_port}"

# Selenium Wire options
seleniumwire_options = {
    'proxy': {
        'http': proxy_url,
        'https': proxy_url,
        'no_proxy': 'localhost,127.0.0.1'
    },
    'ssl_protocols': ['TLSv1', 'TLSv1.1', 'TLSv1.2', 'TLSv1.3']
}

# Initialize Chrome WebDriver with Selenium Wire and selenium-stealth
driver = webdriver.Chrome(
    options=opts,
    seleniumwire_options=seleniumwire_options,
)

# Apply stealth settings
stealth(driver,
    languages=["en-US", "en"],
    vendor="Apple Inc.",
    platform="MacIntel",
    webgl_vendor="Apple Inc.",
    renderer="Apple GPU",
    fix_hairline=True,
    run_on_insecure_origins=True
)

# Function to execute custom JavaScript for hiding WebDriver
def hide_webdriver(driver):
    driver.execute_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        delete navigator.__proto__.webdriver;
        delete navigator.webdriver;
    """)

def set_geolocation(lat, lon, accuracy=100):
    driver.execute_cdp_cmd('Page.enable', {})
    driver.execute_cdp_cmd('Emulation.setGeolocationOverride', {
        "latitude": lat,
        "longitude": lon,
        "accuracy": accuracy
    })

# Get geolocation data for the proxy IP address
latitude, longitude = get_geolocation_from_ip(proxy_address)
set_geolocation(latitude, longitude)

try:
    # Open the webpage and hide WebDriver
    driver.get('https://iphey.com/')
    hide_webdriver(driver)
    time.sleep(30)  # Random delay to simulate human behavior

    # Output cookies
    cookies = driver.get_cookies()
    print('Cookies:', cookies)

    # Output headers
    for request in driver.requests:
        print(request.headers)
        break

finally:
    # Close the browser
    driver.quit()