#!/usr/bin/env python
# encoding: utf-8
"""
learn_cuckoo.py

Created by Philipp Trinius on 2013-11-10.
Copyright (c) 2013 pi-one.net .
Modified and updated by Navein Chanderan & Chang Si Ju on 2017-11-01.

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or (at your option)
any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program; if not, see <http://www.gnu.org/licenses/>


version 0.2 : Edited by Paolo Di Prodi on 2013-11-13; Progress Bar inserted.

"""

__author__ = "philipp trinius, navein chanderan, chang si ju"
__version__ = "0.3"


import os
import json
import sys
import re
import glob
import argparse


class progressBar:
    """ Creates a text-based progress bar. Call the object with the `print'
        command to see the progress bar, which looks something like this:

        [=======>        22%                  ]

        You may specify the progress bar's width, min and max values on init.
    """
    def __init__(self, minValue = 0, maxValue = 100, totalWidth=80):
        self.progBar = "[]"   # This holds the progress bar string
        self.min = minValue
        self.max = maxValue
        self.span = maxValue - minValue
        self.width = totalWidth
        self.amount = 0       # When amount == max, we are 100% done
        self.updateAmount(0)  # Build progress bar string
        self._old_pbar = ""   # used to track change
        self.pbar_str = ""

    def updateAmount(self, newAmount = 0):
        """ Update the progress bar with the new amount (with min and max
            values set at initialization; if it is over or under, it takes the
            min or max value as a default. """
        if newAmount > self.max: newAmount = self.max
        self.amount = newAmount

        # Figure out the new percent done, round to an integer
        diffFromMin = float(self.amount - self.min)
        percentDone = (diffFromMin / float(self.span)) * 100.0
        percentDone = int(round(percentDone))

        # Figure out how many hash bars the percentage should be
        allFull = self.width - 2
        numHashes = (percentDone / 100.0) * allFull
        numHashes = int(round(numHashes))

        # Build a progress bar with an arrow of equal signs; special cases for
        # empty and full
        if numHashes == 0:
            self.progBar = "[>%s]" % (' '*(allFull-1))
        elif numHashes == allFull:
            self.progBar = "[%s]\n" % ('='*allFull)
        else:
            self.progBar = "[%s>%s]" % ('='*(numHashes-1),
                                        ' '*(allFull-numHashes))

        # figure out where to put the percentage, roughly centered
        percentPlace = (len(self.progBar) / 2) - len(str(percentDone))
        percentString = str(percentDone) + "%"

        # slice the percentage into the bar
        self.progBar = ''.join([self.progBar[0:percentPlace], percentString,
                                self.progBar[percentPlace+len(percentString):]
                                ])

    def __str__(self):
        return str(self.progBar)

    def __call__(self, value):
        """ Updates the amount, and writes to stdout. Prints a carriage return
            first, so it will overwrite the current line in stdout."""

        self.updateAmount(value)
        self.pbar_str = str(self)
        if self.pbar_str != self._old_pbar:
            self._old_pbar = self.pbar_str
            sys.stdout.write(self.pbar_str + "\r")
            sys.stdout.flush()

def get_options_and_arguments(program_arguments):
    """ Builds and parse the program arguments and the help to print to console
        :returns: list of arguments
    """
    options, arguments = [], []
    parser=argparse.ArgumentParser(description="""Info: Learn from cuckoo report outputs.""",
                                    epilog="Copyright (c) 2013 pi-one.net ")

    parser.add_argument('file', help="Load from a cuckoo folder",type=str)
    arguments=parser.parse_args(program_arguments)

    if not program_arguments:
        parser.print_help()
        sys.exit(1)
    else:
        return arguments

def run_parser(folder):

    learn_reports = {}
    learn_reports['filesystem'] = {}
    learn_reports['device'] = {}
    learn_reports['services'] = {}
    learn_reports['synchronization'] = {}
    learn_reports['registry'] = {}
    learn_reports['process'] = {}
    learn_reports['network'] = {}
    learn_reports['system'] = {}
    learn_reports['threading'] = {}
    learn_reports['windows'] = {}
    learn_reports['socket'] = {}
    learn_reports['sleep'] = {}
    learn_reports['hooking'] = {}

    i = 0
    for top, dirs, files in os.walk(folder):

        for nm in files:
            try:
                if nm == "report.json":

                    report = os.path.join(top, nm)
                    i += 1
                    print "Processing report number %i (%s) \n" % (i, report)

                    fp = open(report, 'r')
                    jo = json.load(fp)
                    fp.close()

                    sortCalls = {}
                    procs = jo['behavior']['processes']
                    counter = 0
                    if len(procs)>0:
                        progress=progressBar(minValue=0,maxValue=len(procs))
                    for proc in procs:
                        calls = proc['calls']
                        progress(counter)
                        counter+=1
                        for call in calls:
                            sortCalls[call['timestamp']] = (
                                call['category'], call['api'], call['arguments'])
                            for item in sorted(sortCalls.iterkeys()):
                                try:
                                    l = len(
                                        learn_reports[sortCalls[item][0]][sortCalls[item][1]])
                                except:
                                    learn_reports[sortCalls[item][0]][
                                        sortCalls[item][1]] = {}
                                for arg in sortCalls[item][2]:
                                    try:
                                        learn_reports[sortCalls[item][0]][
                                            sortCalls[item][1]][arg['name']][arg['value']] += 1
                                    except:
                                        try:
                                            learn_reports[sortCalls[item][0]][
                                                sortCalls[item][1]][arg['name']][arg['value']] = 1
                                        except:
                                            learn_reports[sortCalls[item][0]][
                                                sortCalls[item][1]][arg['name']] = {}
                                            learn_reports[sortCalls[item][0]][
                                                sortCalls[item][1]][arg['name']][arg['value']] = 1
                    k = i % 10
                    json.dump(learn_reports, open(
                        str(k) + "_learned_from_reports.json", 'wb'))
                    json.dump(learn_reports, open(
                        str(k) + "_learned_from_reports_pretty.json", 'wb'), sort_keys=False,indent=4, separators=(',', ': '))
            except KeyboardInterrupt:
                print("Interrupted scan processed %d " % i)
                sys.exit()
def main():

    try:
        arguments = get_options_and_arguments(sys.argv[1:])
        if arguments.file:
            if os.path.exists(arguments.file):
                run_parser(arguments.file)
            else:
                print "Folder provided does not exists "
                sys.exit()
    except:
        raise

if __name__ == '__main__':
    main()