import senate

def tests(useLocal):
	senateTest.set_useLocal(useLocal)
	print("----getting useLocal-----")
	print(senateTest.get_useLocal())
	print("----getting senateVoteSummary_type-----")
	print(senateTest.get_senateVoteSummary_type())
	print("----pulling data-----")
	senateTest.pullVoteList()
	print(senateTest.get_senateVoteSummary_type())
	print("----saving data-----")
	senateTest.saveVoteList()
	print("----getting senate.head-----")
	senateTest.head()
	print("----getting latest_vote-----")
	print(senateTest.latest_vote())


# ------------------------------------------
# Testing basic stuff
# senateTest = senate.senate(119, 1)

# print("----getting Url-----")
# print(senateTest.get_url())

# print("----Testing with Uselocal == True-----")
# tests(True)


# del senateTest
# senateTest = senate.senate(119, 1)

# print("----Testing with Uselocal == False-----")
# tests(False)

# ------------------------------------------
# Testing 
# senateTest = senate.senate(119, 1)
# senateTest.clearLog()


# senateTest.pullVoteList()
# print(senateTest.latest_vote())
# senateTest.saveVoteList()

# print("------Pulling latest vote-------")

# print(senateTest.pullVote(senateTest.latest_vote()))
# print(senateTest.pullLatestVote())
# senateTest.saveVote(senateTest.latest_vote())

# ------------------------------------------
# test xml parsing
# senateTest = senate.senate(119,1)
# senateTest.clearLog()

# senateTest.log("-----------parse_VoteList-------------")
# senateTest.parse_voteList()
# senateTest.log("-----------parseVote-------------")
# senateTest.parseVote('00627')
# senateTest.log("-----------LOOP-------------")
# for vote in senateTest.voteList:
# 	# senateTest.log(vote.vote_number)
# 	if vote.vote_number == '00627':
# 		senateTest.log("-----------Vote 00627-------------")
# 		senateTest.log(vote)
# 		senateTest.log("-----------Vote 00627 Question-------------")
# 		print("-----------Vote 00627 Question-------------")
# 		senateTest.log(vote.question)
# 		# senateTest.log("-----------printMembers-------------")
# 		# print("-----------printMembers-------------")
# 		# senateTest.log(vote.printMembers())
# 		senateTest.log("-----------print members[]-------------")
# 		senateTest.log(str(vote.members))


# pull everything
senateTest = senate.senate(119,1)
# senateTest.useLocal = False
# senateTest.clearLog()
senateTest.pullAllVotes()