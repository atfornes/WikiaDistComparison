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

distributions = ['power_law', 'truncated_power_law', 'lognormal', 'exponential', 'stretched_exponential']

comparisons = list(itertools.combinations(distributions, 2))

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

# Drop wikis with less that 100 users
df = df[df.num_users > 100]

f, plots = plt.subplots(len(distributions), 4, figsize=(25, 25), sharex='col')

for dist in distributions:
    i = distributions.index(dist)
    passedTests = dist + '_passed_tests'
    losedTests = dist + '_losed_tests'
    #  Wikis in which the distribution won all alternatives
    win = df[df[passedTests]==(len(distributions)-1)]
    #  Wikis in which the distribution lost against an alternative
    lose = df[df[losedTests]>0]
    # Wikis in which the distribution neither won all alternatives
    # nor lost against any alternative
    draw = df[~df.isin(win) & ~df.isin(lose)]
    plots[i][0].scatter(draw['num_users'], draw['total_edits'], c='grey', label='draw');
    p = plots[i][0].scatter( lose['num_users'], lose['total_edits'], c=lose[losedTests], cmap='autumn_r', label=lose[losedTests]);
    plots[i][0].set_title(dist + ' comparison')
    plots[i][0].set_ylabel('Total edits')
    plots[i][0].set_xlabel('Users')
    plots[i][0].set_xscale('log')
    plots[i][0].set_yscale('log')
    cb = plt.colorbar(p, ax=plots[i][0])
    cb.ax.set_ylabel('# of losed tests', rotation=270, labelpad=10)
    plots[i][0].legend();
    if len(win) > 0:
        plots[i][0].scatter(win['num_users'], win['total_edits'], c='green', label='win');
        plots[i][0].legend();
        for param in params[dist]:
            j = 1 + params[dist].index(param)
            paramData = win[dist + '_' + param]
            normFunc = matplotlib.colors.LogNorm();
            #Log normalization does not work for negative values
            if ((len(win[paramData<0]) > 0) |
                # If the order of magnitude of the difference between values is smaller than 10, it does not make sense to use log normalization
                ((max(paramData) / min(paramData)) < 10)):
                normFunc = matplotlib.colors.Normalize();
            p = plots[i][j].scatter(win['total_edits'],
                                    win['num_users'], c=paramData, cmap="Spectral", norm = normFunc);
            plots[i][j].set_title(dist + ' ' + param)
            plots[i][j].set_ylabel('Total edits')
            plots[i][j].set_xlabel('Users')
            plots[i][j].set_xscale('log')
            plots[i][j].set_yscale('log')
            plt.colorbar(p, ax=plots[i][j])

f.savefig('distributions.png')
