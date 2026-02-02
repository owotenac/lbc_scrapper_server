import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
import soup
from flask import request

headers = {
    "cookie": "datadome=VWTfmcc7vLkf2MUSBYUgeq4zgBvQ6c7w~Q6drZcT~TAEBcBaRJ~HUs96iOz47aOAD3xQbI8CrvIRkb6t1psks92cyL6tLxOA7tYLg~OAIFWzwol06sXoXnw~WFBuCMqO; __Secure-Install=ebe89a07-9d1c-4b38-acba-9b082414fdb9; cnfdVisitorId=86beea6f-e4fb-4202-a432-c86ee05f70a6",
    "accept-language": "en-US,en;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-GB;q=0.6",
    "method": "GET",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
}

async def fetch(url, params=None):
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url, params=params) as response:
            mResponse = await response.text()
            return {
                'content': mResponse,
                'status': response.status
            }


def searchItems():
    # url = "https://www.leboncoin.fr/recherche"

    # params = {
    #     "category":"9",
    #     "text":"immeuble",
    #     "price":"min-370000",
    #     "owner_type":"all",
    #     "real_estate_type":"5",
    #     "immo_sell_type":"old",
    #     "locations":"Aniane_34150__43.68942_3.58411_5000_10000"
    # }

    #response = asyncio.run(fetch(url, params=params))

    #url
    url = request.args.get('url', type=str)
    if (url is None or url == ""):
        message = "url parameter is required"
        return { "error": message }, 400

    return searchItemsWithUrl(url)

def buildSearchUrl(city: str):
    url = "https://www.leboncoin.fr/recherche"

    params = {
        "category":"9",
        "text":"immeuble",
        "price":"min-370000",
        "owner_type":"all",
        "real_estate_type":"5",
        "immo_sell_type":"old",
        "locations":city
    }

    return {
        'url': url, 
        'params': params
    }

def searchItemsWithUrl(url: str, params= None):
    response = asyncio.run(fetch(url, params=params))

    if (response['status'] != 200):
        print(f"Failed to fetch page, status code: {response['status']}")
        return response['status']
    
    soup_html = BeautifulSoup(response['content'], 'html.parser')
    data = soup.scrape(soup_html, True)
    return data


def getItemWithUrl(url: str):
    response = asyncio.run(fetch(url))

    if (response['status'] != 200):
        print(f"Failed to fetch page, status code: {response['status']}")
        return response['status']
    
    soup_html = BeautifulSoup(response['content'], 'html.parser')
    data = soup.scrape(soup_html, False)
    return data

def getItem():
    #url
    url = request.args.get('url', type=str)
    if (url is None or url == ""):
        message = "url parameter is required"
        return { "error": message }, 400
    
    return getItemWithUrl(url)



