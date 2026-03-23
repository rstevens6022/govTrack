# import sys
import requests
# import re
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as BS
import os
import vote
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
		self.voteUrlBase = "https://clerk.house.gov/evs/"
		self.latestVote = None
		# self.senateVoteSummaryTree = None
		self.voteList = []
		self.houseVoteSummary = []
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
		return (2 * (int(congressNum)-100) + 1987 + int(congressSession) -1)


	def pullVote(self,voteNum):
		if self.useLocal == True:
			return self.readVote(voteNum)
			
		else:
			# waits a moment to not blast the server
			self.timer()
			# https://clerk.house.gov/evs/2025/roll305.xml
			voteUrl= self.voteUrlBase + str(self.year) + "/roll" + str(voteNum).zfill(3)+".xml"
			print("downloading " + voteUrl)
			self.log("downloading " + voteUrl)
			
			response = requests.get(voteUrl)
			return response.text
	
	def pullAllVotes(self):
		if self.useLocal == True:
			print('To pull all votes useLocal must be set to False.')
			self.log('To pull all votes useLocal must be set to False.')
		else:
			self.log("pulling all votes for congress " + str(self.congressNum) + " session " + str(self.congressSession) )
			if self.houseVoteSummary == []:
				self.pullVoteList()
			for vote in self.houseVoteSummary:
					self.saveVote(vote[0])


	def getLatestVote(self):
		if self.useLocal == True:
			print("useLocal == True, set to False to get the latest vote.")
			self.log("useLocal == True, set to False to get the latest vote.")
			
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
			# 	self.houseVoteSummary.append(item.get_text())	
						
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
					self.houseVoteSummary.append(itemTuple)	
			# print(self.houseVoteSummary)
			# self.log(self.houseVoteSummary)
			# self.log(table)
			# tr=voteListPage.find_all('tr')
			self.latestVote = self.houseVoteSummary[1][0]
			self.cleanVoteList()
			return self.latestVote

	def cleanVoteList (self):
		# places the voteList[] into a set, then returns the resulting list made up of that set.
		# This removes duplications.
		# Sorting the list afterwords
		self.houseVoteSummary = sorted(list(set(self.houseVoteSummary)), reverse = True)
	
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
				print("Getting voteList from " + url)
				self.log("Getting voteList from " + url)
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
						self.houseVoteSummary.append(itemTuple)	

				i=i-1
		self.cleanVoteList()
		self.saveVoteList()


	def saveVoteList(self):
		# No sense saving if reading from local
		if self.useLocal == False:
			path = "data/house/house_votes_" + str(self.congressNum) + "_" + str(self.congressSession) + ".csv"
			
			try:
				with open(path, "w") as f:
					
					for vote in self.houseVoteSummary:
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
					self.houseVoteSummary.append(itemTuple)	
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

	def parseVoteList(self):
		if self.houseVoteSummary == []:
			self.pullVoteList()
		for voteItem in self.houseVoteSummary:
			vote_number = voteItem[0]
			vote_date = voteItem[1]
			issue = voteItem[2]
			question = voteItem[3]
			result = voteItem[4]
			# yeas and nays not reported in houseVoteSummary
			# need to grab them from vote file
			yeas, nays = self.getYeaNay(vote_number)
			title = voteItem[5]
			self.log('appending vote '+ str(vote_number) + ' to voteList')
			self.voteList.append(vote.vote(self.congressNum, self.congressSession, vote_number, vote_date, 
								issue.rstrip(', '), question.rstrip(', '), result.rstrip(', '), yeas, nays, title))	

	
	# TODO Parse the individual vote files into a list or something
	# Below borrowed form senate.py and may not work
	def parseVote(self, voteNum):
		self.log("parsing vote " + str(voteNum))
		print("parsing vote " + str(voteNum))
		# looping through known list. usually would only loo at most recent part for updates which would be placed at the start of the voteList
		for vote in self.voteList:
			if vote.vote_number == voteNum:
				try:
					voteTree = ET.fromstring(self.pullVote(vote.vote_number))
				except TypeError:
					print("vote_number " + vote.vote_number + " not found.")
					self.log("vote_number " + vote.vote_number + " not found.")

					continue

				# counts = voteTree.find('count')
				counts = voteTree.find('vote-metadata').find('vote-totals').find('totals-by-vote')
				# yeas = vote.find('yeas').text.strip()
				# nays = vote.find('nays').text.strip()
				try:
					vote.present = counts.find('present-total').text.strip()
				except AttributeError:
					if type(counts.find('present-total').text) == None:
						vote.present = "0"
				try:
					vote.absent = counts.find('absnot-voting-totalent').text.strip()
				except AttributeError:
					if type(counts.find('not-voting-total').text) == None:
						vote.absent = "0"
				members = voteTree.find('vote-data')
				self.log("Grabbing Member data")
				for member in members.iter('recorded-vote'):
					legislator = member.find('legislator')
					lName = legislator.get('unaccented-name')
					# TODO figure out hwo to grab first name
					# fName = member.find('first_name').text.strip()
					party = legislator.get('party')
					state = legislator.get('state')
					vote_cast = member.find('vote').text.strip()
					lis_member_id = legislator.get('name-id')
					# self.log(str(vote.vote_number) + "addMember:: " + fName + ", " + 
					# 		lName + ", " + party + ", " + state + ", " + 'Senate' +
					# 		 ", " + lis_member_id + ", " + vote_cast)
					
					# TODO Find first names
					# vote.addMember(fName, lName, party, state, 'House', lis_member_id, vote_cast)
					vote.addMember('NA', lName, party, state, 'House', lis_member_id, vote_cast)
				
				# exiting loop since the only vote to be parsed has been parsed.
				self.log("PrintingVote")
				self.log(vote)
				break

	def getYeaNay(self, voteNum):
		self.log('Getting yeas/nays for vote ' + str(voteNum))
		print('Getting yeas/nays for vote ' + str(voteNum))
		voteTree = ET.fromstring(self.pullVote(voteNum))
		totals = voteTree.find('vote-metadata').find('vote-totals').find('totals-by-vote')
		yeas = totals.find('yea-total').text.strip()
		nays = totals.find('nay-total').text.strip()
		return yeas, nays


	def getFirstName(self):
		pass