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
# senateTest = senate.senate(119, 1, True)

# print("----getting Url-----")
# print(senateTest.get_url())

# print("----Testing with Uselocal == True-----")
# tests(True)


# del senateTest
# senateTest = senate.senate(119, 1, True)

# print("----Testing with Uselocal == False-----")
# tests(False)

# ------------------------------------------
#Testing 
# senateTest = senate.senate(119, 1, False)
# senateTest.pullVoteList()
# print(senateTest.latest_vote())
# senateTest.saveVoteList()

# print("------Pulling latest vote-------")

# print(senateTest.pullVote(senateTest.latest_vote()))
# print(senateTest.pullLatestVote())
# senateTest.saveVote(senateTest.latest_vote())

# ------------------------------------------
# test xml parsing
senateTest = senate.senate(119,1,True)
senateTest.parse_voteList()
