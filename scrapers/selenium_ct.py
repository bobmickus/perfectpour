from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from fake_useragent import UserAgent
from pyvirtualdisplay import Display
from TorCtl import TorCtl
import pandas as pd
import re
import time
import math
from stem import Signal
from stem.control import Controller
import stem.connection
import getpass
import sys

def low_bandwidth_chrome():
    """
    Initiates and returns a headless Chrome webdriver that doesn't load images, has a randomized useragent, and runs through privoxy/tor proxy
    See for headless setup:
    https://christopher.su/2015/selenium-chromedriver-ubuntu/
    """

    display = Display(visible=0, size=(1920, 1080))
    display.start()
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images":2}
    chrome_options.add_experimental_option("prefs",prefs)
    chrome_options.add_argument("user-agent={}".format(UserAgent().random))
    chrome_options.add_argument('--dns-prefetch-disable')
    chrome_options.add_argument('--proxy-server=http://127.0.0.1:8118')
    chromedriver = '/usr/local/bin/chromedriver'
    #chromedriver = "/home/ubuntu/bob/chromedriver.exe"

    for attempt in xrange(10):
        try:
            driver = webdriver.Chrome(chrome_options=chrome_options)
            attempt += 1
        except:
            renew_connection()
            attempt += 1

    driver.manage().timeouts().implicitlyWait(2000, TimeUnit.MILLISECONDS);
    driver.manage().timeouts().pageLoadTimeout(40, TimeUnit.SECONDS);
    driver.manage().timeouts().setScriptTimeout(60, TimeUnit.SECONDS);


    TimeoutException = False
    driver.set_page_load_timeout(15)
    if TimeoutException == True:
        renew_connection()
    return driver


def renew_connection():
    """
    Renews the connection to the Tor network, in order to get a new exit node with a different IP address
    See for setup details:
    http://lyle.smu.edu/~jwadleigh/seltest/
    http://sacharya.com/crawling-anonymously-with-tor-in-python/
    For setting up privoxy, need to add { -block } to /etc/privoxy/user.action to prevent filtering of urls
    For TorCTL setup in source 2, also need to change /etc/tor/torrc variable about cookies on line after HashedControlPassword to 0
    """
    conn = TorCtl.connect(controlAddr="127.0.0.1", controlPort=9051,passphrase="mypassword")
    time.sleep(3)
    conn = TorCtl.connect(controlAddr="127.0.0.1", controlPort=9051,passphrase="mypassword")
    time.sleep(3)
    conn = TorCtl.connect(controlAddr="127.0.0.1", controlPort=9051,passphrase="mypassword")
    conn.send_signal("NEWNYM")
    TimeoutException = False
    if TimeoutException == True:
        renew_connection()
    #conn.send_signal("RELOAD")
    #conn.close()

def browser_connect(driver, url):
    """
    Input: webdriver object, url to be visited
    10 second conditional delay to wait for full page load
    Returns: webdriver object after it has visited the page.
    Customized to looks for bncollege page footers
    """
    driver.get(url)
    TimeoutException = False
    driver.set_page_load_timeout(15)
    if TimeoutException == True:
        renew_connection()
    time.sleep(8)
    renew_connection()
    if not driver:
        browser_connect(driver, url)
    return driver

def check_captcha(element, driver):
    print "checking for captcha!"
    text = str(element.text)
    captcha = "Are you human"
    if captcha in text:
        status = True
        while status:
            renew_connection()
            time.sleep(4)
            renew_connection()
            TimeoutException = False
            driver.set_page_load_timeout(15)
            if TimeoutException == True:
                renew_connection()
            element = driver.find_element_by_xpath('/html/head/title')
            text = str(element.text)
            if captcha not in text:
                print "resolved captcha!"
                status = False

def process_rows(driver, all_rows):
    reviews = []
    df = pd.DataFrame()
    print "Made it to process rows!  Length of allrows is:", len(all_rows)
    for x in xrange(2, len(all_rows)):
        reviews.append(all_rows[x].text)
    print "Number of reviews found in all_rows: ", len(reviews)
    page = driver.page_source

    wine_numbers = re.findall('.*([W][0-9]{2,8})', page)
    wine_ids = []
    for wine in wine_numbers:
        if wine not in wine_ids:
            wine_ids.append(wine)

    for i in xrange(len(reviews)):
        print "Processing review number: ", i
        #extract user_id
        search_result = re.findall('.*EditField=iUserOverride">(.*)</a><a', page)
        if len(search_result) == 0:
            search_result.append('')
        if len(search_result) > 15:
            search_result[0] = ''
        try:
            df.set_value(i, 'user_id', search_result[0])
        except:
            pass
        #extract review date
        search_result = re.findall('.*[\n].*[\n].*[\n](.*)\s[-]', reviews[i])
        if len(search_result) == 0:
            search_result[0] = ''
        try:
            df.set_value(i, 'review_date', search_result[0])
        except:
            pass
        #extract wine name
        search_result = re.findall('.*[\n]([0-9][0-9][0-9][0-9].*)[\n]', reviews[i])
        if len(search_result) == 0:
            search_result.append('')
        if search_result[0][:-5:-1] == 'erom':
            search_result[0] = search_result[0][:-5]
        try:
            df.set_value(i, 'wine_name', search_result[0])
        except:
            pass
        #extract user score
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
        #extract user comments
        search_result = re.findall('.*[\n][0-9][0-9][0-9][0-9].*[\n].*[\n].*[\n](.*)[\n]', reviews[i])
        if len(search_result) == 0:
            search_result.append('')
        try:
            df.set_value(i, 'notes', search_result[0])
        except:
            pass
        #load wine id numbers
        try:
            df.set_value(i, 'wine_id', wine_ids[i])
        except:
            pass

    print df
    print 'Number of records in current dataframe: ', len(df)

    return df

def process_user(user, tracking_list):
    print "Made it to process user."
    base_url = 'https://www.cellartracker.com/list.asp?Table=Notes'
    all_rows = []
    #manual_list = list
    df2 = pd.DataFrame()
    manual_list = tracking_list

    print "Opening CellarTracker website, for user no: ", user
    url = base_url+'&iUserOverride='+str(user)

    driver = low_bandwidth_chrome()
    driver = browser_connect(driver,url)
    element = driver.find_element_by_xpath('/html/head/title')
    check_captcha(element, driver)
    TimeoutException = False
    driver.set_page_load_timeout(15)
    if TimeoutException == True:
        print "Time Out Exception Encountered!"
        renew_connection()

    page = driver.page_source
    time.sleep(4)

    search_result = re.findall('.*span>(.*[0-9]{1,4})\sN', page)
    #print "Number of Reviews = ", search_result[0]
    try:
        num_reviews = int(search_result[0].replace(',', ''))
    except:
        num_reviews = 0

    print "Number of reviews for this scrape: ", num_reviews

    if num_reviews > 100:
        manual_list.append(user)
        print "Too many reviews. Skipping user no: \n", user

    if num_reviews == 0:
        print "No reviews....moving to next user.\n"

    if num_reviews > 0 and num_reviews < 101:
        num_pages = math.ceil(num_reviews / 25.0)
        for index in xrange(1, int(num_pages+1)):
            url = base_url+'&iUserOverride='+str(user)+'&Page='+str(index)
            print "Scraping: ", url,  "User No.: ", user, 'No. Reviews: ', num_reviews, 'Page No: ', index, 'of ', num_pages
            print '====================================================================='
            driver = low_bandwidth_chrome()
            driver = browser_connect(driver, url)
            element = driver.find_element_by_xpath('/html/head/title')
            check_captcha(element, driver)
            TimeoutException = False
            driver.set_page_load_timeout(15)
            if TimeoutException == True:
                renew_connection()
            try:
                rows = driver.find_elements_by_tag_name("tr")
                time.sleep(5)
                print "Length of rows: ----------", len(rows)
                df = process_rows(driver, rows)
                df2 = df2.append(df, ignore_index=True)
            except:
                pass

    return df2, manual_list


if __name__ == "__main__":

    with Controller.from_port(port = 9051) as controller:
        #controller.signal(Signal.HUP)
        try:
            controller.authenticate()
        except stem.connection.MissingPassword:
            pw = getpass.getpass("Controller password: ")

    start = raw_input("Enter starting number: ")
    start = int(start)
    stop = start + 1000
    manual_list = []
    df2 = pd.DataFrame()
    df = pd.DataFrame()
    cols = ['user_id', 'review_date','wine_id', 'wine_name', 'score', 'notes']

    #try:
    for user in xrange(start, stop):
        print user

        df, manual_list  = process_user(user, manual_list)
        if len(df) > 0:
            df2 = df2.append(df, ignore_index=True)

        un = str(user)
        file_name = 'user_reviews' + un + '.json'
        df2.to_json(file_name)
        print 'Number of records in master dataframe: ', len(df2)
        print ' Manual List:' , manual_list
    #except:

    renew_connection()

    for user in xrange(start+1000, stop+1000):
        df, manual_list = process_user(user)
        if len(df) > 0:
            df2 = df2.append(df, ignore_index=True)


        un = str(user)
        file_name = 'user_reviews' + un + '.json'
        df2.to_json(file_name)
        print 'Number of records in master dataframe: ', len(df2)

    #finally:
    #driver.quit()
