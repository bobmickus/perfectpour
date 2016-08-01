
from os import path
import graphlab as gl
from datetime import datetime
import pandas as pd



#Table of wines to recommend: wineId, wine_name, year, rating, grape, region, location, price


wines = pd.read_json('./data/wine_master.json')
#wines = pd.read_json('./data/wine_feat_matrix.json')
wines.drop('CurrentReviews', axis=1, inplace=True)
wines.drop('PriceMax', axis=1, inplace=True)
wines.drop('PriceRetail', axis=1, inplace=True)
wines.drop('Reviews', axis=1, inplace=True)
wines.drop('Type', axis=1, inplace=True)
wines['Id'] = wines['Id'].astype('str')
wines['Name'] = wines['Name'].str.encode('utf-8')
wines['Name'] = wines['Name'].astype('str')
wines.rename(columns={'Name': 'wine_name'}, inplace=True)
wines['Year'] = wines['Year'].astype('str')
wines['PriorReviews'] = wines['PriorReviews'].convert_objects(convert_numeric=True)
wines['PriceMin'] = wines['PriceMin'].convert_objects(convert_numeric=True)
wines = wines.reset_index(drop=True)

items = gl.SFrame(wines)
items = items.dropna()



sim_model = gl.recommender.item_content_recommender.create(item_data=items, item_id='Id', max_item_neighborhood_size=64)

# Prepare the data by removing items that are rare


# Show an interactive view
view = model.views.evaluate(validation_data)
view.show()

# Explore predictions
view = model.views.explore(item_data=items,item_name_column='wine_name')

# Explore evals
view = model.views.overview(validation_set=validation_data,item_data=items,item_name_column='wine_name')
view.show()

'''
Parameter Search:

params = dict([('target', 'score'),
                   ('num_factors', [8, 16, 32, 64]),
                   ('regularization', [1e-09, 1e-06]),
                   ('max_iterations', [15, 25, 50]),
                   ('user_id', 'user_id'),
                   ('item_id', 'wine_name') ])


job = gl.grid_search.create((training_data, validation_data),
                                gl.recommender.factorization_recommender.create,
                                params)
job.get_results()

job.get_best_params()

# Show an interactive view
view = model.views.evaluate(validation_data)
view.show()

# Explore predictions
view = model.views.explore(item_data=items,item_name_column='wine_name')

# Explore evals
view = model.views.overview(validation_set=validation_data,item_data=items,item_name_column='wine_name')
view.show()




# Interactively evaluate and explore recommendations
view = model.views.overview(observation_data=training_data,
                            validation_set=validation_data,
                            user_data=actions,
                            user_name_column='user_id',
                            item_data=items,
                            item_name_column='wine_name')
view.show()
'''
