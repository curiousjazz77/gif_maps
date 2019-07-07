# load libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import seaborn as sns
import time
import os
from pysal.esda.mapclassify import Quantiles, Equal_Interval

# set the filepath and load in a shapefile
fp = "datasets/geo-data/gis-boundaries-london/ESRI/London_Borough_Excluding_MHW.shp"

data = gpd.read_file(fp)


# check borough names
data.head()

# load in new csv to merge with geodata
df = pd.read_csv("datasets/MPS_Borough_Level_Crime_Historic.csv", header=0, encoding="utf-8")

df.head()

# filter to include only data labeled as 'Violence Against the Person'
filtered = df['major_category'] == 'Violence Against the Person'

violence = df[filtered]

violence

# groupby to get the sum of each by borough
df3 = violence.groupby('borough').sum()

df3.head()

# then we need to melt the df so it's in tidy format. reshape the table to keep the columns borough, category, year (as variable) and value
melted = pd.melt(violence,  id_vars=['borough','major_category','minor_category'])

melted.head()


df2 = melted.groupby('borough').sum()

df2.head()


# then let's pivot the dataframe to add on the column 'major_category' and add up the values for each borough by year
crime = melted.pivot_table(values='value', index=['borough','major_category'], columns='variable', aggfunc=np.sum)
crime.columns = crime.columns.get_level_values(0)
crime.head()


# join the geodataframe with the cleaned up csv dataframe
merged1 = data.set_index('NAME').join(df3)

merged1 = merged1.reindex(merged1.index.rename('borough'))

merged1.max

# CREATE A LOOP TO MAKE MULTIPLE MAPS WITH YEAR ANNOTATIONS

# save all the maps in the charts folder
output_path = 'charts/maps'

# counter for the for loop
i = 0

# list of years (which are the column names at the moment)
list_of_years = ['200807','200907','201007','201107','201207','201307','201407','201507','201607']

# set the min and max range for the choropleth map
vmin, vmax = 200, 1200

# start the for loop to create one map per year
for year in list_of_years:
    
    # create map
    fig = merged1.plot(column=year, cmap='Purples', figsize=(10,10), linewidth=0.8, edgecolor='0.8', vmin=vmin, vmax=vmax, 
                       legend=True, norm=plt.Normalize(vmin=vmin, vmax=vmax)) # UDPATE: added plt.Normalize to keep the legend range the same for all maps
    
    # remove axis of chart
    fig.axis('off')
    
    # add a title
    fig.set_title('Violent crimes in London', \
              fontdict={'fontsize': '25',
                         'fontweight' : '3'})
    
    # create an annotation for the year
    only_year = year[:4]
    
    # position the annotation to the bottom left
    fig.annotate(only_year,
            xy=(0.1, .225), xycoords='figure fraction',
            horizontalalignment='left', verticalalignment='top',
            fontsize=35)

   # this will save the figure as a high-res png in the output path. you can also save as svg if you prefer.
    filepath = os.path.join(output_path, only_year+'_violence.png')
    chart = fig.get_figure()
    chart.savefig(filepath, dpi=300)


