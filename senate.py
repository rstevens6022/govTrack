import requests
import re
import xml.etree.ElementTree as ET
import os
import senateVote
import time
from datetime import datetime

class senate:
	def __init__(self, congressNum, congressSession):
		self.congressNum = congressNum
		self.congressSession = congressSession
		self.useLocal = True
		self.urlbase = "https://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_"
		self.senate_votes_url = self.urlbase + str(congressNum) + "_" + str(congressSession) + ".xml"
		self.senateVoteSummary = None
		self.voteUrlBase = "https://www.senate.gov/legislative/LIS/roll_call_votes/vote"
		self.senateVoteSummaryTree = None
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

	def get_url(self):
		return self.senate_votes_url

	def pullVoteList(self):
		# downloads and stores votelist .xml 
		if self.useLocal == True:
			try:
				path = "data/senate_votes_" + str(self.congressNum) + "_" + str(self.congressSession) + ".xml"
				self.senateVoteSummary = open(path).read()
			except FileNotFoundError:
				print(path + " not found")
				self.log(path + " not found")
				print("set useLocal to \"False\" to download.")
				self.log("set useLocal to \"False\" to download.")
		else:
			response = requests.get(self.senate_votes_url)
			self.senateVoteSummary = response.text
			self.saveVoteList()

	def saveVoteList(self):
		if self.useLocal == False:
			path = "data/senate_votes_" + str(self.congressNum) + "_" + str(self.congressSession) + ".xml"
			if not os.path.isfile(path):
				if '?xml version="1.0"' in self.senateVoteSummary.splitlines()[0]:
					# print("xml file detected")
					# print("saving senate_votes.xml")
					try:
						with open(path, "w") as f:
							f.write(self.senateVoteSummary)
					except FileNotFoundError:
						self.makeDataDir()
						# Totally won't ever make a recursive death spiral. 
						self.saveVoteList()

	# downloads and returns individual vote xml files. 
	def pullVote(self,voteNum):
		

		if self.useLocal == True:
			try:
				path = "data/senate_vote_" + str(self.congressNum) + "_" + str(self.congressSession) + "_" +str(voteNum) + ".xml"
				vote = open(path).read()
				return vote
			except FileNotFoundError:
				print(path + " not found")
				self.log(path + " not found")
				print("set useLocal to \"False\" to download.")
				self.log("set useLocal to \"False\" to download.")
			
		else:
			# waits a moment to not blast the server
			self.timer()
			# https://www.senate.gov/legislative/LIS/roll_call_votes/vote1191/vote_119_1_00626.xml
			voteUrl= self.voteUrlBase + str(self.congressNum) + str(self.congressSession) + "/vote_" + str(self.congressNum) +"_"+ str(self.congressSession) +"_"+ str(voteNum)+".xml"
			print("downloading " + voteUrl)
			self.log("downloading " + voteUrl)
			
			response = requests.get(voteUrl)
			return response.text
	
	# download and save all votes in the votelist. 
	def pullAllVotes(self):
		if self.useLocal == True:
			print('To pull all votes useLocal must be set to False.')
			self.log('To pull all votes useLocal must be set to False.')
		else:
			self.log("pulling all votes for congress " + str(self.congressNum) + " session " + str(self.congressSession) )
			if self.voteList == []:
				self.parse_voteList()
			for vote in self.voteList:
					self.saveVote(vote.vote_number)

	# saves only if file is not downloaded
	def saveVote(self,voteNum):
		if self.useLocal == False:	
			path = "data/senate_vote_" + str(self.congressNum) + "_" + str(self.congressSession) + "_" +str(voteNum) + ".xml"
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


	def pullLatestVote(self):
		return self.pullVote(self.latest_vote())

	def head(self):
		if self.senateVoteSummary == None:
			self.pullVoteList()

		# prints the first 5 lines of response
		print("First 5 lines of senateVoteSummary")
		self.log("First 5 lines of senateVoteSummary")
		i=0
		for line in self.senateVoteSummary.splitlines():
			i=i+1
			if i==6:
				break
			print(line)
			self.log(line)

	def latest_vote(self):
		if self.senateVoteSummary == None:
			self.pullVoteList()

		pattern = r'>([0-9]*)<'
		for line in self.senateVoteSummary.splitlines():
			if "<vote_number>" in line:
				# print("found latest vote")
				self.latestVoteNum = re.search(pattern, line).group(1)
				break
		return self.latestVoteNum
	
	def set_useLocal(self, useLocal):
		self.useLocal = useLocal

	def get_useLocal(self):
		return self.useLocal

	def get_senateVoteSummary_type(self):
		return type(self.senateVoteSummary)
	
	def parse_voteList(self):
		# Should return a list of all votes by voteNum
		#Maybe make it create a tree that can be dealt with by other funcs.
		#		replace senateVoteSummary???
		if self.senateVoteSummary == None:
			self.pullVoteList()
		self.senateVoteSummaryTree = ET.fromstring(self.senateVoteSummary)

		# i=0
		# voteList = []
		votes = self.senateVoteSummaryTree.find('votes')
		for vote in votes.iter('vote'):
			if not vote.find('en_bloc'):
				# i=i+1
				# if i==6:
				# 	break
				# print(vote.tag, vote.attrib)
				# for child in vote:
				# 	print(child.tag, child.attrib)
				vote_number = vote.find('vote_number').text.strip()
				print("adding vote_number " + str(vote_number) + " into voteList")
				self.log("adding vote_number " + str(vote_number) + " into voteList")
				vote_date = vote.find('vote_date').text.strip()
				try:
					issue = vote.find('issue').text.strip()
					question = vote.find('question').text.strip()
					result = vote.find('result').text.strip()
					vote_tally = vote.find('vote_tally')
					yeas = vote_tally.find('yeas').text.strip()
					nays = vote_tally.find('nays').text.strip()
					title = vote.find('title').text.strip()
				except AttributeError:
					self.log("Warning: Congress " + str(self.congressNum) + " Session " +str(self.congressSession) + " Vote " + str(vote_number) +" has missing data")
					title = vote.find('title').text.strip()
					if "secret" in title:
						issue = "secret"
						question = "secret"
						result = "secret"
						yeas = "-1"
						nays = "-1"
						continue
					# handling thomas.loc.gov era data
					issue = vote.find('issue')
					if not isinstance(issue, str):
						issue = issue.find('A').text.strip()
						self.log("Parsing thomas.loc.gov issue for Congress " + str(self.congressNum) + " Session " +str(self.congressSession) + " Vote " + str(vote_number))
						print("Parsing thomas.loc.gov issue for Congress " + str(self.congressNum) + " Session " +str(self.congressSession) + " Vote " + str(vote_number))
						question = vote.find('question').text.strip()
						result = vote.find('result').text.strip()
						vote_tally = vote.find('vote_tally')
						yeas = vote_tally.find('yeas').text.strip()
						nays = vote_tally.find('nays').text.strip()
						title = vote.find('title').text.strip()



				self.voteList.append(senateVote.senateVote(self.congressNum, self.congressSession, vote_number, vote_date, issue, question, result, yeas, nays, title))	
				
				# print(vote_number, vote_date, issue, question, result, yeas, nays, title)
				# print("-----------------------------")
				# print("vote_number::", vote_number)
				# print("vote_date::", vote_date)
				# print("issue::", issue)
				# print("question::", question)
				# print("result::", result)
				# print("yeas::", yeas)
				# print("nays::", nays)
				# print("title::", title)
			# else:
				#TODO: figure out how/if to handle en bloc votes for nominations. 
				#
				# print('vote was en_bloc')

		# print("------printing votes---------")
		# for vote in self.voteList:
			# print(vote.vote_number)
			# print(vote)


		# with open("senate_votes_" + str(self.congressNum) + "_" + str(self.congressSession) + "_parsed.txt", "w") as f:
		# 	f.write(tree)


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

				
				counts = voteTree.find('count')
				# yeas = vote.find('yeas').text.strip()
				# nays = vote.find('nays').text.strip()
				try:
					vote.present = counts.find('present').text.strip()
				except AttributeError:
					if type(counts.find('present').text) == None:
						vote.present = "0"
				try:
					vote.absent = counts.find('absent').text.strip()
				except AttributeError:
					if type(counts.find('absent').text) == None:
						vote.absent = "0"
				members = voteTree.find('members')
				for member in members.iter('member'):
					lName = member.find('last_name').text.strip()
					fName = member.find('first_name').text.strip()
					party = member.find('party').text.strip()
					state = member.find('state').text.strip()
					vote_cast = member.find('vote_cast').text.strip()
					lis_member_id = member.find('lis_member_id').text.strip()
					# self.log(str(vote.vote_number) + "addMember:: " + fName + ", " + 
					# 		lName + ", " + party + ", " + state + ", " + 'Senate' +
					# 		 ", " + lis_member_id + ", " + vote_cast)
					vote.addMember(fName, lName, party, state, 'Senate', lis_member_id, vote_cast)
				
				# exiting loop since the only vote to be parsed has been parsed.
				break
