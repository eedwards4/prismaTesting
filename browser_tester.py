from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from pathlib import Path
import subprocess
import datetime
import argparse
import time
import csv


def main():
    parser = argparse.ArgumentParser(description='A program for testing secure browsers against large common blocklists')
    # Global args
    parser.add_argument('-v', action='store_true', dest="verbose", help="Verbose mode.")
    parser.add_argument('-d', action='store', dest="target_directory", help="Define a custom directory path for target files.")
    parser.add_argument('--t', nargs='+', required=True, dest="inputs", help="Mark the beginning of the target files.")
    parser.add_argument('-runas', action='store', required=True, dest='runAS', help="Define the target testing program. Options: 'ahk', 'webdriver'")

    # AutoHotKey args
    parser.add_argument('-ahk_dir', action='store', dest='autohotkey_path', help="Define a custom AutoHotKey executible path.")
    parser.add_argument('-ahk_tgt', action='store', dest='autohotkey_script', help="Define a custom AutoHotKey script target path.")

    args = parser.parse_args()
    list_files = args.inputs
    runAS = args.runAS
    total_unblocked = 0
    total_total = 0
    all_unblocked = []

    global AHK_SCRIPT
    global SRC_FILEPATH
    global AHK_PATH
    global VERBOSE
    VERBOSE = False

    # Global config
    SRC_FILEPATH = "{}\\lists".format(Path.cwd())

    # AutoHotKey Config
    AHK_PATH = r"C:/Program Files/AutoHotkey/v2/AutoHotkey64.exe"
    AHK_SCRIPT = "./prisma_test.ahk"

    if args.autohotkey_path is not None:
        AHK_PATH = args.autohotkey_path
    
    if args.autohotkey_script is not None:
        AHK_SCRIPT = args.autohotkey_script
    
    if args.target_directory is not None:
        SRC_FILEPATH = args.target_directory
    
    if args.verbose:
        VERBOSE = True

    print("Begin testing run, time is currently {}".format(datetime.datetime.now()))

    start = time.perf_counter()

    for file in list_files:
        num_unblocked, num_total, unblocked_list = run_test("{}\\{}".format(SRC_FILEPATH, file), runAS)
        total_unblocked += num_unblocked
        total_total += num_total
        all_unblocked.append(unblocked_list)
    
    end = time.perf_counter()

    # Prettyprint
    print("------------------------------------------------------")
    print("All tests complete, elapsed time {}".format(datetime.timedelta(seconds=(end - start))))
    print("Total URLs checked: {}".format(total_total))
    print("Total Undetected URLS: {}".format(total_unblocked))
    if total_total != 0:
        percent = (total_unblocked / total_total) * 100
    else:
        percent = 0
    print("{} percent of URLs were undetected.".format(percent))

    file = open("test-results-cumulative.txt", "w")
    print("Logging all undetected urls to test-results-cumulative.txt")
    print("All tests complete, elapsed time {}".format(datetime.timedelta(seconds=(end - start))), file=file)
    print("Total URLs checked: {}".format(total_total), file=file)
    print("Total Undetected URLS: {}".format(total_unblocked), file=file)
    print("{} percent of URLs were undetected.".format(percent), file=file)
    print("The following URLs were able to escape detection:", file=file)
    for site_list in all_unblocked:
        for site in site_list:
            print(site, file=file)


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

def asWEBDRVR(url):
    driver = webdriver.Chrome()
    start = 0
    if VERBOSE: start = time.perf_counter()

    try:
        driver.get(url)
    except:
        return False
    
    # WebDriverWait(DRIVER, 1).until(
    #     lambda d: d.execute_script("return document.readyState") == "complete"
    # )

    time.sleep(5)

    if VERBOSE: print("{} || {} || ".format(driver.title, url), end="")

    if not "DefensX" in driver.title:
        if VERBOSE: print("Elapsed: {}".format(datetime.timedelta(seconds=(time.perf_counter() - start))))
        driver.quit()
        return True
    
    if VERBOSE: print("Elapsed: {}".format(datetime.timedelta(seconds=(time.perf_counter() - start))))
    driver.quit()
    return False

def asTEST(url):
    return True


def run_test(filepath, runAS, stoppoint=100):
    num_unblocked = 0
    num_total = 0
    unblocked_list = []

    start = time.perf_counter()

    output = open("test-results-{}".format(filepath.split('\\')[-1]), "w")

    # Print statements for logging
    print("------------------------------------------------------")
    print("Running test for file: {}".format(filepath))
    print("------------------------------------------------------", file=output)
    print("Running test for file: {}".format(filepath), file=output)

    # Logic
    iterator = 0
    with open(filepath, 'r', encoding='utf8') as file:
        for line in file:
            if iterator <= stoppoint:
                # Strip URL from line
                url = urlStripper(line)

                if url != "VOID":
                    match runAS:
                        case "ahk":
                            if asAHK(url):
                                num_unblocked += 1
                                unblocked_list.append(url)
                        
                        case "webdriver":
                            if asWEBDRVR(url):
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
    print("Test complete, elapsed time {}".format(datetime.timedelta(seconds=(end - start))))
    print("Total URLs tested: {}".format(num_total))
    print("Undetected URLS: {}".format(num_unblocked))
    if num_total != 0:
        percent = (num_unblocked / num_total) * 100
    else:
        percent = 0
    print("{} percent of URLs were undetected.".format(percent))
    print("See test-results-{} for details on undetected sites".format(filepath.split('\\')[-1]))

    # Log to file
    print("Test complete, elapsed time {}".format(datetime.timedelta(seconds=(end - start))), file=output)
    print("Total URLs tested: {}".format(num_total), file=output)
    print("Undetected URLS: {}".format(num_unblocked), file=output)
    print("{} percent of URLs were undetected.".format(percent), file=output)
    print("The following URLs escaped detection:", file=output)
    for site in unblocked_list:
        print(site, file=output)
    
    output.close()
    file.close()

    return num_unblocked, num_total, unblocked_list


main()