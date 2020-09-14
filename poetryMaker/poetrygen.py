#!/usr/bin/python3

import markovgen
import sys

if len(sys.argv) == 1:
    text = sys.argv[0]
else:
    text = open('./shakespeareSonnets.txt')


markov = markovgen.Markov(text)
markov.generate_markov_text()
