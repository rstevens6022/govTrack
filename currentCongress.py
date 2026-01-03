from datetime import datetime



def currentCongress():
	current_year = datetime.now().year
	# 100th session 1 started 1-6-1987 
	diff = current_year - 1987
	congress = ((diff) / 2) +100
	session = ((diff) % 2) + 1

	return int(congress), session


