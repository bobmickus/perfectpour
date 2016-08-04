import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import matplotlib.patches as mpatches
import matplotlib.cbook as cbook

wines = pd.read_json('../data/master_wines.json')

grapes = wines.Grape.value_counts()
top_grapes = grapes[:10]
top_grapes = dict(top_grapes)

# fig, ax = plt.subplots()
# my_colors = 'rgbkymc'
# ax.bar(range(len(top_grapes), top_grapes.values(), align='center', color=my_colors, alpha=0.5, label=top_grapes.keys())
# #ax.xticks(range(len(top_grapes)), list(top_grapes.keys()), rotation=45)
# plt.xlabel('Grape Varietal')
# plt.title('Top Ten Grapes Found in Reviews')
# plt.ylabel('Number of Reviews')
# ax.legend()
# ax.grid(True)
# plot.legend(loc=2,prop={'size':6})
# fig.tight_layout()


gvalues = top_grapes.values()
labels = top_grapes.keys()
colors = ['#800080',
     '#FF0000',
     '#BC8F8F',
       '#4169E1',
     '#8B4513',
      '#FAFAD2',
      '#87AE73',
     '#FAA460',
     '#2E8B57',
    '#FF4500']
#colors = ['r', 'g', 'y', 'b', 'k', 'm', 'c', 'pumpkin', 'chartreuse', 'burgundy']

df = pd.DataFrame({'value': gvalues,
                   'label': labels,
                    'color': colors})


fig, ax = plt.subplots()

# Plot each bar separately and give it a label.
for index, row in df.iterrows():
    ax.bar([index], [row['value']], color=row['color'], label=row['label'], alpha=0.5, align='center')

ax.legend(loc='best', frameon=False)

# More reasonable limits for a vertical bar plot...
ax.margins(0.05)
ax.set_ylim(bottom=0)

# Styling similar to your example...
ax.patch.set_facecolor('0.9')
ax.grid(color='white', linestyle='-')
ax.set(axisbelow=True, xticklabels=[])
plt.title('Top Ten Grapes Found in Reviews', fontsize = 16)
plt.ylabel('Number of Reviews', fontsize = 14)
plt.legend(loc='best' ,prop={'size':12})


'''
reviews = pd.read_json('../data/clean_reviews.json')
scores = reviews.score.value_counts()
scores = dict(scores)
num_ratings = scores.values()
scores = scores.keys()

df2 = pd.DataFrame({'scores': scores,
                   'Number_of_Reviews': num_ratings})
df2 = df2.sort(['scores'], ascending=[1])
df2 = df2.set_index('scores')
df2 = df2.ix[75:]

ax = df2[['Number_of_Reviews']].plot(kind='bar',figsize=(15,10),legend=True, fontsize=24, color='#701112', alpha = 0.9)
#ax.grid(color='white', linestyle='-')
plt.title('Score Distribution', fontsize = 24)
plt.ylabel('Number of Reviews', fontsize = 18)
plt.xlabel('Score Given', fontsize = 14)



'''
