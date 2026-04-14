from pathlib import Path
import subprocess
import datetime
import time
import csv

AHK_PATH = r"C:/Program Files/AutoHotkey/v2/AutoHotkey64.exe"
SCRIPT = "./prisma_test.ahk"

URLS = []


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
    subprocess.run([AHK_PATH, SCRIPT, url])
    
    file = open("{}/AppData/Local/Temp/ahk_output.txt".format(Path.home()))
    content = file.readline().strip()
    file.close()

    if not "TRUE" in content:
        return True
    
    return False


def run_test(filepath):
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
    with open(filepath, 'r', encoding='utf8') as file:
        for line in file:
            # Strip URL from line
            url = urlStripper(line)

            if url != "VOID":
                if asAHK(url):
                    num_unblocked += 1
                    unblocked_list.append(url)
                
                num_total += 1
    
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
    print("Test complete", file=output)
    print("Total URLs tested: {}".format(num_total), file=output)
    print("Undetected URLS: {}".format(num_unblocked), file=output)
    print("{} percent of URLs were undetected.".format(percent), file=output)
    print("The following URLs escaped detection:", file=output)
    for site in unblocked_list:
        print(site, file=output)
    
    output.close()
    file.close()

    return num_unblocked, num_total, unblocked_list


def main():
    list_files = ["gambling.txt"]

    total_unblocked = 0
    total_total = 0
    all_unblocked = []

    print("Begin testing run, time is currently {}".format(datetime.datetime.now()))
    start = time.perf_counter()

    for file in list_files:
        num_unblocked, num_total, unblocked_list = run_test("{}\\lists\\{}".format(Path.cwd(), file))

        total_unblocked += num_unblocked
        total_total += num_total
        all_unblocked.append(unblocked_list)
    
    end = time.perf_counter()

    # Prettyprint
    print("------------------------------------------------------")
    print("All tests complete, elapsed time {} seconds".format(datetime.timedelta(seconds=(end - start))))
    print("Total URLs checked: {}".format(total_total))
    print("Total Undetected URLS: {}".format(total_unblocked))
    if total_total != 0:
        percent = (total_unblocked / total_total) * 100
    else:
        percent = 0
    print("{} percent of URLs were undetected.".format(percent))

    file = open("test-results-cumulative.txt", "w")
    print("Logging all undetected urls to test-results-cumulative.txt")
    print("The following URLs were able to escape detection:", file=file)
    for site_list in all_unblocked:
        for site in site_list:
            print(site, file=file)


main()