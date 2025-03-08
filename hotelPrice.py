import random
import time
import json
import os
import smtplib
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium_stealth import stealth  # Import stealth
from webdriver_manager.chrome import ChromeDriverManager

# Load environment variables from .env file
load_dotenv()

# === CONFIGURATION ===
HOTEL_URL = "https://uk.trip.com/hotels/detail/?cityId=1187&hotelId=2197664&checkIn=2025-04-28&checkOut=2025-04-29&adult=2&children=0&subStamp=684&crn=1&ages=&travelpurpose=0&curr=GBP"
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
APP_PASSWORD = os.getenv("APP_PASSWORD")  # Use the App Password

EMAIL_RECEIVERS = ["laurj032@gmail.com", "hate7577@gmail.com"]

# === FUNCTIONS ===

def start_driver():
    # Set up Chrome options
    chrome_options = Options()
    
    # 1. Run browser in non-headless mode to avoid detection
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")  # Set the window size

    # 2. Add custom User-Agent to simulate a real browser
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # 4. Disable Automation Flags to Prevent Bot Detection
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Set up the WebDriver with Chrome
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # === APPLY SELENIUM STEALTH ===
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    # Open the hotel URL
    driver.get(HOTEL_URL)
    print(f"🌍 Opening the page... Current URL: {driver.current_url}")

    # Wait for the page to load
    human_delay()

    # Check if we are on the login page
    if "signin" in driver.current_url or "backurl" in driver.current_url:
        print("🔐 Redirected to login page, attempting login...")

        try:
            # Find and fill the email field
            email_field = driver.find_element(By.XPATH, "//*[@id='ibu_login_online']/div/div/div/form/div/div[3]/div/div/input")
            email_field.send_keys(EMAIL_SENDER)
            print("📩 Email entered.")
            human_delay()

            # Click the continue button
            continue_button = driver.find_element(By.XPATH, "//*[@id='ibu_login_online']/div/div/div/form/div/button")
            continue_button.click()
            print("➡️ Continue button clicked.")
            human_delay()

            # Click "login with password"
            login_with_password_link = driver.find_element(By.XPATH, "//*[@id='ibu_login_submit']/span/span[2]")
            login_with_password_link.click()
            print("🔑 Clicked 'Login with password'.")
            human_delay()

            # Enter password
            password_field = driver.find_element(By.XPATH, "//*[@id='ibu_login_online']/div/div/div[2]/form/div/div[3]/div[2]/div/input")
            password_field.send_keys(APP_PASSWORD)  # Use the App Password here
            print("🔐 Password entered.")
            human_delay()

            # Click sign-in button
            sign_in_button = driver.find_element(By.XPATH, "//*[@id='ibu_login_online']/div/div/div[2]/form/div/button")
            sign_in_button.click()
            print("✅ Sign-in button clicked.")
            human_delay()

        except Exception as e:
            print(f"⚠️ Error during login: {e}")

    # Wait for the page to load
    human_delay()

    try:
        # Scrape the price from the specified XPath
        price_element = driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[1]/div[1]/div[2]/div/div[1]/div/div/span")
        price = price_element.text
        print(f"💰 Price found: {price}")
        
        # Send email if price is less than 500
        if float(price.replace("£", "").replace(",", "")) < 500:
            send_email(price)

    except Exception as e:
        print(f"⚠️ Error scraping price: {e}")

    # Close the driver
    driver.quit()

# === HELPER FUNCTIONS ===

# Random human-like delay
def human_delay():
    time.sleep(random.uniform(1.5, 3.0))

# Send email if price drops
def send_email(price):
    subject = f"🔥 Price Drop Alert! £{price} for Loews Portofino Bay Hotel"
    body = f"The price for your hotel has dropped to £{price}!\n\nBook now: {HOTEL_URL}"

    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = ", ".join(EMAIL_RECEIVERS)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # Use App Password for login if you have 2FA enabled
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, APP_PASSWORD)  # Use App Password here
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVERS, msg.as_string())
        server.quit()
        print(f"✉️ Email sent to {', '.join(EMAIL_RECEIVERS)}")
    except Exception as e:
        print(f"❌ Error Sending Email: {e}")

# Run the driver
start_driver()
