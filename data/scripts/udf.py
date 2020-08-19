import json
import re
import time
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

# Tyre types
tyre_types = []

# Get HTML
def getHTML(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    res = urlopen(req).read()
    return res.decode('utf-8')

# Get main categories
def getCategoriesMain(url):
    print('### GETTING MAIN CATEGORIES ###\n')
    soup = BeautifulSoup(getHTML(url), 'html.parser')
    categories = []
    for ctg in soup.find_all(class_='ctg'):
        for ctg_child in ctg.findChildren(class_='item'):
            CAT_ID = ctg_child.get('data-node_id')
            for ctg_name in ctg_child.findChildren(class_='name'):
                CAT_NAME = ctg_name.string
            for ctg_image in ctg_child.findChildren('img'):
                CAT_IMAGE = ctg_image.get('data-srcset')
                categories.append({ 'id': CAT_ID, 'name': CAT_NAME, 'image_url': CAT_IMAGE })
    with open('./../main_cats.json', 'w') as file:
        json.dump(categories, file)

# Get tyre types
def getTyreTypes(url):
    print('### GETTING TYRE TYPES ###\n')
    soup = BeautifulSoup(getHTML(url), 'html.parser')
    for tyre in soup.find_all(class_='table_sizes'):
        for row in tyre.findChildren('span'):
            TYRE_SIZE = row.string
            TYRE_SIZE_R = TYRE_SIZE.split('/')
            tyre_types.append({ 
                'size_full': TYRE_SIZE,
                'size_width': TYRE_SIZE_R[0],
                'size_height': TYRE_SIZE_R[1],
                'size_diameter': TYRE_SIZE_R[2]
            })
    with open('./../tyre_sizes.json', 'w') as file:
        json.dump(tyre_types, file)
            
# Get tyres
def getTyres(url):
    print('### GETTING TYRES ###\n')
    TYRE_NAME = ''
    TYRE_NR = ''
    TYRE_IMG = ''
    TYRE_IMG_BRAND = ''
    TYRES = []
    for type in tyre_types:
        TYRE_TYPE = type['size_full'].split('/')
        TYRE_TYPE_URL = (TYRE_TYPE[0] + '-' + TYRE_TYPE[1] + '-' + TYRE_TYPE[2]).lower()
        soup = BeautifulSoup(getHTML(url + TYRE_TYPE_URL), 'html.parser')
        # Get pagination (max pages)
        pagination = soup.find(class_='pagination')
        last = pagination.find(class_='last').find('a').get('href').split('page=')
        # Max pages
        max_pages = int(last[1]) + 1
        # Loop through all the pages
        # ... get info, then go to next page
        for page in range(1, max_pages):
            print('Getting tyres: ' + TYRE_TYPE_URL + ' | Current page: ' + str(page) + '/' + str(max_pages))
            if page > 1:
                REQ_URL = url + TYRE_TYPE_URL + '?page=' + str(page)
            else:
                REQ_URL = url + TYRE_TYPE_URL
            soup2 = BeautifulSoup(getHTML(REQ_URL), 'html.parser')
            for li in soup2.find_all(class_='ovVisLi'):
                ABOUT = []
                LABELS = []
                # Get tyre name
                for names in li.find_all(class_='name'):
                    for name in names.findChildren('a'):
                        for i, row in enumerate(name):
                            if i == 0:
                                TYRE_NAME = (re.sub(' +', ' ', row.string)).replace('\n', '')
                            if i == 1:
                                TYRE_NR = row.string
                # Get images
                for i, images in enumerate(li.findChildren('img')):
                    if i == 0:
                        TYRE_IMG_BRAND = images.get('data-srcset')
                    if i == 1:
                        TYRE_IMG = images.get('data-srcset')
                # Get product labels
                for labels in li.find_all(class_='eu_re'):
                    A = ''
                    B = ''
                    for i, row in enumerate(labels.findChildren('li')):
                        if i == 0 or i == 2:
                            A = row.img.get('src')
                        # Gas label
                        if i == 1:
                            B = row.img.get('src')
                            LABELS.append({ 'gas': { 'label': A, 'value': B }})
                        # Grip label
                        if i == 3:
                            B = row.img.get('src')
                            LABELS.append({ 'grip': { 'label': A, 'value': B }})
                        # Noise label
                        if row.string != None:
                            LABELS.append({ 'noise': { 'label': 'noise', 'value': row.string }})
                # Get product info
                for about in li.find_all(class_='about'):
                    for line in about.findChildren('li'):
                        LC = ''
                        RC = ''
                        for about_title in line.find_all(class_='lc'):
                            LC = about_title.string
                        for about_title in line.find_all(class_='rc'):
                            RC = about_title.string
                        ABOUT.append({ LC: RC })
                # data
                TYRES.append({
                    'name': TYRE_NAME,
                    'nr': TYRE_NR,
                    'image_url': TYRE_IMG,
                    'image_url_brand': TYRE_IMG_BRAND,
                    'labels': LABELS,
                    'info': ABOUT
                })
            # Sleep for 3 seconds, then go to another page
            time.sleep(3)
        # Print data
        with open('./../tyres/tyres_' + str(type['size_full']) + '.json', 'w') as file:
            json.dump(TYRES, file)