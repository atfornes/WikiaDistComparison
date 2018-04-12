#!/usr/bin/env python

import powerlaw
import pandas as pd
import numpy as np
import pylab
from os import listdir
import pickle
import multiprocessing
import itertools

def intOrNaN(maybeInt="0"):
    try:
        return int(maybeInt)
    except ValueError:
        return np.nan;

def splitOrEmpty(maybeStringList="", splitStr=","):
   try:
       return maybeStringList.split(splitStr)
   except AttributeError:
       return [0]

# WIKIA:

wikiaPath = 'wikiaData/';

wikiaFiles = ['wikia_edits_2018-04-09.csv']

wikiaResults = []

comparisons = list(itertools.combinations(['power_law', 'truncated_power_law', 'lognormal', 'exponential', 'stretched_exponential'], 2))

compColumns = []

for (a, b) in comparisons:
  vs = a + '_vs_' + b
  compColumns += [vs+ '_R', vs +'_p']

resultColumns = ['url', 'wiki_name', 'total_edits', 'max_contribs', 'edits_per_user', 'bots', 'bots_contribs_pct', 'anonymous_contribs_pct', 'num_users', 'power_law_alpha', 'power_law_sigma', 'power_law_xmin', 'truncated_power_law_alpha', 'truncated_power_law_lambda', 'lognormal_mu', 'lognormal_sigma', 'exponential_lambda', 'stretched_exponential_lambda', 'stretched_exponential_beta' ] + compColumns

df = pd.DataFrame(columns=resultColumns)

for f in wikiaFiles:
    print "Reading " + f + "..."
    dfaux = pd.read_csv(wikiaPath + f, quotechar='"', delimiter=';', skipinitialspace = True, converters = {'total_edits': lambda x: intOrNaN(x) if x != '-1' else np.nan})
    df = pd.concat([df, dfaux])

# wikias without statistic information are marked with a -1 in their data
withStatistics = df[df['wiki_name'] != '-1']

df = withStatistics

# wikias without empty user edits
df = df[~np.isnan(df['total_edits'])]

df = df.drop_duplicates(subset='url')

df['edits_per_user'] = df['edits_per_user'].map(lambda x: splitOrEmpty(x, ","))
df['edits_per_user'] = df['edits_per_user'].map(lambda x: filter(lambda y: y > 0, map(intOrNaN, x)))

df['bots'] = df['bots'].map(lambda x: splitOrEmpty(x, ","))
df['bots'] = df['bots'].map(lambda x: filter(lambda y: y > 0, map(intOrNaN, x)))

s = df['edits_per_user'].map(lambda x: len(x)).sort_values(ascending=False).index

df = df.reindex(s, columns=resultColumns)

df = df.reset_index(drop=True)

df['bots_contribs_pct'] = 100 * df['bots'].map(lambda x: intOrNaN(sum(x))) / df['total_edits']

df['anonymous_contribs_pct'] = 100 - ( 100 * ( df['edits_per_user'].map(lambda x: intOrNaN(sum(x))) + df['bots'].map(lambda x: intOrNaN(sum(x)))) / df['total_edits'])

df['num_users'] = df['edits_per_user'].map(lambda x: len(x))

df['max_contribs'] = df['edits_per_user'].map(lambda x: x[0] if len(x) > 0 else np.nan)

dfCensus = pd.read_csv(wikiaPath + 'curated-Wikia-complete-withBirthDate-v2.csv', quotechar='"', delimiter=',', skipinitialspace = True, converters = {'english': lambda x: x if x else False})

df = df.merge(dfCensus, on='url')

for index, row in df[df['edits_per_user'].map(lambda x: len(x))>100].iterrows():
    data = np.array(row['edits_per_user']);
    r = powerlaw.Fit(data, discrete=True);
    df.at[index,'power_law_alpha'] = r.power_law.alpha
    df.at[index,'power_law_sigma'] = r.power_law.sigma
    df.at[index,'power_law_xmin'] = r.power_law.xmin
    df.at[index,'truncated_power_law_alpha'] = r.truncated_power_law.alpha
    df.at[index,'truncated_power_law_lambda'] = r.truncated_power_law.parameter2
    df.at[index,'lognormal_mu'] = r.lognormal.mu
    df.at[index,'lognormal_sigma'] = r.lognormal.sigma
    df.at[index,'exponential_lambda'] = r.exponential.parameter1
    df.at[index,'stretched_exponential_lambda'] = r.stretched_exponential.parameter1
    df.at[index,'stretched_exponential_beta'] = r.stretched_exponential.beta
    for (a, b) in comparisons:
        R, p = r.distribution_compare(a, b);
        df.at[index, a + '_vs_' + b + '_R'] = R
        df.at[index, a + '_vs_' + b + '_p'] = p

df.to_pickle('wikiasDistCompared.pkl');

# to read: with open('wikiasDistCompared.pkl', 'rb') as handle:
#              df = pickle.load(handle)
