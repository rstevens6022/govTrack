class member:

# Ex from senate_vote_119_1_00628.xml
# <member_full>Alsobrooks (D-MD)</member_full>
    #   <last_name>Alsobrooks</last_name>
    #   <first_name>Angela</first_name>
    #   <party>D</party>
    #   <state>MD</state>
    #   <vote_cast>Nay</vote_cast>
    #   <lis_member_id>S428</lis_member_id>

# Ex from congress roll305.xml
# Ex reformatted form one line into human readable
	# <recorded-vote>
	# 	<legislator name-id="A000370" sort-field="Adams" unaccented-name="Adams" party="D" state="NC" role="legislator">Adams</legislator>
	# 	<vote>Nay</vote>
	# </recorded-vote>

	#TODO: House does not list first name. Need to see how to find that.

	def __init__ (self, fName, lName, party, state, chamber, id, vote)
		# self.fName = fName
		self.lName = lName
		self.party = party
		self.state = state
		self.chamber = chamber
		self.id = id
		self.vote = vote