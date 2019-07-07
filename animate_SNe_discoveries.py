#!/usr/bin/env python
import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord
import astropy.units as u
import matplotlib.pyplot as plt
plt.rc('font', family='serif')
"""
Create animation of supernova discoveries using public data from the 
Open Supernova Catalog obtained using their API https://api.sne/space/ 
(retrieved 30 June 2019)
Based in part on code from RCThomas located here:
https://commons.wikimedia.org/wiki/File:Sn_discoveries.gif
"""

### DOWNLOAD DATA ###
cols = 'name+ra+dec+discoverdate+discoverer+claimedtype' # columns to download
args = 'sortby=discoverdate&format=csv'
url = 'https://api.sne.space/catalog/{}?{}'.format(cols, args)
print 'Retrieving data from {} . . .'.format(url)

data = pd.read_csv(url, error_bad_lines=False)

### CLEAN DATA ###
# Convert date to Timestamp; NaN if format not recognized
data['date'] = pd.to_datetime(data['discoverdate'], errors='coerce')

# Remove rows containing NaN values for coordinates and date
req_cols = ['ra','dec','date']
data.dropna(subset=req_cols, inplace=True)

# Keep only bona fide SN types
data.claimedtype.fillna('', inplace=True) # convert Nan types to empty string
isSN = np.asarray([ (('Ia' in i) or ('Ib' in i) or ('Ic' in i) or (i == 'I') \
          or ('II' in i)) for i in data['claimedtype'] ])
hasSN = np.asarray([ 'SN1' in i for i in data['name'] ]) # 'SN1' in the name

years = np.asarray([ d.year for d in data['date'][isSN | hasSN] ])
surveys = np.asarray(data['discoverer'][isSN | hasSN], dtype=str)
names = np.asarray(data['name'][isSN | hasSN], dtype=str)

# Use the 1st coordinate if multiple coordinates listed in database
RA = [ i.split(',')[0] for i in data['ra'][isSN | hasSN] ] 
Dec = [ i.split(',')[0] for i in data['dec'][isSN | hasSN] ]
print 'Converting sexigesimal string of coordinates to astropy SkyCoord . . .'
coords = SkyCoord(ra=RA, dec=Dec, unit=(u.hour, u.deg))

# For selected major surveys, color points (not an exhaustive list!)
colors = []
for i, survey in enumerate(surveys):
    if 'Supernova Cosmology Project' in survey or 'SCP' in survey:
        surveys[i] = 'SCP'
        colors.append('magenta')
    elif 'HZSST' in survey:
        surveys[i] = 'HZSST'
        colors.append('gold')
    elif 'LOSS' in survey or 'LOTOSS' in survey:
        surveys[i] = 'LOSS'
        colors.append('darkviolet')
    elif 'ESSENCE' in survey:
        surveys[i] = 'ESSENCE'
        colors.append('grey')
    elif 'SNLS' in survey or 'Legacy' in survey:
        surveys[i] = 'SNLS'
        colors.append('brown')
    elif 'SDSS-II' in survey or 'SDSS-II' in names[i]:
        surveys[i] = 'SDSS-II'
        colors.append('cyan')
    elif survey.split(',')[0]=='Nearby Supernova Factory' or 'NSF' in survey:
        surveys[i] = 'SNfactory'
        colors.append('darkorange')
    elif 'PTF' in survey.split(',')[0]:
        surveys[i] = 'PTF/iPTF'
        colors.append('blue')
    elif survey.split(',')[0]=='Pan-STARRS1' or survey.split(',')[0]=='PS1':
        surveys[i] = 'PS1'
        colors.append('darkgreen')
    elif "Dark Energy Survey" in survey:
        surveys[i] = 'DES'
        colors.append('red')
    else:
        surveys[i] = 'other'
        colors.append('lime')
colors = np.asarray(colors)

### PLOT ###
survey_used = []
color_used = []
for i, y in enumerate(range(1885, 2020)):
    fig = plt.figure(figsize=(8, 5))
    ax = fig.add_subplot(111, projection='mollweide')
    past = ((years < y) & (years >= 1885)) # discovered in previous years
    if any(past):
        ax.scatter(coords.ra[past].wrap_at(180*u.deg).radian,
                   coords.dec[past].radian, c=colors[past], s=15, alpha=0.5)
    this = years == y # discovered this year
    if any(this):
        ax.scatter(coords.ra[this].wrap_at(180*u.deg).radian,
                   coords.dec[this].radian, c=colors[this], s=15, alpha=1.0)
        for s, c in zip(surveys[this], colors[this]):
            if s == 'other':
                continue
            if s not in survey_used:
                survey_used.append(s)
                color_used.append(c)
    print y, past.sum(), this.sum()
    ax.set_title(y, fontsize=20)
    ax.grid()
    for i, s in enumerate(survey_used):
        if i < 5:
            plt.text(0.78, 0.04-0.05*i, s, color=color_used[i], 
                     transform=ax.transAxes, fontsize=12)
        else:
            plt.text(0.91, 0.04-0.05*(i-5), s, color=color_used[i], 
                     transform=ax.transAxes, fontsize=12)
    fig.tight_layout()
    fig.savefig('SN_{}.png'.format(str(y)))
    plt.close()

# To create a GIF animation using ImageMagick with a 
# delay of 30/100 s between each frame and infinite looping, 
# type the following on the command line in this directory:
# convert -delay 30 -loop 0 SN_*.png SN_Discoveries.gif
