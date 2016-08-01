import time
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import math
import pandas as pd
import numpy as np
from collections import defaultdict
import itertools
import re
import os


def browser_connect():
    # service_args = ['--proxy=localhost:9150', '--proxy-type=socks5',]
    # driver = webdriver.PhantomJS(service_args=service_args)

    profile=webdriver.FirefoxProfile()

    profile.set_preference("network.proxy.type", 1);
    profile.set_preference("network.proxy.socks", "127.0.0.1");
    profile.set_preference("network.proxy.socks_port", 9150);
    profile.set_preference("network.proxy.socks_version", 5);
    profile.set_preference("places.history.enabled", False);
    profile.set_preference("privacy.clearOnShutdown.offlineApps", True);
    profile.set_preference("privacy.clearOnShutdown.passwords", True);
    profile.set_preference("privacy.clearOnShutdown.siteSettings", True);
    profile.set_preference("privacy.sanitize.sanitizeOnShutdown", True);
    profile.set_preference("signon.rememberSignons", False);
    profile.set_preference("network.cookie.lifetimePolicy", 2);
    profile.set_preference("network.dns.disablePrefetch", True);
    profile.set_preference("network.http.sendRefererHeader", 0);
    profile.set_preference("network.proxy.socks_remote_dns", True);

    driver=webdriver.Firefox(profile)
    return driver


if __name__ == "__main__":

    display = Display(visible=0, size=(1920, 1080))
    display.start()
    driver = browser_connect()
    driver.get("http://yahoo.com")
    driver.close()

    base_url = 'https://www.cellartracker.com/list.asp?Table=Notes'
    df2 = pd.DataFrame()
    manual_list = []

    for user in xrange(25000, 30000):
        print user
        driver = browser_connect()
        url = base_url+'&iUserOverride='+str(user)+'&top_paging=1000'
        driver.get(url)
        TimeoutException = False
        time.sleep(15)
        driver.set_page_load_timeout(30)
        if TimeoutException == True:
            driver.close()
            driver = browser_connect()
            user += 1
            url = base_url+'&iUserOverride='+str(user)+'&top_paging=1000'
            driver.get(url)
        page = driver.page_source
        num_reviews = re.findall('.*span>(.*[0-9]{1,3})\sN', page)
        if num_reviews > 100:
            manual_list.append(user)
        num_pages = 1
        try:
            num_reviews = int(num_reviews[0].replace(',', ''))
        except:
            num_reviews = 0
        if num_reviews == 0:
            driver.close()
            pass
        if num_reviews != 0:
            num_pages = math.ceil(num_reviews / 25.0)

        if num_reviews < 101:

            for index in xrange(1, int(num_pages+1)):
                url = base_url+'&iUserOverride='+str(user)+'&Page='+str(index)+'&top_paging=1000'
                print "Scraping: ", url,  "User No.: ", user, 'No. Reviews: ', num_reviews, 'Page No: ', index, 'of ', num_pages
                print '========================================================================'
                driver = browser_connect()
                driver.get(url)
                TimeoutException = False
                time.sleep(10)
                driver.set_page_load_timeout(30)
                if TimeoutException == True:
                    driver.close()
                    driver = browser_connect()
                    pass
                try:
                    all_rows = driver.find_elements_by_tag_name("tr")
                    time.sleep(8)
                except:
                    pass

                cols = ['user_id', 'review_date','wine_id', 'wine_name', 'score', 'notes']
                df = pd.DataFrame(columns = cols)
                pd.to_datetime('review_date', format='%m%d%Y', errors='coerce')
                reviews = []
                for x in xrange(2, len(all_rows)):
                    reviews.append(all_rows[x].text)

                page = driver.page_source
                driver.close()

                wine_numbers = re.findall('.*([W][0-9]{2,8})', page)
                wine_ids = []
                for wine in wine_numbers:
                    if wine not in wine_ids:
                        wine_ids.append(wine)

                for i in xrange(len(reviews)):

                    print "Review Number", i

                    search_result = re.findall('.*iUserOverride.*class="action_wide">(.*)</a><a', page)
                    if len(search_result) == 0:
                        search_result.append('')
                    if len(search_result) > 15:
                        search_result[0] = ''
                    try:
                        df.set_value(i, 'user_id', search_result[0])
                    except:
                        pass

                    search_result = re.findall('.*[\n].*[\n].*[\n](.*)\s[-]', reviews[i])
                    if len(search_result) == 0:
                        search_result[0] = ''
                    try:
                        df.set_value(i, 'review_date', search_result[0])
                    except:
                        pass

                    search_result = re.findall('.*[\n]([0-9][0-9][0-9][0-9].*)[\n]', reviews[i])
                    if len(search_result) == 0:
                        search_result.append('')
                    if search_result[0][:-5:-1] == 'erom':
                        search_result[0] = search_result[0][:-5]
                    try:
                        df.set_value(i, 'wine_name', search_result[0])
                    except:
                        pass

                    score1 = re.findall('.*([0-9][0-9])\spoints+', reviews[i])
                    score2 = re.findall('.*([N][R])+', reviews[i])
                    if len(score1) > 0:
                        df.set_value(i, 'score', score1[0])
                    if len(score2) > 0:
                        df.set_value(i, 'score', score2[0])
                    if len(score1) == 0 and len(score2) == 0:
                        df.set_value(i, 'score', "NR")
                    if len(score1) > 0 and score1[0] == '100':
                        df.set_value(i, 'score', 100)

                    search_result = re.findall('.*[\n][0-9][0-9][0-9][0-9].*[\n].*[\n].*[\n](.*)[\n]', reviews[i])
                    if len(search_result) == 0:
                        search_result.append('')
                    try:
                        df.set_value(i, 'notes', search_result[0])
                    except:
                        pass

                    try:
                        df.set_value(i, 'wine_id', wine_ids[i])
                    except:
                        pass

                    print df2.tail()
            #index += 1
            df2 = df2.append(df, ignore_index=True)
            #driver.close()


        user += 1
        driver.close()
        #display.stop()
