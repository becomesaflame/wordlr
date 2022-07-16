from collections import defaultdict
import datetime
import json
import time

startTime = time.perf_counter()

# Shorthand constants for block colors
Y = 1
G = 2 
B = 0

# Generate all possible rows
def genAllRows():
	allRows = []
	allCells = [G,Y,B]
	for t0 in allCells:
		for t1 in allCells:
			for t2 in allCells:
				for t3 in allCells:
					for t4 in allCells:
						allRows.append([t0,t1,t2,t3,t4])
	return allRows


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

# Load the list of all viable Wordle words
with open('wordList.txt') as f:
    wordlist = [ line.strip() for line in f ]

# given a row and a word, return only the green letters, with ?'s for the
# rest of the letters
greenCache = defaultdict(list)
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


# For a given row, check if the given answer could 
# have produced that row for any guess
def validAnswer(row, answer, dictionary):
	for word in greenCache[greenKey(row,answer)]:
		if row == scoreGuess(answer, word): 
			# answer has at least one valid guess for this row
			return True
	# answer has no valid guesses. Trim answer from subDictionary
	return False

# Generate row lookup table
# For every possible row, generate a list of every possble answer that could result in that row
# dictionary: list of all possible Wordle words
def generateRowLookup(dictionary):
	rowLookup = defaultdict(list)

	allRows = genAllRows()
	for row in allRows:
		strRow = ''.join(str(i) for i in row) # Convert list of ints to str
		rowLookup[strRow] = []
		for answer in dictionary:
			if validAnswer(row, answer, dictionary):
				rowLookup[strRow].append(answer)
		print(strRow)
	f = open("rowLookupTableJSON.py", 'w')
	json.dump(rowLookup, f)
	f.close()
	return rowLookup

if __name__ == '__main__':
	generateRowLookup(wordlist)
	executionTime = (time.perf_counter() - startTime)
	print(f"Execution time h:m:s: {datetime.timedelta(seconds=executionTime)}")
