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

if (len(sys.argv) == 1):
    fileName = 'wikiasDistCompared.pkl'
else:
    fileName = sys.argv[1]

with open(fileName, 'rb') as handle:
    df = pickle.load(handle)

# Drop wikis with less that 100 users
df = df[df.num_users >= 100]

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

fVsWins, plotsVsWins = plt.subplots(len(distributions), len(distributions), figsize=(25, 25), sharex=True, sharey=True)

fVsDraws, plotsVsDraws = plt.subplots(len(distributions), len(distributions), figsize=(25, 25), sharex=True, sharey=True)

for (a, b) in comparisons:
    print a + ' vs ' + b + ' comparison:'
    wins = df[(df[a + '_vs_' + b + '_R'] > 0) & (df[a + '_vs_' + b + '_p'] < 0.1)]
    a_wins_b = len(wins)
    loses = df[(df[a + '_vs_' + b + '_R'] < 0) & (df[a + '_vs_' + b + '_p'] < 0.1)]
    b_wins_a = len(loses)
    draws = df[(~df.isin(loses)) & (~df.isin(wins))]
    ai = distributions.index(a)
    bi = distributions.index(b)
    plotsVsWins[ai][bi].set_title(b + ' wins ' + a);
    plotsVsDraws[ai][bi].scatter(draws['num_users'], draws['total_edits'], alpha=0.3, label='draws', c="grey")
    plotsVsDraws[ai][bi].set_ylabel('Total edits')
    plotsVsDraws[ai][bi].set_xlabel('Users')
    plotsVsDraws[ai][bi].set_xscale('log')
    plotsVsDraws[ai][bi].set_yscale('log')
    plotsVsDraws[ai][bi].set_ylim(ymin=100, ymax=30000000)
    plotsVsDraws[ai][bi].set_xlim(xmin=100, xmax=30000000)
    plotsVsDraws[ai][bi].set_title(a + ' Draws ' + b);
    plotsVsWins[ai][bi].scatter(loses['num_users'], loses['total_edits'], alpha=0.3, label='win')
    plotsVsWins[ai][bi].set_ylabel('Total edits')
    plotsVsWins[ai][bi].set_xlabel('Users')
    plotsVsWins[ai][bi].set_xscale('log')
    plotsVsWins[ai][bi].set_yscale('log')
    plotsVsWins[ai][bi].set_ylim(ymin=100, ymax=30000000)
    plotsVsWins[ai][bi].set_xlim(xmin=100, xmax=30000000)
    plotsVsWins[bi][ai].set_title(a + ' wins ' + b);
    plotsVsWins[bi][ai].scatter(wins['num_users'], wins['total_edits'], alpha=0.3, label='win')
    plotsVsWins[bi][ai].set_ylabel('Total edits')
    plotsVsWins[bi][ai].set_xlabel('Users')
    plotsVsWins[bi][ai].set_xscale('log')
    plotsVsWins[bi][ai].set_yscale('log')
    plotsVsWins[bi][ai].set_ylim(ymin=100, ymax=30000000)
    plotsVsWins[bi][ai].set_xlim(xmin=100, xmax=30000000)
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

f, plots = plt.subplots(len(distributions), 4, figsize=(25, 25), sharex=True, sharey=True)

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
    #draw = df[~df.isin(win) & ~df.isin(lose)]
    noWin = df[~df.isin(win)]
    draw = noWin[~noWin.isin(lose)]
    plotsVsDraws[i][i].set_title(dist + ' ties with all alternatives ');
    plotsVsDraws[i][i].scatter(draw['num_users'], draw['total_edits'], alpha=0.3, c='grey')
    plotsVsDraws[i][i].set_ylabel('Total edits')
    plotsVsDraws[i][i].set_xlabel('Users')
    plotsVsDraws[i][i].set_xscale('log')
    plotsVsDraws[i][i].set_yscale('log')
    plotsVsDraws[i][i].set_ylim(ymin=100, ymax=30000000)
    plotsVsDraws[i][i].set_xlim(xmin=100, xmax=30000000)
#    plots[i][0].scatter(draw['num_users'], draw['total_edits'], alpha=0.3, c='grey', label='draw');
    p = plots[i][0].scatter(noWin['num_users'], noWin['total_edits'], c=noWin[losedTests], cmap="Wistia", label=None, vmin=0, vmax=4);
    plots[i][0].set_title(dist + ' comparison')
    plots[i][0].set_ylabel('Total edits')
    plots[i][0].set_xlabel('Users')
    plots[i][0].set_xscale('log')
    plots[i][0].set_yscale('log')
    plots[i][0].set_ylim(ymin=100, ymax=30000000)
    plots[i][0].set_xlim(xmin=100, xmax=30000000)
    cb = plt.colorbar(p, ax=plots[i][0])
    cb.ax.set_ylabel('# of losed tests', rotation=270, labelpad=10)
    if len(win) > 0:
        plots[i][0].scatter(win['num_users'], win['total_edits'], alpha=0.3, c='teal', label='win');
        plotsVsWins[i][i].set_title(dist + ' wins all alternatives ');
        plotsVsWins[i][i].scatter(win['num_users'], win['total_edits'], alpha=0.3)
        plotsVsWins[i][i].set_ylabel('Total edits')
        plotsVsWins[i][i].set_xlabel('Users')
        plotsVsWins[i][i].set_xscale('log')
        plotsVsWins[i][i].set_yscale('log')
        plotsVsWins[i][i].set_ylim(ymin=100, ymax=30000000)
        plotsVsWins[i][i].set_xlim(xmin=100, xmax=30000000)
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
            p = plots[i][j].scatter(win['num_users'],
                                    win['total_edits'], alpha=0.3, c=paramData, cmap="Spectral", norm = normFunc);
            plots[i][j].set_title(dist + ' ' + param)
            plots[i][j].set_ylabel('Total edits')
            plots[i][j].set_xlabel('Users')
            plots[i][j].set_xscale('log')
            plots[i][j].set_yscale('log')
            plots[i][j].set_ylim(ymin=100, ymax=30000000)
            plots[i][j].set_xlim(xmin=100, xmax=30000000)
            plt.colorbar(p, ax=plots[i][j])

fVsWins.savefig(fileName + 'allVsAll_distributions.png')
fVsDraws.savefig(fileName + 'draws_distributions.png')
f.savefig(fileName + '_distributions.png')
