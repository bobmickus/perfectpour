
import pandas as pd
import numpy as np
import requests
import os
import re
import api_keys as key



def query(url, payload):

    response = requests.get(url, params=payload)
    if response.status_code != 200:
        print 'WARNING', response.status_code
    else:
        return response.text

if __name__ == "__main__":

    url = 'http://api.wine-searcher.com/wine-select-api.lml?'
    payload = {}
    new_wines = pd.DataFrame()


    wines = pd.read_json('../data/master_wines.json')
    reviews = pd.read_json('../data/clean_reviews.json')
    wine_set = set()
    no_price = []
    reviews = reviews.reset_index(drop=True)
    wines = wines.reset_index(drop=True)
    reviews['wine_id'] = reviews['wine_id'].astype('str')
    reviews.set_value(0, 'found', "")
    wines['Id'] = wines['Id'].astype('str')

    for i in xrange(len(wines)):
        extract = wines.Name[i]
        vintage = extract[-4:]
        name = extract[:-5]
        wine = vintage +' '+ name
        wine_set.add(wine)

    winenum = 1
    i = 0
    j = 1

    for review_num in xrange(reviews.shape[0]):
        print "Processing review number", review_num, "============================="
        result = []
        #new_id = "CT" + str(winenum)
        #winenum += 1
        #reviews.set_value(review_num, 'wine_id', new_id)
        # if reviews.loc[review_num, 'score']  >= 89:
        #     reviews.set_value(review_num, 'thumbs_up', 1)
        # else:
        #     reviews.set_value(review_num, 'thumbs_up', 0)
        # #if reviews.loc[review_num, 'found']  != "Y":
        # if reviews.loc[review_num, "wine_name"] in wine_set:
        #     print "This review is in the wine database: ", reviews.loc[review_num, "wine_name"]
        #     name = reviews.loc[review_num, "wine_name"]
        #     year = name[:4]
        #     wine_name = name[5:]
        #     check_name = wine_name + ' ' + year
        #     try:
        #         result = wines[wines['Name'].str.contains(check_name)]
        #         print "Found this wine in wine database: ", result
        #         print "Number of wines found: ", j, '========================================'
        #         j += 1
        #     except:
        #         pass
        #     if len(result) > 0:
        #         result_index = result.index.values
        #         check_wine = wines.iloc[result_index[0]]
        #         check_id = check_wine.Id
        #         '''
        #         if "CT" in check_id:
        #             continue
        #         else:
        #         '''
        #         if review_num > 0:
        #             print "Updating review number: ", review_num
        #
        #             try:
        #                 reviews.set_value(review_num, 'found', "Y")
        #                 price_list = result['PriceMin'].values
        #                 reviews.set_value(review_num, 'price', price_list[0])
        #                 print "Price update to: ", price_list[0]
        #                 if len(price_list) == 0:
        #                     print "PRICE NOT UPDATED FOR NUM: ", review_num
        #                     no_price.append(review_num)
        #                 #wines.set_value(result_index[0], 'Id', new_id)
        #                 #print "Id update to: ", new_id
        #             except:
        #                 pass

        if reviews.loc[review_num, 'found']  != "Y":
            name = reviews.loc[review_num, "wine_name"]
            year = name[:4]
            wine_name = name[5:]
            check_name = wine_name + ' ' + year

            payload['Xkey'] = 'bbmickus'
            payload['Xkeyword_mode'] = 'X'
            payload['Xformat'] = 'J'
            payload['Xscore'] = 'Y'
            payload['Xwinename'] = wine_name
            payload['Xvintage'] = year
            print "Trying wine-searcher site...call number: ", i+1
            if i > 1400:
                break
            content = query(url, payload)
            content = str(content)
            i += 1

            search_result = re.findall('.*return-code":\s"(.*)"', content)
            return_code = int(search_result[0])
            if return_code == 1:
                print "Wine not found in Wine-Searcher........."
                continue
            else:
                #print "Here is the content: ", content
                new_wines.set_value(i, 'Year', year)
                #extract wine name
                search_result = re.findall('.*wine-name":\s"(.*)"', content)
                if len(search_result) == 0:
                    search_result.append('')
                print "Found this wine: ", search_result[0]
                print "Was searching for this wine: ", name
                reviews.set_value(review_num, 'found', "Y")
                new_name = wine_name + ' ' + year
                try:
                    new_wines.set_value(i, 'Name', new_name)
                except:
                    pass
                #extract grape varietal
                search_result = re.findall('.*grape":\s"(.*)"', content)
                if len(search_result) == 0:
                    search_result.append('')
                try:
                    new_wines.set_value(i, 'Grape', search_result[0])
                except:
                    pass
                #extract location
                search_result = re.findall('.*region":\s"(.*)"', content)
                if len(search_result) == 0:
                    search_result.append('')
                try:
                    new_wines.set_value(i, 'Location', search_result[0])
                except:
                    pass
                #extract region
                search_result = re.findall('.*location":\s"(.*)"', content)
                if len(search_result) == 0:
                    search_result.append('')
                try:
                    new_wines.set_value(i, 'Region', search_result[0])
                except:
                    pass
                #extract price
                search_result = re.findall('.*average":\s"(.*)"', content)
                if len(search_result) == 0:
                    search_result.append('')
                try:
                    new_wines.set_value(i, 'PriceMin', search_result[0])
                except:
                    pass
                #extract wine score
                search_result = re.findall('.*score":\s"(.*)"', content)
                if len(search_result) == 0:
                    search_result.append('')
                try:
                    new_wines.set_value(i, 'PriorReviews', search_result[0])
                except:
                    pass
                try:
                    new_wines.set_value(i, 'Id', new_id)
                except:
                    pass



                #wines = wines.append(new_wines, ignore_index=True)

            # wines.to_json('./data/wine_master.json')
            # new_wines.to_json('./data/new_wines/' + fname)
            # wine_feat_matrix.to_json('./data/wine_feat_matrix.json')
            # reviews.to_json('./data/master_reviews.json')


        #new_wines = new_wines.drop_duplicates()
        #reviews = reviews.drop_duplicates()


'''

Review Columns = 'notes', u'review_date', u'score', u'user_id', u'wine_id',
       u'wine_name']
Wines Columns = [u'CurrentReviews', u'Grape', u'Id', u'Location', u'Name', u'PriceMax',
       u'PriceMin', u'PriceRetail', u'PriorReviews', u'Region', u'Reviews',
       u'Type', u'Year']

new_wines=new_wines.rename(columns = {'year':'Year', 'wine_name': 'Name', 'grape': 'Grape', 'location':'Region', 'region': 'Location', 'price':'PriceMin', 'prior_avg':'PriorReviews'})

for review_num in xrange(reviews.shape[0]):
        id = reviews.loc[review_num, 'wine_id']
        id = str(id)
        id = id.split(' ', 1)[0]
        reviews.loc[review_num, 'wine_id'] = id
count = 1
for wine in xrange(wines.shape[0]):
    x = wines.loc[wine, 'Id']
    y = str(x)
    if 'CT' in y:
        print y


        .str.contains('CT'):
        print "Found number: ", count
        count += 1


'''
