#!/usr/bin/env python

import powerlaw
import pandas as pd
import numpy as np
import matplotlib
import pylab
from os import listdir
import itertools
import sys


# source https://stackoverflow.com/a/9251091/4928558
def find_csv_filenames( path_to_dir=".", suffix=".csv", prefix=""):
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if (filename.startswith( prefix ) and filename.endswith( suffix )) ]


# WIKIA:

wikiaPath = 'wikiaData/';

if (len(sys.argv) > 2):
    wikiaPath = sys.argv[2]



wikiaFiles = find_csv_filenames(wikiaPath, 'wikia.com.csv')

wikiaResults = []


botIds = []
bots =  []
if (len(sys.argv) > 1):
    botIdsFileName = sys.argv[1]
    bots = pd.read_csv(wikiaPath + botIdsFileName)
    bots = list(bots.values.flatten())
    bots = map(lambda x: str(x), bots)
    print str(len(bots)) + ' bot ids loaded'

df = pd.DataFrame()

for f in wikiaFiles:
    url = f[:-4]
    print url
    dfaux = pd.read_csv(wikiaPath + f, delimiter=";", quotechar="|")
    data = pd.DataFrame()
    anonymous = dfaux[dfaux['contributor_id'].str.contains('\.')]
    users = dfaux[(~dfaux['contributor_id'].str.contains('\.')) & (~dfaux['contributor_id'].isin(bots))]
    botContribs = dfaux[(dfaux['contributor_id'].isin(bots))]
    data['edits_per_anonymous'] = [sorted(list(anonymous.groupby(['contributor_id'])['contributor_id'].count()), reverse=True)]
    data['edits_per_user'] = [sorted(list(users.groupby(['contributor_id'])['bytes'].count()), reverse=True)]
    #data['bytes_contrib'] = list(dfaux.groupby(['contributor_id'])['bytes'].sum())
    data['edits_per_bot'] = [sorted(list(botContribs.groupby(['contributor_id'])['bytes'].count()), reverse=True)]
    data['url'] = url
    data['anonymous_edits'] = data['edits_per_anonymous'].map(lambda x: sum(x))
    data['registered_edits'] = data['edits_per_user'].map(lambda x: sum(x))
    data['bot_edits'] = data['edits_per_bot'].map(lambda x: sum(x))
    data['total_edits'] = data['registered_edits'] + data['anonymous_edits']
    data['num_anonymous'] = data['edits_per_anonymous'].map(lambda x: len(x))
    data['num_bots'] = data['edits_per_bot'].map(lambda x: len(x))
    data['num_users'] = data['edits_per_user'].map(lambda x: len(x))
    df = pd.concat([df, data])

comparisons = list(itertools.combinations(['power_law', 'truncated_power_law', 'lognormal', 'exponential', 'stretched_exponential'], 2))

s = df['edits_per_user'].map(lambda x: len(x)).sort_values(ascending=False).index

df = df.reindex(s)

df = df.reset_index(drop=True)

def compare(df, withAnon=False):
    for index, row in df[df['edits_per_user'].map(lambda x: len(x))>=100].iterrows():
        if (withAnon):
            data = np.array(row['edits_per_user']+row['edits_per_anonymous']);
        else:
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

compare(df, False)

df.to_pickle(wikiaPath + 'registeredWithoutAnons+' + ('bots+' if len(bots) == 0 else 'FILTEREDbots+') + 'DistCompared.pkl');

compare(df, True)

df.to_pickle(wikiaPath + 'registeredWithAnons+' + ('bots+' if len(bots) == 0 else 'FILTEREDbots+') + 'DistCompared.pkl');
