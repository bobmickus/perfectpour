
import pandas as pd
import numpy as np
import requests
import os
import re



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


    wines = pd.read_json('./data/wine_master.json')
    reviews = pd.read_json('./data/master_reviews.json')
    wine_set = set()
    reviews = reviews.reset_index(drop=True)
    wines = wines.reset_index(drop=True)

    for i in xrange(len(wines)):
        extract = wines.wine_name[i]
        vintage = extract[-4:]
        name = extract[:-5]
        wine = vintage +' '+ name
        wine_set.add(wine)

    #wines_reviewed = set(reviews.wine_name.values)

    i = 1
    j = 1

    cols = ['Id', 'Name', 'Year', 'Type', 'Grape', 'Region', 'Location', 'PriceMin', 'PriceRetail', 'PriceMax', 'CurrentReviews', 'PriorReviews', 'Reviews']
    wine_feat_matrix = pd.DataFrame(columns = cols)

    count = 1

    for review_num in xrange(reviews.shape[0]):
        wineid = "WS" + str(review_num)
        if reviews.loc[review_num, "wine_name"] in wine_set:
            #continue
            print "MATCH NO: ", count,  review_num
            name = reviews.loc[review_num, "wine_name"]
            year = name[:4]
            wine_name = name[5:]
            try:
                record = wines[wines['wine_name'].str.contains(wine_name)]
            except:
                pass
            if len(record) > 1:
                try:
                    record = record[record['Year'].str.contains(year)]
                except:
                    pass
            if len(record) > 1:
                record = record.iloc[0]
            id = record['Id']
            id = str(id)
            id = id.split(' ', 1)[0]

            # extract_rating = str(record.CurrentReviews)
            # ratings = re.findall('\d+', extract_rating)
            # sum = 0
            # avg = 0
            # for rating in ratings:
            #         sum += int(rating)
            # try:
            #     avg = sum/len(ratings)
            # except:
            #     pass
            # idx = record.index
            # record.loc['CurrentReviews'] = avg

            #print record
            wine_feat_matrix = wine_feat_matrix.append(record, ignore_index=True)

            if len(record) == 0:
                pass
            else:
                try:
                    reviews.set_value(review_num, 'wine_data', "Y")
                    reviews.set_value(review_num, 'price', record.PriceMin)
                    reviews.set_value(review_num, 'price', record.PriceMin)
                    reviews.set_value(review_num, 'wine_id', id)
                    reviews.set_value(review_num, 'critic_score', avg)
                except:
                    pass
                try:
                    if id == '':
                        record.Id = wineid
                        wines.set_value(record.index, 'Id', wineid)
                except:
                    pass
                #reviews.set_value(review_num, 'wine_id', record.Id)
                try:
                    if id.empty:
                        reviews.set_value(review_num, 'wine_id', wineid)
                        record['Id'] = wineid
                except:
                    pass

            count += 1


        else:

            name = reviews.loc[review_num, "wine_name"]
            year = name[:4]
            wine_name = name[5:]

            payload['Xkey'] = 'bbmickus'
            payload['Xkeyword_mode'] = 'X'
            payload['Xformat'] = 'J'
            payload['Xscore'] = 'Y'
            payload['Xwinename'] = wine_name
            payload['Xvintage'] = year
            print "Trying wine-searcher site...call number: ", i+1
            content = query(url, payload)
            content = str(content)

            search_result = re.findall('.*return-code":\s"(.*)"', content)
            return_code = int(search_result[0])
            if return_code == 1:
                print j, "number of wines not found in Wine-Searcher........."
                j += 1
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
                    new_wines.set_value(i, 'Id', wineid)
                except:
                    pass
                try:
                    reviews.set_value(review_num, 'wine_id', wineid)
                except:
                    pass
                try:
                    reviews.set_value(review_num, 'wine_data', "Y")
                except:
                    pass

                i += 1
                fname = "new_wines" + str(i) + '.json'

                if i >= 1200:  continue



                wines = wines.append(new_wines, ignore_index=True)


            wines.to_json('./data/wine_master.json')
            new_wines.to_json('./data/new_wines/' + fname)
            wine_feat_matrix.to_json('./data/wine_feat_matrix.json')
            reviews.to_json('./data/master_reviews.json')


        #new_wines = new_wines.drop_duplicates()
        #reviews = reviews.drop_duplicates()

    print "Number of total matches found in User Reviews: ", count



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


'''
