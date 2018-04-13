#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt
import pickle
import pandas as pd
import numpy as np
import itertools


def intOrZero(maybeInt="0"):
    try:
        return int(maybeInt)
    except ValueError:
        return 0;


with open('wikiasDistCompared.pkl', 'rb') as handle:
    df = pickle.load(handle)

f, plots = plt.subplots(len(numeric_cols), 2, figsize=(15, 75), sharey='row')

distributions = ['power_law', 'truncated_power_law', 'lognormal', 'exponential', 'stretched_exponential']

comparisons = list(itertools.combinations(distributions, 2))

for dist in distributions:
    distComparisons = filter(lambda x: x.count(dist) > 0, comparisons)
    passedTests = map(lambda x: 1 * (((1 if x.index(dist) == 0 else -1) * df[x[0] + '_vs_' + x[1] + '_R'] > 0) & (df[x[0] + '_vs_' + x[1] + '_p'] < 0.1)), distComparisons)
    df[dist + '_passed_tests'] = reduce(lambda x, y: y + x, passedTests)

for dist in distributions:
    print 'times ' + dist + ' is better than all alternatives: ' + str(len(df[df[dist + '_passed_tests'] == 4]))

num_wikis = len(df[(df['num_users'] >= 100)])

print 'Total wikis: ' + str(num_wikis)

for (a, b) in comparisons:
    print a + ' vs ' + b + ' comparison:'
    a_wins_b = len(df[(df[a + '_vs_' + b + '_R'] > 0) & (df[a + '_vs_' + b + '_p'] < 0.1)])
    b_wins_a = len(df[(df[a + '_vs_' + b + '_R'] < 0) & (df[a + '_vs_' + b + '_p'] < 0.1)])
    remain = num_wikis - a_wins_b - b_wins_a
    print '  - %.2f' % (100.0 * a_wins_b / num_wikis) + '% ' + a + ' wins ' + b + ' in ' + str(a_wins_b) + ' cases'
    print '  - %.2f' % (100.0 * b_wins_a / num_wikis) + '% ' + b + ' wins ' + a + ' in ' + str(b_wins_a) + ' cases'
    print '  - %.2f' % (100.0 * (num_wikis - a_wins_b - b_wins_a) / num_wikis) + '% Remaining cases:' + str(remain)


params = {
    'power_law': ['alpha', 'sigma', 'xmin'],
    'truncated_power_law': ['alpha', 'lambda'],
    'lognormal': ['mu', 'sigma'],
    'exponential': ['lambda'],
    'stretched_exponential': ['lambda', 'beta'],
}

f, plots = plt.subplots(len(distributions), 3, figsize=(25, 25), sharex=True, sharey= True)

for dist in distributions:
    i = distributions.index(dist)
    passedTests = dist + '_passed_tests';
    data = df[(df['num_users']>100) & (df[passedTests]>3)]
    if len(data) > 0:
        for param in params[dist]:
            j = params[dist].index(param)
            normFunc = matplotlib.colors.LogNorm();

            p = plots[i][j].scatter(data['total_edits'],
                                    data['num_users'], c=data[dist + '_' + param], cmap="Spectral", norm = normFunc);
            plots[i][j].set_title(dist + ' ' + param)
            plots[i][j].set_ylabel('Total edits')
            plots[i][j].set_xlabel('Users')
            plots[i][j].set_xscale('log')
            plots[i][j].set_yscale('log')
            plt.colorbar(p, ax=plots[i][j])

f.savefig('distributions.png')

norm=,
