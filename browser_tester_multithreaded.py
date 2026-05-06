from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from pathlib import Path
import subprocess
import threading
import datetime
import argparse
import time

def main():
    parser = argparse.ArgumentParser(description='A program for testing secure browsers against large common blocklists')
    # Global args
    parser.add_argument('-v', action='store_true', dest="verbose", help="Verbose mode.")
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
    
    if args.num_urls is not None:
        stoppoint = int(args.num_urls)
    
    if args.verbose:
        VERBOSE = True
        
    if VERBOSE: 
        print("Verbose mode enabled. Current configuration is as follows: ")
        print(">Stoppoint: {} \n>Running As: {} \n>Target Dir: {} \n>AutoHotKey: {} \n>AHK Script: {}".format(stoppoint, runAS, SRC_FILEPATH, AHK_PATH, AHK_SCRIPT))
        print("------------------------------------------------------")
    
    print("Begin testing run, time is currently {}".format(datetime.datetime.now()))

    start = time.perf_counter()

    for file in list_files:
        num_unblocked, num_total, unblocked_list = run_test("{}\\{}".format(SRC_FILEPATH, file), runAS, stoppoint)
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





def run_test(filepath, runAS, stoppoint):
    num_unblocked = 0
    num_total = 0
    unblocked_list = []

    start = time.perf_counter()

    

    end = time.perf_counter()

    return num_unblocked, num_total, unblocked_list