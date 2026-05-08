from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time

def main():
    options = Options()
    options.add_argument(r"--user-data-dir=C:\\Users\\ethan.edwards\\AppData\\Local\\Google\\Chrome\\User Data")
    # options.add_argument('--headless') # TODO: TEST THIS, MIGHT BE ABLE TO SPEED TESTING UP SIGNIFICANTLY
    # options.add_argument('--disable-features=DisableLoadExtensionCommandLineSwitch')
    # options.add_argument('--load-extension=\\Users\\ethan.edwards\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Extensions\\kdgfdpfnfmmedmkakcfckhblalhincph\\4.3.187_0')

    driver = webdriver.Chrome(options=options)

    try:
        driver.get("chrome-extension://kdgfdpfnfmmedmkakcfckhblalhincph/index.html#/dashboard")
        time.sleep(50)
        print("Extension loaded successfully.")
    except:
        driver.execute_script("window.stop();")
        driver.quit()
        print("Failed to load extension.")
    
    return


if __name__ == "__main__":
    main()