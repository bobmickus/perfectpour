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


def get_reviews(review_url):

    """Scrapes wine review data from specified user on cellartracker.com
    Args:
        url (str):  the url for the target page
    Returns:
        response:   html file of the page
    """
    response = requests.get(review_url)
    print(response.url)

    if response.status_code != 200:
        print 'WARNING', response.status_code
    else:
        return response.text

def load_data(html):

    """Extracts needed data from html file and inserts into Pandas DataFrame
    Args:
        html (str):  name of the html file that will be loaded into the DataFrame
    Returns:
        df:   the dataframe containg the needed columns
    """

    soup = bs4.BeautifulSoup(html, 'html.parser')
    table = soup.findAll("table", "tasting_notes")

    cols = ['user_id', 'review_date','wine_id', 'wine_name', 'score', 'notes']
    df = pd.DataFrame(columns = cols)
    pd.to_datetime('review_date', format='%m%d%Y', errors='coerce')

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

    for row in xrange(1,len(rows)):
        reviews.append(rows[row])

    for i in xrange(1, len(reviews)):

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


    return df


if __name__ == "__main__":
    base_url = 'https://www.cellartracker.com/list.asp?Table=Notes'
    user = 2
    pagenum = 3

    for index in xrange(1, pagenum):
        url = base_url+'&iUserOverride='+str(user)+'&Page='+str(pagenum)
        print "Scraping------User No.: ", user, url
        print '======================================================================'
        html = get_reviews(url)

        df_master = pd.DataFrame()
        df = load_data(html)

        df_master = df_master.append(df, ignore_index=True)
        pagenum += 1
        time.sleep(15)
