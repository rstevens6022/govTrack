# import sys
import requests
# import re
# import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as BS
import os
# import senateVote
import time
from datetime import datetime

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
			pass
			# try:
			# 	path = "data/senate/senate_vote_" + str(self.congressNum) + "_" + str(self.congressSession) + "_" +str(voteNum) + ".xml"
			# 	vote = open(path).read()
			# 	return vote
			# except FileNotFoundError:
			# 	print(path + " not found")
			# 	self.log(path + " not found")
			# 	print("set useLocal to \"False\" to download.")
			# 	self.log("set useLocal to \"False\" to download.")
			
		else:
			# waits a moment to not blast the server
			self.timer()
			# https://clerk.house.gov/evs/2025/roll305.xml
			voteUrl= self.voteUrlBase + str(self.year) + "/" + str(voteNum)+".xml"
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
			pass
			# try:
			# 	path = "data/senate/senate_votes_" + str(self.congressNum) + "_" + str(self.congressSession) + ".xml"
			# 	self.senateVoteSummary = open(path).read()
			# except FileNotFoundError:
			# 	print(path + " not found")
			# 	self.log(path + " not found")
			# 	print("set useLocal to \"False\" to download.")
			# 	self.log("set useLocal to \"False\" to download.")
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


	def saveVoteList(self):
		if self.useLocal == False:
			path = "data/house/house_votes_" + str(self.congressNum) + "_" + str(self.congressSession) + ".csv"
			
			try:
				with open(path, "w") as f:
					for item in self.voteList:
						outline = str(item) + '\n'
						# outline = ', '.join(str(item)) + '\n'
						f.write(str(outline))
			except FileNotFoundError:
				self.makeDataDir()
				# Totally won't ever make a recursive death spiral. 
				self.saveVoteList()