sn-discoveries
==============

_Create animation of SN discoveries across the sky_

This code retrieves supernova data from the <a href="https://sne.space">Open Supernova Catalog</a>
using the <a href="https://github.com/astrocatalogs/OACAPI">Open Astronomy Catalog API</a> and
plots the sky locations of supernovae over time from 1885 to the present. A series of plots (135
PNGs) are generated in the current directory, after which I use ImageMagick to compile them into a
GIF animation.

Python
------

**Requirements**

- numpy
- pandas
- astropy
- matplotlib

ImageMagick
-----------

The Python script itself does not require ImageMagick. However, I use ImageMagick's convert
command to create the final GIF animation by typing the following into the command line:

```
convert -delay 30 -loop 0 SN_*.png SN_Discoveries.gif
```

This creates an infinite loop GIF animation with a delay of 30/100 of a second between
each frame.

Acknowledgments
---------------

This code is based in part on <a href="https://commons.wikimedia.org/wiki/File:Sn_discoveries.gif">
code</a> written by RCThomas.
