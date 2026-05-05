# A program to open crab rave until your browser crashes :)
from pathlib import Path
import subprocess
import datetime
import psutil
import time

AHK_PATH = "C:\\Program Files\\AutoHotkey\\v2\\AutoHotkey64.exe"
AHK_SCRIPT = "./load_test.ahk"


def is_process_running(process_name):
    for proc in psutil.process_iter(['name']):
        try:
            if process_name.lower() in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def get_num_prisma_processes():
    count = 0
    for proc in psutil.process_iter(['name']):
        try:
            if "PrismaAccessBrowser.exe" in proc.info['name']:
                count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return count


def run_test():
    print("Beginning load test at {}".format(datetime.datetime.now()))
    start = time.perf_counter()
    baseCount = get_num_prisma_processes() # The number of Prisma processes running before the test starts
    count = 0 # The number of Prisma processes that have been opened by the test
    print(f"{baseCount} Prisma processes were already running before the test started.")
    while is_process_running("PrismaAccessBrowser.exe") and psutil.virtual_memory().percent < 95:
        subprocess.run([AHK_PATH, AHK_SCRIPT])
        count = get_num_prisma_processes() - baseCount
        print(f"{count} Prisma processes opened so far...") # Redundancy in case prisma doesn't crash before the system runs out of memory and the test is killed manually
    
    end = time.perf_counter()

    print(f"Load test complete. {count} Prisma processes were opened before the program crashed or was killed manually.")
    print(f"Elapsed time: {datetime.timedelta(seconds=(end-start))} seconds")


def main():
    run_test()

if __name__ == "__main__":
    main()