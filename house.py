# import sys
import requests
# import re
# import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as BS
import os
# import senateVote
import time
from datetime import datetime
import csv

class house:
	def __init__(self, congressNum, congressSession):
		self.congressNum = congressNum
		self.congressSession = congressSession
		self.year = self.getYear(congressNum, congressSession)
		self.useLocal = True
		# self.urlbase = "https://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_"
		# self.senate_votes_url = self.urlbase + str(congressNum) + "_" + str(congressSession) + ".xml"
		# self.senateVoteSummary = None
		self.voteUrlBase = "https://clerk.house.gov/evs/"
		self.latestVote = None
		# self.senateVoteSummaryTree = None
		self.voteList = []
		self.lastPullTime = time.time()

	def makeLogDir(self):
		try:
			os.mkdir('logs')
		except FileExistsError:
			print("logs directory already exists")
	
	def makeDataDir(self):
		try:
			os.mkdir('data')
		except FileExistsError:
			print("data directory already exists")
		try:
			os.mkdir('data/house')
		except FileExistsError:
			print("house directory already exists")

	def clearLog(self):
		try:
			open("logs/logFile.txt", "w")
			self.log("New Log File")
		except FileNotFoundError:
			self.makeLogDir()

	def log(self,text):
		try:
			with open("logs/logFile.txt", "a") as f:
				f.write(datetime.today().strftime('%Y-%m-%d %H:%M:%S') + " :: " + str(text) + '\n')
		except FileNotFoundError:
			self.makeLogDir()

	def timer(self):
		now = time.time()
		# print("now::" + str(now) + " lastPullTime::" + str(self.lastPullTime) + " diff::" + str(now - self.lastPullTime))
		# self.log("now::" + str(now) + " lastPullTime::" + str(self.lastPullTime) + " diff::" + str(now - self.lastPullTime))
		if now - self.lastPullTime <= 2:
			# print("wait")
			# self.log("wait")
			time.sleep(2)
		self.lastPullTime = now

	def getYear(self, congressNum, congressSession):
		return (2 * (congressNum-100) + 1987 + congressSession -1)


	def pullVote(self,voteNum):
		if self.useLocal == True:
			return readVote(voteNum)
			
		else:
			# waits a moment to not blast the server
			self.timer()
			# https://clerk.house.gov/evs/2025/roll305.xml
			voteUrl= self.voteUrlBase + str(self.year) + "/roll" + str(voteNum).zfill(3)+".xml"
			print("downloading " + voteUrl)
			self.log("downloading " + voteUrl)
			
			response = requests.get(voteUrl)
			return response.text

	def getLatestVote(self):
		if self.useLocal == True:
			print("useLocal == True")
			self.log("useLocal == True")
			pass
			#Check local files to see latest vote downloaded
		else:
			print("useLocal == False")
			self.log("useLocal == False")
			# waits a moment to not blast the server
			self.timer()
			# https://clerk.house.gov/evs/2026/index.asp
			url= self.voteUrlBase + str(self.year) + "/index.asp"

			response = requests.get(url)
			# print(response.text)
			#need to parse url to get latest vote from html table. 
			#elemetree might work for this.
			#https://docs.python.org/3/library/xml.etree.elementtree.html
			voteListPage = BS(response.text, 'html.parser')
			
			# table = voteListPage.table.find_all('td')
			# for item in table:
			# 	self.voteList.append(item.get_text())	
						
			table = voteListPage.table.find_all('tr')
			for td in table:
				itemList = []
				for item in td:
					if not item.get_text() == '\n':
						itemList.append(item.get_text())
						# itemList = itemList + tuple(item.get_text().split())
				# Need to convert itemList[0] to int except if it is the header line.
				if itemList[0] != 'Roll':
					itemList[0] = int(itemList[0])
					itemTuple = tuple(itemList)
					self.voteList.append(itemTuple)	
			# print(self.voteList)
			# self.log(self.voteList)
			# self.log(table)
			# tr=voteListPage.find_all('tr')
			self.latestVote = self.voteList[1][0]
			self.cleanVoteList()
			return self.latestVote

	def cleanVoteList (self):
		# places the voteList[] into a set, then returns the resulting list made up of that set.
		# This removes duplications.
		# Sorting the list afterwords
		self.voteList = sorted(list(set(self.voteList)), reverse = True)
	
	def pullVoteList(self):
		# downloads and stores votelist .xml 
		if self.useLocal == True:
			self.readVoteList()

		else:
			if self.latestVote == None:
				self.getLatestVote()
			i = int(self.latestVote) // 100
			while i >= 0 :
				self.timer()
				# https://clerk.house.gov/evs/2026/ROLL_000.aspquit
				url= self.voteUrlBase + str(self.year) +"/ROLL_" + str(i) + "00.asp"
				print("Getting votelist from " + url)
				self.log("Getting votelist from " + url)
				response = requests.get(url)
				# print(response)
				# self.log(response)
				# print(response.text)
				# self.log(response.text)
				voteListPage = BS(response.text, 'html.parser')
				table = voteListPage.table.find_all('tr')
				for td in table:
					itemList = []
					for item in td:
						if not item.get_text() == '\n':
							itemList.append(item.get_text().strip('\xa0'))
							# itemList = itemList + tuple(item.get_text().split())
					if itemList[0] != 'Roll':
						itemList[0] = int(itemList[0])
						itemTuple = tuple(itemList)
						self.voteList.append(itemTuple)	

				i=i-1
		self.cleanVoteList()
		self.saveVoteList()


	def saveVoteList(self):
		# No sense saving if reading from local
		if self.useLocal == False:
			path = "data/house/house_votes_" + str(self.congressNum) + "_" + str(self.congressSession) + ".csv"
			
			try:
				with open(path, "w") as f:
					
					for vote in self.voteList:
						outline = ''
						i=0
						for item in vote:
							#parse individual item so I can remove '' and add "" for string in final element
							if i == 0:
								outline = str(item)
							elif i in [2,3,5]:
								outline = outline + ', "' + str(item) +'"'
							else:
								outline = outline + ", " + str(item)
								
							i = i + 1
						# outline = str(vote) + '\n'
						outline = outline + '\r\n'
						# outline = ', '.join(str(item)) + '\n'
						f.write(str(outline))
			except FileNotFoundError:
				self.makeDataDir()
				# Totally won't ever make a recursive death spiral. 
				self.saveVoteList()

	def readVoteList(self):
		# Why would this read if not using local. Test for useLocal should be in calling function.
		path = "data/house/house_votes_" + str(self.congressNum) + "_" + str(self.congressSession) + ".csv"
		try:
			with open(path, 'r') as f:
				# for line in f:
				# 	self.log(line.strip())
				# 	# list of tuples
				reader = csv.reader(f)
				for row in reader:
					# Put this in a loop? It looks dumb this way, but would a loop be more efficient?
					row[0] = int(row[0])
					row[1] = row[1].strip()
					row[2] = row[2].strip().strip('\"')
					row[3] = row[3].strip().strip('\"')
					row[4] = row[4].strip()
					row[5] = row[5].strip().strip('\"')
					self.log(row)
					itemTuple = tuple(row)
					self.voteList.append(itemTuple)	
		except FileNotFoundError:
			print(path + " not found")
			self.log(path + " not found")
			print("set useLocal to \"False\" to download.")
			self.log("set useLocal to \"False\" to download.")

	def saveVote(self, voteNum):
		if self.useLocal == False:	
			path = "data/house/house_vote_" + str(self.congressNum) + "_" + str(self.congressSession) + "_" +str(voteNum) + ".xml"
			if not os.path.isfile(path):
				vote = self.pullVote(voteNum)
				if '?xml version="1.0"' in vote.splitlines()[0]:
						# print("xml file detected")
						# print("saving senate_votes.xml")
						self.log("saving " + path)
						with open(path, "w") as f:
							f.write(vote)
				else:
					print("voteNum " + voteNum + "File not saved. Not an XML file.")
					self.log("voteNum " + voteNum + "File not saved. Not an XML file.")

	def readVote(self, voteNum):
		try:
			path = "data/house/house_vote_" + str(self.congressNum) + "_" + str(self.congressSession) + "_" +str(voteNum) + ".xml"
			vote = open(path).read()
			return vote
		except FileNotFoundError:
			print(path + " not found")
			self.log(path + " not found")
			print("set useLocal to \"False\" to download.")
			self.log("set useLocal to \"False\" to download.")

	# TODO Parse the votelist file into a list or something
	# TODO Parse the individual vote files into a list or something