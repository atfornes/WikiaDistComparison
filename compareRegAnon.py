#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt
import pickle
import pandas as pd
import numpy as np
import itertools
import sys

def intOrZero(maybeInt="0"):
    try:
        return int(maybeInt)
    except ValueError:
        return 0;

if (len(sys.argv) != 3):
    print 'usage: compareRegAnon.py registeredContribsFile.pkl registered+AnonContribsFile.pkl'

regFile = sys.argv[1]
regAnonFile = sys.argv[2]

with open(regAnonFile, 'rb') as handle:
    dfRegAnon = pickle.load(handle)

with open(regFile, 'rb') as handle:
    dfReg = pickle.load(handle)

#dfRegAnon['url'] = 'http://' + dfRegAnon['url'] + '/'
#dfReg['url'] =  'http://' + dfReg['url'] + '/'

#dfReg = dfReg[dfReg['url'].isin(dfRegAnon['url'])]

distributions = ['power_law', 'truncated_power_law', 'lognormal', 'exponential', 'stretched_exponential']

comparisons = list(itertools.combinations(distributions, 2))

def printComparisonData(df):
    for dist in distributions:
        distComparisons = filter(lambda x: x.count(dist) > 0, comparisons)
        passedTests = map(lambda x: 1 * (((1 if x.index(dist) == 0 else -1) * df[x[0] + '_vs_' + x[1] + '_R'] > 0) & (df[x[0] + '_vs_' + x[1] + '_p'] < 0.1)), distComparisons)
        df[dist + '_passed_tests'] = reduce(lambda x, y: y + x, passedTests)
        losedTests = map(lambda x: 1 * (((-1 if x.index(dist) == 0 else 1) * df[x[0] + '_vs_' + x[1] + '_R'] > 0) & (df[x[0] + '_vs_' + x[1] + '_p'] < 0.1)), distComparisons)
        df[dist + '_losed_tests'] = reduce(lambda x, y: y + x, losedTests)

    for dist in distributions:
        print 'times ' + dist + ' is better than all alternatives: ' + str(len(df[df[dist + '_passed_tests'] == 4]))

    num_wikis = len(df[(df['num_users'] >= 100)])

    print 'Total wikis: ' + str(num_wikis)

print 'Distribution comparison of registered user contribution:'
printComparisonData(dfReg)

print 'Distribution comparison of anonymous and registered user contribution:'
printComparisonData(dfRegAnon)
