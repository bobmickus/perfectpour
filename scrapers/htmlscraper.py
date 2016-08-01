import urllib
import bs4
import re
import json
import pandas as pd
import numpy as np
import os
from collections import defaultdict
import itertools
import requests
import time



if __name__ == "__main__":
    #path where data files are stored
    path = './data/html_reviews/'
    paths = [path + f_name for f_name in os.listdir(path) if f_name != '.DS_Store']

    reviews  = []
    print "number of files: ", len(paths)

    for f_name in paths:
        rows = []
        url = f_name
        if url.startswith('./'):
            url = url[2:]
            html = urllib.urlopen(url)

        soup = bs4.BeautifulSoup(html, 'html.parser')
        table = soup.findAll("table", "tasting_notes")

        try:
            rows = table[1].findAll('tr')
        except:
            pass

        if len(rows) == 0:
            try:
                rows = table[0].findAll('tr')
            except:
                pass

        print f_name, len(rows)

        for index in xrange(1,len(rows)):
            reviews.append(rows[index])


    cols = ['user_id', 'review_date','wine_id', 'wine_name', 'score', 'notes']
    df = pd.DataFrame(columns = cols)
    pd.to_datetime('review_date', format='%m%d%Y', errors='coerce')


    for i in xrange(len(reviews)):

        print "Review Number", i

        search_result =  re.findall('.*>(.*)\swrote+', str(reviews[i]))
        if len(search_result) == 0:
            search_result.append('')
        if len(search_result) > 15:
            search_result[0] = ''
        df.set_value(i, 'user_id', search_result[0])

        search_result = re.findall('.*<h3>([0-9]{1,2}.*[0-9][0-9][0-9][0-9])\s', str(reviews[i]))
        if len(search_result) == 0:
            search_result[0] = ''
        df.set_value(i, 'review_date', search_result[0])

        search_result = re.findall('.*[h][3][>]([0-9][0-9][0-9][0-9].*)</h', str(reviews[i]))
        if len(search_result) == 0:
            search_result.append('')
        df.set_value(i, 'wine_name', search_result[0])

        score1 = re.findall('.*([0-9][0-9])\spoints+', str(reviews[i]))
        score2 = re.findall('.*([N][R])+', str(reviews[i]))
        if len(score1) > 0:
            df.set_value(i, 'score', score1[0])
        if len(score2) > 0:
            df.set_value(i, 'score', score2[0])
        if len(score1) == 0 and len(score2) == 0:
            df.set_value(i, 'score', "NR")

        search_result = re.findall('.*>.*\swrote.*[\n]<p>(.*)</p', str(reviews[i]))
        if len(search_result) == 0:
            search_result = re.findall('.*[s,R]</h3>\n<p>(.*)</p', str(reviews[i]))
        if len(search_result) == 0:
            search_result.append('')
        df.set_value(i, 'notes', search_result[0])

        wine_numbers = re.findall('.*>.*Wine=([0-9]{1,8})', str(reviews[i]))
        if len(wine_numbers) == 0:
            wine_numbers[0] = ""
        df.set_value(i, 'wine_id', wine_numbers[0])


    '''
    review_data['user_id'] = list(itertools.chain.from_iterable(review_data['user_id']))
    review_data['wine_name'] = list(itertools.chain.from_iterable(review_data['wine_name']))
    review_data['score'] = list(itertools.chain.from_iterable(review_data['score']))
    review_data['comments'] = list(itertools.chain.from_iterable(review_data['comments']))
    #review_data['wine_id'] = list(itertools.chain.from_iterable(review_data['wine_id']))


    df = pd.DataFrame(data=review_data)


    for key, value in review_data.iteritems():
        print key, len(value)
    '''
