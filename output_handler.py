import datetime


class OutputHandler:
    def __init__(self, cwd, verbose, log, stoppoint, runAS, srcFilepath, ahkPath, ahkScript):
        self.cwd = cwd
        self.vebose = verbose
        self.log = log
        self.logfilename = "log-{}.txt".format(datetime.datetime.now())

        if self.verbose:
            print("Verbose mode enabled. Current configuration is as follows: ")
            print(">Stoppoint: {} \n>Running As: {} \n>Target Dir: {} \n>AutoHotKey: {} \n>AHK Script: {}".format(stoppoint, runAS, srcFilepath, ahkPath, ahkScript))
            print("------------------------------------------------------")
        
        if self.log:
            self.logfile = open(self.logfilename, 'w')
            print("Logging mode enabled. Output at {}/{}".format(self.cwd, self.logfilename))
            print("------------------------------------------------------")


    def testInit(filepath):
        output = open("test-results-{}".format(filepath.split('\\')[-1]), "w")
        print("------------------------------------------------------")
        print("Running test for file: {}".format(filepath))
        print("------------------------------------------------------", file=output)
        print("Running test for file: {}".format(filepath), file=output)
        output.close()


    def testOutput(unblocked, total, ubList, startTime, endTime, filepath):
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


    def finalOutput(unblocked, total, ubList, startTime, endTime):
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