from astropy.io import ascii
import pandas as pd
import numpy as np
import re

# load abundance data
abund_data = ascii.read("abund_data_v4.txt") # your file name here (.txt or something)

# transform abund_data table into DataFrame
abund_data = pd.DataFrame(abund_data.as_array())

# grab the unique names of all stars in the sample
all_stars = abund_data["star"].unique()

# the logic will be to create abundance tables for each star and, then, concatenate them together with pandas
# in the process, i will save the individual abundance tables for each star as well

for STAR in all_stars:
	# loop through each of our stars
	star_X = abund_data[abund_data["star"]==STAR] #all_stars[i]]
	# get all individual elements/species for that star
	species = star_X["elem"]
	# first, lets build our HEADER
	# NOTE: I realized afterwards that I should also initialize the 'header' and 'row' with the metallicity from FeI 
	header = ["name", "[FeI/H]", "[FeI/H]_unc"] # stars with "name" which is going to be the column for the names of stars
	# we also initialize our row, which is going to be filled with the abundance values for that one star
	row    = [str(STAR.split('_')[0]), float(star_X["[X/H]"][star_X["elem"]=="Fe I"]), float(star_X["e_XH"][star_X["elem"]=="Fe I"])]
	# now we loop through the different species to construct our header
	for x in species:
		# add things to our header
		XFe    = "["+str(re.sub('[^a-zA-Z]+', '', x))+"/Fe]" # the craziness is because I am removing the spaces (e.g., "Na I" becomes "NaI") 
		e_XFe  = XFe+"_unc"
		ul_XFe = "flag_"+XFe
		header.append(XFe)
		header.append(e_XFe)
		header.append(ul_XFe)
		# add the values to our row
		XFe    = float(star_X["[X/Fe]"][star_X["elem"]==x])
		e_XFe  = float(star_X["e_XFe" ][star_X["elem"]==x])
		ul_XFe = float(star_X["ul"    ][star_X["elem"]==x])
		if ul_XFe == 0:
			ul_XFe = "det"
		else:
			ul_XFe = "ul"
		row.append(XFe)
		row.append(e_XFe)
		row.append(ul_XFe)
	# save a file which stacks 'header' and 'row' together
	tab = np.vstack((header,row))
	np.savetxt(str(STAR.split('_')[0])+"_format_abund.csv", tab, delimiter=',', fmt='%s')
	# the above code WORKS (smiley face here), but we still need to create the 'master' abundance table with all info
	# to do this, I think the best way is to concatenate with pandas
	# for this to work, the 'tab' needs to be a pandas DataFrame, so... 
	tab = pd.DataFrame(tab, columns=tab[0])
	tab = tab.tail(-1) # this removes the first row of a DataFrame, so it does not repeat the columns names 
	if STAR == all_stars[0]: 
		master_abund_table = tab # if this is the first star in the list, there is nothing to concatenate with
	else:
		master_abund_table = pd.concat([master_abund_table, tab], sort=False, ignore_index=True)

print(master_abund_table)
master_abund_table.to_csv("master_abund_table.csv", index=False) # it's stupid to save over and over, but this works
	
