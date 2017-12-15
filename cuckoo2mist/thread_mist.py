#!/usr/bin/env python
# encoding: utf-8
"""
thread_mist.py

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

__author__ = "philipp trinius, navein chanderan, chang si ju"
__version__ = "0.4"

import os
import sys
from threading import Thread
from class_mist import MIST

class MISTThread(Thread):
	def __init__(self, input_file, output_file,
		         apis, default_values, logger):
		Thread.__init__(self)
		self.input_file = input_file
		self.output_file = output_file
		self.apis = apis
		self.default_values = default_values
		self.log = logger

	def run(self):
		mist = MIST(self.input_file, apis=self.apis,
			        default_values=self.default_values)
		if mist.convert():
			mist.write(self.output_file)
		if len(mist.errormsg) > 0:
			self.log.warning(mist.errormsg)
