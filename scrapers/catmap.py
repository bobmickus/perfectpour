
import json
import urllib
import xml.etree.ElementTree as ET

#url to access wine.com categories
url = 'http://services.wine.com/api/beta2/service.svc/XML/categorymap?filter=categories(490)&apikey=81f9f30bf15a4a3c3b2fdc683b2f2ed5'

#url to access red wines
http://services.wine.com/api/beta2/service.svc/XML/catalog?filter=categories(490+124)&offset=100&size=5&apikey=81f9f30bf15a4a3c3b2fdc683b2f2ed5


document = urllib.urlopen (url).read()
print 'Retrieved', len(document), 'characters.'
tree = ET.fromstring(document)
count = 0
for Category in tree.findall('Description'):
    print
    count = count + 1
    if count>10:
        break
    print Description.find('Id').text

    '''
    screen_name').text status = user.find('status')
    if status :
        txt = status.find('text').text print ' ',txt[:50]
    '''
