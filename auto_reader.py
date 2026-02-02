import reader
import model
from urllib.parse import urlparse
import json
from flask import Response, jsonify
import os
import shutil
from flask import request
import random
import string

CURRENT_FOLDER = os.getcwd()
OUTPUT_FOLDER = "ads\\results"
REMOVED_FOLDER = 'ads\\removed'

def auto_reader():

    #url
    url = request.args.get('url', type=str)
    if (url is None):
        message = "url parameter is required"
        return { "error": message }, 400
    
    # Generate the unique folder name
    unique_folder_name = generate_unique_folder_name()
    base_path = f'{CURRENT_FOLDER}\\{unique_folder_name}'
    os.makedirs(base_path)

    # we get all item from the search
    all_items = reader.searchItemsWithUrl(url)
    
    # we launch the analysis
    for item in all_items:
        item_url = item['url']
        result = urlparse( item_url )
        id = result.path.split('/')[-1]

        if os.path.exists( f'{CURRENT_FOLDER}\\{OUTPUT_FOLDER}\\{id}.json'):
            continue
        #do not rerun if we removed it
        if os.path.exists(f'{CURRENT_FOLDER}\\{REMOVED_FOLDER}\\{id}.json'):
            continue

        print(f'Reading: {item_url}')
        #we don't have the body in the description so we read it
        data_item = reader.getItemWithUrl(item_url)

        description = data_item['body']
        features = data_item['attributes_cleaned']
        data = model.ai_analysisWithData(description=description, features=features)
        #we keep it
        data_item['analysis'] = data['analysis']
        data_item['financials'] = data['financials']
        #we save on disk
        filename  = f'{base_path}\\{id}.json'
        with open(filename, 'w',  encoding='utf-8') as f:
            json.dump(data_item, f)

    
    return Response({"folder": unique_folder_name}, status=200)

def coldData():
    data = []
    folder = f'{CURRENT_FOLDER}\\{OUTPUT_FOLDER}\\'
    for filename in os.listdir(folder):  
        if filename.endswith('.json'):
            filepath = os.path.join(folder, filename)
            with open(filepath, 'r') as file:
                data.append(json.load(file))
                
    return jsonify(data)    

def removeColdData():
    #url
    url = request.args.get('url', type=str)
    if (url is None):
        message = "url parameter is required"
        return { "error": message }, 400

    result = urlparse( url )
    id = result.path.split('/')[-1]
    filename  = f'{CURRENT_FOLDER}\\{OUTPUT_FOLDER}\\{id}.json'
    if os.path.exists(filename):
        # Move the file
        shutil.move(filename, REMOVED_FOLDER)
        return Response({ "status" : "Removed" }, status=200)
    

    return Response({ "status": "Not Removed" }, status=500)


def saveItem():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing 'data' in request body"}), 400
    
    if 'item' not in data:
        return jsonify({"error": "Missing 'description' in request body"}), 400
    item = data['item']

    item_url = item['url']
    result = urlparse( item_url )
    id = result.path.split('/')[-1]

    #we save on disk
    filename  = f'{CURRENT_FOLDER}\\{OUTPUT_FOLDER}\\{id}.json'
    with open(filename, 'w',  encoding='utf-8') as f:
        json.dump(item, f)

    return Response({ "status" : "Saved" }, status=200)


def generate_unique_folder_name(length=8):
    """Generate a unique folder name."""
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))
