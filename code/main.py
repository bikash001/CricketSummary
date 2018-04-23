import sys

class CustomDictionary(dict):
	"""dot.notation access to dictionary attributes"""
	__getattr__ = dict.get
	__setattr__ = dict.__setitem__
	__delattr__ = dict.__delitem__

class Batsman(CustomDictionary):
	pass

def create_batsman(n, s, r, b, f, sx, sr):
	return Batsman(name=n, status=s, run=int(r),
		ball=int(b), four=int(f), six=int(sx),
		sr=float(sr))

class Match(CustomDictionary):
	pass

class Bowler():
	def __init__(self, name, over):
		self._name = name
		self._data = []
		self._overs = 0
		self._wickets = 0
		self._runs = 0
		self._maidens = 0
		self.add_over(over)

	def add_over(self, over):
		self._data.append(over)
		self._overs += 1
		self._analyse(over)

	def _analyse(self, over):
		w, r = 0, 0
		for x in over:
			if len(x) == 1:
				if x == 'W':
					w += 1
				else:
					r += int(x)
			else:
				cnt = 0
				if x[0].isdigit():
					cnt = int(x[0])
					x = x[1:]
				if x == 'Wd':
					r += cnt if cnt>0 else 1
				elif x == 'W':
					w += 1
				else:
					r += cnt
		if r == 0:
			self._maidens += 1
		self._wickets += w
		self._runs += r

	def overs(self):
		return self._overs

	def wickets(self):
		return self._wickets

	def runs(self):
		return self._runs

	def maidens(self):
		return self._maidens

def create_or_load_bowler(inning, info):
	name, data = info.split(':')
	name = name.strip()
	data = map(str.strip, data.split())
	if name in inning.bowler_info:
		inning.bowler_info[name].add_over(data)
	else:
		inning.bowler_info[name] = Bowler(name, data)
	inning.bowlers.append(name)

class Innings(CustomDictionary):
	pass

def create_innings():
	return (Innings(batsmans=[], bowlers=[], bowler_info={}, run=None, wicket=None), 
			Innings(batsmans=[], bowlers=[], bowler_info={}, run=None, wicket=None))

def create_match():
	return Match(day='', date="", venue="",
			teams=None, toss=None, innings=create_innings())

def parse_input(file):
	match = create_match()
	with open(file, 'r') as fp:
		# date
		label = fp.readline().strip()
		if label != 'Day:':
			raise ValueError('Label should be %s but got %s' %('Day:', label))
		data = fp.readline().split(',')
		match.day = data[0].strip()
		match.date = data[1].strip()+', '+data[2].strip()
		# print match.day, match.date
		
		# venue
		label = fp.readline().strip()
		if label != 'Venue:':
			raise ValueError('Label should be %s but got %s' %('Venue:', label))
		match.venue = fp.readline().strip()
		# print match.venue
		
		# teams
		label = fp.readline().strip()
		if label != 'Teams:':
			raise ValueError('Label should be %s but got %s' %('Teams:', label))
		data = fp.readline().split(',')
		match.teams = (data[0].strip(), data[1].strip())
		# print match.teams		
		
		# toss
		label = fp.readline().strip()
		if label != 'Toss:':
			raise ValueError('Label should be %s but got %s' %('Toss:', label))
		data = fp.readline()
		idx = data.find('(')
		toss_winner = data[:idx].strip()
		choose = data[idx+1: idx+2]
		match.toss = (0 if toss_winner == match.teams[0] else 1, 0 if choose == 'B' else 1)
		# print match.toss
		
		# Winner
		label = fp.readline().strip()
		if label != 'Winner:':
			raise ValueError('Label should be %s but got %s' %('Winner:', label))
		data = fp.readline().strip()
		print data
		match.winner = 0 if match.teams[0]==data else 1
		# print match.winner, data
		
		# First Inning
		inning = match.innings[0]
		label = fp.readline().strip()
		if label != 'Batting:':
			raise ValueError('Label should be %s but got %s' %('Batting: (first)', label))
		

		# batting
		count = 0
		data = fp.readline().strip()
		while data != 'Wickets:':
			count += 1
			if count > 11:
				raise ValueError('Label should be %s but got %s' %('Wickets: (first)', data))
			inning.batsmans.append(
					create_batsman(*map(str.strip, data.split(',')))
				)
			data = fp.readline().strip()

		# wickets
		label = 'Wickets:'
		data = fp.readline().strip()
		# print data

		# Bowling
		label = fp.readline().strip()
		if label != 'Bowling:':
			raise ValueError('Label should be %s but got %s' %('Bowling: (first)', label))
		data = fp.readline().split(',')
		for player_info in data:
			create_or_load_bowler(inning, player_info)

		# second inning
		inning = match.innings[1]
		label = fp.readline().strip()
		if label != 'Batting:':
			raise ValueError('Label should be %s but got %s' %('Batting: (second)', label))
		
		# batting
		count = 0
		data = fp.readline().strip()
		while data != 'Wickets:':
			count += 1
			if count > 11:
				raise ValueError('Label should be %s but got %s' %('Wickets: (first)', data))
			inning.batsmans.append(
					create_batsman(*map(str.strip, data.split(',')))
				)
			data = fp.readline().strip()

		# wickets
		label = 'Wickets:'
		data = fp.readline().strip()
		

		# Bowling
		label = fp.readline().strip()
		if label != 'Bowling:':
			raise ValueError('Label should be %s but got %s' %('Bowling: (second)', label))
		data = fp.readline().split(',')
		for player_info in data:
			create_or_load_bowler(inning, player_info)

	count_run_and_wicket(match.innings[0])
	count_run_and_wicket(match.innings[1])
	return match

def count_run_and_wicket(inning):
	if inning.run is not None:
		return inning.run, inning.wicket
	
	total_run = 0
	for batsman in inning.batsmans:
		total_run += batsman.run

	total_wicket = 0
	for name, bowler in inning.bowler_info.items():
		total_wicket += bowler.wickets()

	inning.run = total_run
	inning.wicket =  total_wicket
	return total_run, total_wicket

def main():
	summary = []
	match = parse_input(sys.argv[1])

	# first batting team won (batting = 0)
	if ((match.toss[1] == 0 and  match.toss[0] == match.winner) or 
			(match.toss[1] == 1 and match.toss[0] != match.winner)):
		summary.append("{} registered {}-run victory against {} at {} on {}.".format(
			match.teams[match.winner], (match.innings[0].run-match.innings[1].run),
			match.teams[0 if match.winner==1 else 1], match.venue, match.day))
	else:
		summary.append("{} beat {} by {} wickets at {} on {}.".format(
			match.teams[match.winner], match.teams[0 if match.winner==1 else 1],
			(11-match.innings[1].wicket),
			, match.venue, match.day))
	
	print summary[0]
	
if __name__ == '__main__':
	main()