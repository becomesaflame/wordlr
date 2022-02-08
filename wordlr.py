import datetime
import os
import re
import tweepy

# To run from interactive session:
# exec(open("wordlr.py").read())


# rows = parseGram("""⬛Yellow squareGreen square⬛⬛
# Green square⬛Green squareGreen squareGreen square
# Green squareGreen squareGreen squareGreen squareGreen square
# ⬜⬜Yellow square⬜Yellow square
# Green squareYellow square⬜⬜⬜
# Green square⬜⬜Green square⬜
# Green square⬜Green squareGreen squareGreen square
# Green squareGreen squareGreen squareGreen squareGreen square
# ⬛Yellow square⬛Green square⬛
# ⬛⬛Green squareGreen square⬛
# ⬛⬛Green squareGreen square⬛
# ⬛⬛Green squareGreen squareGreen square
# Green square⬛Green squareGreen squareGreen square
# ⬜Yellow square⬜⬜Yellow square
# Yellow square⬜⬜Green squareGreen square
# Green squareGreen squareGreen squareGreen squareGreen square
# ⬛Yellow square⬛⬛⬛
# ⬛⬛⬛Green square⬛
# ⬛⬛⬛Yellow square⬛
# Green squareYellow square⬛⬛⬛
# Green squareYellow squareGreen square⬛Yellow square
# Green square⬜Green squareGreen square⬜
# Green square⬜Green squareGreen squareGreen square
# Green square⬛⬛⬛⬛
# Green square⬛Green square⬛⬛
# Green squareGreen squareGreen square⬛⬛
# ⬛⬛⬛⬛⬛
# ⬛⬛Green square⬛Yellow square
# ⬛Yellow squareGreen square⬛⬛
# Green square⬛Green squareGreen square⬛
# Green square⬛Green squareGreen squareGreen square
# ⬛Yellow square⬛⬛⬛
# Green squareYellow squareYellow squareGreen square⬛
# Green square⬛Green squareGreen squareGreen square
# ⬛Yellow square⬛⬛⬛
# ⬛⬛Yellow squareGreen square⬛
# ⬛Yellow squareYellow square⬛Yellow square
# Green square⬛Green squareGreen squareGreen square
# ⬜⬜⬜⬜⬜
# ⬜Yellow square⬜⬜⬜
# Yellow square⬜⬜⬜⬜
# ⬜⬜⬜Yellow square⬜
# Green square⬜Green square⬜⬜
# Green squareYellow square⬛⬛⬛
# Green squareYellow square⬛⬛Green square
# Green square⬛Green squareGreen squareGreen square
# ⬛⬛Green square⬛⬛
# ⬛⬛Green squareGreen squareGreen square
# ⬛⬛Green squareGreen squareGreen square
# Green square⬛Green squareGreen squareGreen square
# Yellow square⬛⬛⬛⬛
# ⬛⬛⬛⬛⬛
# Green square⬛⬛Green square⬛
# ⬛⬛⬛Yellow square⬛
# ⬛Yellow squareYellow square⬛Yellow square
# Green squareYellow squareGreen square⬛Yellow square
# ⬛⬛⬛Yellow square⬛
# ⬛⬛Green square⬛⬛
# Green squareYellow squareGreen square⬛⬛
# ⬜⬜⬜Yellow square⬜
# Green square⬜Green square⬜Yellow square
# ⬜⬜⬜Yellow square⬜
# Green square⬜Green square⬜Yellow square
# ⬛⬛Yellow squareGreen square⬛
# ⬛Yellow squareYellow square⬛Yellow square
# ⬛⬛⬛⬛Yellow square
# Green square⬛⬛⬛Yellow square
# Green squareGreen square⬛⬛⬛
# Green squareGreen squareGreen square⬛⬛
# ⬜Yellow square⬜⬜Yellow square
# Yellow square⬜⬜Green squareGreen square""")



# rows = [[G,B,G,G,G],[G,Y,Y,Y,B],[G,G,G,B,B],[G,B,B,G,B],[B,B,B,B,Y],[Y,Y,B,B,B],[G,B,G,B,Y],[G,B,B,Y,G],[G,B,B,B,Y],[B,B,G,G,Y],[B,B,B,Y,B],[B,B,G,B,Y],[B,Y,G,Y,B],[B,B,G,G,B],[G,Y,G,B,Y],[G,Y,G,B,Y],[Y,Y,B,B,B]] + rows
from collections import defaultdict

with open('wordList.txt') as f:
    wordlist = [ line.strip() for line in f ]
# 
Y = 1
G = 2 
B = 0
wordleEpoch = datetime.date(2021, 6, 19)
wordleNumberToday = (datetime.date.today() - wordleEpoch).days

greenCache = defaultdict(list)

# given a row and a word, return only the green letters, with ?'s for the
# rest of the letters
def greenKey(row,answer):
	k = ""
	for i, color in enumerate(row):
		if color == G:
			k += answer[i]
		else:
			k += "?"
	return k

# print(greenKey([2,2,0,0,2], "TESTS"))

# Make a list of all combinations of greens
# This is just enumerating binary numbers for 5 bits (green/black)
greenRows = []
for i in range(32):
	greenRows.append([G if ((1 << bit) & i) != 0 else B for bit in range(5)])
# print(greenRows)

for word in wordlist:
	for row in greenRows:
		greenCache[greenKey(row,word)].append(word)



# Score a guess. Given an answer and guess, return the row
def scoreGuess(answer, guess):
	answer = list(answer)
	guess = list(guess)
	row = [0,0,0,0,0]
	lettersLeft = answer.copy()
	# Figure out greens
	for letterIndex,letter in enumerate(guess):
		if guess[letterIndex] == answer[letterIndex]:
			row[letterIndex] = 2
			lettersLeft.remove(guess[letterIndex])
	# Figure out yellows
	for letterIndex,letter in enumerate(guess):
		if row[letterIndex] == 2:
			continue
		elif guess[letterIndex] in lettersLeft:
			row[letterIndex] = 1;
			lettersLeft.remove(guess[letterIndex])
	return row

# For a given row, check if the answer is valid
def validAnswer(row, answer, dictionary):
	for word in greenCache[greenKey(row,answer)]:
		if row == scoreGuess(answer, word): 
			# answer has at least one valid guess for this row
			return True
	# answer has no valid guesses. Trim answer from subDictionary
	return False

# Take a row and trim down the dictionary
# Go through dictionary
# For each word, assume it's the answer
# check that there is at least one other word in the dictionary that would 
# result in the given score
def trimDictionary(row, subDictionary, dictionary):
	for answer in subDictionary:
		if not validAnswer(row, answer, dictionary):
			str1 = ''
			# print("Trimming ", str1.join(answer))
			subDictionary.remove(str1.join(answer))


# Trim the dictionary based on a list of rows
def trimDictionaryRows(rows, subDictionary, dictionary):
	for row in rows:
		trimDictionary(row, subDictionary, dictionary)
		print("trimmed down to ",len(subDictionary))
		# if len(subDictionary) == 1:
		# 	print(subDictionary[0])
		# 	return subDictionary
	return subDictionary


# Trim the dictionary based on a list of rendered tweets
# renderedTweets should be a list of lists of rows
def trimDictionaryRenderedTweets(renderedTweets, subDictionary, dictionary):
	for i, renderedTweet in enumerate(renderedTweets):
		trimDictionaryRows(renderedTweet, subDictionary, dictionary)
		# if len(subDictionary) == 1:
		# 	return subDictionary
	return subDictionary

# Takes a row, and increments the count for each 
# word of a tally dictionary that doesn't fit the row
# tallyDictionary input should be a dict
# key is word, value is tally
# dictionary is the list of words to validate rows
def tallyRowStrikes(row, tallyDictionary, dictionary):
	for word in list(tallyDictionary.keys()):
		if not validAnswer(row, word, dictionary):
			tallyDictionary[word] += 1

# Convert a pasted wordle gram to a list of rows
def parseGram(gram):
	g = re.sub("[a-z ]","",gram)
	rows = []
	for gramRow in g.split('\n'):
		row = []
		for block in gramRow:
			if block == "Y":
				row.append(1)
			elif block == "G":
				row.append(2)
			elif block == "⬛" or block == "⬜":
				row.append(0)
			else:
				raise Exception("Ohno: " + block )
		rows.append(row)
	return rows

# dictionary = wordlist.copy()


# TODO move this to a test
# # Check if the set of all possible rows for the given answer will narrow down the dictionary to that answer
# # Generate all possible rows
# allRows = []
# allCells = [G,Y,B]
# for t0 in allCells:
# 	for t1 in allCells:
# 		for t2 in allCells:
# 			for t3 in allCells:
# 				for t4 in allCells:
# 					allRows.append([t0,t1,t2,t3,t4])

# validRows = []
# for row in allRows:
# 	if validAnswer(row, "skill", dictionary):
# 		validRows.append(row)

# d = trimDictionaryRows(validRows, dictionary)
# print(d)		



# ref:
# https://dev.to/twitterdev/a-comprehensive-guide-for-using-the-twitter-api-v2-using-tweepy-in-python-15d9
#
# API: 
# https://docs.tweepy.org/en/stable/client.html
def scrapeTwitter():
	# consumer_key = os.environ.get("TWITTER_API_KEY")
	# consumer_secret = os.environ.get("TWITTER_API_KEY_SECRET")
	bearer_token = os.environ.get("TWITTER_BEARER_TOKEN")
	# access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
	# access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

	# auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	# auth.set_access_token(access_token, access_token_secret)
	# api = tweepy.API(auth,wait_on_rate_limit=True)
	client = tweepy.Client(bearer_token=bearer_token)

	text_query = 'Wordle 6'
	try:
		# tweets = client.search_recent_tweets(query=text_query, max_results=100)

		tweets = []
		for tweet in tweepy.Paginator(client.search_recent_tweets, query=text_query, max_results=100).flatten(limit=5000):
			tweets.append(tweet.data['text'])

		return tweets 

	except BaseException as e:
	    print('failed on_status,',str(e))
	    time.sleep(3)

# Takes a list of Wordle tweet text fields
# Sanitizes, parses, and renders them into rows
# Return will be list of list of rows
# Each tweet will become a list of rows with length 0-6 
def parseTweets(tweets, wordleNumberToday):
	renderedTweets = []
	for i, tweet in enumerate(tweets):
		try:
			rows = [] # rendered rows in this tweet
			tweetLines = tweet.split('\n')
			# Skip any introductory added text and find start of wordle grid
			for line in tweetLines:
				match = re.match("Wordle ([0-9]{3}) ([X1-6])/6", line)
				wordleNumber = int(match.group(1)) if match else None
				score = match.group(2) if match else None
				if wordleNumber != wordleNumberToday:
					raise Exception("Wrong wordle")
				if score == 'X':
					score = 6
				score = int(score)
				tweetLines.remove(line)
				if match:
					break
			if tweetLines[0] == '':
				del tweetLines[0]
			else:
				raise Exception('Unexpected post format - no blank line between header and rows')
			# Parse rows of squares
			for line in tweetLines[:score]:
				row = []
				if len(line) != 5:
					raise Exception('Unexpected post format - row length')
				for box in list(line):
					if box == '\N{Black Large Square}' or box == '\N{White Large Square}':
						row.append(B)
					elif box == '\N{Large Yellow Square}' or box == '\N{Large Blue square}':
						row.append(Y)
					elif box == '\N{Large Green Square}' or box == '\N{Large Orange square}':
						row.append(G)
					else:
						raise Exception('Unexpected post format - row contains unexpected character')
				rows.append(row)
			renderedTweets.append(rows)
		except BaseException as err:
			print(f"Unexpected {err=}, {type(err)=}, parsing tweet {i}:")
			print(tweet)
			print("stripped down to lines: ")
			print(tweetLines)
			continue
	return renderedTweets

def checkAnswer(answer, tweets, dictionary, wordleNumberToday):
	renderedTweets = parseTweets(tweets, wordleNumberToday)
	for i, renderedTweet in enumerate(renderedTweets):
		for j, row in enumerate(renderedTweet):
			if validAnswer(row, answer, dictionary) == False:
				print(f"Row {j} in Tweet {i} is invalid. Tweet: ")
				print(tweets[i].split('\n'))
				print("Rendered tweet: ")
				print(renderedTweet)


tweets = scrapeTwitter()
dictionary = wordlist.copy()
subDictionary = dictionary.copy()
renderedTweets = parseTweets(tweets, wordleNumberToday)
# subDictionary = trimDictionaryRenderedTweets(renderedTweets, subDictionary, dictionary)
# while len(subDictionary) != 1:
# 	renderedTweets = parseTweets(tweets, wordleNumberToday)
# 	subDictionary = trimDictionaryRenderedTweets(renderedTweets, subDictionary, dictionary)
# 	print(subDictionary)
# 	sleep(30)

def sortDict(inDict, topWords):
	for word in list(inDict.keys()):
		if len(topWords) != 2:
			topWords.append(word)
		if inDict[word] < inDict[topWords[0]]:
			topWords[1] = topWords[0]
			topWords[0] = word
		elif inDict[word] > inDict[topWords[0]]+50:
			del inDict[word]
	return topWords

dictionary = wordlist.copy()
tallyDictionary = dict.fromkeys(dictionary, 0)
topWords = []
for tweet in renderedTweets:
	for row in tweet:
		if row == [G,G,G,G,G]:
			continue
		tallyRowStrikes(row, tallyDictionary, dictionary)
		# tallyRowStrikes = sorted(tallyRowStrikes, key=tallyRowStrikes.get) # sort by strikes
		topWords = sortDict(tallyDictionary, topWords)
		print(topWords[0], ":", tallyDictionary[topWords[0]], " old:", topWords[1],":",tallyDictionary[topWords[1]], " Remaining:", len(tallyDictionary))
		if tallyDictionary[topWords[0]] < tallyDictionary[topWords[1]] - 10:
			print(f"{topWords[0]} wins with {tallyDictionary[topWords[0]]}")
			print(f"{topWords[1]} in second with {tallyDictionary[topWords[1]]}")
			# return topWords[0]
