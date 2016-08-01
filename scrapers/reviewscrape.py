import urllib
import bs4
import re
import json
import pandas as pd
import numpy as np
import os


def clean_data(df_name):

    """Cleans the master dataset by extracting needed features and removing unneeded data.
    Args:
        str:  name of DataFrame
    Returns:
        cleaned DataFrame
    """

    wines = df_name
    wines = wines.rename(columns={'Vintage': 'Year'})
    wines['Location'] = wines['Appellation'].apply(lambda x: x['Region']['Name'])
    wines['Region'] = wines['Appellation'].apply(lambda x: x['Name'])
    wines['Type'] = wines['Varietal'].apply(lambda x: x['WineType']['Name'])
    wines['Grape'] = wines['Varietal'].apply(lambda x: x['Name'])
    wines['Reviews'] = wines['Community'].apply(lambda x: x['Reviews']['Url'])
    drop_columns = ['Appellation', 'Community', 'Description', 'GeoLocation', 'Labels', 'ProductAttributes','Ratings','Retail', 'Url', 'Varietal', 'Vineyard', 'Vintages']
    wines.drop(drop_columns, axis=1, inplace=True)
    wines = wines[['Id', 'Name', 'Year', 'Type', 'Grape', 'Location', 'Region', 'PriceRetail', 'PriceMin', 'PriceMax', 'Reviews']]
    wines['CurrentReviews'] = '' #wines['CurrentReviews'].apply(lambda x: [""])
    wines['PriorReviews'] = ''  #wines['PriorReviews'].apply(lambda x: [''])

    return wines


def get_reviews(review_url):

    """Scrapes data from the wine.com website for each wine in the file and finds the wine critic scores.
    Args:
        str:  the url where the reviews can be found
    Returns:
        tuple:  current reviews of the wine, consisting of initials of reviewer and score that was given
        float:  average score from reviews of all past vintages
    """
    print review_url
    html = urllib.urlopen(review_url).read()
    soup = bs4.BeautifulSoup(html, 'html.parser')

    rating_scores = soup.findAll("span", "ratingScore")
    num_ratings = len(rating_scores) - 1

    current_reviews = soup.findAll("div", "currentVintageProfessinalReviews")
    num_cur_reviews = str(current_reviews).count('ratingProvider')
    past_reviews = soup.findAll("ul", "pastVintagesProfessionalReviews")
    num_past_reviews = str(past_reviews).count('ratingProvider')

    print  'There are {0} reviews for prior vintages of this wine.'.format(num_past_reviews)
    print 'There are {0} current reviews for this vintage.\n'.format(num_cur_reviews)

    rating_provider = soup.findAll("span", "ratingProvider")
    rating_score = soup.findAll("span", "ratingScore")
    reviewers = re.findall('(?<![A-Z])[>]([A-Z]+(?![A-Z]))', str(rating_provider))
    ratings = re.findall('(?<![A-Z])[0-9]{2}(?![A-Z])', str(rating_score))

    print "Ratings List:", ratings
    print "Current Reviews: ", num_cur_reviews

    currentreviews = []
    for j in range(num_cur_reviews):
        print "Current Review #"+str(j+1)+":", reviewers[j], ratings[j]
        currentreviews.append((reviewers[j], ratings[j]))
    print currentreviews

    print "\nPast Reviews: ", num_past_reviews
    past_review_ratings = []
    for k in range(num_cur_reviews, num_past_reviews+num_cur_reviews):
        #print "Past Review #"+str(k-num_cur_reviews+1)+":", reviewers[k], int(ratings[k])
        past_review_ratings.append(float(ratings[k]))
        if k > 30:
            break
    if num_past_reviews != 0:
        avg_past_reviews = sum(past_review_ratings)/len(past_review_ratings)
        round(avg_past_reviews, 2)
    else:
        avg_past_reviews = 0

    print "Average of Past Reviews: ", avg_past_reviews

    return currentreviews, avg_past_reviews

if __name__ == "__main__":
    #path where data files are stored
    path = './data/white_wines/'
    paths = [path + f_name for f_name in os.listdir(path) if f_name != '.DS_Store']
    #read all data files into one Pandas DataFrame
    df = pd.read_json(paths[0])
    for f_name in paths[1:]:
        df = df.append(pd.read_json(f_name), ignore_index=True)

    wines = clean_data(df)

    #scrape wines.com web-site to obtain wine critic reviews
    for wine_num in xrange(wines.shape[0]):
        print "WINE NUMBER: ---------  {}".format(wine_num+1)
        review_url = wines.loc[wine_num, 'Reviews']
        currentreviews, avg_past_reviews = get_reviews(review_url)
        wines.set_value(wine_num, 'CurrentReviews', currentreviews)
        wines.set_value(wine_num, 'PriorReviews', avg_past_reviews)
