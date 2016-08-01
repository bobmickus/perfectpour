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

def query(url, payload):

    response = requests.get(url, params=payload)
    if response.status_code != 200:
        print 'WARNING', response.status_code
    else:
        return response.text

if __name__ == "__main__":

    driver = browser_connect()


    wines = pd.read_csv('./data/redwines.csv')
    reviews = pd.read_json('./data/userreviews_0717.json')


    count = 0
    match = 0

    wines = pd.read_csv('./data/redwines.csv')
    reviews = pd.read_json('./data/userreviews_0717.json')
    names = set(reviews.wine_name.values)

    for i in xrange(10):  #len(wines)):

        extract = wines.Name[i]
        vintage = extract[-4:]
        name = extract[:-5]
        wine = vintage +' '+ name
        #print wine
        if wine in names:
            match += 1
            print "Match Number: ", match, wine

        if wine not in names:

            url = 'https://www.vivino.com/search'

            driver = browser_connect()
            driver.get(url)

            #page = driver.page_source
            element = driver.find_element_by_xpath('//*[@id="wine-search-form"]/div/div[1]/div/input')

            element.send_keys(wine)
            element.submit()

            break
            try:
                result = driver.find_element_by_xpath('//*[@id="content"]/div/div/div[2]/div[1]/h2')
            except:
                result = driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[2]/div[3]/h2')
            text = str(result.text)

            try:
                empty = "couldn't find a match"
                if empty in text:
                    driver.close()
                    pass
            except:
                try:
                    element = driver.find_element_by_xpath(' //*[@id="content"]/div[2]/div[2]/div[4]/div/p/a')
                except:
                    element = driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[2]/div[5]/div/div[2]/a')
                element.click()
                element = driver.find_element_by_xpath('//*[@id="detailFrm"]/div[1]/div[2]/div[1]/div[3]/span/span/strong')
                print wine, "found at lwines site!"
                price = element.text
                print "Price is:", price
                wines.set_value(i, 'PriceMin', price)
                element = driver.find_element_by_class_name("H3ProductDetail_detail")
                varietal = element.text
                print "Grape is:", varietal
                wines.set_value(i, 'Grape', varietal)
                info_rows = driver.find_elements_by_class_name("detail_td")
                sub_region = info_rows[2].text
                search_result = re.findall('(.*)\s-', sub_region)
                sub_region = search_result[0]
                wines.set_value(i, 'Location', sub_region)
                appellation = info_rows[3].text
                search_result = re.findall('(.*)\s-', appellation)
                appellation = search_result[0]
                wines.set_value(i, 'Region', appellation)

            driver.close()



            '''
            url = 'http://www.wine-searcher.com/find/-'

            driver = browser_connect()
            driver.get(url)
            wine = 'Clos du Val Cabernet Sauvignon 2013'

            page = driver.page_source
            element = driver.find_element_by_xpath('//*[@id="Xwinename"]')
            element.send_keys(wine)
            element.submit()

            result = driver.find_element_by_xpath('          //*[@id="wine_list"]/tbody/tr/td[2]/p[2]')
            text = str(result.text)
            empty = 'That search came up empty'
            if empty in text:
                pass


            break


            payload = {}
            payload['Xwinename'] = wine

            # payload['type'] = 'TEXT'
            # payload['name'] = 'Xwinename'
            # payload['value'] = ''
            # payload['title'] = wine


            #content = query(url, payload)
            '''
