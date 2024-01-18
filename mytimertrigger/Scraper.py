#title Importing libraries
import requests
import re
from bs4 import BeautifulSoup
from datetime import date, timedelta
import json
import logging

logging.info('Scraper.py file was successfully opened')

header = {'User-Agent': 'Mozilla/5.0'}

def make_soup(url):

  page = requests.get(url, headers=header)
  soup = BeautifulSoup(page.content, 'html.parser')
  return soup


def remaining_data_extractor(soup):

  #---extracting 
  raw_description = re.findall(r'(Kateqoriya.*)+</div></div></div>', str(soup))
  elements = ['</label>', '<span class="product-properties__i-value">', '</label>', '</span>', '</div>', '<div class="product-properties__i">', '<label class="product-properties__i-name">']

  raw_collected = raw_description[0]

  for i in elements:
    raw_collected = raw_collected.replace(i, ' ')

  untidy_collected = raw_collected.split(',,')
  split_data = ' '.join(untidy_collected).split('    ')
  renamed_dict = {}


  for item in split_data:
    category, value = item.split(maxsplit=1)
    renamed_dict[category] = value
  
  key_mappings = {
        'Kateqoriya': 'Category',
        'Mərtəbə': 'Floor',
        'Sahə': 'Area',
        'Otaq': 'Rooms',
        'Çıxarış': 'Document',
        'İpoteka': 'Mortgage',
        'Təmir': 'Renovation'
        }
  blank_dict = {'Category': '',
                'Floor':'',
                'Area':'',
                'Rooms':'',
                'Document':'',
                'Mortgage':'',
                'Renovation':''}
  renamed_dict = {key_mappings.get(key, key): value for key, value in renamed_dict.items()}
  
  result_dict = {key: value 
                 for key, value in renamed_dict.items()
                 if key in key_mappings.values()}
  
  blank_dict.update(result_dict)
  return (blank_dict)



import pandas as pd

df = pd.DataFrame(columns = ['Ad number', 'Date', 'Type', 'Category', 'Floor', 'Highest Floor','Area', 'Rooms', 'Document', 'Mortgage', 'Renovation', 'Price', 'Lattitude', 'Longitude','District', 'Nearby places'])

def extract(url):

  soup = make_soup(url)


  ### extracting date
  months_dictionary = {'Yanvar': 1,
                'Fevral': 2,
                'Mart': 3,
                'Aprel': 4,
                'May': 5,
                'İyun': 6,
                'İyul': 7,
                'Avqust': 8,
                'Sentyabr': 9,
                'Oktyabr': 10,
                'Noyabr': 11,
                'Dekabr': 12}
  
  raw_date = re.findall(r'Yeniləndi:\s(.*)\s<\/span><\/div>', str(soup))[0]

  ### filtering date of the ad post
  if 'Bugün' in raw_date:
    ad_date =  date.today().strftime('%Y.%m.%d')
  elif 'Dünən' in raw_date:
    ad_date = (date.today() - timedelta(days=1)).strftime('%Y.%m.%d')
  else:
    tempvar = raw_date.split(' ')
    ad_date = date(int(tempvar[2]), int(months_dictionary[tempvar[1]]), int(tempvar[0]))
  
  ### determining if the entity is to sell or rent
  if re.findall(r'İcarəyə verilir', str(soup)):
    ad_type = 'Rent'
  elif re.findall(r'Satılır', str(soup)):
    ad_type = 'Sale'

  ### determining district of the entity places nearby
  test = re.findall(r'(?<=target="_blank">)(.*?)(?=<\/a><\/li>)', str(soup))
  district = [x for x in test if 'r.' in x]
  nearby_places = [x.rstrip() for x in test if 'r.' not in x]
  if len(district) > 0:
    district = district[0]
  else:
    district = ''

  ### extracting lattitude and longitude
  lat = re.findall(r'data-lat="(\d+\.+\d+)', str(soup))[0]
  lon = re.findall(r'data-lng="(\d+\.+\d+)', str(soup))[0]

  ### extracting price
  price = re.findall(r'<span class="price-val">(\d+.?\d+.?\d+)', str(soup))[0].replace(' ', '')

  ad_number = url[-7:]
  categories_data = remaining_data_extractor(soup)
  


  collected_data = {'Ad number': int(ad_number),
              'Date': str(ad_date),
              'Type': ad_type,
              **categories_data,
              'Price': int(price),
              'Lattitude': float(lat),
              'Longitude': float(lon),
              'District': district,
              'Nearby places': str(nearby_places)}
  
  df = pd.DataFrame([collected_data])
  
  return df

logging.info('before env')

import os
import dotenv
dotenv.load_dotenv()

url_link = os.environ.get('url')

logging.info('after env')

def export_to_df(x):  
  # u = int(url[-7:])
  # b = url[:-7]
  global df
  for i in x:
    url = url_link +str(i)
    
    try:
      new_df = extract(url)
      df = pd.concat([df, new_df], ignore_index = True)
    except:
      print(f'Ad {i} is not found with the link')
  return df






def transform (df):

  key_mapping = {'Yeni tikili': 'New building',
                 'Köhnə tikili': 'Old building',
                 'Mənzil': 'Apartment',
                 'Həyət evi / Bağ evi' : 'House',
                 'Ofis': 'Office',
                 'Torpaq': 'Land',
                 'Obyekt': 'Commerical'}
  
  for i in range(df.shape[0]):
    #transform the Highest floor column
    try:
      df.loc[i, ('Highest Floor')] = int(re.findall(r'\/.(\d+)', df.loc[i, ('Floor')] )[0])
      df.loc[i, ('Floor')] = int(re.findall(r'(.*\d)\s', df.loc[i, ('Floor')] )[0])
    except:
      pass
    
    try:
      df.loc[i, ('Category')] = key_mapping[ df.loc[i, ('Category')]]
    except:
      pass
      
    try:
      df.loc[i, ('Area')] = re.findall(r'\d+(?:\.\d+)?', df.loc[i, ('Area')])[0]
    except:
      pass

    try:
      df.loc[i, ('Rooms')] = int(re.findall(r'(\d+)', df.loc[i, ('Rooms')])[0])
    except:
      pass
      
    
    value = df.loc[i, 'Renovation']
    if isinstance(value, float):
      value = str(value)
    if 'var' in value:
      df.loc[i, 'Renovation'] = 'Yes'
    elif 'yoxdur' in value:
      df.loc[i, 'Renovation'] = 'No'
    
    value = df.loc[i, 'Mortgage']
    if isinstance(value, float):
      value = str(value)
    if 'var' in value:
      df.loc[i, 'Mortgage'] = 'Yes'
    elif 'yoxdur' in value:
      df.loc[i, 'Mortgage'] = 'No'
    
    value = df.loc[i, 'Document']
    if isinstance(value, float):
      value = str(value)
    if 'var' in value:
      df.loc[i, 'Document'] = 'Yes'
    elif 'yoxdur' in value:
      df.loc[i, 'Document'] = 'No'
    
    try:
      df['Nearby places'] = df['Nearby places'].astype(str)
    except:
      continue
  
  return df


df.drop(df.index, inplace=True)

import random
ad_list = random.sample(range(3900000, 4150000), 15)
logging.info(f'{ad_list}')
predata = export_to_df(ad_list)


ready_df = transform(predata).copy()
ready_df.fillna('', inplace=True)
ready_df['Nearby places'] = ready_df['Nearby places'].map(lambda x: json.dumps(x, ensure_ascii=False))
