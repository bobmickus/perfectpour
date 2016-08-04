import pandas as pd
import numpy as np
import os


if __name__ == "__main__":
    #path where data files are stored

    master = pd.DataFrame()

    path = '../data/json_reviews/'
    paths = [path + f_name for f_name in os.listdir(path) if f_name != '.DS_Store']
    #read all data files into one Pandas DataFrame
    i = 0

    print paths

    for f_name in paths:
        print f_name
        #print paths[0]
        dfname = 'df'+str(i)
        print dfname
        dfname = pd.read_json(f_name)
        for index in xrange(len(dfname)):
            value = dfname.loc[index, "score"]
            if value == 'NR':
                dfname.loc[index, "score"] = np.nan
            if value == 0:
                dfname.loc[index, "score"] = 100
        i += 1
        print dfname.shape
        master = master.append(dfname, ignore_index = True)

    master = master.drop_duplicates()


'''

master['score'] = master['score'].convert_objects(convert_numeric=True)
master = master[np.isfinite(master['score'])]


master['score'] = master['score'].dropna().apply(lambda x: str(int(x)) )

for review_num in xrange(reviews2.shape[0]):
    if reviews2[reviews2['wine_id'].str.contains('WS')]:
        continue
    else:
        reviews2.wine_id.dropna().apply(lambda x: str(int(x)) )

    if reviews2.wine_id
df.col = df.col.dropna().apply(lambda x: str(int(x)) )

Review Columns = 'notes', u'review_date', u'score', u'user_id', u'wine_id',
       u'wine_name']
Wines Columns = [u'CurrentReviews', u'Grape', u'Id', u'Location', u'Name', u'PriceMax',
       u'PriceMin', u'PriceRetail', u'PriorReviews', u'Region', u'Reviews',
       u'Type', u'Year'],



'''
