import requests
import re
import xml.etree.ElementTree as ET
import senateVote

class senate:
	def __init__(self, congressNum, congressSession, useLocal):
		self.congressNum = congressNum
		self.congressSession = congressSession
		self.useLocal = useLocal
		self.urlbase = "https://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_"
		self.senate_votes_url = self.urlbase + str(congressNum) + "_" + str(congressSession) + ".xml"
		self.senateVoteSummary = None
		self.voteUrlBase = "https://www.senate.gov/legislative/LIS/roll_call_votes/vote"
		self.senateVoteSummaryTree = None
		self.voteList = []

	def get_url(self):
		return self.senate_votes_url

	def pullVoteList(self):
		if self.useLocal == True:
			try:
				self.senateVoteSummary = open("senate_votes_" + str(self.congressNum) + "_" + str(self.congressSession) + ".xml").read()
			except FileNotFoundError:
				print("senate_votes_" + str(self.congressNum) + "_" + str(self.congressSession) + ".xml" + " not found")
				print("set useLocal to \"False\" to download.")
		else:
			response = requests.get(self.senate_votes_url)
			self.senateVoteSummary = response.text

	def saveVoteList(self):
		if self.useLocal == False:
			if '?xml version="1.0"' in self.senateVoteSummary.splitlines()[0]:
				# print("xml file detected")
				# print("saving senate_votes.xml")
				with open("senate_votes_" + str(self.congressNum) + "_" + str(self.congressSession) + ".xml", "w") as f:
					f.write(self.senateVoteSummary)

	def pullVote(self,voteNum):
		if self.useLocal == True:
			try:
				vote = open("senate_vote_" + str(self.congressNum) + "_" + str(self.congressSession) + "_" +str(voteNum) + ".xml").read()
			except FileNotFoundError:
				print("senate_vote_" + str(self.congressNum) + "_" + str(self.congressSession) + "_" +str(voteNum) + ".xml" + " not found")
				print("set useLocal to \"False\" to download.")
		else:
			# https://www.senate.gov/legislative/LIS/roll_call_votes/vote1191/vote_119_1_00626.xml
			# https://www.senate.gov/legislative/LIS/roll_call_votes/vote1
			voteUrl= self.voteUrlBase + str(self.congressNum) + str(self.congressSession) + "/vote_" + str(self.congressNum) +"_"+ str(self.congressSession) +"_"+ str(voteNum)+".xml"
			print(voteUrl)
			response = requests.get(voteUrl)
			return response.text

	def saveVote(self,voteNum):
		if self.useLocal == False:	
			vote = self.pullVote(voteNum)
			if '?xml version="1.0"' in vote.splitlines()[0]:
					# print("xml file detected")
					# print("saving senate_votes.xml")
					with open("senate_vote_" + str(self.congressNum) + "_" + str(self.congressSession) + "_" +str(voteNum) + ".xml", "w") as f:
						f.write(vote)
			else:
				print("File not saved. Not an XML file.")

	def pullLatestVote(self):
		return self.pullVote(self.latest_vote())

	def head(self):
		if self.senateVoteSummary == None:
			self.pullVoteList()

		# prints the first 5 lines of response
		i=0
		for line in self.senateVoteSummary.splitlines():
			i=i+1
			if i==6:
				break
			print(line)

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
				vote_date = vote.find('vote_date').text.strip()
				issue = vote.find('issue').text.strip()
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
