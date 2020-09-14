#!/usr/bin/python3

import re
import random
import sys

# These mappings can get fairly large -- they're stored globally to
# save copying time.

# (tuple of words) -> {dict: word -> number of times the word appears following the tuple}
# Example entry:
#    ('eyes', 'turned') => {'to': 2.0, 'from': 1.0}
# Used briefly while first constructing the normalized mapping
tempMapping = {}

# (tuple of words) -> {dict: word -> *normalized* number of times the word appears following the tuple}
# Example entry:
#    ('eyes', 'turned') => {'to': 0.66666666, 'from': 0.33333333}
mapping = {}

# Contains the set of words that can start sentences
starts = []

# We want to be able to compare words independent of their capitalization.
def fixCaps(word):
    # Ex: "FOO" -> "foo"
    if word.isupper() and word != "I":
        word = word.lower()
        # Ex: "LaTeX" => "Latex"
    elif word[0].isupper():
        word = word.lower().capitalize()
        # Ex: "wOOt" -> "woot"
    else:
        word = word.lower()
    return word

# Tuples can be hashed; lists can't.  We need hashable values for dict keys.
# This looks like a hack (and it is, a little) but in practice it doesn't
# affect processing time too negatively.
def toHashKey(lst):
    return tuple(lst)

# Returns the contents of the file, split into a list of words and
# (some) punctuation.
def wordlist(filename):
    f = open(filename, 'r')
    wordlist = [fixCaps(w) for w in re.findall(r"[\w']+|[.,!?;]", f.read())]
    f.close()
    return wordlist

# Self-explanatory -- adds "word" to the "tempMapping" dict under "history".
# tempMapping (and mapping) both match each word to a list of possible next
# words.
# Given history = ["the", "rain", "in"] and word = "Spain", we add "Spain" to
# the entries for ["the", "rain", "in"], ["rain", "in"], and ["in"].
def addItemToTempMapping(history, word):
    global tempMapping
    while len(history) > 0:
        first = toHashKey(history)
        if first in tempMapping:
            if word in tempMapping[first]:
                tempMapping[first][word] += 1.0
            else:
                tempMapping[first][word] = 1.0
        else:
            tempMapping[first] = {}
            tempMapping[first][word] = 1.0
        history = history[1:]

# Building and normalizing the mapping.
def buildMapping(wordlist, markovLength):
    global tempMapping
    starts.append(wordlist [0])
    for i in range(1, len(wordlist) - 1):
        if i <= markovLength:
            history = wordlist[: i + 1]
        else:
            history = wordlist[i - markovLength + 1 : i + 1]
        follow = wordlist[i + 1]
        # if the last elt was a period, add the next word to the start list
        if history[-1] == "." and follow not in ".,!?;":
            starts.append(follow)
        addItemToTempMapping(history, follow)
    # Normalize the values in tempMapping, put them into mapping
    for first, followset in tempMapping.items():
        total = sum(followset.values())
        # Normalizing here:
        mapping[first] = dict([(k, v / total) for k, v in followset.items()])

# Returns the next word in the sentence (chosen randomly),
# given the previous ones.
def next(prevList):
    global randType
    sum = 0.0
    retval = ""
    index = random.random()
    # Shorten prevList until it's in mapping
    while toHashKey(prevList) not in mapping:
        prevList.pop(0)

    for k, v in mapping[toHashKey(prevList)].items():
        sum += v
        if sum >= index and retval == "":
            retval = k
    return retval

def syllable_count(word):
    word = word.lower()
    count = 0
    vowels = "aeiouy"
    #print(word)
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
    if word.endswith("e"):
        count -= 1
    if count == 0:
        count += 1
    return count

def genPoem(markovLength):
    global randType
    #number of sentences:
    lines = 0
    wordBuff = 0
    if randType == 2:
        rand = 14
        rand2 = 10
    else:
        rand = random.randint(10, 14)
        rand2 = random.randint(7, 10)
    # Start with a random "starting word"
    curr = random.choice(starts)
    sent = curr.capitalize()
    prevList = [curr]
    while lines < rand:
        curr = next(prevList)
        prevList.append(curr)
        # if the prevList has gotten too long, trim it
        if len(prevList) > markovLength:
            prevList.pop(0)
        if wordBuff > rand2 and curr not in ".,!?;":
            sent += "\n"
            wordBuff = 0
        if curr.isupper():
            rand3 = random.randint(1, 3)
            if rand3 == 3:
                sent += "\n"
            elif rand3 == 2:
                curr == curr.lower()
        if (curr in ","):
            x = random.randint(1, 3)
            if x == 1 and len(curr) < 40:
                curr = curr[:-1]
            if x == 2:
                curr = curr[:-1] + "."
        if (curr not in ".,!?;"):
            sent += " " # Add spaces between words (but not punctuation)
            wordBuff += 1
        if (curr  in ".!?;"):
            sent += curr
            sent += "\n"*random.choices(population = [1,2], weights = [0.8, 0.2])[0]
            lines += 1
            wordBuff = 0
        else:
            sent += curr
        if len(sent) > 1200:
            continue
            
    if randType == 2:
        print("Wow it's *almost* traditional")
        syls = 0
        words1 = sent.replace("\n", "")
        words = list(words1.split(" "))
        #print(words1)
        #print(words)
        wordtups = []
        for i in words:
            syls += int(syllable_count(i))
            wordtups.append((i, int(syllable_count(i))))
        #print(wordtups)
        sylCut = int(syls / 15)
        """
        for i in range(0, 10):
            sylCut = 11 - 0
            if syls % sylCut == 0:
                continue
        """
        sylCount = 0
        sent2 = ""
        lineCount = 1
        for addword in wordtups:
            if lineCount > 14:

                continue
            elif addword[1] + sylCount > sylCut and lineCount in [4, 8, 11, 14]:
                sent2 += "\n\n " + addword[0].capitalize() + " "
                sylCount = 0
                lineCount += 1
            elif addword[1] + sylCount > sylCut and lineCount not in [4, 8, 11, 14]:
                sent2 += "\n " + addword[0].capitalize() + " "
                sylCount = 0
                lineCount += 1
            else:
                sent2 += addword[0] + " "
                sylCount += addword[1]
        sent = sent2
    else:
        print("He's wild")

    while sent[-1] in ";,: ":
        sent = sent[:-1]

    print("============ENJOY============")
    print("")
    print(sent)




def main():
    global randType
    randType = random.randint(1, 2)
    #params
    if len(sys.argv) < 2:
        print("Shakespeare made you something a bit more 21st century, and he's doin somethin mean to it:")
        print("")
        filename = "shakespeareSonnets.txt"
        markovLength = 1

    if len(sys.argv) == 2:
        print(sys.argv[1][-1])
        if sys.argv[1][-1] == "t":
            print("Damn, your poet has some new edgy material: ")
            print("")
            filename = sys.argv[1]
            markovLength = 1
        else:
            print("Shakespeare made you something a bit more 21st century:")
            print("")
            filename = "shakespeareSonnets.txt"
            markovLength = int(sys.argv[1])

    if len (sys.argv) == 3:
        print("Thanks for the heavy inspiration ! Let's check your poet's wokeness level:")
        print("")
        filename = sys.argv[1]
        markovLength = int(sys.argv[2])


    buildMapping(wordlist(filename), markovLength)
    genPoem(markovLength)

if __name__ == "__main__":
    main()
