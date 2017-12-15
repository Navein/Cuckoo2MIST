#!/usr/bin/env python
# encoding: utf-8
"""
cuckoo2mist.py

Created by Dr. Philipp Trinius on 2013-11-10.
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
"""

from __future__ import print_function

__author__ = "philipp trinius, navein chanderan, chang si ju"
__version__ = "0.4"

import os
import sys
import time
import argparse
import logging
import xml.etree.ElementTree as ET
from thread_mist import MISTThread

CUCKOO2MIST_DIR = os.path.dirname(os.path.abspath(__file__))

logger = logging.getLogger()

def read_configuration(confdir="conf"):
    apis = ET.ElementTree()
    apis.parse(os.path.join(confdir, "cuckoo_elements2mist.xml"))

    default_values = ET.ElementTree()
    default_values.parse(os.path.join(confdir, "cuckoo_types2mist.xml"))

    return (apis, default_values)

def init_logging():
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s:%(message)s')

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)

    fh = logging.FileHandler(os.path.join(os.path.expanduser("~"), "cuckoo2mist.log"))
    fh.setFormatter(formatter)
    fh.setLevel(logging.INFO)
    logger.addHandler(fh)

def generate_mist_reports(files, outputdir, apis, default_values, logger=logger, max_threads=10):
    """Convert Cuckoo behaviour reports to MIST reports in multiple threads."""
    threads = []
    try:
        for file in files:
            (froot, fext) = os.path.splitext(file)
            output_file = froot + ".mist"
            while len(threads) >= max_threads:
                time.sleep(5)
                for t in threads:
                    t.join(2.0)
                    if not t.is_alive():
                        threads.remove(t)
            t = MISTThread(input_file=file,
                           output_file=output_file,
                           apis=apis,
                           default_values=default_values,
                           logger=logger)
            threads.append(t)
            t.start()
    except KeyboardInterrupt:
        pass

    for t in threads:
        t.join()
        threads.remove(t)
        sys.stdout.flush()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--confdir", type=str, default="", help="directory of configuration files")
    parser.add_argument("-i", "--inputdir", type=str, default="", help="directory of Cuckoo behaviour reports")
    parser.add_argument("-o", "--outputdir", type=str, default="", help="directory where MIST reports to be saved")
    args = parser.parse_args()

    init_logging()

    if args.confdir:
        confdir = args.confdir
    else:
        confdir = os.path.join(CUCKOO2MIST_DIR, "conf")

    if not os.path.exists(confdir):
        logger.warning("Configuration directory not valid")
        return

    if args.inputdir:
        inputdir = args.inputdir
    else:
        inputdir = os.path.join(os.path.dirname(CUCKOO2MIST_DIR), "reports")

    files = []
    if os.path.exists(inputdir):
        for file in os.listdir(inputdir):
            path = os.path.join(inputdir, file)
            if path.endswith(".json") or path.endswith(".gz"):
                files.append(path)
    else:
        logger.warning("Input directory not valid")
        return

    if args.outputdir:
        outputdir = args.outputdir
    else:
        outputdir = os.path.join(os.path.dirname(CUCKOO2MIST_DIR), "reports")

    if not os.path.exists(outputdir):
        logger.warning("Output directory not valid")
        return

    (apis, default_values) = read_configuration(confdir)

    generate_mist_reports(files,
                          outputdir=outputdir,
                          apis=apis,
                          default_values=default_values,
                          logger=logger)
