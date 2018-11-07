#!/usr/bin/python

# Purpose: This script is supplied information to connect to a web server. It then checks for a robots.txt file and downloads a local copy of each disallowed entry.
#			I wanted to create this script as I got tired of doing it in bash all the time.
# Testing: This script was tested against Windows Server 2016 IIS 10 FTP
# Issues: Will not work for unix FTP in current state since we use "DIR" regex to determine folders.
# Author: Wade Guest (https://github.com/wguest/scripting)
# Last Modified Date: 07/11/2018

# Future improvements:
# - More command line options for specifying a download directory.
# - Further testing with redirects and alternative ports isz likely needed.

import requests,sys,re
from optparse import OptionParser

def main():
	#Define and handle options
	parser = OptionParser(usage="usage: %prog [options]")
	parser.add_option("-H","--host",dest="HOST",type="string", help="Enter IP/host. (required)")
	parser.add_option("-P","--port",dest="PORT",type="int",default=80, help="Enter webserver report. (Default is 80/443 for HTTPS)")
	parser.add_option("-s","--https",action="store_true",dest="SSL",help="Set to true for HTTPS (Default is false)")
	(options, args) = parser.parse_args()
	if options.HOST is None:
		print("[!] No host was provided.")
		print(parser.usage)
		exit(1)

	HOST = options.HOST
	SSL = options.SSL
	PORT = options.PORT
	SCHEMA = "http://"

	if SSL:
		SCHEMA = "https://"
		if PORT == 80:
			PORT =443

	base_url = SCHEMA + HOST + ":" + str(PORT)
	robot_url = SCHEMA + HOST + ":" + str(PORT) + "/robots.txt"


	print "[#] Trying url " + robot_url	
	r = requests.get(robot_url)
	if r.status_code != 200:
		print "[!] Status code was not 200. Exiting script..."

	disallowed = re.compile(r'Disallow\:\s+([ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789\-\.\_\~\:\/\?\#\[\]\@\!\$\&\'\(\)\*\+\,\;\=]+)')
	robots = disallowed.findall(r.text)
	print "[#] Found " + str(len(robots)) + " disallowed robots entries"
	for link in robots:
		print "Downloading " + link
		fn = link[1:]
		r = requests.get(base_url + link,stream=True)
		with open(fn,'wb') as f:
			for chunk in r.iter_content(chunk_size=1024):
				if chunk:
					f.write(chunk)

if __name__ == '__main__':
	main()
	exit()