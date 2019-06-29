#!/usr/bin/env python
import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord
import astropy.units as u
import matplotlib.pyplot as plt
plt.rc('font', family='serif')
"""
Create animation of supernova discoveries based on data 
from the Open Supernova Catalog obtained using their API 
https://api.sne/space/ (retrieved 29 June 2019)
"""

# Download data 
cols = 'name+ra+dec+discoverdate+discoverer+claimedtype' # columns to download
args = 'sortby=discoverdate&format=csv'
url = 'https://api.sne.space/catalog/{}?{}'.format(cols, args)
print 'Retrieving data from {} . . .'.format(url)

data = pd.read_csv(url, error_bad_lines=False)

### CLEAN DATA ###
# Convert date to Timestamp, NaN if format not recognized
data['date'] = pd.to_datetime(data['discoverdate'], errors='coerce')

# Remove rows containing NaNs values for coordinates and date
req_cols = ['ra','dec','date']
data.dropna(subset=req_cols, inplace=True)

# Keep only bonafide SN types
data.claimedtype.fillna('', inplace=True) # convert Nan types to empty string
isSN = np.asarray([ (('Ia' in i) or ('Ib' in i) or ('Ic' in i) or (i == 'I') \
          or ('II' in i)) for i in data['claimedtype'] ])
hasSN = np.asarray([ 'SN1' in i for i in data['name'] ])# 'SN1' in the name

# Use the 1st coordinate if multiple coordinates listed
RA = [ i.split(',')[0] for i in data['ra'][isSN | hasSN] ] 
Dec = [ i.split(',')[0] for i in data['dec'][isSN | hasSN] ]
print 'Converting sexigesimal string of coordinates to astropy SkyCoord . . .'
coords = SkyCoord(ra=RA, dec=Dec, unit=(u.hour, u.deg))
years = np.asarray([ d.year for d in data['date'][isSN | hasSN] ])

# Plot
for i, y in enumerate(range(1885, 2020)):
    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot(111, projection='mollweide')
    past = ((years < y) & (years >= 1885)) # discovered in previous years
    if any(past):
        ax.scatter(coords.ra[past].wrap_at(180*u.deg).radian,
                   coords.dec[past].radian, c='b', s=15, alpha=0.5)
    this = years == y # discovered this year
    if any(this):
        ax.scatter(coords.ra[this].wrap_at(180*u.deg).radian,
                   coords.dec[this].radian, c='b', s=15, alpha=1.0)
    print y, past.sum(), this.sum()
    ax.set_title(y)
    ax.grid()
    fig.tight_layout()
    imgname = 'SN_{}.png'.format(str(y))
    fig.savefig(imgname)
    plt.close()

# To create gif animation with ImageMagick with 
# delay of 30/100 s between each frame and infinite loop, 
# type the following on the command line in this directory:
# convert -delay 30 -loop 0 SN_*.png SN_Discoveries.gif
