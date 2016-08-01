
from os import path
import graphlab as gl
from datetime import datetime
import pandas as pd



#Table of interactions between users and items: user_id, wine_id, score, timestamp

#reviews = pd.read_csv('./data/user_reviews.csv')

reviews = pd.read_json('./data/clean_reviews.json')
reviews = reviews.drop(['notes', 'found', 'review_date', 'price'], 1)
bob = pd.DataFrame()
#bob.loc[0, 'review_date'] = '09/12/2015'
bob.loc[0, 'score'] = 92.0
bob.loc[0, 'user_id'] = 'bob_mickus'
bob.loc[0, 'wine_name'] = 'Michael David Winery Freakshow Cabernet Sauvignon 2014'

reviews = reviews.reset_index(drop=True)
#reviews = reviews.loc[reviews['review_date'].notnull(), :]
reviews = reviews.loc[reviews['score'].notnull(), :]
#reviews = reviews.drop(['notes', 'wine_data'], 1)
reviews['user_id'] = reviews['user_id'].str.encode('utf-8')
reviews['user_id'] = reviews['user_id'].astype('str')
reviews['wine_id'] = reviews['wine_id'].astype('str')
reviews['wine_name'] = reviews['wine_name'].str.encode('utf-8')
reviews['wine_name'] = reviews['wine_name'].astype('str')
#reviews['wine_name'] = reviews['wine_name'].map(lambda x: x.lstrip('0123456789 '))
#reviews['score'] = reviews['score'].dropna().apply(lambda x: str(int(x)) )
# x = reviews.loc[reviews['score'].isin([0.0])]
# for review in x:
#     reviews.loc[x.index, 'score'] = 100.0

try:
    pd.to_datetime(reviews['review_date'], format='%m/%d/%Y')
except:
    pass
actions = gl.SFrame(reviews)
actions = actions.dropna()

#Table of wines to recommend: wineId, wine_name, year, rating, grape, region, location, price\

wines = pd.read_json('./data/clean_wines.json')
#wines = pd.read_json('./data/wine_feat_matrix.json')
wines.drop('CurrentReviews', axis=1, inplace=True)
wines.drop('PriceMax', axis=1, inplace=True)
wines.drop('PriceRetail', axis=1, inplace=True)
wines.drop('Reviews', axis=1, inplace=True)
#wines.drop('Type', axis=1, inplace=True)
wines['Id'] = wines['Id'].astype('str')
wines.rename(columns={'Id': 'wine_id'}, inplace=True)
wines.rename(columns={'Name': 'wine_name'}, inplace=True)
wines['wine_name'] = wines['wine_name'].str.encode('utf-8')
wines['wine_name'] = wines['wine_name'].astype('str')
for i in xrange(len(wines)):
    extract = wines.wine_name[i]
    vintage = extract[-4:]
    name = extract[:-5]
    wine = vintage +' '+ name
    wines.set_value(i, 'wine_name', wine)
wines['Year'] = wines['Year'].astype('str')
wines['PriorReviews'] = wines['PriorReviews'].convert_objects(convert_numeric=True)
wines['PriceMin'] = wines['PriceMin'].convert_objects(convert_numeric=True)
wines = wines.reset_index(drop=True)

items = gl.SFrame(wines)
items = items.dropna()

# Prepare the data by removing items that are rare

rare_items = actions.groupby('wine_name', gl.aggregate.COUNT).sort('Count')
rare_items = rare_items[rare_items['Count'] <= 3]
items = items.filter_by(rare_items['wine_name'], 'wine_name', exclude=True)

rare_users = actions.groupby('user_id', gl.aggregate.COUNT).sort('Count')
rare_users = rare_users[rare_users['Count'] <= 5]
actions = actions.filter_by(rare_users['user_id'], 'user_id', exclude=True)

actions = actions[(actions['score'] >= 85.0) ] #& (actions['score'] <= 85.0) ]
actions = actions.filter_by(rare_items['wine_name'], 'wine_name', exclude=True)


high_rated_reviews = actions[(actions['score'] >= 93.0)]
low_rated_reviews = actions[(actions['score'] < 93.0)]
train_data_1, test_data = gl.recommender.util.random_split_by_user(high_rated_reviews, user_id='user_id', item_id='wine_name')

training_data = train_data_1.append(low_rated_reviews)

#training_data, validation_data = gl.recommender.util.random_split_by_user(actions, 'user_id', 'wine_name')

#sim_model = gl.item_similarity_recommender.create(training_data, user_id='user_id', item_id='wine_name',  similarity_type='pearson')

#ranking_factorization_model
model = gl.recommender.ranking_factorization_recommender.create(training_data, user_id= 'user_id', item_id = 'wine_name', target='score', num_factors = 48, regularization = .0001, max_iterations = 50, ranking_regularization=0)

#model = gl.recommender.create(training_data, user_id= 'user_id', item_id = 'wine_name', target='score')

# m1 = gl.item_similarity_recommender.create(training_data, user_id='user_id', item_id='wine_name', target='score')
# m2 = gl.item_similarity_recommender.create(training_data, user_id='user_id', item_id='wine_name', target='score',only_top_k=1)

#Load and compare multiple models:

# high_filter = gl.load_model('./models/high_filter')
# onezero = gl.load_model('./models/onezero')
# baseline = gl.load_model('./models/baseline')
# gridsearch = gl.load_model('./models/gridsearch')

# gl.recommender.util.compare_models(test_data, [m1, m2, baseline, gridsearch, high_filter, onezero], model_names=["m1", "m2", "baseline", "gridsearch", "high_filter", "onezero"], metric='rmse')
#
#model_comp = gl.recommender.util.compare_models(test_data, [baseline, gridsearch, high_filter, onezero] )
#
#gl.show_comparison(model_comp, [m1, m2, baseline, gridsearch, high_filter, onezero])

# Show an interactive view
#view = model.views.evaluate(test_data)
#view.show()

# Explore predictions
#view = model.views.explore(item_data=items,item_name_column='wine_name')

# Explore evals
#view = model.views.overview(validation_set=test_data,item_data=items,item_name_column='wine_name')
#view.show()



'''

Grid Search:

params = dict([('target', 'score'),
                   ('num_factors', [32, 48, 64]),
                   ('regularization', [.001, 0.0001, 0.00001, 0.0000001]),
                   ('max_iterations', [25, 50, 100]),
                   ('ranking_regularization',[ 0, 0.1, 0.5, 1.]),
                   ('user_id', 'user_id'),
                   ('item_id', 'wine_name') ])


job = gl.grid_search.create((training_data, validation_data),gl.recommender.factorization_recommender.create,params)
job.get_results()

job.get_best_params()

'''
