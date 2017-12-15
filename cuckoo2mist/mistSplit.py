#!/usr/bin/env python
# encoding: utf-8
"""
mistSplit.py

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

import ntpath


# die functionen splitdrive, split und splitext entsprechen groesstenteils den
# entsprechenden functionen in im ntpath-Modul. allerdings wird in diesen
# functionen auf der "/" als seperator betrachtet. dies wurde in den hier
# eingefuehrten functionen entfernt.

def splitdrive(p):
	"""Split a pathname into drive and path specifiers. Returns a 2-tuple
	"(drive,path)";  either part may be empty"""
	if p[1:2] == ':':
		return p[0:2], p[2:]
	return '', p

def split(p):
	d, p = splitdrive(p)
	i = len(p)
	while i and p[i-1] not in '/\\':
		i = i - 1
	head, tail = p[:i], p[i:]  # now tail has no slashes
	# remove trailing slashes from head, unless it's all slashes
	head2 = head
	while head2 and head2[-1] in '/\\':
		head2 = head2[:-1]
	head = head2 or head
	return d + head, tail

def splitext(p):
	"""Split the extension from a pathname.

	Extension is everything from the last dot to the end.
	Return (root, ext), either part may be empty."""
	i = p.rfind('.')
	if i<=p.rfind('\\'):
		return p, ''
	else:
		return p[:i], p[i:]

def my_splitext(p):
	"""Split the extension from a pathname.

	Extension is everything from the last dot to the end.
	Return (root, ext), either part may be empty."""
	i = p.rfind('.')
	if i<=p.rfind('\\'):
		return p, '', ''
	elif i < len(p):
		return p[:i], p[i], p[i:]
	elif i == len(p):
		return p[:i], p[i], ''

def splitWindows(value):
#		"<>|:*?/\
	result = {}
#	print value
	(result['drive'], value)	= splitdrive(value)
#	print result['drive'] + '	' + value
	pos  = len(value)+1
	if value.find('"') >= 0:
		pos = min(value.find('"'), pos)
	if value.find('/') >= 0:
		pos = min(value.find('/'), pos)
	if value.find('|') >= 0:
		pos = min(value.find('|'), pos)
	if value.find('*') >= 0:
		pos = min(value.find('*'), pos)
	if value.find('?') >= 0:
		pos = min(value.find('?'), pos)
	if value.find(':') >= 0:
		pos = min(value.find(':'), pos)
	if value.find('<') >= 0:
		pos = min(value.find('<'), pos)
	if value.find('>') >= 0:
		pos = min(value.find('>'), pos)
	(result['path'], ffile) 			= split(value[:pos])
#	print result['path'] + '	' + ffile
	(result['filename'], result['seperator'], extension) 	= my_splitext(ffile)
#	print result['filename'] + '	' + extension
	pos2 = len(extension)+1
	pos2 = extension.find(' ')
	if pos2 != -1:
		result['extension'] = extension[1:pos2]
		result['parameter'] = extension[pos2:].replace('  ', ' ') + value[pos:].replace('  ', ' ')
	else:
		result['extension'] = extension[1:]
		result['parameter'] = value[pos:].replace('  ', ' ')
#	print result['extension']
#	print result['parameter']
	return result

def splitFile(value, justWindows):
	result = {}
#	value = value.encode('utf-8')
#	value = value.lower().replace('"', '&quot;')
	if justWindows == 1:
		(result['path'], ffile) 					= split(value)
		(result['filename'], extension) 			= splitext(ffile)
	else:
		(result['path'], ffile) 					= ntpath.split(value)
		(result['filename'], extension) 			= ntpath.splitext(ffile)
	result['extension'] = extension[1:len(extension)]
	return result

