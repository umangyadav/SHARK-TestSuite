import os, sys, argparse, tabulate, pickle


def loadTable(reportpkl):
    table = None
    if os.path.exists(reportpkl):
        with open(reportpkl, "rb") as pkf:
            table = pickle.load(pkf)
        pkf.close()
    return table


def checkAndGetHeader(headers):
    retheader = None
    # Check if headers match, else cannot process
    for i, item in enumerate(headers):
        for j in range(i + 1, len(headers)):
            if headers[i] != headers[j]:
                print(f"The headers of reports in given run dirs differ.")
                print(
                    f"One of them had: {headers[i]}\nWhile the other had:{headers[j]}"
                )
                sys.exit(1)
    # pick one of the headers as merged header to be build
    if len(headers) > 0:
        retheader = headers[0]
    return retheader


def createMergedHeader(runnames, oneheader):
    mergedheader = ["test-name"]
    for i in range(len(oneheader)):
        for run in runnames:
            columnname = oneheader[i] + "-" + run
            mergedheader += [columnname]
    return mergedheader


def createMergedRows(runnames, reportdict, headerlen):
    mergedrows = []
    for test, dictOfRuns in reportdict.items():
        merged = [test]
        listOfRuns = []
        for run in runnames:
            if dictOfRuns.get(run):
                listOfRuns += [dictOfRuns[run]]
            else:
                listOfRuns += [["NA" for i in range(headerlen)]]

        # zip creates a tuple by taking same index value from each of the
        # unpacked (using * operator) run in listOfRuns
        for runs in zip(*listOfRuns):
            merged.extend(runs)

        mergedrows += [merged]

    return mergedrows


def addToDict(reportdict, reportpkl, runname):
    table = loadTable(reportpkl)
    # skip test name, hence from 1
    header = [table[0][1:]]
    # skip table header, hence index from 1
    for i in range(1, len(table)):
        testname = table[i][0]
        # Add to dictionary of testname to dictionary of run name
        if reportdict.get(testname):
            reportdict[testname][runname] = table[i][1:]
        else:
            reportdict[testname] = {runname: table[i][1:]}

    return header


if __name__ == "__main__":
    msg = "The script to diff and combine reports generated by e2eshark run.pl"
    parser = argparse.ArgumentParser(description=msg, epilog="")
    parser.add_argument(
        "inputdirs",
        nargs="*",
        help="Input test run directory names",
    )
    parser.add_argument(
        "-d",
        "--do",
        choices=["diff", "merge"],
        default="merge",
        help="Merge the reports in two directories to create or diff the two reports",
    )
    parser.add_argument(
        "-f",
        "--reportformat",
        choices=["pipe", "github", "html", "csv"],
        default="pipe",
        help="Format of the test report summary file. It takes subset of tablefmt value of python tabulate",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Write merged outout into this file. Default is to display on stdout.",
    )
    parser.add_argument(
        "-t",
        "--type",
        choices=["status", "time"],
        default="status",
        help="Process status report vs time report",
    )

    args = parser.parse_args()
    if args.do == "diff":
        print(f"Ability to diff reports is not implemented yet.")
        sys.exit(1)
    dirlist = args.inputdirs
    reportdict = {}
    allheaders = []
    runnames = []
    mergedreportfilename = ""

    for item in dirlist:
        rundir = os.path.abspath(item)
        runname = os.path.basename(rundir)
        runnames += [runname]
        if not os.path.exists(rundir):
            print("The given file ", rundir, " does not exist\n")
            sys.exit(1)
        if args.type == "time":
            reportpkl = rundir + "/timereport.pkl"
        else:
            reportpkl = rundir + "/statusreport.pkl"

        if not os.path.exists(reportpkl):
            print(f"{reportpkl} does not exist. This report will be ignored.")
            continue
        allheaders += addToDict(reportdict, reportpkl, runname)

    oneheader = checkAndGetHeader(allheaders)
    # Create merged header
    mergedheader = createMergedHeader(runnames, oneheader)
    mergedrows = createMergedRows(runnames, reportdict, len(oneheader))
    mergedtable = tabulate.tabulate(
        mergedrows, headers=mergedheader, tablefmt=args.reportformat
    )
    outf = sys.stdout
    if args.output:
        outf = open(args.output, "w")
    print(mergedtable, file=outf)

    sys.exit(0)