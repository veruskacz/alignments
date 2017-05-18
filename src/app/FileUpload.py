#!/usr/bin/python

import os
import commands
import cgi, cgitb

cgitb.enable()
print "Content-Type: text/html"
print
print 'start!'
form = cgi.FieldStorage()
file_data = form['upload']