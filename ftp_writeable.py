#!/usr/bin/python3

# Purpose: This script takes an FTP server and will scan for any directories this user can write to.
# Testing: This script was tested against Windows Server 2016 IIS 10 FTP
# Issues: Will not work for unix FTP in current state since we use "DIR" regex to determine folders.
# Author: Wade Guest (https://github.com/wguest/ftpw_writeable.py)
# Last Modified Date: 07/11/2018

# Future improvements:
# - More command line options for timeout, specifying directories, etc.
# - Provide an interactive mode to choose whether to go down a certain path
# - Change the way the temporary file is created/used. Likely a more sophisticated solution exists.

from optparse import OptionParser
from ftplib import FTP
from ftplib import error_perm,error_reply
import socket,os,sys,re

#Change this to start from a more specific location
STARTING_DIR = "/"

def testconn(HOST,PORT,USER,PASS):
	ftp = FTP(timeout=30)
	try:
		ftp.connect(HOST,PORT)
		ftp.login(USER,PASS)
		return ftp
	except (ConnectionRefusedError,OSError):
		print("[!] Error connecting to machine")
		return 1
	except:
		print("[!] Cannot authenticate to host with provided credentials.")
		return 1		


def rundir(ftp,curr):

	try:
		ftp.cwd(curr)
	except error_perm as e:
		print("[!] Error changing to directory: " + curr)
	
	# Lazy use of two lists rather than because of the retrlines callback
	raw_list =  []
	curr_list = []
	
	# Get directory listing
	ftp.retrlines('LIST',raw_list.append)

	# Use regex to only add directories to our traversal list
	for item in raw_list:
		if "<DIR>" in item:
			matchObj = re.search(r'\<DIR\>\s+(.+)',item)
			curr_list.append(matchObj.group(1))

	# recurse!
	for folder in curr_list:
		rundir(ftp,folder)
		ftp.cwd('..')

	# Attempt to transfer a file to current folder.
	try:

		#Using a temporary testing file created where this script is being executed
		with open('test.ftp','r') as f:
			ftp.storlines('STOR %s' % 'test.txt', f)

		# If succesful, output and remove the file on the server
		print("[+] Found writable directory: " + ftp.pwd())
		ftp.delete('test.txt')
	except error_perm as e:
		if "Access is denied" in str(e) or "The system cannot find the file specified." in str(e):
			pass
		else: 
			exit("[!] An error has occured while checking write access")

def main():

	#Define and handle options
	parser = OptionParser(usage="usage: %prog [options]")
	parser.add_option("-H","--host",dest="HOST",type="string", help="Enter IP/host. (required)")
	parser.add_option("-P","--port",dest="PORT",type="int",default=21, help="Enter port where FTP is listening. (default is 21)")
	parser.add_option("-u","--username",dest="USER",type="string",default="anonymous",help="User to login to FTP with. (Default is anonymous)")
	parser.add_option("-p","--password",dest="PASS",type="string",default="anonymous",help="Password to login to FTP with. (Default is anonymous)")
	(options, args) = parser.parse_args()
	if options.HOST is None:
		print("[!] No host was provided.")
		print(parser.usage)
		exit(1)

	HOST = options.HOST
	PORT = options.PORT
	USER = options.USER
	PASS = options.PASS

	# Test connecting/authenticating to the ftp server.
	# We also save the FTP connection in ftpconn
	ftpconn = testconn(HOST,PORT,USER,PASS)

	# The testconn function returns 1 if it runs into any issues.
	if ftpconn == 1:
		print("[!] Could not complete FTP connection")
	else:
		print("[+] Connected and authenticated to server successfully!")
		print("[#] Beginning directory scan...")
		write_file = open("./test.ftp",'w+')
		write_file.write("testing...")
		rundir(ftpconn,STARTING_DIR)

if __name__ == '__main__':
	main()
	exit(0)
