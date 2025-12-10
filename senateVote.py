
class senateVote:
	def __init__ (self,congress, session, vote_number, vote_date, issue, question, result, yeas, nays, title):
		self.congress = congress
		self.session = session
		self.vote_number = vote_number
		self.vote_date = vote_date
		self.issue = issue
		self.question = question
		self.result = result
		# self.vote_tally = vote_tally
		self.yeas = yeas
		self.nays = nays
		self.title = title
		self.members = []

	def __str__ (self):
		return (str(self.congress) + "," + 
			str(self.session) + "," + 
			str(self.vote_number) + "," + 
			str(self.vote_date) + "," + 
			str(self.issue) + "," + 
			str(self.question) + "," + 
			str(self.result) + "," + 
			# str(self.vote_tally) + "," + 
			str(self.yeas) + "," + 
			str(self.nays) + "," + 
			str(self.title))