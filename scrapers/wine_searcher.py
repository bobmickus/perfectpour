import requests
import bs4
import json


'''
<form name="searchform" method="GET" action="http://www.wine-searcher.com/wine-select.lml">
<input type="hidden" name="Xfromsearch" value="Y">
<input id="Xwinename" type="TEXT" name="Xwinename" value="" title="Search phrase"

'''

# Query the wine-searcher.com API once
def query(url, payload):

    response = requests.get(url, params=payload)
    if response.status_code != 200:
        print 'WARNING', response.status_code
    else:
        return response.json()


if __name__ == "__main__":
    url = 'http://www.wine-searcher.com/ws-api.lml'

    payload = {}

    payload['Xkeyword_mode'] = 'X'
    payload['Xwinename'] = 'haut+brion'
    payload['Xvintage'] = 1995
    payload['Xcurrencycode'] = 'USD'


    content = query(url, payload)




    ''' Beautiful Soup - scraping method no 2

    wine_names = []
    wine_locations = []
    wine_ids = []
    scores = []
    reviews = []

    for span in soup.findAll('span', attrs={'class':'el nam'}):
        #print "Wine Name:", span.get_text()
        wine_names.append(span.get_text())
    for span in soup.findAll('span', attrs={'class':'el loc'}):
        #print "Location:", span.get_text()
        wine_locations.append(span.get_text())
    for span in soup.findAll('span', attrs={'class':'el var'}):
        wine_id = re.findall('[0-9]{1,10}', str(span.contents))
        #print "Wine ID:", wine_id
        wine_ids.append(wine_id)

    text = soup.findAll("p")
    #j = 1
    for i in xrange(1,len(text)-1,2):
        #print "Review: ===========", j
        #j += 1
        reviews.append(text[i])

    #soup.findAll('h3', text = re.compile('[0-9][0-9]\spoints'))
    #scores = re.findall('.*([0-9][0-9]\spoints)+', html)

    tags = soup('h3')

    for tag in tags:
        score1 = re.findall('.*([0-9][0-9])\spoints+', str(tag.contents))
        score2 = re.findall('.*([N][R])+', str(tag.contents))
        if len(score1) > 0:
            scores.append(score1)
        if len(score2) > 0:
            scores.append(score2)
