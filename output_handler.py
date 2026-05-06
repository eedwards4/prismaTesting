import datetime
import threading


class OutputHandler:
    def __init__(self, cwd, verbose, log, stoppoint, runAS, srcFilepath, ahkPath, ahkScript):
        self.cwd = cwd
        self.verbose = verbose
        self.log = log
        self.logfilename = "log-{}.txt".format(datetime.datetime.now()).replace(" ", "_").replace(":", "-").replace(".", "-")
        self.vbsLock = threading.Lock()
        self.logLock = threading.Lock()

        if self.verbose:
            print("Verbose mode enabled. Current configuration is as follows: ")
            print(">Stoppoint: {} \n>Running As: {} \n>Target Dir: {} \n>AutoHotKey: {} \n>AHK Script: {}".format(stoppoint, runAS, srcFilepath, ahkPath, ahkScript))
            print("------------------------------------------------------")
        
        if self.log:
            self.logfile = open(self.logfilename, 'w')
            print("Logging mode enabled. Output at {}/{}".format(self.cwd, self.logfilename))
            print("------------------------------------------------------")


    def write(self, message, end="\n"):
        if self.verbose:
            with self.vbsLock:
                print(message, end=end)

        if self.log:
            with self.logLock:
                self.logfile.write(message + "\n")
                self.logfile.flush()
    

    def logException(self, exception, start, end, url):
        if self.verbose or self.log:
            if "net:ERR_NAME_NOT_RESOLVED" in exception:
                self.write("Ignored Name Resolution Error || {} || Elapsed: {}".format(url, datetime.timedelta(seconds=(end - start))))
            elif "Message: timeout:" in exception:
                self.write("Ignored Renderer Timeout || {} || Elapsed: {}".format(url, datetime.timedelta(seconds=(end - start))))
            elif "selenium.common.exceptions.TimeoutException:" in exception:
                self.write("Ignored Timeout Exception || {} || Elapsed: {}".format(url, datetime.timedelta(seconds=(end - start))))
            else:
                self.write("{} || WARN: Encountered the following error: \n {}".format(url, exception))


    def testInit(self, filepath):
        output = open("test-results-{}".format(filepath.split('\\')[-1]), "w")
        print("------------------------------------------------------")
        print("Running test for file: {}".format(filepath))
        print("------------------------------------------------------", file=output)
        print("Running test for file: {}".format(filepath), file=output)
        output.close()


    def testOutput(self, unblocked, total, ubList, startTime, endTime, filepath):
        output = open("test-results-{}".format(filepath.split('\\')[-1]), "w")

        print("Test complete, elapsed time {}".format(datetime.timedelta(seconds=(endTime - startTime))))
        print("Total URLs tested: {}".format(total))
        print("Undetected URLS: {}".format(unblocked))
        if total != 0:
            percent = (unblocked / total) * 100
        else:
            percent = 0
        print("{} percent of URLs were undetected.".format(percent))
        print("See test-results-{} for details on undetected sites".format(filepath.split('\\')[-1]))

        # Log to file
        print("Test complete, elapsed time {}".format(datetime.timedelta(seconds=(endTime - startTime))), file=output)
        print("Total URLs tested: {}".format(total), file=output)
        print("Undetected URLS: {}".format(unblocked), file=output)
        print("{} percent of URLs were undetected.".format(percent), file=output)
        print("The following URLs escaped detection:", file=output)
        for site in ubList:
            print(site, file=output)
        
        output.close()


    def finalOutput(self, unblocked, total, ubList, startTime, endTime):
        print("------------------------------------------------------")
        print("All tests complete, elapsed time {}".format(datetime.timedelta(seconds=(endTime - startTime))))
        print("Total URLs checked: {}".format(total))
        print("Total Undetected URLS: {}".format(unblocked))
        if total != 0:
            percent = (unblocked / total) * 100
        else:
            percent = 0
        print("{} percent of URLs were undetected.".format(percent))

        file = open("test-results-cumulative.txt", "w")
        print("Logging all undetected urls to test-results-cumulative.txt")
        print("All tests complete, elapsed time {}".format(datetime.timedelta(seconds=(endTime - startTime))), file=file)
        print("Total URLs checked: {}".format(total), file=file)
        print("Total Undetected URLS: {}".format(unblocked), file=file)
        print("{} percent of URLs were undetected.".format(percent), file=file)
        print("The following URLs were able to escape detection:", file=file)
        for site_list in ubList:
            for site in site_list:
                print(site, file=file)
        
        file.close()