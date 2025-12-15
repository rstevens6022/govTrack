#This file is to be used to send the pulled senate data into the postgresql db

# Psycopg 3
import psycopg


class toDB:
	def __init__(self, dbname):
		self.dbname = dbname
		self.user = "postgress"