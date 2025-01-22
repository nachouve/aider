# I want a function to use in `aider\sendchat.py` that:
# . - receives a `plain_message` text
# . - opens the web "https://chat.lmsys.org/?__cf_chl_rt_tk=5KaIqnAUV07yCQ_8wE49XTWSD983eRPq4P_qjylu8EE-1715428814-0.0.1.1-1471"
# . - Enters the text in a textarea with placeholder that contains "Enter your prompt and press ENTER"
# . - Press button with text "Send"
# . - Waits for the response of the first div.id = "chatbot", and print in console

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def send_chat_message(plain_message):
    # Initialize the Chrome driver
    driver = webdriver.Chrome()

    # Open the web page
    driver.get("https://chat.lmsys.org/?__cf_chl_rt_tk=5KaIqnAUV07yCQ_8wE49XTWSD983eRPq4P_qjylu8EE-1715428814-0-0.1.1-1471")

    # Find the textarea with the placeholder "Enter your prompt and press ENTER"
    textarea = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Enter your prompt and press ENTER']"))
    )

    # Enter the message in the textarea
    textarea.send_keys(plain_message)

    # Find the "Send" button and click it
    send_button = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//button[text()='Send']"))
    )
    send_button.click()

    # Wait for the response to appear in the div with id "chatbot"
    response_div = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "chatbot"))
    )

    # Print the response in the console
    response_text = response_div.text
    print(response_text)

    # Close the browser
    driver.quit()

if __name__ == '__main__':
    send_chat_message("Hello, how are you?")