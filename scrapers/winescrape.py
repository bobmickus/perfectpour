import requests
import bs4
import json
# from pymongo import MongoClient
# from pymongo.errors import DuplicateKeyError, CollectionInvalid
# import datetime as dt

# Optional:  use MongoDB to store data
# Define the MongoDB database and table
# db_client = MongoClient()
# db = db_client['winedotcom']
# table = db['wine']

# Query the wine.com API once
def query(url, payload):
    #payload  = dict(apikey.items() + params['params'].items())
    response = requests.get(url, params=payload)
    if response.status_code != 200:
        print 'WARNING', response.status_code
    else:
        return response.json()   #  ['Products']['List']


if __name__ == "__main__":

    #url to access red wines
    #http://services.wine.com/api/beta2/service.svc/json/catalog?filter=categories(490+124)&offset=100&size=5&apikey=81f9f30bf15a4a3c3b2fdc683b2f2ed5

    url = 'http://services.wine.com/api/beta2/service.svc/json/catalog'
    url2 = 'http://services.wine.com/api/beta2/service.svc/format/categorymap'

    payload = { 'apikey': '81f9f30bf15a4a3c3b2fdc683b2f2ed5'}

    #payload['search'] = '1992+Optima+Cabernet+Sauvignon+Alexander+Valley'

    start_record = 0
    for iter in range(0,500):
        print "Downloading Batch Number: ", iter
        #starting record number
        payload['offset'] = start_record
        #number of records to download.  max=100
        payload['size'] = 100
        content = query(url, payload)
        wines = content['Products']['List']
        with open('./data/white_wines/white_wine_data'+str(iter)+'.json', 'w') as f:
            json.dump(wines, f)
        start_record += 100
