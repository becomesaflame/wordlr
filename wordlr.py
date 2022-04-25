from collections import defaultdict
import copy
import datetime
import json
import os
import re
import time
import tweepy

# To run from interactive session:
# exec(open("wordlr.py").read())

WIN_GAP = 20 # How much of a lead one answer needs to achieve before declaring victory

ANSWER_CHECK = '' # Debug: Put correct answer here to flag erroneous strikes

# Load the list of all viable Wordle words
with open('wordList.txt') as f:
    wordlist = [ line.strip() for line in f ]

# Shorthand constants for block colors
Y = 1
G = 2 
B = 0

# Figure out today's Wordle number
wordleEpoch = datetime.date(2021, 6, 19)
wordleNumberToday = (datetime.date.today() - wordleEpoch).days

def sortDict(inDict, topWords):
	for word in list(inDict.keys()):
		if len(topWords) != 2:
			topWords.append(word)
		elif inDict[word] < inDict[topWords[0]]:
			topWords[1] = topWords[0]
			topWords[0] = word
		elif inDict[word] < inDict[topWords[1]] and word != topWords[0]:
			topWords[1] = word
		elif inDict[word] > inDict[topWords[0]]+WIN_GAP+1:
			del inDict[word]
	return topWords

def tallyRowStrikesFast(row, tallyDictionary, rowLookup):
	if row == [G,G,G,G,G]:
		return # TODO check syntax for exiting with no return value
	for answer in tallyDictionary.keys():
		if not answer in rowLookup[''.join(str(i) for i in row)]: # Convert row to str
			tallyDictionary[answer] += 1
			if answer == ANSWER_CHECK:
				print("False strike on row:")
				print(row)
				breakpoint()

# Tally Strikes
# For a list of parsed tweets, check each row against every
# word in the dictionary. Tally a strike against each word
# that could not be an answer that generated that row
def tallyStrikes(tallyDictionary, renderedTweets, dictionary, rowLookup, lineCount):
	topWords = []
	win = False
	for tweet in renderedTweets: # note that invalid tweets are still here as empty lists
		for row in tweet:
			lineCount += 1
			tallyRowStrikesFast(row, tallyDictionary, rowLookup)
		topWords = sortDict(tallyDictionary, topWords)
		print(topWords[0], ":", tallyDictionary[topWords[0]], " second place:", topWords[1],":",tallyDictionary[topWords[1]], " Remaining:", len(tallyDictionary), "Processed ", lineCount, " lines")
		if tallyDictionary[topWords[0]] < tallyDictionary[topWords[1]] - WIN_GAP:
			win = True
			break
	return topWords, win, lineCount

# ref:
# https://dev.to/twitterdev/a-comprehensive-guide-for-using-the-twitter-api-v2-using-tweepy-in-python-15d9
#
# API: 
# https://docs.tweepy.org/en/stable/client.html
def initTweepyClient():
	bearer_token = os.environ.get("TWITTER_BEARER_TOKEN")
	client = tweepy.Client(bearer_token=bearer_token)
	return client

def scrapeTwitter(client):
	text_query = 'Wordle 6'
	try:
		tweets = []
		for tweet in tweepy.Paginator(client.search_recent_tweets, query=text_query, max_results=100).flatten(limit=1000):
			tweets.append(tweet.data['text'])
		return tweets 
	except BaseException as e:
		print('failed on_status,',str(e))
		print('Did you load the API key into your environment?')
		time.sleep(3)

# Takes a list of Wordle tweet text fields
# Sanitizes, parses, and renders them into rows
# Return will be list of list of rows
# Each tweet will become a list of rows with length 0-6 
def parseTweets(tweets, wordleNumberToday):
	renderedTweets = []
	for i, tweet in enumerate(tweets):
		rows = [] # rendered rows in this tweet
		try:
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
		except BaseException as err:
			print(f"Unexpected {err=}, {type(err)=}, parsing tweet {i}:")
			print(tweet)
			print("stripped down to lines: ")
			print(tweetLines)
		renderedTweets.append(rows)
	return renderedTweets


# Loads the rowLookup dict
# import rowLookupTable.py
exec(open("rowLookupTable.py").read())

dictionary = wordlist.copy()

if __name__ == '__main__':
	# Scrape and parse tweets
	client = initTweepyClient()

	tallyDictionary = dict.fromkeys(dictionary, 0)
	lineCount = 0
	win = False

	while win == False:
		# breakpoint()

		# Scrape 100 tweets
		tweets = scrapeTwitter(client)
		# Parse the tweets into rows
		renderedTweets = parseTweets(tweets, wordleNumberToday)

		# Run with vote method
		topWords, win, lineCount = tallyStrikes(tallyDictionary, renderedTweets, dictionary, rowLookup, lineCount)

	print(f"{topWords[0]} wins with {tallyDictionary[topWords[0]]}")
	print(f"{topWords[1]} in second with {tallyDictionary[topWords[1]]}")
	print(f"Parsed {lineCount} lines")


