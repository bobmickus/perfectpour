import json
from os.path import join, dirname
from watson_developer_cloud import AlchemyLanguageV1
import requests
import urllib
import pandas as pd
import numpy as np


def query(url, payload):
    #payload  = dict(apikey.items() + params['params'].items())
    response = requests.get(url, params=payload)
    if response.status_code != 200:
        print 'WARNING', response.status_code
    else:
        return response.json()   #  ['Products']['List']


if __name__ == "__main__":
    url = "https://gateway-a.watsonplatform.net/calls/text/TextGetTargetedSentiment"

    reviews = pd.read_json('../data/clean_reviews.json')
    reviews = reviews.reset_index(drop=True)
    reviews = reviews.loc[reviews['review_date'].notnull(), :]
    reviews = reviews.loc[reviews['score'].notnull(), :]
    reviews = reviews.loc[reviews['price'].notnull(), :]
    reviews = reviews.drop(['found'], 1)
    reviews['user_id'] = reviews['user_id'].str.encode('utf-8')
    reviews['user_id'] = reviews['user_id'].astype('str')
    reviews['wine_id'] = reviews['wine_id'].astype('str')
    reviews['wine_name'] = reviews['wine_name'].str.encode('utf-8')
    reviews['wine_name'] = reviews['wine_name'].astype('str')

    rows = np.random.choice(reviews.index.values, 10000)
    review_sample = reviews.ix[rows]
    review_sample = review_sample.reset_index(drop=True)
    #review_sample = pd.read_json('../data/review_sample.json')

    i = 0
    for review_num in xrange(review_sample.shape[0]):
        #if i > 10:
        #    break
        #if review_sample.loc[review_num, 'sentiment_reviewed']  != "Y":
            print "Processing review number", review_num, "============================"

            tasting_note = ''
            try:
                tasting_note = review_sample.loc[review_num, 'notes'].encode('utf-8')
            except:
                pass
            if len(tasting_note) > 0:
                print tasting_note
                print "Score given: ", review_sample.loc[review_num, 'score']

                urlencode = urllib.quote_plus(tasting_note)

                payload = { 'apikey': 'eaa3248c223ed4d72cb73daddd6945f7c9197523'}
                payload['outputMode'] = 'json'
                payload['html'] =  urlencode
                payload['text'] = tasting_note
                payload['targets'] = "wine|taste|flavor|aroma|aromas|nose|palate|bouquet|mouth|color|finish|notes|fruit|bottle|structure|spice"

                #payload['sentiment'] = 1
                #payload['extract'] = 'keywords'

                content = query(url, payload)
                print content
                try:
                    sent_polarity = content['results'][0]['sentiment']['type']
                    print "Sentiment Polarity: ", sent_polarity
                except:
                    pass
                try:
                    sent_scores = []
                    count = 0
                    total = 0
                    for score in xrange(len(content['results'])):
                        try:
                            sent_score = content['results'][score]['sentiment']['score']
                            sent_scores.append(sent_score)
                            count += 1
                        except:
                            pass
                    for score in sent_scores:
                        total = total + float(score)
                    sent_score = total / count
                    print "Sentiment Score: \n", sent_score
                except:
                    pass
                try:
                    review_sample.set_value(review_num, 'sentiment_reviewed', 'Y')
                except:
                    pass
                try:
                    review_sample.set_value(review_num, 'sentiment_polarity', sent_polarity)
                except:
                    pass
                try:
                    review_sample.set_value(review_num, 'sentiment_score', sent_score)
                except:
                    pass

                i += 1
