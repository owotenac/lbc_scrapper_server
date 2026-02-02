import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
import model


def scrape(soup, search=True):
    content = soup.find_all(id='__NEXT_DATA__', recursive=True)
    #content = soup.find_all('script', recursive=True)
    if len(content) == 0:
        print("Content not found")
        return
    r = content[0].string
    data = json.loads(r)
    # we keep only the relevant part
    if search:
        if 'searchData' in data['props']['pageProps']:
            data = data['props']['pageProps']['searchData']['ads']
            cleaned_data = []
            for d in data:
                cleaned_data.append(convertData(d))
            return cleaned_data
        
    #no search => we get the ad
    data = data['props']['pageProps']['ad']
    return convertData(data)

def convertData(data):
    #keep 1 set of images
    data['images_url'] = []
    if (data.get('images') is not None):
        if (data['images'].get('urls') is not None):
            data['images_url'] = data['images']['urls']
        
    data.pop('images')

    #clean attributes
    cleaned_data = [
        {
            "key": item.get("key", ""),
            "key_label": item.get("key_label", ""),
            "value_label": item.get("value_label", ""),

        }
        for item in data['attributes']
    ]
    data['attributes_cleaned'] = cleaned_data
    data.pop('attributes')

    #convert price
    price = data.get('price_cents', None)
    price = price / 100 if price is not None else None
    data['price_euros'] = price
    data['attributes_cleaned'].append({
        "key": "price_euros",
        "key_label": "Price in Euros",
        #"value_label": f"{price} €" if price is not None else "N/A",
        'value_label': price
    })

    data.pop('price_cents', None)

    # if (data.get('body')):
    #     ai_description = model.getDescription(data.get('body'))
    #     data['ai_description'] = ai_description
    #print(json.dumps(data, indent=4, ensure_ascii=False))
    return data


