# -*- coding: utf-8 -*-
#
# v0.4 - copyright by meigrafd @ 31.07.2015
#
#
###
# import the libraries
from __future__ import print_function
from datetime import timedelta
import time, sys, os
try: #python2
	from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
except ImportError: #python3
	from http.server import BaseHTTPRequestHandler,HTTPServer


PORT_NUMBER = 7070


def getPiUptime():
  with open('/proc/uptime', 'r') as f:
    uptime_seconds = float(f.readline().split()[0])
    uptime = str(timedelta(seconds = uptime_seconds))
  return uptime

def getPiRam():
  with open('/proc/meminfo', 'r') as mem:
    tmp = 0
    for i in mem:
      sline = i.split()
      if str(sline[0]) == 'MemTotal:':
        total = int(sline[1])
      elif str(sline[0]) in ('MemFree:', 'Buffers:', 'Cached:'):
        tmp += int(sline[1])
    free = tmp
    used = int(total) - int(free)
    usedPerc = (used * 100) / total
    totalMB = int(total/1024)
    freeMB = int(free/1024)
    return "%s / %s" % (freeMB, totalMB)

def getPiTemperature():
  with open("/sys/class/thermal/thermal_zone0/temp", 'r') as f:
    content = f.read().splitlines()
  return float(content[0]) / 1000.0

def getPiCpuLoad():
  with open("/proc/loadavg", 'r') as f:
    content = f.readline().split(" ")[:3]
  return ' , '.join(content)

def getCPUuse():
	return(str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip()))

def getDiskSpace(): # Return information about disk space as a list (unit included)
	# Index 0: total disk space
	# Index 1: used disk space
	# Index 2: remaining disk space
	# Index 3: percentage of disk used
	p = os.popen("df -h /")
	i = 0
	while 1:
		line = p.readline()
		i += 1
		if i==2:
			return(line.split()[1:5])
# Disk information
#DISK_stats = getDiskSpace()
#DISK_total = DISK_stats[0]
#DISK_used = DISK_stats[1]
#DISK_free = DISK_stats[2]
#DISK_perc = DISK_stats[3]


# http://www.acmesystems.it/python_httpd
# This class will handles any incoming request from the browser 
class myHandler(BaseHTTPRequestHandler):
	
	# Handler for the GET requests
	def do_GET(self):
		try:
			sendReply = False

			if self.path.startswith("/cputemp?"):
				Response = str(getPiTemperature())
				mimetype = 'text/html'
				sendReply = True

			elif self.path.startswith("/cpuload?"):
				Response = str(getPiCpuLoad())
				mimetype = 'text/html'
				sendReply = True

			elif self.path.startswith("/ram?"):
				Response = str(getPiRam())
				mimetype = 'text/html'
				sendReply = True

			elif self.path.startswith("/uptime?"):
				Response = str(getPiUptime()).split(".")[0]
				mimetype = 'text/html'
				sendReply = True

			if sendReply == True:
				self.send_response(200)
				self.send_header('Content-type', mimetype)
				self.end_headers()
				# Send the html message
				self.wfile.write(Response)
			else:
				self.send_error(404,'File Not Found: %s' % self.path)
			return

		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)

try:
	# Create a web server and define the handler to manage the incoming request
	server = HTTPServer(('', PORT_NUMBER), myHandler)
	print('Started httpserver on port ' , PORT_NUMBER)
	
	# Wait forever for incoming http requests
	server.serve_forever()

except (KeyboardInterrupt, SystemExit):
	print('Shutting down http server')
	server.socket.close()
