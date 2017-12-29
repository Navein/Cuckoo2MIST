#!/usr/bin/env python
# encoding: utf-8
"""
class_mist.py

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
"""

from __future__ import print_function

__author__ = "philipp trinius, navein chanderan, chang si ju"
__version__ = "0.4"

import os
import sys
import re
import json
import gzip
import mmh3
from collections import OrderedDict
import xml.etree.cElementTree as ET
from cStringIO import StringIO

username_pattern = re.compile('[a-z]\\:[\\\\\\/_]{1,4}users[\\\\\\/_]{1,4}([^\\\\\\/\\:\\?\\,\\|\\"\\*_]+)')

filepath_pattern = re.compile('^(((\\\\\\?\\?)?(\\\\\\\\\\?)?((\\\\)?[a-z]\\:)?' \
                              '(\\\\[^\\\\\\/\\:\\?\\,\\|\\"\\*]+)*)\\\\)?' \
                              '(([^\\\\\\/\\:\\?\\,\\|\\"\\*]+)\\.([^ \\\\\\/\\:\\?\\,\\|\\"\\*]+))?' \
                              '(\\?([^\\?]*))?$')

instruction_template = ['', '', '', '']

class MIST(object):
    def __init__(self, input_file, apis, default_values):
        self.input_file = input_file
        self.behaviour_report = ""
        self.apis = apis
        self.default_values = default_values
        self.mist_report = StringIO()
        self.cache = {}
        self.missing = {}
        self.nomatch = {}
        self.errormsg = ""

    def parse_report(self):
        if not os.path.exists(self.input_file):
            self.errormsg = "Behaviour report does not exist."
            return False
        try:
            if self.input_file.endswith(".json"):
                with open(self.input_file, "r") as json_report:
                    self.behaviour_report = json.load(json_report)
                    return True
            elif self.input_file.endswith(".gz"):
                with gzip.open(self.input_file, "r") as json_report:
                    self.behaviour_report = json.load(json_report)
                    return True
        except Exception as e:
            self.errormsg = "Could not parse the behaviour report. (%s)" % e
            return False

    def result(self):
        return self.mist_report.getvalue()

    def write(self, output_file):
        """Write the converted report to file on disk."""
        try:
            with file(output_file, 'w') as w_file:
                w_file.write(self.result())

            # with open('reports/cache.txt', 'w') as f:
            #     for k, v in self.cache.iteritems():
            #         f.write('%s;;%s\n' % (k, v))

        except Exception as e:
            self.errormsg = "%s" % e
            return False
        return True

    def remove_newline(self, value):
        return re.sub("\n", "", value)

    def murmurhash3(self, key):
        h = 0
        try:
            h = str(mmh3.hash(key, signed=False))[:8]
        except:
            pass
        return h

    def hexvalue(self, value, length=8):
        """
        @param value: integer input to be converted into hex.
        @param length: length of the hex.
        @return: hex value
        """
        assert value is not None
        try:
            h = ('0' * length) + "%x" % int(value)
        except ValueError:
            h = ('0' * length) + "%x" % int(value, 16)
        h = h[length * -1:]
        return h

    def mist_hex(self, value, length=8, lookup=True):
        if lookup:
            try:
                return self.cache[value]
            except:
                h = self.hexvalue(value)
                self.cache[value] = h
                return h
        else:
            return self.hexvalue(value)

    def mist_str(self, value):
        value = value.lower()

        # Replace unique username in path with 'username'.
        match = re.search(username_pattern, value)
        if match:
            if match.group(1):
                value = re.sub(match.group(1), 'username', value, count=1)

        try:
            return self.cache[value]
        except:
            h = self.murmurhash3(value)
            x = self.mist_hex(h, lookup=False)
            self.cache[value] = x
            return x

    def split_filepath(self, filepath):
        filepath = filepath.lower()
        extension = ""
        path = ""
        filename = ""
        parameters = ""

        match = re.search(filepath_pattern, filepath)
        if match:
            if match.group(2):
                path = match.group(2)
            if match.group(9):
                filename = match.group(9)
            if match.group(10):
                extension = match.group(10)
            if match.group(12):
                parameters = match.group(12)
        else:
            path = filepath

        # if path:
        #     # Replace unique username in path with 'username'.
        #     # For example, c:\users\david becomes c:\users\username.
        #     pattern = '^[a-z]\\:\\\\users\\\\([^\\\\\\/\\:\\?\\,\\|\\"\\*]+)'
        #     match = re.search(pattern, path)
        #     if match:
        #         if match.group(1):
        #             path = re.sub(match.group(1), 'username', path,
        #                           count=1)

        return (extension, path, filename, parameters)

    def mist_filepath(self, instruction, value, level):
        (extension, path, filename, parameters) = self.split_filepath(value)
        instruction[level] = instruction[level] + " " + self.mist_str(extension) + " " + self.mist_str(path)
        instruction[level + 1] = instruction[level + 1] + " " + self.mist_str(filename) + " " + self.mist_str(parameters)
        return instruction

    def mist_url(self, instruction, value, level):
        # TODO Possibly convert URL to a more meaningful form.

        # Replace unique username in url(/path) with 'username'
        # value = value.lower()
        # pattern = '[a-z]\\:(?:\\\\|\\/)users(?:\\\\|\\/)([^\\\\\\/\\:\\?\\,\\|\\"\\*]+)'
        # match = re.search(pattern, value)
        # if match:
        #     if match.group(1):
        #         value = re.sub(match.group(1), 'username', value, count=1)
        # print(value)
        instruction[level] = instruction[level] + " " + self.mist_str(value)
        return instruction

    def convert_thread(self, pid, tid, api_calls):
        """Convert API calls for a thread to MIST format."""
        self.mist_report.write("# process " + str(pid) + " thread " + str(tid) + " #\n")

        for api_call in api_calls:
            arguments = api_call["arguments"]
            category = api_call["category"]
            api = api_call["api"]
            instruction = list(instruction_template)

            category_node = self.apis.getroot().find(category)
            if category_node != None:
                api_node = category_node.find(api)
            else:
                api_node = None
                try:
                    self.missing[category]
                except:
                    self.missing[category] = []

            if api_node == None:
                try:
                    if api not in self.missing[category]:
                        self.missing[category].append(api)
                except:
                    self.missing[category] = [api]
                continue

            instruction[0] = category_node.attrib["code"] + " " + api_node.attrib["code"]

            for attrib_node in api_node.iter():
                valtype = attrib_node.get("type")
                if valtype == None:
                    continue

                level = attrib_node.get("level")
                try:
                    i = int(level) - 1
                except:
                    i = 1

                value = self.default_values.find(valtype).get("default")

                arg_found = False
                for arg in arguments:
                    if arg["name"].lower() == attrib_node.tag.lower():
                        value = arg["value"]
                        arg_found = True
                        break

                if valtype == "type_hex":
                    value = self.remove_newline(value)
                    x = value[2:10]
                    while len(x) < 8:
                        x = "0" + x
                    instruction[i] = instruction[i] + " " + x
                elif valtype == "type_integer":
                    instruction[i] = instruction[i] + " " + self.mist_hex(value)
                elif valtype == "type_string":
                    instruction[i] = instruction[i] + " " + self.mist_str(value)
                elif valtype == "type_filepath":
                    self.mist_filepath(instruction, value, i)
                elif valtype == "type_url":
                    self.mist_url(instruction, value, i)

                if not arg_found:
                    # For error message building purpose.
                    key = "(" + category + ") " + api
                    try:
                        if attrib_node.tag not in self.nomatch[key]:
                            self.nomatch[key].append(attrib_node.tag)
                    except:
                        self.nomatch[key] = [attrib_node.tag]

            line = " |".join(instruction)
            self.mist_report.write(line + "\n")

        return True

    def convert(self):
        """Convert the behaviour report to MIST report."""
        if not self.parse_report():
            return False

        processes = OrderedDict()
        procs = self.behaviour_report["behavior"]["processes"]
        for proc in procs:
            process_id = proc["process_id"]
            parent_id = proc["parent_id"]
            process_name = proc["process_name"]
            calls = proc["calls"]
            threads = OrderedDict()
            for call in calls:
                thread_id = call["thread_id"]
                try:
                    threads[thread_id].append(call)
                except:
                    threads[thread_id] = []
                    threads[thread_id].append(call)
            processes[process_id] = {}
            processes[process_id]["parent_id"] = parent_id
            processes[process_id]["process_name"] = process_name
            processes[process_id]["threads"] = threads

        for p_id in processes:
            for t_id in processes[p_id]["threads"]:
                self.convert_thread(p_id, t_id, processes[p_id]["threads"][t_id])

        if len(self.missing.keys()) > 0:
            self.errormsg  = "%s:\n" % self.input_file
            self.errormsg += "Missing from cuckoo_elements2mist.xml:\n%s\n" % json.dumps(self.missing)
            self.errormsg += "Missing from %s:\n%s" % (self.input_file, json.dumps(self.nomatch))
            # print(self.errormsg)

        return True

# if __name__ == '__main__':
#     conf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conf")
#     apis = ET.ElementTree()
#     apis.parse(os.path.join(conf_dir, "cuckoo_elements2mist.xml"))
#     default_values = ET.ElementTree()
#     default_values.parse(os.path.join(conf_dir, "cuckoo_types2mist.xml"))

#     input_file = "reports/report3.json"
#     output_file = os.path.splitext(input_file)[0] + ".mist"
#     print("Generating MIST report for %s" % input_file)
#     x = MIST(input_file, apis=apis, default_values=default_values)
#     if x.convert():
#         if x.write(output_file):
#             print("  Done")
#     else:
#         print(x.errormsg)

    # instruction = ["", "", "", ""]
    # x.mist_url(instruction, 'file:///C:/Users/David/AppData/Local/Temp/VirusShare_880d4fb8326db7483fdf30bcaa525cad.html')
    # instruction = [sec.lstrip() for sec in instruction]
    # print(instruction)

    # print(x.mist_filepath('C:\\Users\\David\\AppData\\Local\\Microsoft\\Windows\\Temporary Internet Files\\Low\\SuggestedSites.dat') + "\n")
    # print(x.mist_filepath('C:\\Users\\David\\AppData\\Local') + "\n")
    # print(x.mist_filepath('comctl32.dll') + "\n")
    # print(x.mist_filepath('C:\\??') + "\n")
    # print(x.mist_filepath('C:\\') + "\n")
    # print(x.mist_filepath('\\\\?\\STORAGE#Volume#{213744c0-6e87-11e7-a5df-806e6f6e6963}#0000000006500000#{53f5630d-b6bf-11d0-94f2-00a0c91efb8b}\\') + "\n")
    # print(x.mist_filepath('\\\\?\\IDE#CdRomPLDS_DVD+-RW_DS-8A9SH___________________ED11____#5&2117b2e5&0&1.0.0#{53f5630d-b6bf-11d0-94f2-00a0c91efb8b}\\') + "\n")
    # print(x.mist_filepath('\\\\?\\Volume{cb36d33a-6861-11e7-99c9-806e6f6e6963}\\') + "\n")
    # print(x.mist_filepath('\\??\\MountPointManager') + "\n")
    # print(x.mist_filepath('\\??\\UNC\\pecasgnv.com.br\\wp-content\\plugins\\woocommerce\\assets\\js\\jquery-blockui\\jquery.blockUI.min.js') + "\n")

    # print(x.mist_url('C:\\Users\\David\\AppData\\Local\\Microsoft\\Windows\\Temporary Internet Files\\Low\\SuggestedSites.dat') + "\n")
