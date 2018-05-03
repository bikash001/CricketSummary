import sys
import re
import inflect

inflect_engine = inflect.engine()

class CustomDictionary(dict):
	"""dot.notation access to dictionary attributes"""
	__getattr__ = dict.get
	__setattr__ = dict.__setitem__
	__delattr__ = dict.__delitem__

class Batsman(CustomDictionary):
	pass

# name (string) = batsman name
# status (string) = (not out, if out how? ("run out (Chris Woakes/CJ Anderson")))
# run (int)
# ball (int) = no. of ball played
# four (int) = no. of 4's
# six (int) = no. of 6's
# sr (float) = strike rate
def create_batsman(n, s, r, b, f, sx, sr):
	data = re.findall(r'[\w ]+', n)
	return Batsman(name=data[0].strip(),  status=s, run=int(r),
		ball=int(b), four=int(f), six=int(sx),
		sr=float(sr))

class Bowler():
	def __init__(self, name, over):
		self._name = name  	# name of bowler (string)
		self._data = [] 	# contains raw data e.g. [W 1 1 W 1 1]
		self._overs = 0 	# no. of overs
		self._wickets = 0 	# no. of wickets
		self._runs = 0 		# no. of runs 
		self._maidens = 0	# no. of maiden overs
		self.add_over(over)

	def add_over(self, over):
		self._data.append(over)
		self._overs += 1
		self._analyse(over)

	# analyse each over
	# i.e. calculate runs, wickets, maidens, etc.
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

# preprocess raw data like "McClenaghan: W 1 1 W 1 1"
def create_or_load_bowler(inning, info):
	name, data = info.split(':')
	name = name.strip()
	data = map(str.strip, data.split())
	if name in inning.bowler_info:
		inning.bowler_info[name].add_over(data)
	else:
		inning.bowler_info[name] = Bowler(name, data)
	inning.bowlers.append(name)
	inning.overs.append(data)

# Innings class
# batsman (list contains Batsman object)
# bowlers (list contains bowlers name in the order of bowling)
# bowler_info (dictionary contains bowler_name as key and Bowler object as value)
# run (int) = total runs in the inning
# wicket (int) = total wicket in the inning
class Innings(CustomDictionary):
	pass

def create_innings():
	return (Innings(batsmans=[], overs=[], batsman_info={}, bowlers=[], bowler_info={}, run=None, wicket=None, over_details={}, team=""), 
			Innings(batsmans=[], overs=[], batsman_info={}, bowlers=[], bowler_info={}, run=None, wicket=None, over_details={}, team=""))

# Match class
# day (string) = day of week e.g. Monday
# date (string) = complete date e.g. 12th Jan, 2018
# venue (string)
# teams (tuple of string) = name of teams
# toss (tuple of int) = (a, b) where a is the index in teams which won toss, b is 0 if batting, 1 if fielding
class Match(CustomDictionary):
	pass

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
		# print data
		match.winner = 0 if match.teams[0]==data else 1
		# print match.winner, data
		
		# First Inning
		inning = match.innings[0]
		inning.team = match.toss[0] if match.toss[1] == 0 else 1 if match.toss[0] == 0 else 0
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
			bm = create_batsman(*map(str.strip, data.split(',')))
			inning.batsman_info[bm.name] = bm
			inning.batsmans.append(bm.name)
			data = fp.readline().strip()

		# wickets
		label = 'Wickets:'
		data = fp.readline().strip().split('),')
		for x in data:
			y = re.findall(r"[\w\d \.-]+", x) # y = ['0-1 ', 'Suryakumar Yadav', ' 0.1']
			ovr = int(float(y[2].strip()))+1
			if not ovr in inning.over_details:
				inning.over_details[ovr] = [y[1].strip()]
			else:
				inning.over_details[ovr].append(y[1].strip())	
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
		inning.team = 0 if match.innings[0].team == 1 else 1
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
			bm = create_batsman(*map(str.strip, data.split(',')))
			inning.batsman_info[bm.name] = bm
			inning.batsmans.append(bm.name)
			data = fp.readline().strip()

		# wickets
		label = 'Wickets:'
		data = fp.readline().strip().split('),')
		for x in data:
			y = re.findall(r"[\w\d \.-]+", x) # y = ['0-1 ', 'Suryakumar Yadav', ' 0.1']
			ovr = int(float(y[2].strip()))+1
			if not ovr in inning.over_details:
				inning.over_details[ovr] = [y[1].strip()]
			else:
				inning.over_details[ovr].append(y[1].strip())	

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
	for name, batsman in inning.batsman_info.items():
		total_run += batsman.run

	total_wicket = 0
	for name, bowler in inning.bowler_info.items():
		total_wicket += bowler.wickets()

	inning.run = total_run
	inning.wicket =  total_wicket
	return total_run, total_wicket

def winner(match, summary):
	# return
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
			match.venue, match.day))
	
	# print summary[0]
	
def six_four_threshold():
	return 3

def run_threshold():
	return 20

def calculate_inning_info(inning):
	overs = []
	b1 = inning.batsmans[0]
	b2 = inning.batsmans[1]
	count = 0
	total_runs = 0
	prev_run = 0

	for y, over in zip(inning.bowlers, inning.overs):
		while count < len(inning.batsmans) and inning.batsman_info[inning.batsmans[count]].status == 'not out':
			count += 1

		w, r = 0, 0
		pp = []
		pr = []
		for x in over:
			if len(x) == 1:
				if x == 'W':
					w += 1
					pp.append('%s,%s' %(b1, b2))
					pr.append(total_runs + r - prev_run)
					prev_run = total_runs + r
					if b1 == inning.batsmans[count]:
						if count+1 < len(inning.batsmans)
							b1 == inning.batsmans[count+1]
					else:
						if count+1 < len(inning.batsmans):
							b2 = inning.batsmans[count+1]
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
					pp.append('%s,%s' %(b1, b2))
					pr.append(total_runs + r - prev_run)
					prev_run = total_runs + r
					if b1 == inning.batsmans[count]:
						if count+1 < len(inning.batsmans)
							b1 == inning.batsmans[count+1]
					else:
						if count+1 < len(inning.batsmans):
							b2 = inning.batsmans[count+1]
				else:
					r += cnt
		total_runs += r
		overs.append({'run': r, 'wicket': w, 'partners':pp, 'prun': pr})
	return overs

def schemas(match, summary):
	# start --> winner losing_team_batting winning_team_batting
	# winner (report who won and by how much)
	# losing_team_batting --> batsman_formance batsman_out_by_bowler
	winner(match, summary)
	if match.winner == match.innings[0].team:
		inning = match.innings[1]
	else:
		inning = match.innings[0]

	over_wise_status = calculate_inning_info(inning)
	not_out_players = [obj	for _, obj in inning.batsman_info.items() if obj.status == 'not out']

	for i in range(1, 21):
		if i in inning.over_details:
			for player in inning.over_details[i]:
				batsman = inning.batsman_info[player]
				if batsman.run < run_threshold():
					continue
				summary.append('{} scored {} run.'.format(player, batsman.run))
				if batsman.six + batsman.four >= six_four_threshold():
					sentence = '{} hit'.format(player)
					if batsman.six > 0 and batsman.four > 0:
						sentence += ' {} six and {} four.'.format(batsman.six, batsman.four)
					elif batsman.six > 0:
						sentence += ' {} sixes.'.format(batsman.six)
					else:
						sentence += ' {} fours.'.format(batsman.four)
					summary.append(sentence)
				if batsman.status[0] == 'b':
					summary.append('{} was clean bowled by {}.'.format(player, inning.bowlers[i]))
				elif batsman.status[0] == 'c':
					summary.append('{} was caught by {}.'.format(player, re.findall(r'[\w(][\w ()]+\w(?= +b )', batsman.status[1:])[0]))
				elif batsman.status[:2] == 'st':
					summary.append('{} was stumped by {}.'.format(player, re.findall(r'[\w(][\w ()]+\w(?= +b )', batsman.status[2:])[0]))
				elif 'run out' in batsman.status:
					summary.append('{} got run out.'.format(player))

	for player in not_out_players:
		if player.run >= 50:
			summary.append('{} remained unbeaten on {}.'.format(player.name, player.run))
			sentence = 'He hit'
			if player.six == 1:
				sentence = 'He smacked a six'
				if player.four == 1:
					sentence += ' and a four'
				elif player.four > 1:
					sentence += ' and %s fours' %(inflect_engine.number_to_words(player.four), player.ball)
				sentence += ' in %d balls.' %(player.ball)
				summary.append(sentence)
			elif player.six > 1:
				sentence += ' %s sixes' %(inflect_engine.number_to_words(player.six))
				if player.four == 1:
					sentence += ' and a four'
				elif player.four > 1:
					sentence += ' and %s fours' %(inflect_engine.number_to_words(player.four))
				sentence += ' in %d balls.' %(player.ball)
				summary.append(sentence)
			else:
				if player.four > 1:
					sentence += ' %s fours in %d balls.' %(inflect_engine.number_to_words(player.four), player.ball)
					summary.append(sentence)
			continue
		else:
			summary.append('{} scored {} run.'.format(player.name, player.run))
		batsman = player
		if batsman.six + batsman.four >= six_four_threshold():
			sentence = '{} hit'.format(player.name)
			if batsman.six > 0 and batsman.four > 0:
				sentence += ' {} six and {} four.'.format(batsman.six, batsman.four)
			elif batsman.six > 0:
				sentence += ' {} sixes.'.format(batsman.six)
			else:
				sentence += ' {} fours.'.format(batsman.four)
			summary.append(sentence)
		
	summary.append('\t')

	if match.winner == match.innings[0].team:
		inning = match.innings[0]
	else:
		inning = match.innings[1]

	over_wise_status = calculate_inning_info(inning)
	not_out_players = [obj	for _, obj in inning.batsman_info.items() if obj.status == 'not out']

	for i in range(1, 21):
		if i in inning.over_details:
			for player in inning.over_details[i]:
				batsman = inning.batsman_info[player]
				if batsman.run < run_threshold():
					continue
				summary.append('{} scored {} run.'.format(player, batsman.run))
				if batsman.six + batsman.four >= six_four_threshold():
					sentence = '{} hit'.format(player)
					if batsman.six > 0 and batsman.four > 0:
						sentence += ' {} six and {} four.'.format(batsman.six, batsman.four)
					elif batsman.six > 0:
						sentence += ' {} sixes.'.format(batsman.six)
					else:
						sentence += ' {} fours.'.format(batsman.four)
					summary.append(sentence)
				if batsman.status[0] == 'b':
					summary.append('{} was clean bowled by {}.'.format(player, inning.bowlers[i]))
				elif batsman.status[0] == 'c':
					summary.append('{} was caught by {}.'.format(player, re.findall(r'[\w(][\w ()]+\w(?= +b )', batsman.status[1:])[0]))
				elif batsman.status[:2] == 'st':
					summary.append('{} was stumped by {}.'.format(player, re.findall(r'[\w(][\w ()]+\w(?= +b )', batsman.status[2:])[0]))
				elif 'run out' in batsman.status:
					summary.append('{} got run out.'.format(player))

	for player in not_out_players:
		if player.run >= 50:
			summary.append('{} remained unbeaten on {}.'.format(player.name, player.run))
			sentence = 'He hit'
			if player.six == 1:
				sentence = 'He smacked a six'
				if player.four == 1:
					sentence += ' and a four'
				elif player.four > 1:
					sentence += ' and %s fours' %(inflect_engine.number_to_words(player.four), player.ball)
				sentence += ' in %d balls.' %(player.ball)
				summary.append(sentence)
			elif player.six > 1:
				sentence += ' %s sixes' %(inflect_engine.number_to_words(player.six))
				if player.four == 1:
					sentence += ' and a four'
				elif player.four > 1:
					sentence += ' and %s fours' %(inflect_engine.number_to_words(player.four))
				sentence += ' in %d balls.' %(player.ball)
				summary.append(sentence)
			else:
				if player.four > 1:
					sentence += ' %s fours in %d balls.' %(inflect_engine.number_to_words(player.four), player.ball)
					summary.append(sentence)
			continue
		else:
			summary.append('{} scored {} run.'.format(player.name, player.run))
		batsman = player
		if batsman.six + batsman.four >= six_four_threshold():
			sentence = '{} hit'.format(player.name)
			if batsman.six > 0 and batsman.four > 0:
				sentence += ' {} six and {} four.'.format(batsman.six, batsman.four)
			elif batsman.six > 0:
				sentence += ' {} sixes.'.format(batsman.six)
			else:
				sentence += ' {} fours.'.format(batsman.four)
			summary.append(sentence)


if __name__ == '__main__':
	summary = []
	match = parse_input(sys.argv[1])
	schemas(match, summary)
	print '\n'.join(summary)