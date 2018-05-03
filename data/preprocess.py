import sys
from bs4 import BeautifulSoup
import requests

def bowling(arg):
	with open(arg[1], 'w') as wf:
		with open(arg[0], 'r') as rf:
			i = 0
			for line in rf:
				i += 1
				if i % 10 == 2:
					over = line.strip()
				elif i % 10 == 9:
					wf.write('{}: {}, '.format(line.strip(), over))

def batting(arg):
	with open(arg[1], 'w') as wf:
		with open(arg[0], 'r') as rf:
			i = 0
			arr = []
			for line in rf:
				i += 1
				arr.append(line.strip())
				if i % 7 == 0:
					wf.write('{}\n'.format(', '.join(arr)))
					arr = []

def scrap():
	url = 'http://www.cricbuzz.com/live-cricket-scores/20091/rcb-vs-mi-31st-match-indian-premier-league-2018'
	# url = 'https://en.wikipedia.org/wiki/Cricket'
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

	response = requests.get(url, headers=headers)

	data  = response.text
	# print data

	soup = BeautifulSoup(data, "lxml")  #.find('section', class_='content')
	print soup.get_text().encode('utf-8')

if __name__ == '__main__':
	# scrap()
	if len(sys.argv) < 4:
		raise ValueError('invalid argument') 
	if int(sys.argv[1]) == 0:
		bowling(sys.argv[2:])
	else:
		batting(sys.argv[2:])