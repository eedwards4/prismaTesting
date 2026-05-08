from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from pathlib import Path
import output_handler
import subprocess
import datetime
import argparse
import time


def main():
    parser = argparse.ArgumentParser(description='A program for testing secure browsers against large common blocklists')
    # Global args
    parser.add_argument('-v', action='store_true', dest="verbose", help="Verbose mode.")
    parser.add_argument('-l', action='store_true', dest="log", help="Logging mode.")
    parser.add_argument('-n', action='store', dest="num_urls", help="The number of URLs to check per list. Default 100.")
    parser.add_argument('-d', action='store', dest="target_directory", help="Define a custom directory path for target files.")
    parser.add_argument('--t', nargs='+', required=True, dest="inputs", help="Mark the beginning of the target files.")
    parser.add_argument('-runas', action='store', required=True, dest='runAS', help="Define the target testing program. Options: 'ahk', 'webdriver'")

    # AutoHotKey args
    parser.add_argument('-ahk_dir', action='store', dest='autohotkey_path', help="Define a custom AutoHotKey executible path.")
    parser.add_argument('-ahk_tgt', action='store', dest='autohotkey_script', help="Define a custom AutoHotKey script target path.")

    args = parser.parse_args()
    list_files = args.inputs
    runAS = args.runAS
    stoppoint = 10
    total_unblocked = 0
    total_total = 0
    all_unblocked = []

    global AHK_SCRIPT
    global SRC_FILEPATH
    global AHK_PATH
    global VERBOSE
    global LOG

    # Global config
    SRC_FILEPATH = "{}\\lists".format(Path.cwd())
    VERBOSE = False
    LOG = False

    # AutoHotKey Config
    AHK_PATH = r"C:/Program Files/AutoHotkey/v2/AutoHotkey64.exe"
    AHK_SCRIPT = "./prisma_test.ahk"

    if args.autohotkey_path is not None: AHK_PATH = args.autohotkey_path
    
    if args.autohotkey_script is not None: AHK_SCRIPT = args.autohotkey_script
    
    if args.target_directory is not None: SRC_FILEPATH = args.target_directory
    
    if args.num_urls is not None: stoppoint = int(args.num_urls)
    
    if args.verbose: VERBOSE = True
    
    if args.log: LOG = True

    output = output_handler.OutputHandler(Path.cwd(), args.verbose, args.log, stoppoint, runAS, SRC_FILEPATH, AHK_PATH, AHK_SCRIPT)
    
    print("Begin testing run, time is currently {}".format(datetime.datetime.now()))

    start = time.perf_counter()

    for file in list_files:
        num_unblocked, num_total, unblocked_list = run_test("{}\\{}".format(SRC_FILEPATH, file), runAS, stoppoint, output)
        total_unblocked += num_unblocked
        total_total += num_total
        all_unblocked.append(unblocked_list)
    
    end = time.perf_counter()

    # Prettyprint
    output.finalOutput(total_unblocked, total_total, all_unblocked, start, end)


def urlStripper(line):
    line = line.strip()

    if line.startswith('#') or not line:
        url = "VOID"
    else:
        url = line.split(" ")[1]
        url = "https://{}".format(url)

    return url


# Test programs
def asAHK(url):
    # Run AHK script on URL
    subprocess.run([AHK_PATH, AHK_SCRIPT, url])
    
    file = open("{}/AppData/Local/Temp/ahk_output.txt".format(Path.home()))
    content = file.readline().strip()
    file.close()

    if not "TRUE" in content:
        return True
    
    return False

def asWEBDRVR(url, output):
    # Load extension (if extension)
    options = Options()
    options.add_argument(r"--user-data-dir=C:\\Users\\fts\\AppData\\Local\\Google\\Chrome\\User Data")
    options.add_argument("--remote-debugging-port=9222")
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    start = time.perf_counter()

    try:
        driver.get(url)
    except Exception as e:
        driver.execute_script("window.stop();")
        output.logException(str(e), start, time.perf_counter(), url)
        driver.quit()
        return False
    
    try:
        WebDriverWait(driver, 1).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    except Exception as e:
        output.logException(str(e), start, time.perf_counter(), url)
        driver.quit()
        return False   

    # time.sleep(5)

    output.write("{} || {} || ".format(driver.title, url), end="")

    whitelist = ("DefensX", "403", "Domain", "domain", "Not found.")
    target = True

    for i in whitelist:
        if i in driver.title:
            target = False

    if target:
        output.write("Elapsed: {}".format(datetime.timedelta(seconds=(time.perf_counter() - start))))
        driver.quit()
        return True
    
    output.write("Elapsed: {}".format(datetime.timedelta(seconds=(time.perf_counter() - start))))
    driver.quit()
    return False

def asTEST(url):
    return True


def run_test(filepath, runAS, stoppoint, output):
    num_unblocked = 0
    num_total = 0
    unblocked_list = []

    # Logging
    output.testInit(filepath)

    start = time.perf_counter()

    # Logic
    iterator = 0
    with open(filepath, 'r', encoding='utf8') as file:
        for line in file:
            if iterator < stoppoint:
                # Strip URL from line
                url = urlStripper(line)

                if url != "VOID":
                    match runAS:
                        case "ahk":
                            if asAHK(url):
                                num_unblocked += 1
                                unblocked_list.append(url)
                        
                        case "webdriver":
                            if asWEBDRVR(url, output):
                                num_unblocked += 1
                                unblocked_list.append(url)
                        
                        case "test":
                            if asTEST(url):
                                num_unblocked += 1
                                unblocked_list.append(url)
                
                    num_total += 1
                    iterator += 1
            else:
                break
    
    end = time.perf_counter()
    
    # More logging
    output.testOutput(num_unblocked, num_total, unblocked_list, start, end, filepath)

    return num_unblocked, num_total, unblocked_list


main()