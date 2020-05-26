from os import path
import sys
import requests
from fake_useragent import UserAgent
import sqlite3


ua = UserAgent()

class Db:
	def __init__(self, dbname):
		try:
			self.con = sqlite3.connect(dbname, check_same_thread=False, timeout=10)
			self.con.row_factory = sqlite3.Row
			self.cur = self.con.cursor()
		except Exception as e:
			print("Error connecting to db: "+ str(e))

	def createtable(self, table, param):
		self.cur.execute(f"CREATE TABLE IF NOT EXISTS {table} ({param})")
		self.con.commit()

	def createdb(self, dquery):
		self.cur.execute(dquery)
		self.con.commit()

	def fetch(self, param):
		self.cur.execute(param)
		return self.cur.fetchall()

	def insert(self, table, paramname, paramvalue):
		self.cur.execute(
			f"INSERT INTO {table} ({paramname}) VALUES({paramvalue})")
		self.con.commit()

	def check(self, checkval, table, param):
		self.cur.execute(f"SELECT {checkval} FROM {table} WHERE {param}")
		return self.cur.fetchone()

	def others(self, param):
		self.cur.execute(param)
		self.con.commit()

	def getTotal(self, param):
		totalrow = self.cur.execute(param).rowcount
		return totalrow

	def __del__(self):
		self.con.close()
  
  
def pprint(va):
    print(str(va))
    with open('config-log.txt', 'a') as et:
        et.write(str(va)+'\n')


def respath(filename):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")

    return path.join(base_path, filename)


def remoteread_file(dfile, proxy=''):
    try:
        with requests.get(dfile, headers={'User-Agent': ua.random}, verify=False, stream=True, proxies={"http": proxy, "https": proxy}) as response:
            allowcode = [200, 202, 201, 203, 206, 302, 301, 303, 305, 307, 404]
            if response.status_code in allowcode:
                # now proceed with the grabbing
                return response.content.decode('utf-8')
            else:
                return response.status_code
    except Exception as e:
        pprint('Requests '+ str(e))
        return False
