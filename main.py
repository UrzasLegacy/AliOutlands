version = "6.0"

import os
import glob
import requests
import re
import time
import datetime
import webbrowser
import sqlite3
import threading
import queue
import keyboard
import pywinauto
#import numpy as np
#import pyautogui
import socket
import aiohttp
import asyncio
import tkinter as tk

from tkinter import ttk
from multiprocessing import Pool, cpu_count
from bs4 import BeautifulSoup
from contextlib import contextmanager
from urllib.parse import quote_plus
from collections import defaultdict
from OutlandsDicts import *
from OutlandsUtils import *
from requests.cookies import RequestsCookieJar



#TODO Small history stack for clipboard: Ctrl-z to undo script append
#TODO For image analysis of inventory, instead of screen capture, snip and use last image on clipboard
#TODO add clothes,boat stuff (crew, upgrades), jugglin torches n shit
#TODO check if antiquity is registered before buying
#TODO remove superfluous item ids from quick buy scripts. Only need the ids of items that are searched for in quick scrape
#TODO OR use item_serial to find item and then getlabel check against the itemDescriptions list to confirm no shenanigans.
#TODO item id method allows buying things out of order at a location.
#TODO fix recurse search in buy scripts to search each time a container is opened

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=logging.DEBUG,  # Set the minimum log level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Format for log messages
    datefmt='%Y-%m-%d %H:%M:%S',  # Format for timestamps
    handlers=[
        logging.FileHandler('app.log')  # Output logs to a file
    ]
)
logger = logging.getLogger('MallScraper')

master_prices = collate_master_price_dict()

def multi_parse_wide(in_tuple):
    item = in_tuple[0]
    price_depth = in_tuple[1]
    time_frame = in_tuple[2]
    cutoff_threshold = in_tuple[3]
    outlands_cookie = in_tuple[4]
    corrupted_link_price_threshold = 200000
    steps = {
        "Aspect Core": core_prices,
        "Aspect Extract": extract_prices,
        "Aspect Distillation": distil_prices,
        "Undeciphered": tmap_prices,
        "Skill Mastery Scroll": scroll_prices,
        "Mastery Chain Link": link_prices,
        "Misc Crafting": misc_crafting_prices,
    }
    prices_obj = steps[item]
    if item == 'Misc Crafting':
        page_url = "https://outlandmalls.com/?item=&search_category_id=21&search_sub_category_id=98" #temp_url = f"{page_url}&page={i}"
    else:
        page_url = "https://outlandmalls.com/?item=" + quote_plus(item) + "&search_category_id=0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    agg_rows = []
    i = 0
    failsafe = 0 
    
    while i < 10:
        time.sleep(1)
        if i > 0:
            temp_url = f"{page_url}&page={i}"
        else:
            temp_url = page_url
        cookie = {"app": outlands_cookie}
        response = requests.get(temp_url, headers=headers, cookies=cookie)
        if response.status_code != 200:
            print(f"multi_parse_wide: Failed to retrieve the webpage: {item}. Status code: {response.status_code}")
            if failsafe == 0:
                break
            failsafe = 0
            time.sleep(.3)
            continue
        soup = BeautifulSoup(response.content, 'lxml')
        if soup:
            table = soup.find('table', id="item-search-results")
            if not table:
                print('Table not found')
                break
            rows = table.tbody.find_all('tr')
            agg_rows.extend(rows)
            if rows and len(rows) < 500:
                print(f'Premature break, results: {len(rows)}')
                break
        i += 1

    out_data = []
    my_fetched_locations = my_locations.items()
    for row in agg_rows:
        cells = row.find_all('td')
        time_cell = cells[8]
        time_string = time_cell.text.strip().lower()
        if is_time_recent_multi(time_string,time_frame):
            vendor_cell = cells[1]
            location_cell = cells[2]
            name_cell = cells[4]
            quantity_cell = cells[5]
            price_cell = cells[7]
            vendor_string = vendor_cell.text.strip()
            vendor_serial = vendor_cell.find('a')['href'].split('/')[-1]
            item_serial = vendor_cell.find('span')['data-item_id']
            item_price = vendor_cell.find('span')['data-price']
            location_coordinates = location_cell.text.strip()
            location_link = location_cell.find('a')['href']
            location_link_split = location_link.split('#')
            location_split = location_coordinates.split(',')
            x1, y1 = map(int,location_split)
            closest_location = min(my_fetched_locations, key=lambda loc: get_distance_squared(x1, y1, loc[1][0], loc[1][1]))
            location_name = closest_location[0]

            formatted_location_link = f"{location_link_split[0]}?{vendor_serial}?{item_serial}?{item_price}#{location_link_split[1]}"
            quantity_string = quantity_cell.text.strip()
            name_string = name_cell.text.strip()
            name_check_string = format_ingame_name(name_string, quantity_string)
            try:
                price_cell_sanitized = re.sub(r"\D",'',price_cell.text)
                price = float(price_cell_sanitized)
            except Exception as e:
                print(f"multi_parse_wide: {name_string}:{location_name}:{vendor_string}:{price_cell.text.strip()}")
            if item == 'Mastery Chain Link':
                if name_string.startswith('a '):
                    name_string = name_string[2:]
                chain_name = clean_chainlink_string(name_string)
                if name_string.startswith('bronze mastery chain link'):
                    threshold = float(prices_obj.get(chain_name,[0,0,0])[0])
                elif name_string.startswith('silver mastery chain link'):
                    threshold = float(prices_obj.get(chain_name,[0,0,0])[1])
                elif name_string.startswith('gold mastery chain link'):
                    threshold = float(prices_obj.get(chain_name,[0,0,0])[2])
                elif name_string.startswith('corrupted mastery chain link'):
                    threshold = float(corrupted_link_price_threshold)
                else:
                    threshold = 0
            else:
                threshold = float(prices_obj.get(name_string, 0))
            if threshold > 0:
                cost_to_price_ratio = round(price / threshold,2)
            elif price == 999 and not is_junk(name_string,quantity_string):
                cost_to_price_ratio = 1001
            else:
                cost_to_price_ratio = 1000
            if cost_to_price_ratio != 1001 and cost_to_price_ratio > cutoff_threshold and price_depth != 2:
                continue
            if(price <= threshold or price_depth == 2): #self.search_pricedepth.get()
                total_cost = round(price * int(quantity_string),0)
                total_profit = round(threshold * int(quantity_string) - total_cost,0)
                format_url = "https://outlandmalls.com/?item=" + quote_plus(name_string) + "&search_category_id=0"
                out_data.append((f"{name_string}",f"{price}/{threshold}",f"{cost_to_price_ratio}",f"{quantity_string}",f"{total_profit}",f"{vendor_string}",f"{location_coordinates}\t{location_name}",f"{time_string}",f"{formatted_location_link}",f"{format_url}",f"{total_cost}",f"{name_check_string}"))
    if len(out_data) > 0:
        return (out_data,)
    else:
        return (None,)

def simple_parse_wide(in_tuple):
    item = in_tuple[0]
    price_depth = in_tuple[1]
    time_frame = in_tuple[2]
    cutoff_threshold = in_tuple[3]
    corrupted_link_price_threshold = 200000
    steps = {
        "Aspect Core": core_prices,
        "Aspect Extract": extract_prices,
        "Aspect Distillation": distil_prices,
        "Undeciphered": tmap_prices.update(rmap_prices),
        "Skill Mastery Scroll": scroll_prices,
        "Mastery Chain Link": link_prices,
        "Misc Crafting": misc_crafting_prices,
    }
    prices_obj = steps[item]
    if item == 'Misc Crafting':
        page_url = "https://outlandmalls.com/?item=&search_category_id=21&search_sub_category_id=98"
    else:
        page_url = "https://outlandmalls.com/?item=" + quote_plus(item) + "&search_category_id=0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    agg_rows = []
    i = 0
    failsafe = 0 
    while i < 10:
        if i > 0:
            temp_url = f"{page_url}&page={i}"
        else:
            temp_url = page_url
        cookie = {"app": user_config["outlands_cookie"]}
        response = requests.get(temp_url, headers=headers, cookies=cookie)
        if response.status_code != 200:
            print(f"simple_parse_wide: Failed to retrieve the webpage: {item}. Status code: {response.status_code}")
            if failsafe == 0:
                break
            failsafe = 0
            time.sleep(.3)
            continue
        soup = BeautifulSoup(response.content, 'lxml')
        if soup:
            table = soup.find('table', id="item-search-results")
            if not table:
                print('Table not found')
                break
            rows = table.tbody.find_all('tr')
            agg_rows.extend(rows)
            if rows and len(rows) < 500:
                print(f'Premature break, results: {len(rows)}')
                break
        i += 1

    out_data = []
    my_fetched_locations = my_locations.items()
    for row in agg_rows:
        cells = row.find_all('td')
        time_cell = cells[8]
        time_string = time_cell.text.strip().lower()
        if is_time_recent_multi(time_string,time_frame):
            vendor_cell = cells[1]
            location_cell = cells[2]
            name_cell = cells[4]
            quantity_cell = cells[5]
            price_cell = cells[7]
            vendor_string = vendor_cell.text.strip()
            vendor_serial = vendor_cell.find('a')['href'].split('/')[-1]
            item_serial = vendor_cell.find('span')['data-item_id']
            item_price = vendor_cell.find('span')['data-price']
            location_coordinates = location_cell.text.strip()
            location_link = location_cell.find('a')['href']
            location_link_split = location_link.split('#')
            location_split = location_coordinates.split(',')
            x1, y1 = map(int,location_split)
            closest_location = min(my_fetched_locations, key=lambda loc: get_distance_squared(x1, y1, loc[1][0], loc[1][1]))
            location_name = closest_location[0]

            
            formatted_location_link = f"{location_link_split[0]}?{vendor_serial}?{item_serial}?{item_price}#{location_link_split[1]}"
            quantity_string = quantity_cell.text.strip()
            name_string = name_cell.text.strip()
            name_check_string = format_ingame_name(name_string, quantity_string)
            try:
                price_cell_sanitized = re.sub(r"\D",'',price_cell.text)
                price = float(price_cell_sanitized)
            except Exception as e:
                print(f"simple_parse_wide: {name_string}:{location_name}:{vendor_string}:{price_cell.text.strip()}")
            if item == 'Mastery Chain Link':
                if name_string.startswith('a '):
                    name_string = name_string[2:]
                chain_name = clean_chainlink_string(name_string)
                if name_string.startswith('bronze mastery chain link'):
                    threshold = float(prices_obj.get(chain_name,[0,0,0])[0])
                elif name_string.startswith('silver mastery chain link'):
                    threshold = float(prices_obj.get(chain_name,[0,0,0])[1])
                elif name_string.startswith('gold mastery chain link'):
                    threshold = float(prices_obj.get(chain_name,[0,0,0])[2])
                elif name_string.startswith('corrupted mastery chain link'):
                    threshold = float(corrupted_link_price_threshold)
                else:
                    threshold = 0
            else:
                threshold = float(prices_obj.get(name_string, 0))
            if threshold > 0:
                cost_to_price_ratio = round(price / threshold,2)
            elif price == 999 and not is_junk(name_string,quantity_string):
                cost_to_price_ratio = 1001
            else:
                cost_to_price_ratio = 1000
            if cost_to_price_ratio != 1001 and cost_to_price_ratio > cutoff_threshold and price_depth != 2:
                continue
            if(price <= threshold or price_depth == 2): #self.search_pricedepth.get()
                total_cost = round(price * int(quantity_string),0)
                total_profit = round(threshold * int(quantity_string) - total_cost,0)
                format_url = "https://outlandmalls.com/?item=" + quote_plus(name_string) + "&search_category_id=0"
                out_data.append((f"{name_string}",f"{price}/{threshold}",f"{cost_to_price_ratio}",f"{quantity_string}",f"{total_profit}",f"{vendor_string}",f"{location_coordinates}\t{location_name}",f"{time_string}",f"{formatted_location_link}",f"{format_url}",f"{total_cost}",f"{name_check_string}"))
    if len(out_data) > 0:
        return (out_data,)
    else:
        return (None,)

def multi_parse_misc(in_tuple):
    html = in_tuple[0]
    searchPrice = in_tuple[1]
    page_url = in_tuple[2]
    time_frame = in_tuple[3]
    price_depth = in_tuple[4]
    cutoff_threshold = in_tuple[5]
    my_fetched_locations = my_locations.items()
    soup = BeautifulSoup(html, 'lxml')
    if soup:
        table = soup.find('table', id="item-search-results")
        if not table:
            print(f"multi_parse_misc: No table: {page_url}")
            return False
        rows = table.tbody.find_all('tr')
        out_data = []
        for row in rows:
            cells = row.find_all('td')
            time_cell = cells[8]
            time_string = time_cell.text.strip().lower()
            if is_time_recent_multi(time_string,time_frame):
                price_cell = cells[7]
                price_cell_sanitized = re.sub(r"\D",'',price_cell.text)
                price = float(price_cell_sanitized)
                ratio = round(price / searchPrice,2)
                if ratio > cutoff_threshold and price_depth != 2:
                        continue
                if price <= searchPrice or price_depth == 2:
                    vendor_cell = cells[1]
                    location_cell = cells[2]
                    name_cell = cells[4]
                    quantity_cell = cells[5]
                    vendor_string = vendor_cell.text.strip()
                    vendor_serial = vendor_cell.find('a')['href'].split('/')[-1]
                    item_serial = vendor_cell.find('span')['data-item_id']
                    item_price = vendor_cell.find('span')['data-price']
                    location_coordinates = location_cell.text.strip()
                    location_link = location_cell.find('a')['href']
                    location_link_split = location_link.split('#')
                    location_split = location_coordinates.split(',')
                    x1, y1 = map(int,location_split)
                    closest_location = min(my_fetched_locations, key=lambda loc: get_distance_squared(x1, y1, loc[1][0], loc[1][1]))
                    location_name = closest_location[0]
                    formatted_location_link = f"{location_link_split[0]}?{vendor_serial}?{item_serial}?{item_price}#{location_link_split[1]}"
                    quantity_string = quantity_cell.text.strip()
                    name_string = name_cell.text.strip()
                    name_check_string = format_ingame_name(name_string,quantity_string)
                    total_cost = round(price * int(quantity_string),0)
                    total_profit = round(searchPrice * int(quantity_string) - total_cost,0)
                    out_data.append((f"{name_string}",f"{price}/{searchPrice}",f"{ratio}",f"{quantity_string}",f"{total_profit}",f"{vendor_string}",f"{location_coordinates}\t{location_name}",f"{time_string}",f"{formatted_location_link}",f"{page_url}",f"{total_cost}",f"{name_check_string}"))
        return out_data

def simple_parse_narrow(in_tuple): #(response.content,searchPrices,page_url,60,1,.93)
    from lxml import html as lxml_html
    html, searchPrices, page_url, time_frame, price_depth, cutoff_threshold = in_tuple

    tree = lxml_html.fromstring(html)

    table = tree.xpath('//table[@id="item-search-results"]')[0]

    rows = table.xpath('.//tbody/tr')
    out_data = []
    my_fetched_locations = my_locations.items()

    for row in rows:
        cells = row.xpath('.//td')
        name_cell = cells[4]
        name_string = name_cell.text_content().strip()
        searchPrice = float(searchPrices.get(name_string, 1))
        time_cell = cells[8]
        time_string = time_cell.text_content().strip().lower()

        if not is_time_recent_multi(time_string,time_frame):
            continue

        price_cell = cells[7]
        price_cell_sanitized = re.sub(r"[^\d.]",'',price_cell.text_content())
        price = float(price_cell_sanitized)
        ratio = round(price / searchPrice,2)

        if ratio > cutoff_threshold and price_depth != 2:
            continue
        if price > searchPrice and price_depth != 2:
            continue

        vendor_cell = cells[1]
        location_cell = cells[2]
        quantity_cell = cells[5]
        vendor_string = vendor_cell.text_content().strip()
        vendor_serial = vendor_cell.xpath('.//a/@href')[0].split('/')[-1]
        item_serial = vendor_cell.xpath('.//span/@data-item_id')[0]
        item_price = vendor_cell.xpath('.//span/@data-price')[0]

        location_coordinates = location_cell.text_content().strip()
        location_link = location_cell.xpath('.//a/@href')[0]
        location_link_split = location_link.split('#')
        location_split = location_coordinates.split(',')

        x1, y1 = map(int,location_split)

        closest_location = min(my_fetched_locations, key=lambda loc: get_distance_squared(x1, y1, loc[1][0], loc[1][1]))
        location_name = closest_location[0] if closest_location else 'N/A'
        formatted_location_link = f"{location_link_split[0]}?{vendor_serial}?{item_serial}?{item_price}#{location_link_split[1]}"
        quantity_string = quantity_cell.text_content().strip()
        name_check_string = format_ingame_name(name_string,quantity_string)
        total_cost = round(price * int(quantity_string),0)
        total_profit = round(searchPrice * int(quantity_string) - total_cost,0)
        out_data.append((f"{name_string}",f"{price}/{searchPrice}",f"{ratio}",f"{quantity_string}",f"{total_profit}",f"{vendor_string}",f"{location_coordinates}\t{location_name}",f"{time_string}",f"{formatted_location_link}",f"{page_url}",f"{total_cost}",f"{name_check_string}"))
    return out_data
    
### JOURNAL MANAGEMENT
def delete_most_recent_log(event=None):
    file = get_most_recent_log()
    os.remove(file)

def get_most_recent_log():
    folder_path = "C:\\Program Files (x86)\\Ultima Online Outlands\\ClassicUO\\Data\\Client\\JournalLogs\\"
    files = [f for f in glob.glob(os.path.join(folder_path, '*.txt')) if os.path.isfile(f)]
    sorted_files = sorted(files, key=os.path.getmtime, reverse=True)
    latest_files = sorted_files[:6]
    accessible_files = [f for f in latest_files if check_accessibility(f)]
    try:
        latest_file = max(accessible_files, key=os.path.getmtime)
    except Exception as e:
        print(f"get_most_recent_log: Unexpected error when accessing {folder_path}: {str(e)}")
        latest_file = False
    return latest_file

def check_accessibility(file_path):
    try:
        with open(file_path):
            pass
        return True
    except Exception as e:
        return False

def parse_log_to_object():
    #my_vendors = [0x2A2814, 0x2A280D, 0x2A27FA, 0x2A27F3, 0x2A281C, 0x2A2830, 0x2A2835, 0x2A283D]
    my_vendors = user_config['vendor_info']
    vendors = {}
    current_vendor = None
    latest_log = get_most_recent_log()
    if not latest_log:
        return False
    character_name = None
    pass_flag = False
    my_vendor_objs = []
    with open(latest_log, 'r', encoding='utf-8') as lines:
        for line in lines:
            if "System: Welcome" in line:
                match = re.search(r'System: Welcome (.+)!', line)
                character_name = match.group(1) if match else 'Invalid Name'
            elif "…item" in line and current_vendor is not None:
                if "Not for sale" in line:
                    continue
                match = re.search(r'ID:(\d+) Price: ([\d,]+) (.+?)(?:( : (\d+))(.*))?$', line)
                if match:
                    item_id = int(match.group(1))
                    item_price = int(match.group(2).replace(',',""))
                    item_description = match.group(3)
                    if " dye " in item_description and ") (hue" in item_description:
                        item_description = item_description.split(") (hue")[0] + ")"
                    item_match = f"{item_description}{match.group(4)}" if match.group(4) else item_description
                    item_quantity = int(match.group(5)) if match.group(5) else 1
                    item_suffix = match.group(6) if match.group(5) else ''
                    if(item_suffix):
                        item_description += item_suffix
                    item_unitprice = round(item_price / item_quantity,4)
                    item = {
                        'id': item_id,
                        "price": item_unitprice,
                        "description": item_description,
                        "full_description": item_match,
                        "quantity": item_quantity,
                        'location': location,
                        'location_name': location_name
                    }
                    pass_flag = True
                    current_vendor["items"].append(item)
                else:
                    print('parse_log_to_object: missing: ' + line)
            elif "…vendorStart" in line:
                parts = line.split()
                vendor_id = int(parts[4])
                vendor_name = ' '.join(parts[5:])
                date_string = parts[0][1:]
                time_string = parts[1][:1]
                current_vendor = {
                    "id": vendor_id,
                    "name": vendor_name,
                    "time": f"{date_string} {time_string}",
                    "items": []
                }
                vendors[vendor_id] = current_vendor
            elif "…vendorEnd" in line:
                if current_vendor['id'] in my_vendors:
                    my_vendor_objs.append(current_vendor)
                    #HandleMyVendor(current_vendor)
                current_vendor = None
            elif "System: Current location is" in line:
                match = re.search(r'Current location is \((\d+), (\d+)', line)
                if match:
                    x1 = match.group(1)
                    y1 = match.group(2)
                    location = f"{x1}, {y1}"
                    check_dist = float('inf')
                    closest = None
                    for location_name, tuple_loc in my_locations.items():
                        x2 = int(tuple_loc[0])
                        y2 = int(tuple_loc[1])
                        distance = get_distance(int(x1),int(y1),x2,y2)
                        if distance < check_dist:
                            check_dist = distance
                            closest = location_name
                    location_name = closest if closest else 'N/A'
                else:
                    location = "0,0"
        if pass_flag:
            if len(my_vendor_objs):
                handle_my_vendors(my_vendor_objs)
            return (vendors, latest_log, character_name)
    if character_name:
        return (latest_log, character_name)
    
def handle_my_vendors(vendor_obj_list):
    initialize_db()
    full_items = []
    for vendor_obj in vendor_obj_list:
        items = vendor_obj['items']
        for item in items:
            full_items.append(item)
    update_snapshots(full_items)



### DATABASE
@contextmanager
def connect_db():
    conn = sqlite3.connect('inventory.db')
    try:
        yield conn
    finally:
        conn.close()

def execute_query(query, params=()):
    with connect_db() as conn:
        c = conn.cursor()
        c.execute(query, params)
        conn.commit()

def fetch_query(query, params=()):
    with connect_db() as conn:
        c = conn.cursor()
        c.execute(query, params)
        return c.fetchall()
    
def initialize_db():
    if not os.path.exists('inventory.db'):
        execute_query('''CREATE TABLE IF NOT EXISTS inventory_snapshots
                    (snapshot_time TEXT, id TEXT PRIMARY KEY, price INTEGER, description TEXT, quantity INTEGER)''')

        execute_query('''CREATE TABLE IF NOT EXISTS sales_history
                    (snapshot_time TEXT, id TEXT PRIMARY KEY, price INTEGER, description TEXT, quantity INTEGER)''')
        
        print("Database and tables initialized.")

def take_snapshot(inventory_items):
    inserted_rows = []
    try:
        with connect_db() as conn:
            c = conn.cursor()
            snapshot_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            previous_snapshot = get_most_recent_inventory_snapshot()
            previous_length = len(previous_snapshot)
            if previous_length == 0 or (previous_length and not snapshots_are_identical(previous_snapshot,inventory_items)):
                for item in inventory_items:
                    c.execute("INSERT INTO inventory_snapshots (snapshot_time, id, price, description, quantity) VALUES (?, ?, ?, ?, ?)",
                            (snapshot_time, item['id'], item['price'], item['description'], item['quantity']))
                    
                    last_row_id = c.lastrowid
                    c.execute("SELECT * FROM inventory_snapshots WHERE rowid=?", (last_row_id,))
                    inserted_row = c.fetchone()
                    inserted_rows.append(inserted_row)
                conn.commit()
                return inserted_rows
            else:
                return previous_snapshot
    except Exception as e:
        print(f"take_snapshot: Exception: {e}")

def read_full_db():
    try:
        with connect_db() as conn:
            c = conn.cursor()
            c.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = c.fetchall()
            table_names = [table[0] for table in tables]
            print('-FULL DB-')
            for table in table_names:
                print(f"Fetching records from table: {table}")
                c.execute(f"SELECT * FROM {table}")
                rows = c.fetchall()
                for row in rows:
                    print(row)
            print("-END DB-")
    except Exception as e:
        print(f"An error occurred: {e}")
    
def get_most_recent_inventory_snapshot():
    try:
        fetches = fetch_query("SELECT MAX(snapshot_time) FROM inventory_snapshots") #returns fetchall
        if len(fetches):
            most_recent_time = fetches[0][0]
            return fetch_query("SELECT * FROM inventory_snapshots WHERE snapshot_time=?", (most_recent_time,))
        return []
    except Exception as e:
        print(f"get_most_recent_inventory_snapshot: An error occurred: {e}")
        return []

def get_most_recent_sales_time():
    try:
        fetches = fetch_query("SELECT MAX(snapshot_time) FROM sales_history") #returns fetchall
        if len(fetches):
            most_recent_time = fetches[0][0]
            return most_recent_time
        return None
    except Exception as e:
        print(f"get_most_recent_sales_time: An error occurred: {e}")
        return None

def delete_db():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("DELETE FROM inventory_snapshots")
    conn.commit()
    conn.close()

def simulate_snapshot(inventory_items):
    sim_snap = []
    for item in inventory_items:
        sim_snap.append(tuple(item.values()))
    return sim_snap[:-1]

def snapshots_are_identical(snapshot, inventory_items):
    truncated_snapshot = [t[1:] for t in snapshot]
    simulated_snapshot = simulate_snapshot(inventory_items)
    # Sort both snapshots by the 'id' field (assuming id is at index 0)
    sorted_snap1 = sorted(truncated_snapshot, key=lambda x: x[0])
    sorted_snap2 = sorted(simulated_snapshot, key=lambda x: x[0])

    # If their lengths are different, they can't be identical
    if len(sorted_snap1) != len(sorted_snap2):
        return False
    for item1, item2 in zip(sorted_snap1, sorted_snap2):
        if item1 != item2:
            return False
    return True

def update_snapshots(inventory_items):
    snapshot1 = get_most_recent_inventory_snapshot()
    if len(snapshot1) == 0:
        take_snapshot(inventory_items)
        return    
    if snapshots_are_identical(snapshot1, inventory_items):
        return
    snapshot2 = take_snapshot(inventory_items)

    # Assuming that id is at index 1
    snapshot1_dict = {item[1]: (item[2],item[3],item[4]) for item in snapshot1}
    snapshot2_dict = {item[1]: (item[2],item[3],item[4]) for item in snapshot2}
    snapshot_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sold_items = {}
    for id, item_info in snapshot1_dict.items():
        price1, description1, quantity1 = item_info
        if id in snapshot2_dict:
            price2, description2, quantity2 = snapshot2_dict[id]
            sold_quantity = quantity1 - quantity2
            if sold_quantity > 0:
                sold_items[id] = (price1,description1,sold_quantity)
        else:
            sold_items[id] = item_info  # Or some other logic
    for id, item_info in sold_items.items():
        price, description, quantity = item_info
        record_sale(snapshot_time,id,price,description,quantity)
    return sold_items

def record_sale(snapshot_time, id, price, description, quantity):
    try:
        existing_records = fetch_query("SELECT * FROM sales_history WHERE id = ?", (id,))
        if len(existing_records) == 0:
            execute_query("INSERT INTO sales_history (snapshot_time, id, price, description, quantity) VALUES (?, ?, ?, ?, ?)",
                    (snapshot_time, id, price, description, quantity))
    except Exception as e:
        print(f"record_sale: An error occurred: {e}")

class AliApp:
    def __init__(self,root):
        self.root = root
        self.root.title(f"Ali's OutlandMalls Scraper v{version}")
        self.root.geometry("1160x870")
        self.root.minsize(1300, 870)
        #self.root.maxsize(900, 700)
        self.root.bind("<Return>", self.ParseMostRecentJournalLog)
        self.root.bind("<Control-Return>", self.ScrapeOutlandMall)
        self.root.bind("<Control-Alt-Return>", self.PriorityScrapeOutlandMall)
        self.root.bind("<KeyPress-3>", self.set_all_checkboxes)
        self.root.bind("<KeyPress-4>", self.set_none_checkboxes)
        self.root.bind("<KeyPress-1>", self.set_hp_variables)
        self.root.bind("<KeyPress-2>", self.set_lp_variables)
        self.root.bind("<KeyPress-`>", self.on_backtick_press)
#        self.root.bind("<Alt-Return>", self.set_hp_variables)
#        self.root.bind("<Shift-Return>", self.set_lp_variables) 
        self.root.bind("<F1>", self.sort_tree_quick) #sort_tree_quick sort_tree_density
        self.root.bind("<Control-F1>", delete_most_recent_log)
        self.root.grid_columnconfigure(0, weight=10)
        self.root.grid_columnconfigure(1, weight=0)
        self.root.grid_columnconfigure(2, weight=0)
        self.root.grid_rowconfigure(0, weight=15)
        self.root.grid_rowconfigure(1, weight=0)

        # Create a frame to hold the Tree widget and the Scrollbar
        self.tree_frame = tk.Frame(self.root)
        self.tree_frame.grid(row=0, column=0, sticky='nsew', padx=(10,0))
        self.tree_frame.grid_columnconfigure(0, weight=10)
        self.tree_frame.grid_columnconfigure(1, weight=0)
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(1, weight=0)

        # Create the Treeview
        self.tree = ttk.Treeview(self.tree_frame, columns=("Item", "Price","Ratio","#","Profit","Vendor","Location","Time","#9","#10","#11","#12"),show='headings')
        self.tree.heading("Item", text="Item", command=lambda _col="Item",_col2 ="Ratio": self.sort_column_tuple(_col, _col2, False, sort_key_tuple))
        self.tree.heading("Price", text="Price")
        self.tree.heading("Ratio", text="%", command=lambda _col="Ratio",_col2 ="Time": self.sort_column_tuple(_col, _col2, False, sort_key_tuple))
        self.tree.heading("#", text="#")
        self.tree.heading("Profit", text="Profit", command=lambda _col="Profit",_col2 ="Time": self.sort_column_tuple(_col, _col2, False, sort_key_tuple))
        self.tree.heading("Vendor", text="Vendor", command=lambda _col="Vendor",_col2 ="Item": self.sort_column_tuple(_col, _col2, False, sort_key_tuple))
        #self.tree.heading("Location", text="Location", command=lambda _col="Location",_col2 ="Ratio": self.sort_column_tuple(_col, _col2, False, sort_key_tuple))
        self.tree.heading("Location", text="Location", command=self.sort_tree_density)
        self.tree.heading("Time", text="Time", command=lambda _col="Time",_col2 ="Ratio": self.sort_column_tuple(_col, _col2, False, sort_key_tuple))
        self.tree.column("Item", width=300)
        self.tree.column("Price", width=100)
        self.tree.column("Ratio", width=25)
        self.tree.column("#", width=15)
        self.tree.column("Profit", width=70)
        self.tree.column("Vendor", width=125)
        self.tree.column("Location", width=205) 
        self.tree.column("Time", width=100)
        self.tree.column("#9", width=0,stretch=False)
        self.tree.column("#10", width=0,stretch=False)
        self.tree.column("#11", width=0,stretch=False)
        self.tree.column("#12", width=0,stretch=False)
        self.tree.configure(height=20)
        self.tree.grid(row=0, column=0,sticky='nsew')
        self.tree.tag_configure("mistake", background="#D3D3D3")
        self.tree.tag_configure("ultra", background="#FF0000")
        self.tree.tag_configure("high", background="#FFA500")
        self.tree.tag_configure("med", background="#FFD700")
        self.tree.tag_configure("low", background="#00FF00")
        self.tree.tag_configure("verylow", background="#00BFFF")
        self.tree.tag_configure("base", background="#ADD8E6")
        self.tree.bind("<Button-1>", self.on_treeview_click)

        # Create context menu
#        self.context_menu = tk.Menu(self.root, tearoff=0)
#        self.context_menu.add_command(label='Insert To Sales History', command=self.on_treeview_select)
        #self.context_menu.add_command(label='Option 2', command=lambda: print("Option 2 clicked"))
        # Bind right-click event
        self.tree.bind('<Button-3>', self.on_treeview_right_click)

        # Create a Scrollbar and associate it with the Tree widget
        self.scrollbar = tk.Scrollbar(self.tree_frame,orient='vertical', command=self.tree.yview)
        self.scrollbar.grid(row=0, column=1, sticky='ns')
        self.tree.config(yscrollcommand=self.scrollbar.set)

        self.config_frame = tk.Frame(self.root)#,bg='green')
        self.config_frame.grid(row=0, column=2,pady=10,padx=(0,10),sticky='nesw')
        self.config_frame.grid_rowconfigure(0, weight=1)
        self.config_frame.grid_rowconfigure(1, weight=1)
        self.config_frame.grid_columnconfigure(0, weight=1)

        # Checkbox Panel
        self.checkbox_frame = tk.Frame(self.config_frame)#,bg='blue')
        self.checkbox_frame.grid(row=0, column=0,pady=10,padx=(0,10),sticky='nesw')
        # self.checkbox_frame.grid_columnconfigure(0, weight=1)
        # self.checkbox_frame.grid_columnconfigure(1, weight=1)
        #self.checkbox_frame.grid_rowconfigure(0, weight=1)
        #self.checkbox_frame.grid_rowconfigure(1, weight=1)
        self.check_core_var = tk.BooleanVar(self.root)
        self.check_extract_var = tk.BooleanVar(self.root)
        self.check_distil_var = tk.BooleanVar(self.root)
        self.check_tmaps_var = tk.BooleanVar(self.root)
        self.check_skillscrolls_var = tk.BooleanVar(self.root)
        self.check_chainlinks_var = tk.BooleanVar(self.root)
        self.check_hp_misc_var = tk.BooleanVar(self.root)
        self.check_lp_misc_var = tk.BooleanVar(self.root)
        self.check_cloth_var = tk.BooleanVar(self.root)
        self.check_dye_var = tk.BooleanVar(self.root)
        self.check_ingot_var = tk.BooleanVar(self.root)
        self.check_board_var = tk.BooleanVar(self.root)
        self.check_leather_var = tk.BooleanVar(self.root) 

        self.checkbox_core_search = ttk.Checkbutton(self.checkbox_frame, text="Search Cores", variable=self.check_core_var)
        self.checkbox_core_search.grid(row=0, column=0,sticky='ew', padx=(27,0),columnspan=2)
        self.check_distil_search = ttk.Checkbutton(self.checkbox_frame, text="Search Extracts", variable=self.check_extract_var)
        self.check_distil_search.grid(row=1, column=0,sticky='ew', padx=(27,0),columnspan=2)
        self.check_extract_search = ttk.Checkbutton(self.checkbox_frame, text="Search Distils", variable=self.check_distil_var)
        self.check_extract_search.grid(row=2, column=0,sticky='ew', padx=(27,0),columnspan=2)
        self.check_tmaps_search = ttk.Checkbutton(self.checkbox_frame, text="Search Tmaps", variable=self.check_tmaps_var)
        self.check_tmaps_search.grid(row=3, column=0,sticky='ew', padx=(27,0),columnspan=2)
        self.check_skillscrolls_search = ttk.Checkbutton(self.checkbox_frame, text="Search Skill Scrolls", variable=self.check_skillscrolls_var)
        self.check_skillscrolls_search.grid(row=4, column=0,sticky='ew', padx=(27,0),columnspan=2)
        self.check_chainlinks_search = ttk.Checkbutton(self.checkbox_frame, text="Search Chain Links", variable=self.check_chainlinks_var)
        self.check_chainlinks_search.grid(row=5, column=0,sticky='ew', padx=(27,0),columnspan=2)

        self.check_lp_misc_search = ttk.Checkbutton(self.checkbox_frame, text="Search LP Misc", variable=self.check_lp_misc_var)
        self.check_lp_misc_search.grid(row=6, column=0,sticky='ew', padx=(27,0),columnspan=2)
        self.check_hp_misc_search = ttk.Checkbutton(self.checkbox_frame, text="Search HP Misc", variable=self.check_hp_misc_var)
        self.check_hp_misc_search.grid(row=7, column=0,sticky='ew', padx=(27,0),columnspan=2)

        self.check_cloth_search = ttk.Checkbutton(self.checkbox_frame, text="Search Cloth", variable=self.check_cloth_var)
        self.check_cloth_search.grid(row=8, column=0,sticky='ew', padx=(27,0),columnspan=2)
        self.check_dye_search = ttk.Checkbutton(self.checkbox_frame, text="Search Dyes", variable=self.check_dye_var)
        self.check_dye_search.grid(row=9, column=0,sticky='ew', padx=(27,0),columnspan=2)
        self.check_ingot_search = ttk.Checkbutton(self.checkbox_frame, text="Search Ingots", variable=self.check_ingot_var)
        self.check_ingot_search.grid(row=10, column=0,sticky='ew', padx=(27,0),columnspan=2)
        self.check_board_search = ttk.Checkbutton(self.checkbox_frame, text="Search Boards", variable=self.check_board_var)
        self.check_board_search.grid(row=11, column=0,sticky='ew', padx=(27,0),columnspan=2)
        self.check_leather_search = ttk.Checkbutton(self.checkbox_frame, text="Search Leather", variable=self.check_leather_var)
        self.check_leather_search.grid(row=12, column=0,sticky='ew', padx=(27,0),columnspan=2)
        self.btn_hp_checkboxes = ttk.Button(self.checkbox_frame, text="HP", command=self.set_hp_variables)
        self.btn_hp_checkboxes.grid(row=13, column=0, sticky='ew', padx=(0,2), pady=(10,2))
        self.btn_lp_checkboxes = ttk.Button(self.checkbox_frame, text="LP", command=self.set_lp_variables)
        self.btn_lp_checkboxes.grid(row=13, column=1, sticky='ew', padx=(2,0), pady=(10,2))
        self.btn_all_checkboxes = ttk.Button(self.checkbox_frame, text="All", command=self.set_all_checkboxes)
        self.btn_all_checkboxes.grid(row=14, column=0, sticky='ew', padx=(0,2), pady=(2,5))
        self.btn_none_checkboxes = ttk.Button(self.checkbox_frame, text="None", command=self.set_none_checkboxes)
        self.btn_none_checkboxes.grid(row=14, column=1, sticky='ew', padx=(2,0), pady=(2,5))

        # Combobox Panel
        self.combobox_frame = tk.Frame(self.config_frame)#,bg='yellow')
        self.combobox_frame.grid(row=1,column=0)
        self.combobox_frame.grid_columnconfigure(0, weight=0)
        self.combobox_frame.grid_rowconfigure(0, weight=1)
        self.combobox_frame.grid_rowconfigure(1, weight=1)
        self.options = ["30 Seconds", "1 Minute", "5 Minutes", "30 Minutes", "1 Hour", "All Time"]
        self.search_combobox_timeframe = tk.StringVar(self.root)
        self.search_combobox_timeframe.set("30 Seconds")
        self.label_timeframe = ttk.Label(self.combobox_frame,text='Time Frame:')
        self.label_timeframe.grid(row=0,column=0,pady=(5,0))
        self.combobox = ttk.Combobox(self.combobox_frame, values=self.options, textvariable=self.search_combobox_timeframe, state='readonly')
        self.combobox.grid(row=1, column=0,sticky='nsew')

        # Radio Panel
        self.radio_frame = tk.Frame(self.config_frame)#,bg='yellow')
        self.radio_frame.grid(row=2, column=0)
        self.radio_frame.grid_columnconfigure(0, weight=0)
        self.radio_frame.grid_columnconfigure(1, weight=0)
        self.radio_frame.grid_rowconfigure(0, weight=1)
        self.radio_frame.grid_rowconfigure(1, weight=1)
        self.radio_frame.grid_rowconfigure(2, weight=1)
        self.radio_frame.grid_rowconfigure(3, weight=1)
        self.radio_frame.grid_rowconfigure(4, weight=1)
        self.radio_frame.grid_rowconfigure(5, weight=1)
        self.radio_frame.grid_rowconfigure(6, weight=1)
        self.radio_frame.grid_rowconfigure(7, weight=1)
        self.radio_frame.grid_rowconfigure(8, weight=1)
        self.radio_frame.grid_rowconfigure(9, weight=1)
        self.radio_frame.grid_rowconfigure(10, weight=1)
        self.radio_frame.grid_rowconfigure(11, weight=1)
        self.search_pricedepth = tk.IntVar(self.root)
        self.search_pricedepth.set(1)
        self.search_sortmode = tk.IntVar(self.root)
        self.search_sortmode.set(2)

        self.label_pricedepth = ttk.Label(self.radio_frame,text='Price Depth:')
        self.label_pricedepth.grid(row=0,column=0,columnspan=2,pady=(5,0))
        self.radio3 = ttk.Radiobutton(self.radio_frame, text="Show Deals", variable=self.search_pricedepth, value=1)
        self.radio3.grid(row=1, column=0,sticky='w')
        self.radio4 = ttk.Radiobutton(self.radio_frame, text="Show All", variable=self.search_pricedepth, value=2)
        self.radio4.grid(row=1, column=1,sticky='w')
        self.cutoff_threshold = tk.DoubleVar(self.root)
        self.cutoff_slider = tk.Scale(self.radio_frame, from_=0.01, to=1.0, orient='horizontal', resolution=0.01, variable=self.cutoff_threshold)
        self.cutoff_slider.grid(row=2,column=0,columnspan=2,sticky='ew')
        self.cutoff_slider.set(0.93)
        # self.label_sortmode = ttk.Label(self.radio_frame,text='Sort Mode:')
        # self.label_sortmode.grid(row=3,column=0,columnspan=2,pady=(5,0))
        # self.radio5 = ttk.Radiobutton(self.radio_frame, text="Indexed", variable=self.search_sortmode, value=1)
        # self.radio6 = ttk.Radiobutton(self.radio_frame, text="Best Ratio", variable=self.search_sortmode, value=2)
        # self.radio5.grid(row=4, column=0,sticky='w')
        # self.radio6.grid(row=4, column=1,sticky='w')
        self.btn_assmon = ttk.Button(self.radio_frame, text="AssMonGUI", command=self.open_assmon)
        self.btn_assmon.grid(row=4, column=0, sticky='ew', padx=10, pady=(15,5), columnspan=2)
        self.btn_locations = ttk.Button(self.radio_frame, text="Hotkeys", command=self.open_hotkey_help)
        self.btn_locations.grid(row=5, column=0, sticky='ew', padx=10, pady=5, columnspan=2)
        self.btn_visit_web = ttk.Button(self.radio_frame, text="Open Website", command=lambda: webbrowser.open("https://outlandmalls.com/"))
        self.btn_visit_web.grid(row=6, column=0, sticky='ew', padx=10, pady=5, columnspan=2)
        self.btn_open_folder = ttk.Button(self.radio_frame, text="Open Folder", command=lambda: os.system('explorer "C:\\Program Files (x86)\\Ultima Online Outlands\\ClassicUO\\Data\\Client\\JournalLogs"'))
        self.btn_open_folder.grid(row=7, column=0, sticky='ew', padx=10, pady=5, columnspan=2)
        self.btn_inventory = ttk.Button(self.radio_frame, text="Inventory")
        self.btn_inventory.bind("<Button-1>", lambda event: self.read_db_current_inventory(True))
        self.btn_inventory.bind("<Control-Button-1>", lambda event: self.read_db_current_inventory(False))
        self.btn_inventory.grid(row=8, column=0, sticky='ew', padx=10, pady=5, columnspan=2)
        self.btn_recent_sales = ttk.Button(self.radio_frame, text="Sales", command=self.read_db_total_sales) # read_db_recent_sales
        self.btn_recent_sales.grid(row=9, column=0, sticky='ew', padx=10, pady=5, columnspan=2)
        self.btn_post_journal = ttk.Button(self.radio_frame, text="POST", command=self.PostJournalLog)
        self.btn_post_journal.grid(row=10, column=0, sticky='ew', padx=10, pady=5, columnspan=2)

        # Floor Panel
        self.button_frame = tk.Frame(self.root)
        self.button_frame.grid(row=1, column=0,pady=10)
        self.button_frame.columnconfigure(0,weight=1)
        self.button_frame.columnconfigure(1,weight=1)
        self.btn_start = ttk.Button(self.button_frame, text="OutlandMalls", command=self.ScrapeOutlandMall)
        self.btn_start.grid(row=0, column=1, sticky='ew', padx=10)
        self.btn_reset = ttk.Button(self.button_frame, text="Journal Log", command=self.ParseMostRecentJournalLog)
        self.btn_reset.grid(row=0, column=0, sticky='ew', padx=10)

        # Status Panel
        self.status_frame = tk.Frame(self.root)
        self.status_frame.grid(row=1, column=2,sticky='nesw')
        self.status_frame.grid_rowconfigure(0, weight=1)
        self.status_frame.grid_rowconfigure(1, weight=1)
        self.status_frame.grid_columnconfigure(0, weight=1)
        self.status_frame.grid_propagate(False)
        self.status_label = tk.Label(self.status_frame, text='Status:')
        self.status_label.grid(row=0,column=0,pady=(3,0))
        self.status_var = tk.StringVar(self.root)
        self.update_label = tk.Label(self.status_frame, textvariable=self.status_var, font=("Arial", 10))
        self.update_label.grid(row=1,column=0,pady=(0,10))
        
        self.set_all_checkboxes()
        self.queue_append = queue.Queue()
        self.queue_emptySort_flag = False
        self.queue_emptyFastSort_flag = False
        self.queue_daemon()
        self.queue_append.put("Idle") 
    
    def open_assmon(self):
        assmon_gui = AssMonGui(self.root)
        assmon_gui.start_monitoring()

    #TODO add discord notif detector? Might be better to just interval scan
    # def detect_notification(self): 
    #     def images_are_equal(img1, img2):
    #         arr1 = np.array(img1)
    #         arr2 = np.array(img2)
    #         return np.array_equal(arr1, arr2)
    #     def send_udp_message(message, target_ip, target_port):
    #         sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #         sock.sendto(message.encode(), (target_ip, target_port))
    #     x, y, width, height = 715, 1150, 782, 135  # Update these values
    #     time_stamp = time.time()
    #     initial_screenshot = pyautogui.screenshot(region=(x, y, width, height))
    #     while True:
    #         new_screenshot = pyautogui.screenshot(region=(x, y, width, height))
    #         if time.time() > time_stamp and not images_are_equal(new_screenshot, initial_screenshot):
    #             time_stamp = time.time() + 5
    #             send_udp_message("Triggered", "10.0.0.61", 8080)  # Update IP and port
    #         initial_screenshot = new_screenshot
    #         time.sleep(0.2)

    def udp_daemon(self,port=8080):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', port))
        while True:
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            print("Received message:", data.decode())

    def summon_udp_daemon(self):
        monitor_thread = threading.Thread(target=self.udp_daemon)
        monitor_thread.start()

    def set_hp_variables(self,event=None):
        self.cutoff_threshold.set(0.90)
        self.search_pricedepth.set(1)
        self.search_combobox_timeframe.set("1 Minute")
        self.check_core_var.set(False)
        self.check_extract_var.set(False)
        self.check_distil_var.set(False)
        self.check_tmaps_var.set(True)
        self.check_skillscrolls_var.set(False)
        self.check_chainlinks_var.set(False)
        self.check_lp_misc_var.set(False)
        self.check_hp_misc_var.set(True)
        self.check_cloth_var.set(False)
        self.check_dye_var.set(False)
        self.check_ingot_var.set(False)
        self.check_board_var.set(False)
        self.check_leather_var.set(False)

    def set_lp_variables(self,event=None):
        self.cutoff_threshold.set(0.75)
        self.search_pricedepth.set(1)
        self.search_combobox_timeframe.set("5 Minutes")
        self.check_core_var.set(True)
        self.check_extract_var.set(True)
        self.check_distil_var.set(True)
        self.check_tmaps_var.set(False)
        self.check_skillscrolls_var.set(True)
        self.check_chainlinks_var.set(True)
        self.check_lp_misc_var.set(True)
        self.check_hp_misc_var.set(False)
        self.check_cloth_var.set(True)
        self.check_dye_var.set(True)
        self.check_ingot_var.set(True)
        self.check_board_var.set(True)
        self.check_leather_var.set(True)

    def set_all_checkboxes(self,event=None):
        self.check_core_var.set(True)
        self.check_extract_var.set(True)
        self.check_distil_var.set(True)
        self.check_tmaps_var.set(True)
        self.check_skillscrolls_var.set(True)
        self.check_chainlinks_var.set(True)
        self.check_lp_misc_var.set(True)
        self.check_hp_misc_var.set(True)
        self.check_cloth_var.set(True)
        self.check_dye_var.set(True)
        self.check_ingot_var.set(True)
        self.check_board_var.set(True)
        self.check_leather_var.set(True)

    def set_none_checkboxes(self,event=None):
        self.check_core_var.set(False)
        self.check_extract_var.set(False)
        self.check_distil_var.set(False)
        self.check_tmaps_var.set(False)
        self.check_skillscrolls_var.set(False)
        self.check_chainlinks_var.set(False)
        self.check_lp_misc_var.set(False)
        self.check_hp_misc_var.set(False)
        self.check_cloth_var.set(False)
        self.check_dye_var.set(False)
        self.check_ingot_var.set(False)
        self.check_board_var.set(False)
        self.check_leather_var.set(False)

    def scrape_vendor_updates(self):
        headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        cookie = {"app": user_config["outlands_cookie"]}
        
        url = "https://outlandmalls.com/vendors/"
        response = requests.get(url, headers=headers,cookies=cookie)
        if response.status_code != 200:
            print(f"scrape_vendor_updates: Failed to retrieve the webpage: {url}. Status code: {response.status_code}")
            self.queue_append.put('Vendor Page Failed')
            return
        self.queue_append.put(f"Scanning user_config[")
        soup = BeautifulSoup(response.content, 'lxml')
        if not soup:
            self.queue_append.put('Vendor Page Soup Failed')
            return
        table = soup.find_all('table')[1]
        rows = table.tbody.find_all('tr')
        loc_hash_set = set() #used to filter out duplicate locations
        found_locations = []
        for row in rows:
            cells = row.find_all('td')
            vendor_name_cell = cells[1]
            update_time_cell = cells[2]
            location_cell = cells[3]
            update_time_string = update_time_cell.text
            location_string = location_cell.text
            vendor_name_string = vendor_name_cell.text
            if location_string in loc_hash_set:
                continue
            loc_hash_set.add(location_string)
            found_locations.append((update_time_string,location_string.split(', '),vendor_name_string))
        out_arr = []
        for location_name, tuple_loc in my_locations.items():
            x1 = int(tuple_loc[0])
            y1 = int(tuple_loc[1])
            closest = None
            min_distance = 20
            min_time = 1000000
            for update_time, list_loc,vendor_name in found_locations:
                x2, y2 = map(int,list_loc)
                distance = get_distance(x1,y1,x2,y2)
                if distance > min_distance:
                    continue
                sec_since_scan = get_vendor_seconds_from_string(update_time)
                if not sec_since_scan:
                    sec_since_scan = 1000000
                if sec_since_scan < min_time:
                    min_time = sec_since_scan
                    closest = (update_time,x2,y2,vendor_name)
            scan_time_string = closest[0] if closest else 'Not Scanned'
            scan_x = closest[1] if closest else '0'
            scan_y = closest[2] if closest else '0'
            scan_name = closest[3] if closest else 'No Name!'
            out_arr.append((location_name,scan_time_string,min_time,scan_x,scan_y,scan_name))
        out_arr.sort(key=lambda x:x[2],reverse=True)
        new_window = tk.Toplevel(self.root)
        new_window.wm_attributes("-topmost", 1)
        new_window.title("Results")
        self.scrollbar = tk.Scrollbar(new_window, orient="vertical")
        listbox = tk.Listbox(new_window, yscrollcommand=self.scrollbar.set, width=60, height=20)
        self.scrollbar.config(command=listbox.yview)
        self.scrollbar.pack(side="right", fill="y")
        listbox.pack(side="left", fill="both", expand=True)
        for locName,scanString,minTime,x,y,name in out_arr:
            result = f"{locName}: {scanString}: {x},{y}"
            listbox.insert(tk.END, result)
        self.queue_append.put("Idle")

    def open_hotkey_help(self):
        help_string = """MallScraper Window:
    [Enter]:                Search most recent journal log

    [Ctrl + Enter]:         Full scrape of OutlandMalls

    [Ctrl + Alt + Enter]:   Fast scrape of OutlandMalls

    [3]:                    Check all category checkboxes

    [4]:                    Uncheck all category checkboxes

    [F1]:                   Sort list by time:location:ratio

    [Ctrl + F1]:            Delete most recent journal log

    [Left click on list]:   Clear clipboard and append Outlands buy script for that item

    [Right click on list]:  Append Outlands buy script to previous clipboard contents


Game/Assistant Window:
    [Ctrl + Alt + C]:       If game client or assistant window is focused, pastes your clipboard to 
                            the preset script ("aaaTemptScript") in the assistant and runs it in game.
                            Do not click your mouse for a short duration as the script switches windows

    [Ctrl + Alt + `]:       If game client window is focused, focuses the assistant for that character and vice versa

    [Alt + Shift + `]:      Focuses scraper window"""
        new_window = tk.Toplevel(self.root)
        new_window.wm_attributes("-topmost", 1)
        new_window.geometry("1024x512")
        new_window.title("Hotkeys")
        self.scrollbar = tk.Scrollbar(new_window, orient="vertical")
        textbox = tk.Text(new_window, yscrollcommand=self.scrollbar.set, width=160, height=50, font=("Consolas", 11))
        self.scrollbar.config(command=textbox.yview)
        self.scrollbar.pack(side="right", fill="y")
        textbox.pack(side="left", fill="both", expand=True)
        textbox.insert(tk.END, help_string)

    def parse_combobox(self):
        option = self.search_combobox_timeframe.get()
        option_dict = {
            '30 Seconds': 30,
            '1 Minute': 60,
            '5 Minutes': 300,
            '30 Minutes': 1800,
            '1 Hour': 3600,
            'All Time': 'All Time'
        }
        return option_dict[option]
    
    def on_treeview_modded_click(self,event):
        print("Ctrl and/or Shift detected")

    def on_backtick_press(self,event):
        interface_data = self.get_interface_data_from_tree()
        squozen_data = self.squeeze_interface_data(interface_data)
        razor_script = self.build_razor_script_from_squeezed_data(squozen_data)
        print(razor_script)

    def get_interface_data_from_tree(self):
        selected_rows = self.get_selected_items()
        interface_data = []
        my_fetched_locations = my_locations.items()
        for row in selected_rows:
            location_raw = row[6].split('\t')
            location_split = location_raw[0].split(',')
 
            x1, y1 = map(int,location_split)
            closest_location = min(my_fetched_locations, key=lambda loc: get_distance_squared(x1, y1, loc[1][0], loc[1][1]))
            location_name = closest_location[0]
            if my_locations.get(location_name) is None:
                print(f"on_backtick_press: No match in dictionary for location name: {location_name}")
                continue

            value_to_copy_raw = row[8]
            serial_match = re.search(r'\?(\d+)(?:\?(\d+))(?:\?(\d+))?#', value_to_copy_raw) #'https://www.exploreoutlands.com/?471890?1251126567?312345125#pos:869,1381,13'
            if not serial_match:
                serial_match = re.search(r'\?(\d+)\?', value_to_copy_raw)
            vendor_serial = serial_match.group(1) if serial_match else 0
            item_id = serial_match.group(2) if serial_match else 0
            total_cost = int(float(row[10]))
            total_cost_str = format_with_commas(total_cost)
            item_description = row[11]
            item_description_compare = f"Price: {total_cost_str} {item_description}"

            interface_data.append((location_name, vendor_serial, item_id, item_description_compare))
        return interface_data
    
    def squeeze_interface_data(self,interface_data):
        vendors_by_location = defaultdict(list)
        item_descriptions = []
        vendors = 0
        items = 0
        for location_name, vendor_serial, item_id, item_description_compare in interface_data:
            if vendor_serial not in vendors_by_location[location_name]:
                vendors_by_location[location_name].append(vendor_serial)
                vendors += 1
            if item_description_compare not in item_descriptions:
                item_descriptions.append(item_description_compare)
                items += 1
        
        print(f"Locations: {len(vendors_by_location.keys())}\nVendors: {vendors}\nItems: {items}")
        return vendors_by_location, item_descriptions

    def build_razor_script_from_squeezed_data(self,squeezed_interface_data):
        script_string = '''removelist "itemDescriptions"
createlist "itemDescriptions"
@setvar! "timeout" 250'''

        vendors_by_location, item_descriptions = squeezed_interface_data

        for item_description in item_descriptions:
            script_string += f'''
pushlist "itemDescriptions" "{item_description}"'''
            
        for location_name, vendors in vendors_by_location.items(): #recall to locations
            location_data = my_locations[location_name][2]
            location_character = location_data[0]
            book_hue = location_data[1]
            location_recall_code = location_data[2]
            location_button_code = location_data[3]
            for vendor_serial in vendors: #open vendors
                script_string += f"""
clearignore
if find {vendor_serial} ground any any 20
    overhead "● ▼▼ HERE ▼▼ ●" 88 {vendor_serial}
else
    @setvar! "myTome" 0
    for 3
        if findtype "runetome" backpack {book_hue} as "tome"
            @setvar! "myTome" "tome"
            break
        endif
        dclick backpack
        wait "timeout"
    endfor
    if "myTome" = 0
        overhead "NO TOME" 33
        stop
    endif
    if findtype "bank deposit safe" ground any any 14 as "safe"
        getlabel "safe" "desc"
        overhead "desc"
        sysmsg "desc"
    endif
    overhead "recalling to spot {location_name} in {location_character}'s book" 1159
    dclick "myTome"
    waitforgump 167090027 1000
    if not gumpexists 167090027
        dclick "myTome"
        waitforgump 167090027 2000
    endif
    gumpresponse {location_recall_code} 167090027
    waitforgump 167090027 2000
    gumpresponse {location_button_code} 167090027
    wait 500
endif
while not dead
    if find {vendor_serial} ground any any 20
        overhead "● ▼▼ HERE ▼▼ ●" 88 {vendor_serial}
        if findtype 3701 {vendor_serial} 0 0 0 as "mainBackpack"
            @setvar! "searching" 1
            @ignore "mainBackpack"
            @setvar! "currentContainer" "mainBackpack"
            while "searching" == 1
                @setvar! "searching" 0
                dclick "currentContainer"
                wait "timeout"
                if hidden
                else
                    skill "hiding"
                endif
                while findtype 7956 "mainBackpack" as "decoy"
                    @ignore "decoy"
                endwhile 
                while findtype 24434|5356|576|1489|1496|1763|2207|2213|2219|2323|2409|2413|2418|2419|2425|2463|2594|2595|2596|2597|2726|2807|2845|3091|3092|3108|3203|3204|3206|3207|3211|3214|3215|3217|3219|3220|3221|3222|3223|3224|3225|3226|3227|3228|3229|3230|3231|3232|3233|3234|3235|3237|3238|3239|3240|3241|3242|3243|3255|3256|3257|3258|3259|3262|3263|3268|3271|3272|3273|3288|3302|3305|3306|3307|3308|3309|3310|3311|3312|3313|3314|3320|3323|3326|3329|3332|3340|3341|3342|3343|3344|3345|3346|3347|3348|3365|3366|3367|3368|3370|3372|3374|3376|3377|3381|3383|3391|3392|3492|3496|3519|3520|3527|3528|3529|3530|3531|3568|3569|3591|3637|3638|3639|3640|3641|3642|3656|3657|3658|3659|3699|3700|3713|3714|3715|3717|3718|3719|3720|3721|3722|3735|3736|3737|3738|3740|3741|3742|3762|3763|3764|3773|3786|3787|3788|3789|3790|3791|3792|3793|3794|3827|3828|3829|3830|3831|3832|3833|3834|3835|3836|3837|3838|3839|3840|3841|3842|3843|3844|3856|3859|3861|3862|3865|3873|3877|3878|3885|3892|3897|3898|3907|3908|3909|3910|3911|3912|3913|3914|3915|3916|3917|3918|3919|3920|3921|3922|3932|3933|3934|3935|3936|3937|3938|3939|3985|3999|4025|4026|4201|4225|4226|4248|4249|4250|4251|4252|4253|4254|4255|4256|4257|4258|4259|4277|4656|4831|5039|5040|5041|5042|5043|5044|5045|5046|5049|5050|5056|5059|5060|5061|5063 "mainBackpack" as "foundItem"
                    @ignore "foundItem"
                    getlabel "foundItem" "desc"
                    if inlist "itemDescriptions" "desc"
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 200
                    endif
                endwhile
                while findtype 5070|5074|5075|5076|5078|5085|5089|5090|5101|5103|5105|5106|5112|5113|5114|5115|5116|5117|5118|5119|5120|5121|5122|5123|5124|5125|5126|5127|5129|5131|5132|5135|5138|5139|5142|5143|5144|5146|5176|5177|5178|5179|5180|5181|5182|5183|5184|5185|5186|5187|5188|5189|5190|5191|5201|5203|5204|5205|5207|5355|5359|5360|5361|5362|5363|5364|5365|5366|5370|5373|5374|5376|5377|5378|5379|5416|5418|5421|5453|5534|5645|5661|5662|5899|5900|5901|5902|5903|5904|5905|5906|5981|5982|5983|5984|5985|5986|5987|5988|6039|6049|6187|6193|6238|6464|7026|7027|7029|7031|7033|7034|7035|7107|7109|7116|7127|7128|7129|7130|7131|7132|7139|7140|7141|7142|7143|7144|7145|7146|7147|7148|7149|7150|7151|7152|7153|7154|7155|7156|7157|7158|7159|7160|7161|7162|7169|7170|7173|7175|7177|7179|7181|7369|7370|7371|7372|7377|7378|7379|7380|7381|7382|7383|7384|7385|7610|7732|7866|7947|8012|8031|8032|8040|8041|8042|8043|8044|8417|8438|8454|8455|8478|8479|8480|8481|8484|8501|8502|8503|8750|8751|8752|8753|8786|8787|8826|8901|9006|9010|9076|9078|9079|9253|9917|10136|10245|10247|10324|10527|10827|11225|11227|11229|11231|11552|11761|11762|11763|11764|11881|11882|11883|11884|11885|11886|11887|11888|11889|11890|11891|11893|11895|11897|11942|12215|12282|12320|12321|12322|12323|12324|12686|13278|13290|13291|13292|13297|13298|13299 "mainBackpack" as "foundItem"
                    @ignore "foundItem"
                    getlabel "foundItem" "desc"
                    if inlist "itemDescriptions" "desc"
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 200
                    endif
                endwhile
                while findtype 13300|13301|13305|13307|13308|13309|13310|13311|13312|13313|13314|13316|13318|13319|13320|13321|13328|13330|13335|13336|13591|13597|13613|14428|14442|14444|14448|14450|14451|14454|14456|14458|14470|14484|14490|14496|14506|14512|14514|14520|14522|14530|14536|14538|14542|14544|14562|14568|14571|14574|14594|15178|15293|15294|15295|15296|15297|15298|15577|15580|15635|15638|16898|17081|17083|17087|17686|18075|18082|18083|18085|18087|18218|18233|18282|18283|18400|18652|18653|18658|18704|19199|19226|19227|19228|19229|19230|19231|19232|19233|19234|19235|19236|19237|19238|19239|19240|19241|19242|19243|19244|19245|19246|19247|19248|19249|19250|19251|19252|19253|19254|19255|19256|19370|19372|19403|19508|19512|19513|19520|19521|19522|19524|19525|19528|19529|19532|19582|19583|19785|19793|19795|19799|19805|19812|19814|19821|20006|20008|20010|20012|20014|20016|20309|20374|20375|20376|20377|20378|20379|20381|20383|20384|20385|20391|20392|20466|20467|20495|20496|20499|20502|21387|21397|21398|21399|21400|21401|21402|21403|21404|21405|21780|21781|21783|21784|21785|21786|21787|21788|21789|21790|21791|21797|21798|21799|21800|21801|21803|21804|21805|21806|21807|21808|21809|21810|21814|21818|21824|21826|21827|21828|21829|21830|21831|21835|21836|21838|21840|21841|21842|21843|21844|21845|21847|21848|21849|21852|21853|21856|21859|21860|21861|21862|21863|21864|21865|21866|21867|21868|21870|21871|21872|21873|21874|21875|21876|21877|21878|21879|21880|21881|21882|21883|21884|21885|21886|21889|21891|21893 "mainBackpack" as "foundItem"
                    @ignore "foundItem"
                    getlabel "foundItem" "desc"
                    if inlist "itemDescriptions" "desc"
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 200
                    endif
                endwhile
                while findtype 21894|21895|21896|21897|21898|21899|21901|21902|21904|21905|21906|21907|21908|21909|21911|21917|21918|21921|21923|21924|21925|21926|21927|21929|21931|21933|21934|21935|21936|21937|21938|21939|21940|21942|21943|21944|21945|21947|21948|21949|21950|21951|21953|21954|21956|21957|21960|21962|21963|21964|21969|21978|21981|21988|21996|21997|21998|21999|22151|22152|22153|22154|22155|22157|22158|22163|22164|22165|22166|22167|22168|22169|22170|22171|22172|22173|22174|22175|22177|22178|22179|22180|22181|22182|22183|22184|22185|22186|22187|22188|22189|22190|22191|22192|22193|22194|22195|22196|22197|22199|22261|22264|22272|22285|22286|22287|22288|22289|22290|22291|22292|22293|22294|22295|22296|22297|22298|22326|22336|22417|22418|22419|22420|22421|22422|22423|22426|22427|22428|22429|22430|22431|22432|22433|22434|22435|22436|22437|22438|22439|22440|22441|22442|22443|22444|22445|22449|22451|22453|22455|22456|22489|22717|22845|23009|23034|23035|23048|23049|23050|23051|23052|23774|23867|23868|23869|23870|23871|23872|23873|23874|23875|23876|23877|23878|23879|23880|23881|23882|23883|23884|23885|23886|23887|23889|23890|23891|23892|23893|23894|23895|23899|23900|23901|23902|23903|23904|23905|23906|23907|23908|23909|23910|23953|23954|23955|23956|23996|23997|24175|24179|24181|24182|24183|24184|24187|24188|24190|24191|24193|24195|24196|24197|24199|24208|24246|24345|24382|24383|24384|24385|24386|24387|24388|24389|24390|24391|24392|24393|24394|24395|24396|24397|24398|24399|24400|24401|24402|24403|24404 "mainBackpack" as "foundItem"
                    @ignore "foundItem"
                    getlabel "foundItem" "desc"
                    if inlist "itemDescriptions" "desc"
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 200
                    endif
                endwhile
                while findtype 24405|24406|24407|24408|24409|24410|24411|24412|24413|24414|24415|24416|24417|24418|24419|24420|24421|24422|24423|24424|24425|24426|24427|24428|24429|24430|24431|24432|24433|25359|25490|25526|25527|25529|25531|25533|25535|25538|25569|25581|25583|25647|25670|25730|25750|25758|25759|26640|26664|26669|26670|26671|26672|26688|26689|26693|26700|26701|26719|26720|26721|26724|26732|26734|26735|26736|26737|27561|27562|27563|27564|27565|27577|27580|27584|27611|27612|27640|27642|27666|27668|28237|28238|28263|28314|28322|28341|28344|28350|28376|28410|28760|28765|28768|28775|28795|28799|28803|28879|28880|28881|28883|28885|28908|28909|28910|28911|28924|28993|28994|28995|29001|29012|29024|29025|29026|29027|29028|29029|29030|29031|29032|29033|29034|29035|29036|29037|29038|29040|29045|29064|29103|29104|29105|29106|29107|29108|29142|29343|29345|29350|29352|29354|29355|29382|29421|29425|29428|29430|29431|29463|29495|29497|29498|29502|29773|29774|29868|30561|30562|30563|30564|30565|30566|30567|30568|30573|30574|30575|30576|30577|30578|30579|30580|30582|30583|30585|30586|30587|30588|30589|30590|30591|30592|30596|30599|30601|30602|30603|30604|30608|30609|30610|30611|30612|30613|30614|30615|30617|30618|30621|30622|30623|30624|30625|30626|30627|30628|30629|30630|30631|30632|30633|30634|30635|30636|30637|30638|30639|30640|30641|30642|30643|30644|30645|30646|30647|30648|30649|30650|30651|30652|30653|30655|30657|30658|30659|30660|30661|30662|30663|30765|30766|30767|30768|30769|30770|30771|30772 "mainBackpack" as "foundItem"
                    @ignore "foundItem"
                    getlabel "foundItem" "desc"
                    if inlist "itemDescriptions" "desc"
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 200
                    endif
                endwhile
                while findtype 30773|30775|30776|30778|30818|30819|30821|30822|30823|30825|30826|30827|30828|30829|30850|30851|30852|30853|30854|30855|30856|30857|30858|30859|30860|30866|30867|30868|30869|30870|30871|30872|30878|30967|30969|30970|30971|30972|30973|30974|30975|30976|30977|30978|30979|30980|30981|30982|30983|30984|30985|30986|30988|30989|30990|30991|30992|30993|30994|30995|30996|30997|30998|30999|31000|31001|31002|31003|31004|31005|31006|31007|31008|31009|31010|31011|31012|31014|31015|31017|31019|31021|31023|31025|31027|31029|31031|31033|31035|31037|31038|31041|31043|31045|31047|31049|31051|31053|31055|31117|31118|31119|31120|31121|31122|31123|31124|31125|31126|31128|31130|31141|31142|31143|31144|31148|31149|31150|31151|31152|31153|31154|31155|31156|31157|31163|31164|31166|31169|31172|31176|31178|31180|31182|31184|31186|31188|31190|31191|31197|31198|31199|31200|31201|31202|31203|31204|31206|31207|31210|31211|31212|31213|31214|31215|31216|31231|31232|31233|31234|31236|31237|31238|31239|33323|33342|33343|33344|33345|36752|37049|37050|37051|37052|37053|37054|37055|37056|37057|37060|37061|37063|37064|37065|37066|37067|37068|37181|39264|39343|39344|39345|39346|39347|39348|39349|39350|39351|39352|39353|39517|39889|39891|39892|39896|39897|39898|39905|39909|39911|39912|39916|39917|39918|40697|40698|40701|40702|40800|40954|40955|40958|40959|40960|40980|40981|41449|41451|41453|41455|41459|41460|41461|41462|41466|41509|41510|41584|41596|41605|41607|41614|41619|41631|41632|41634|41638|41642|41646|41650 "mainBackpack" as "foundItem"
                    @ignore "foundItem"
                    getlabel "foundItem" "desc"
                    if inlist "itemDescriptions" "desc"
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 200
                    endif
                endwhile
                while findtype 41662|41669|41671|41674|41675|41679|41680|41967|41973|41998|42000|42003|42227|42239|42240|42242|42243|42244|42380|42493|42516|42517|42519|42564|42574|42648|42665|42830|42832|42834|42836|42843|42847|42850|42851|42854|43159|43160|43161|43162|43163|43164|43165|43166|43167|43168|43169|43170|43171|43172|43173|43174|43175|43176|43177|43178|43179|43180|43181|43182|43206|43207|43208|43209|43210|43277|43279|43320|43375|43453|43461|44127|44129|44131|44310|44312|44314|44315|44328|44716|44718|44720|44722|44724|44795|44796|44797|44798|44799|44800|44801|44804|44805|44808|44810|44836|44837|44846|44919|44921|44923|44925|44926|44929|44949|44951|44953|44955|44957|44959|44986|44987|44997|44998|45002|45120|45156|45157|45182|45193|45208|45211|45214|45216|45218|45220|45222|45235|45236|45238|45239|45241|45242|45246|45247|45248|45250|45251|45252|45254|45255|45257|45281|45282|45285|45300|45315|45316|45320|45371|45372|45373|45374|45375|45376|45377|45378|45379|45380|45381|45382|45383|45384|45385|45386|45387|45388|45389|45390|45391|45392|45393|45394|45395|45396|45397|45398|45399|45400|45401|45402|45403|45404|45405|45406|45407|45408|45409|45410|45411|45412|45413|45414|45415|45416|45417|45418|45419|45420|45421|45422|45423|45424|45425|45426|45427|45428|45429|45430|45828|45830|45832|45835|45839|46527|47107|47109|47111|47148|47194|47201|47203|47205|47207|47209|47211|47213|47214|47217|47219|47221|47223|47225|47227|47229|47577|47591|48261|48291|48295|48299|48302|48303|48357|48358|48359|48360|48361|48362|48363 "mainBackpack" as "foundItem"
                    @ignore "foundItem"
                    getlabel "foundItem" "desc"
                    if inlist "itemDescriptions" "desc"
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 200
                    endif
                endwhile
                while findtype 48364|48365|48366|48367|48368|48369|48370|48371|48372|48373|48374|48375|48376|48377|48378|48379|48380|48381|48382|48383|48384|48385|48386|48387|48388|48389|48390|48391|48392|48393|48394|48395|48396|48397|48398|48399|48400|48401|48402|48403|48404|48405|48406|48407|48793|48802|48805|48807|48815|48820|48822|48823|48825|48827|49035|49039|49042|49053|49058|49063|49070|49079|49088|49100|49110|49113|49114|49118|49211|49215|49224|49229|49235|49236|49291|49293|49295|49297|49299|49301|49302|49306|49314|49316|49324|49330|49334|49359|49382|49527|49535|49554|49555|49557|49561|49571|49574|49578|49580|49582|49584|49597|49613|49633|49650|49672|49683|49698|49738|49749|49760|49762|49763|49764|49765|49766|49767|49768|49769|49770|49784|49789|49804|49806|49807|49810|49812|49814|49816|49819|49857|49985|50285|50298|50308|50632|50651|50675|51016|51037|51041|51043|51045|51047|51049|51055|51056|51058|51060|51062|51064|51076|51078|51094|51098|51100|51200|51201|51202|51203|51204|51205|51206|51207|51208|51209|51210|51211|51212|51213|51214|51215|51216|51217|51218|51219|51220|51221|51222|51223|51224|51225|51226|51227|51228|51229|51230|51231|51232|51233|51234|51235|51236|51237|51238|51239|51240|51241|51242|51243|51244|51245|51246|51247|51248|51249|51250|51251|51252|51253|51254|51255|51256|51257|51258|51259|51260|51261|51262|51263|51264|51265|51266|51267|51268|51269|51270|51271|51272|51273|51274|51275|51276|51277|51278|51279|51280|51281|51282|51283|51284|51285|51286|51287|51288|51289|51290|51291|51292|51293 "mainBackpack" as "foundItem"
                    @ignore "foundItem"
                    getlabel "foundItem" "desc"
                    if inlist "itemDescriptions" "desc"
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 200
                    endif
                endwhile
                while findtype 51294|51295|51296|51297|51298|51299|51300|51301|51302|51303|51304|51305|51306|51307|51308|51309|51310|51311|51312|51313|51314|51315|51316|51317|51318|51319|51320|51321|51322|51323|51324|51325|51326|51327|51328|51329|51330|51331|51332|51333|51334|51335|51336|51337|51338|51339|51340|51341|51342|51343|51344|51345|51346|51347|51348|51349|51350|51351|51352|51353|51354|51355|51356|51357|51358|51359|51360|51361|51362|51363|51364|51365|51366|51367|51368|51369|51370|51371|51372|51373|51374|51375|51400|51401|51402|51403|51404|51405|51406|51407|51408|51409|51410|51411|51412|51413|51414|51415|51416|51417|51418|51419|51420|51421|51422|51423|51424|51425|51426|51427|51428|51429|51430|51431|51432|51433|51434|51435|51436|51437|51438|51439|51440|51441|51442|51443|51444|51445|51446|51447|51448|51449|51450|51451|51452|51453|51454|51455|51456|51457|51458|51459|51460|51461|51462|51463|51464|51465|51466|51467|51468|51469|51470|51471|51472|51473|51474|51475|51476|51477|51478|51479|51494|51965|51986|51988|51996|51998|52000|52002|52030|52032|52034|52044|52060|52140|52142|52144|52146|52149|52200|52203|52216|52217|52219|52221|52227|52229|52231|52233|52236|52276|52414|52417|52486|52488|52496|52504|52506|52507|52512|52514|52577|52618|52620|52622|52630|52634|52648|52649|52651|52652|52653|52655|52675|52676|52677|52678|52679|52689|52696|52703|52705|52731|52757|52817|52819|52821|52824|52831|52844|52867|52870|52932|52957|52960|53037|53038|53053|53127|53134|53139|53161|53178|53179|53181|53192|53326|53327|53331 "mainBackpack" as "foundItem"
                    @ignore "foundItem"
                    getlabel "foundItem" "desc"
                    if inlist "itemDescriptions" "desc"
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 200
                    endif
                endwhile
                while findtype 53334|53338|53343|53347|53355|53375|53408|53409|53411|53413|53415|53416|53418|53422|53441|53450|53451|53547|53548|53549|53550|53551|53552|53553|53554|53555|53556|53557|53558|53559|53560|53561|53562|53563|53564|53565|53566|53567|53568|53569|53570|53571|53572|53573|53574|53575|53576|53577|53578|53579|53580|53581|53582|53583|53584|53585|53586|53587|53588|53589|53590|53591|53592|53593|53594|53595|53596|53597|53598|53599|53600|53601|53602|53603|53604|53605|53606|53607|53608|53609|53610|53611|53675|53681|53769|53775|53792|53813|53821|53837|53869|53877|53892|53895|53899|53902|53904|53906|53912|53920|53946|53954|53963|53964|53969|53982|54088|54099|54103|54107|54109|54111|54115|54121|54161|54162|54163|54164|54167|54182|54184|54185|54191|54192|54194|54195|54197|54199|54201|54205|54207|54214|54216|54218|54220|54221|54222|54319|54321|54327|54357|54359|54361|54366|54454|54455|54459|54463|54474|54476|54486|54488|54490|54496|54497|54498|54557|54563|54572|54574|54576|54578|54580|54582|54583|54584|54590|54600|54608|54627|54630|54639|54650|54652|54656|54659|54664|54666|54678|54682|54684|54717|54718|54752|54753|54754|54785|54789|54793|54815|54832|54844|54847|54854|54856|54859|54864|54869|54883|54887|54901|54908|54917|54920|54923|54925|54947|54951|54953|54965|54973|54981|54984|54997|55003|55005|55013|55041|55047|55052|55108|55121|55139|55157|55159|55161|55164|55173|55193|55207|55209|55211|55217|55225|55234|55239|55247|55318|55336|55338|55340|55376|55386|55398|55400|55402|55409|55419|55432|55434 "mainBackpack" as "foundItem"
                    @ignore "foundItem"
                    getlabel "foundItem" "desc"
                    if inlist "itemDescriptions" "desc"
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 200
                    endif
                endwhile
                while findtype 55443|55447|55450|55456|55457|55543|55547|55555|55578|55590|55607|55668|55674|55675|55694|55696|55736|55738|55741|55743|55744|55745|55747|55751|55753|55755|55763|55764|55765|55773|55775|55777|55785|55787|55789|55791|55793|55818|55820|55822|55824|55842|55843|55845|55849|55855|55859|55863|55867|55869|55874|55879|55887|55890|55926|55933|55939|55963|56144|56160|56162|56164|56170|56173|56176|56181|56186|56192|56204|56206|56212|56214|56215|56235|56238|56250|56252|56274|56275|56276|56293|56308|56311|56313|56314|56319|56323|56326|56330|56381|56387|56390|56392|56393|56395|56399|56401|56409|56418|56424|56426|56433|56436|56445|56453|56633|56663|56665|56671|56678|56680|56682|56684|56686|56688 "mainBackpack" as "foundItem"
                    @ignore "foundItem"
                    getlabel "foundItem" "desc"
                    if inlist "itemDescriptions" "desc"
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 200
                    endif
                endwhile
                while "searching" == 0 and findtype 2472|2473|2474|2475|2476|2480|2481|2482|2604|2605|2606|2607|2608|2609|2610|2611|2612|2613|2614|2615|2616|2617|2618|2619|2620|2621|2622|2623|2624|2625|2626|2627|2628|2629|2630|2631|2632|2633|2634|2635|2636|2637|2638|2639|2640|2641|2642|2643|2711|2712|2713|2714|2715|2716|2717|2718|3644|3645|3646|3647|3648|3649|3650|3651|3701|3702|3703|3704|3705|3706|3708|3709|3710|3711|3712|7808|7809|9002|9003|11010|11011|12657|29833|29832 "mainBackpack" as "subContainer"
                    @ignore "subContainer"
                    getlabel "subContainer" "desc"
                    if "Price: Not for sale" in "desc"
                        @setvar! "currentContainer" "subContainer"
                        @setvar! "searching" 1
                    endif
                endwhile
            endwhile
            break
        endif
    else
        wait "timeout"
    endif
endwhile"""
        self.root.clipboard_clear()
        self.root.clipboard_append(script_string)
        self.root.update()

    def get_selected_items(self):
        selected_items = self.tree.selection()  # Get selected item IDs
        selected_texts = [self.tree.item(item,"values") for item in selected_items]
        #print("Selected Items:", json.dumps(selected_texts,indent=2))
        return selected_texts

    def on_treeview_click(self, event):
        if self.tree.identify_region(event.x, event.y) == "heading":
            return
        if event.state & (0x0001 | 0x0004):  # 0x0001 is the bitmask for the Shift key, 0x0004 is the bitmask for the Control key
            return self.on_treeview_modded_click(event)
        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        url = None
        if(len(self.tree.item(row_id,'values')) > 1 and self.tree.item(row_id,'values')[1]):
            if col_id == "#1":
                url = self.tree.item(row_id, "values")[9]
            elif col_id == "#7":
                url = self.tree.item(row_id, "values")[8]                
            location_raw = self.tree.item(row_id, "values")[6].split('\t')
            location_split = location_raw[0].split(',')
            x1, y1 = map(int,location_split)
            closest_location = min(my_locations.items(), key=lambda loc: get_distance_squared(x1, y1, loc[1][0], loc[1][1]))
            location_name = closest_location[0]

            if my_locations.get(location_name) is None:
                print(f"on_treeview_click: No match in dictionary for location name: {location_name}")
                return
            location_data = my_locations[location_name][2]
            location_character = location_data[0]
            book_hue = location_data[1]
            location_recall_code = location_data[2]
            location_button_code = location_data[3]
            value_to_copy_raw = self.tree.item(row_id, "values")[8]
            serial_match = re.search(r'\?(\d+)(?:\?(\d+))(?:\?(\d+))?#', value_to_copy_raw) #'https://www.exploreoutlands.com/?471890?1251126567?312345125#pos:869,1381,13'
            second_try = re.search(r'\?(\d+)\?', value_to_copy_raw)
            vendor_serial = serial_match.group(1) if serial_match else second_try.group(1) if second_try else 0
            item_id = serial_match.group(2) if serial_match else 0
            item_price = serial_match.group(3) if serial_match else 0
            str_price = format_with_commas(item_price)
            total_cost = int(float(self.tree.item(row_id, "values")[10]))
            total_cost_str = format_with_commas(total_cost)
            item_description = self.tree.item(row_id, "values")[11]
            scriptString = f"""

@setvar! "timeout" 650
@setvar! "myTome" 0
@clearignore

if find {vendor_serial} ground -1 -1 20
else
    removelist "runetomeList"
    createlist "runetomeList"
    for 3
        if findtype "runetome" backpack {book_hue} as "tome"
            @setvar! "myTome" "tome"
            break
        endif
        dclick backpack
        wait "timeout"
    endfor

    if "myTome" = 0
        overhead "NO TOME" 33
        stop
    endif
    if findtype "bank deposit safe" ground -1 -1 14 as "safe"
        getlabel "safe" "label"
        overhead "label"
        sysmsg "label"
    endif
    overhead "recalling to spot {location_name} in {location_character}'s book" 1159
    dclick "myTome"
    waitforgump 167090027 1000
    if not gumpexists 167090027
        dclick "myTome"
        waitforgump 167090027 2000
    endif
    gumpresponse {location_recall_code} 167090027
    waitforgump 167090027 2000
    gumpresponse {location_button_code} 167090027
    wait 500

    while not dead
        if hidden or cooldown "skill" > 0
            break
        endif
        skill "hiding"
        wait 200
        if insysmsg "You must be a friend of this house, or have a rental vendor, in order to hide here."
            @clearsysmsg
            break
        endif
    endwhile
endif

while not dead
    if find {vendor_serial} ground -1 -1 20
        overhead "● ▼▼ HERE ▼▼ ●" 88 {vendor_serial}
        if findtype 3701 {vendor_serial} 0 0 0 as "pack"
            while findtype "book|recall rune" "pack" as "decoys"
                @ignore "decoys"
            endwhile
            if find {item_id} "pack"
            else
                dclick "pack"
                wait "timeout"
            endif
            if hidden
            else
                skill "hiding"
            endif
            if {item_id} = 0
                overhead "No itemID" 33
                stop
            endif
            @setvar! "foundItem" 0
            if find {item_id} "pack" as "item"
                @setvar! "foundItem" "item"
            else
                while findtype 2472|2473|2474|2475|2476|2480|2481|2482|2604|2605|2606|2607|2608|2609|2610|2611|2612|2613|2614|2615|2616|2617|2618|2619|2620|2621|2622|2623|2624|2625|2626|2627|2628|2629|2630|2631|2632|2633|2634|2635|2636|2637|2638|2639|2640|2641|2642|2643|2711|2712|2713|2714|2715|2716|2717|2718|3644|3645|3646|3647|3648|3649|3650|3651|3701|3702|3703|3704|3705|3706|3708|3709|3710|3711|3712|7808|7809|9002|9003|11010|11011|12657|29833|29832 "pack" as "subContainer"
                    @ignore "subContainer"
                    while findtype "book|recall rune" "pack" as "decoys"
                        @ignore "decoys"
                    endwhile
                    if find {item_id} "pack"
                    else
                        dclick "subContainer"
                        wait "timeout"
                    endif
                    if find {item_id} "pack" as "item"
                        @setvar! "foundItem" "item"
                        break
                    endif
                endwhile
                @clearignore
            endif
            if "foundItem" != 0
                getlabel "foundItem" "foundItemLabel"
                sysmsg "FOUND {{{{foundItemLabel}}}}" 1159
                if "Description: " in "foundItemLabel"
                elseif "{item_description}" in "foundItemLabel"
                    if "Price: {str_price} " in "foundItemLabel"
                        sysmsg "opening buy menu" 1159
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 100
                        if findtype "bank deposit safe" ground -1 -1 14 as "safe"
                            getlabel "safe" "label"
                            overhead "label"
                        endif
                        wait 100
                    elseif "Price: {total_cost_str} " in "foundItemLabel"
                        sysmsg "opening buy menu" 1159
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 100
                        if findtype "bank deposit safe" ground -1 -1 14 as "safe"
                            getlabel "safe" "label"
                            overhead "label"
                        endif
                        wait 100
                    else
                        overhead "BEWARE PRICE CHANGE" 33
                        sysmsg "BEWARE PRICE CHANGE" 33
                    endif
                else
                    overhead "BEWARE ITEM CHANGE" 33
                    sysmsg "BEWARE ITEM CHANGE" 33
                endif
            else
                sysmsg "Could not find item for sale {item_description}" 1159
            endif
        endif
        wait 650
        break
    endif
    wait 500
endwhile"""

            self.root.clipboard_append(scriptString)
            self.root.update()
            if url:
                webbrowser.open(url)

    def on_treeview_right_click(self,event=None):
        if self.tree.identify_region(event.x, event.y) == "heading":
            return
        if event.state & (0x0001 | 0x0004):  # 0x0001 is the bitmask for the Shift key, 0x0004 is the bitmask for the Control key
            return self.on_treeview_modded_click(event)
        row_id = self.tree.identify_row(event.y)
        try:
            location_raw = self.tree.item(row_id, "values")[6].split('\t')
        except:
            return
        location_split = location_raw[0].split(',')
        x1, y1 = map(int,location_split)
        closest_location = min(my_locations.items(), key=lambda loc: get_distance_squared(x1, y1, loc[1][0], loc[1][1]))
        location_name = closest_location[0]

        if my_locations.get(location_name) is None:
            print(f"on_treeview_right_click: No match in dictionary for location name: {location_name}")
            return
        location_data = my_locations[location_name][2]
        location_character = location_data[0]
        book_hue = location_data[1]
        location_recall_code = location_data[2]
        location_button_code = location_data[3]
        value_to_copy_raw = self.tree.item(row_id, "values")[8]
        serial_match = re.search(r'\?(\d+)(?:\?(\d+))(?:\?(\d+))?#', value_to_copy_raw) #'https://www.exploreoutlands.com/?471890?1251126567?312345125#pos:869,1381,13'
        second_try = re.search(r'\?(\d+)\?', value_to_copy_raw)
        vendor_serial = serial_match.group(1) if serial_match else second_try.group(1) if second_try else 0
        item_id = serial_match.group(2) if serial_match else 0
        item_price = format_with_commas(serial_match.group(3)) if serial_match else 0
        str_price = format_with_commas(item_price)
        total_cost = int(float(self.tree.item(row_id, "values")[10]))
        total_cost_str = format_with_commas(total_cost)
        item_description = self.tree.item(row_id, "values")[11]
        scriptString = f"""@setvar! "timeout" 650
@setvar! "myTome" 0
@clearignore

if find {vendor_serial} ground -1 -1 20
else
    removelist "runetomeList"
    createlist "runetomeList"
    for 3
        if findtype "runetome" backpack {book_hue} as "tome"
            @setvar! "myTome" "tome"
            break
        endif
        dclick backpack
        wait "timeout"
    endfor

    if "myTome" = 0
        overhead "NO TOME" 33
        stop
    endif
    if findtype "bank deposit safe" ground -1 -1 14 as "safe"
        getlabel "safe" "label"
        overhead "label"
        sysmsg "label"
    endif
    overhead "recalling to spot {location_name} in {location_character}'s book" 1159
    dclick "myTome"
    waitforgump 167090027 1000
    if not gumpexists 167090027
        dclick "myTome"
        waitforgump 167090027 2000
    endif
    gumpresponse {location_recall_code} 167090027
    waitforgump 167090027 2000
    gumpresponse {location_button_code} 167090027
    wait 500

    while not dead
        if hidden or cooldown "skill" > 0
            break
        endif
        skill "hiding"
        wait 200
        
        if insysmsg "You must be a friend of this house, or have a rental vendor, in order to hide here."
            break
        endif
    endwhile
endif

while not dead
    if find {vendor_serial} ground -1 -1 20
        overhead "● ▼▼ HERE ▼▼ ●" 88 {vendor_serial}
        if findtype 3701 {vendor_serial} 0 0 0 as "pack"
            while findtype "book|recall rune" "pack" as "decoys"
                @ignore "decoys"
            endwhile
            if find {item_id} "pack"
            else
                dclick "pack"
                wait "timeout"
            endif
            if hidden
            else
                skill "hiding"
            endif
            if {item_id} = 0
                overhead "No itemID" 33
                stop
            endif
            @setvar! "foundItem" 0
            if find {item_id} "pack" as "item"
                @setvar! "foundItem" "item"
            else
                while findtype 2472|2473|2474|2475|2476|2480|2481|2482|2604|2605|2606|2607|2608|2609|2610|2611|2612|2613|2614|2615|2616|2617|2618|2619|2620|2621|2622|2623|2624|2625|2626|2627|2628|2629|2630|2631|2632|2633|2634|2635|2636|2637|2638|2639|2640|2641|2642|2643|2711|2712|2713|2714|2715|2716|2717|2718|3644|3645|3646|3647|3648|3649|3650|3651|3701|3702|3703|3704|3705|3706|3708|3709|3710|3711|3712|7808|7809|9002|9003|11010|11011|12657|29833|29832 "pack" as "subContainer"
                    @ignore "subContainer"
                    while findtype "book|recall rune" "pack" as "decoys"
                        @ignore "decoys"
                    endwhile
                    if find {item_id} "pack"
                    else
                        dclick "subContainer"
                        wait "timeout"
                    endif
                    if find {item_id} "pack" as "item"
                        @setvar! "foundItem" "item"
                        break
                    endif
                endwhile
                @clearignore
            endif
            if "foundItem" != 0
                getlabel "foundItem" "foundItemLabel"
                sysmsg "FOUND {{{{foundItemLabel}}}}" 1159
                if "Description: " in "foundItemLabel"
                elseif "{item_description}" in "foundItemLabel"
                    if "Price: {str_price} " in "foundItemLabel"
                        sysmsg "opening buy menu" 1159
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 100
                        if findtype "bank deposit safe" ground -1 -1 14 as "safe"
                            getlabel "safe" "label"
                            overhead "label"
                        endif
                        wait 100
                    elseif "Price: {total_cost_str} " in "foundItemLabel"
                        sysmsg "opening buy menu" 1159
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 100
                        if findtype "bank deposit safe" ground -1 -1 14 as "safe"
                            getlabel "safe" "label"
                            overhead "label"
                        endif
                        wait 100
                    else
                        overhead "BEWARE PRICE CHANGE" 33
                        sysmsg "BEWARE PRICE CHANGE" 33
                    endif
                endif
            else
                sysmsg "Could not find item for sale {item_description}" 1159
            endif
        endif
        wait 650
        break
    endif
    wait 500
endwhile"""
        self.root.clipboard_clear()
        self.root.clipboard_append(scriptString)
        self.tree.selection_set(row_id)

    def quick_scrape(self):
        start_time = time.time()
        temp_list = []
        async def main():
            responses = await request_gen_simple()
            num_cores = cpu_count()
            with Pool(num_cores) as pool:
                try:
                    for result in pool.imap_unordered(simple_parse_narrow, responses):
                        temp_list.append(result)
                except Exception as e:
                    print(f"quick_scrape: Pool failed: {e}")
        
        asyncio.run(main())

        filt_tmp = [tmp for tmp in temp_list if tmp]
        for temp in filt_tmp:
            self.queue_append.put(temp)

        elapsed_time = round(time.time() - start_time, 2)
        self.queue_append.put(f"Finished FAST:{elapsed_time}")


    def async_scraping(self):
        start_time = time.time()
        seconds_threshold = self.parse_combobox()
        price_depth = self.search_pricedepth.get()
        cutoff_threshold = self.cutoff_threshold.get()
        
        def request_gen():
            bools = [
                (self.check_lp_misc_var.get(), misc_lp_prices),
                (self.check_hp_misc_var.get(), misc_hp_prices),
            ]
            gathered_misc_prices = {}
            for bool, prices in bools:
                if bool:
                    gathered_misc_prices.update(prices)
            for searchString, searchPrice in gathered_misc_prices.items():
                self.queue_append.put(f"{searchString}")
                page_url = "https://outlandmalls.com/?item=" + quote_plus(searchString) + "&search_category_id=0"
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                time.sleep(1)
                cookie = {"app": user_config["outlands_cookie"]}
                response = requests.get(page_url, headers=headers, cookies=cookie)

                if response.status_code != 200:
                    print(f"async_scraping: request_gen: Failed to retrieve the webpage: {searchString}. Status code: {response.status_code}")
                    continue
                yield (response.content,searchPrice,page_url,seconds_threshold,price_depth,cutoff_threshold)


        if self.check_lp_misc_var.get() or self.check_hp_misc_var.get():
            num_cores = cpu_count()
            with Pool(num_cores) as pool:
                for result in pool.imap_unordered(multi_parse_misc,request_gen()):
                    self.queue_append.put(result)

        steps = [
            ["Aspect Core", core_prices, self.check_core_var.get()],
            #["Aspect Extract", extract_prices, self.check_extract_var.get()],
            #["Aspect Distillation", distil_prices, self.check_distil_var.get()],
            ["Undeciphered", tmap_prices.update(rmap_prices), self.check_tmaps_var.get()],
            ["Skill Mastery Scroll", scroll_prices, self.check_skillscrolls_var.get()],
            ["Mastery Chain Link", link_prices, self.check_chainlinks_var.get()],
            ["Misc Crafting", misc_crafting_prices, self.check_hp_misc_var.get()],
        ]
        
        price_depth = self.search_pricedepth.get()
        seconds_threshold = self.parse_combobox()
        cutoff_threshold = self.cutoff_threshold.get()
        cookie = user_config["outlands_cookie"]
        
        tuple_list = []
        for step in steps:
            bool = step[2]
            if not bool:
                continue
            name = step[0]
            tuple_list.append((name,price_depth,seconds_threshold,cutoff_threshold,cookie))

        self.queue_append.put("Searching Wide")
        num_cores = cpu_count()
        with Pool(num_cores) as pool:
            for result in pool.imap_unordered(multi_parse_wide,tuple_list):
                self.queue_append.put(result[0])
        elapsed_time = round(time.time() - start_time,2)
        self.queue_append.put(f"Complete: {elapsed_time}s")

    def ScrapeOutlandMall(self,event=''):
        self.clear_tree()
        async_bot = threading.Thread(target=self.async_scraping,name='AsyncScraper')
        async_bot.start()

    def PriorityScrapeOutlandMall(self,event=''):
        self.clear_tree()
        async_bot = threading.Thread(target=self.quick_scrape,name='QuickScraper')
        async_bot.start()

    def search_self_parse_obj(self,parse_obj):
        cutoff_threshold = self.cutoff_threshold.get()
        price_depth = self.search_pricedepth.get()
        self_parse_extra_misc = self.check_lp_misc_var.get()
        bools = [
            (self.check_core_var.get(), core_prices),
            (self.check_extract_var.get(), extract_prices),
            (self.check_distil_var.get(), distil_prices),
            (self.check_tmaps_var.get(), tmap_prices),
            (self.check_skillscrolls_var.get(), scroll_prices),
            (self.check_chainlinks_var.get(), link_prices),
            (self.check_cloth_var.get(), 'cloth'),
            (self.check_dye_var.get(), 'dyes'),
            (self.check_hp_misc_var.get(), misc_hp_prices),
            (self_parse_extra_misc, self_parse_extra_prices),
            (self_parse_extra_misc, commodity_2500_prices),
            (self_parse_extra_misc, commodity_5000_prices),
            (self_parse_extra_misc, deed_prices),
            (self_parse_extra_misc, rmap_prices),
            (self.check_lp_misc_var.get(), misc_lp_prices),
            (self.check_lp_misc_var.get(), misc_crafting_prices),
            (self.check_ingot_var.get(), ingot_prices),
            (self.check_board_var.get(), board_prices),
            (self.check_leather_var.get(), leather_prices),
        ]
        self_parse_prices = {}
        for bool, prices in bools:
            if bool:
                if prices == 'cloth':
                    self_parse_prices.update(alter_hue_dict(True,'rare cloth'))
                elif prices == 'dyes':
                    dye_list = ['accessory dye','runebook dye','headwear dye','carpet dye','furniture dye','hair dye','facial hair dye','backpack dye','mount gear dye']
                    for dye in dye_list:
                        self_parse_prices.update(alter_hue_dict(True,dye))
                else:
                    self_parse_prices.update(prices)
        vendors = parse_obj[0]
        latest_log = parse_obj[1]
        file_info = latest_log.split('\\')[-1].split('_') #2023_09_02_17_07_16_journal.txt
        out_string_date = '/'.join(file_info[1:3])
        out_string_time = ':'.join(file_info[3:5])
        out_string = f"{out_string_date} {out_string_time}"
        out_data = []
        for vendor_id, vendor_data in vendors.items():
            vendor_string = vendor_data['name']
            vendor_items = vendor_data["items"]
            for item in vendor_items:
                threshold = 0.0
                name_string = item['description']
                full_description = item['full_description']
                price = round(item['price'],4)
                if 'chain link' in name_string:
                    if name_string.startswith('a '):
                        name_string = name_string[2:]
                    chain_name = clean_chainlink_string(name_string)
                    if name_string.endswith('reforging tool'):
                        threshold = float(self_parse_prices.get(chain_name,0))
                    elif name_string.startswith('bronze mastery chain link'):
                        threshold = float(self_parse_prices.get(chain_name,[0,0,0])[0])
                    elif name_string.startswith('silver mastery chain link'):
                        threshold = float(self_parse_prices.get(chain_name,[0,0,0])[1])
                    elif name_string.startswith('gold mastery chain link'):
                        threshold = float(self_parse_prices.get(chain_name,[0,0,0])[2])
                    elif name_string.startswith('corrupted mastery chain link'):
                        threshold = float(self_parse_prices.get("corrupted_link_price_threshold",0))
                    else:
                        threshold = 0.
                elif self_parse_extra_misc:
                    if "invulnerability" in name_string:
                        if ("bone" in name_string or "studded" in name_string) and not ("skirt" in name_string or "cap" in name_string or "bustier" in name_string):
                            threshold = float(self_parse_extra_aliases.get('invulnerability studded', 0))
                        elif "platemail" in name_string:
                            threshold = float(self_parse_extra_aliases.get('invulnerability platemail', 0))
                    elif "fortification" in name_string and "platemail" in name_string:
                        threshold = float(self_parse_extra_aliases.get('fortification platemail', 0))
                    elif "tome" in name_string and not "summoner's tome" in name_string and not "a rune tome" in name_string:
                        threshold = float(self_parse_extra_aliases.get('tome', 0))
                    elif "mount token" in name_string:
                        threshold =  float(self_parse_extra_aliases.get('mount token', 0))
                    elif 'a lore page' in name_string:
                        if "of 15)" in name_string:
                            threshold = float(self_parse_extra_aliases.get('lore page /15', 0))
                        else:
                            threshold = float(self_parse_extra_aliases.get('lore page /10', 0))
                    elif "antiquity" in name_string:
                        if "thief antiquity" in name_string:
                            threshold = float(self_parse_extra_aliases.get('thief antiquity', 0))
                        elif "harvest antiquity" in name_string:
                            threshold = float(self_parse_extra_aliases.get('harvest antiquity', 0))
                        elif "crafting antiquity" in name_string:
                            threshold = float(self_parse_extra_aliases.get('crafting antiquity', 0))
                        elif "portrait painting antiquity" in name_string:
                            threshold = float(self_parse_extra_aliases.get('portrait painting antiquity', 0))
                        elif "landscape painting antiquity" in name_string:
                            threshold = float(self_parse_extra_aliases.get('landscape painting antiquity', 0))
                        elif "large painting antiquity" in name_string:
                            threshold = float(self_parse_extra_aliases.get('large painting antiquity', 0))
                        elif "battle antiquity" in name_string:
                            threshold = float(self_parse_extra_aliases.get('battle antiquity', 0))
                        elif "ocean antiquity" in name_string:
                            threshold = float(self_parse_extra_aliases.get('ocean antiquity', 0))
                        elif "chest antiquity" in name_string:
                            threshold = float(self_parse_extra_aliases.get('chest antiquity', 0))
                    elif 'totem' in name_string and 'lustrous' in name_string:
                        threshold = float(self_parse_extra_aliases.get('lustrous totem', 0))
                if threshold == 0.0:
                    threshold = float(self_parse_prices.get(name_string, 0))
                if threshold > 0.0:
                    cost_to_price_ratio = round(price / threshold,2)
                elif price == 999 and not is_junk(name_string,item['quantity']):
                    cost_to_price_ratio = 1001
                else:
                    cost_to_price_ratio = 1000
                if cost_to_price_ratio != 1001 and cost_to_price_ratio > cutoff_threshold and price_depth != 2:
                    continue
                if(price <= threshold or price_depth == 2 or price == 999):
                    location_coordinates = item['location']
                    location_coordinates_cleaned = re.sub(' ', '', location_coordinates)
                    location_name = item['location_name']
                    quantity_int = item['quantity']
                    web_name = name_string
                    if " (hue " in name_string: #furniture dye (hue 1156: dark blueberry)
                        match = re.search(r"(.*) \(hue \d+: (.*)\)", name_string)
                        if match:
                            web_item = match.group(1)
                            hue = match.group(2)
                            web_name = f"{hue} {web_item}"
                    format_url = "https://outlandmalls.com/?item=" + quote_plus(web_name) + "&search_category_id=0"
                    location_link = f"https://www.exploreoutlands.com/#pos:{location_coordinates_cleaned},13"
                    location_link_split = location_link.split('#')
                    total_cost = round(price * quantity_int,0)
                    total_profit = round(threshold * quantity_int - total_cost,0)
                    formatted_location_link = f"{location_link_split[0]}?{vendor_id}?{item['id']}?{int(price * quantity_int)}#{location_link_split[1]}"
                    out_data.append((f"{name_string}",f"{int(price)}/{int(threshold)}",f"{cost_to_price_ratio}",f"{quantity_int}",f"{total_profit}",f"{vendor_string}",f"{location_coordinates}\t{location_name}",f"{out_string}",f"{formatted_location_link}",f"{format_url}",f"{total_cost}",f"{full_description}"))
        self.queue_append.put(out_data)

    def ParseMostRecentJournalLog(self,event=''):
        self.clear_tree()
        obj = parse_log_to_object()
        if type(obj[0]) is str:
            file_info = obj[0].split('\\')[-1].split('_') #2023_09_02_17_07_16_journal.txt
            out_string_date = '/'.join(file_info[1:3])
            out_string_time = ':'.join(file_info[3:5])
            out_string = f"{out_string_date} {out_string_time}"

            self.queue_append.put(f"X: {obj[1][:6]}: {out_string}")
            return
        self.search_self_parse_obj(obj)
        tree_children = self.tree.get_children()
        if tree_children:
            self.tree.see(tree_children[0])
        self.queue_append.put(f'Recent: {obj[2][:6]}')
        self.root.update()

    def PostJournalLog(self,event=''):
        url = 'https://outlandmalls.com/uploads'
        headers = {'Authorization': user_config["upload_key"]}
        data = {'tz': 'America/New_York'}
        file_path = get_most_recent_log()
        if not file_path:
            self.queue_append.put('POST failed')
            return
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f)}
            response = requests.post(url, headers=headers, files=files, data=data)
            self.queue_append.put(f"{response}")

    def read_db_total_sales(self):
        try:
            with connect_db() as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM sales_history")
                rows = c.fetchall()
                columns = [desc[0] for desc in c.description]
            total_sales_window = tk.Toplevel(self.root)
            total_sales_window.title("Sales Report")
            self.scrollbar = tk.Scrollbar(total_sales_window, orient="vertical")
            listbox = tk.Listbox(total_sales_window, yscrollcommand=self.scrollbar.set, width=60, height=20)
            self.scrollbar.config(command=listbox.yview)
            self.scrollbar.pack(side="right", fill="y")
            listbox.pack(side="left", fill="both", expand=True)
            total_revenue = 0
            for row in rows:
                row_dict = dict(zip(columns, row))
                total_price = row_dict['price'] * row_dict['quantity']
                total_revenue += total_price
                result = f"{row_dict['snapshot_time']} ID:{row_dict['id']}, {row_dict['description']}: {row_dict['quantity']}x @ {row_dict['price']} = {total_price}"
                listbox.insert(tk.END, result)
            rev_string = f"Total Revenue: {total_revenue}"
            listbox.insert(tk.END, rev_string)
            return rows
        except Exception as e:
            print(f"read_db_total_sales: An error occurred: {e}")
            return []

    def read_db_recent_sales(self):
        try:
            with connect_db() as conn:
                c = conn.cursor()
                c.execute("SELECT MAX(snapshot_time) FROM sales_history")
                entries = c.fetchall()
                most_recent_time = entries[0][0]
                c.execute("SELECT * FROM sales_history WHERE snapshot_time=?",(most_recent_time,))
                rows = c.fetchall()
                columns = [desc[0] for desc in c.description]
            sales_window = tk.Toplevel(self.root)
            sales_window.title("Sales Report")
            self.scrollbar = tk.Scrollbar(sales_window, orient="vertical")
            listbox = tk.Listbox(sales_window, yscrollcommand=self.scrollbar.set, width=60, height=20)
            self.scrollbar.config(command=listbox.yview)
            self.scrollbar.pack(side="right", fill="y")
            listbox.pack(side="left", fill="both", expand=True)
            total_revenue = 0
            for row in rows:
                row_dict = dict(zip(columns, row))
                total_price = row_dict['price'] * row_dict['quantity']
                total_revenue += total_price
                result = f"{row_dict['snapshot_time']} ID:{row_dict['id']}, {row_dict['description']}: {row_dict['quantity']}x @ {row_dict['price']} = {total_price}"
                listbox.insert(tk.END, result)
            rev_string = f"Total Revenue: {total_revenue}"
            listbox.insert(tk.END, rev_string)
            return rows
        except Exception as e:
            print(f"read_db_recent_sales: An error occurred: {e}")
            return []
        
    def read_db_current_inventory(self,only_report_incorrect_inventory=False):
        try:
            rows = get_most_recent_inventory_snapshot()
            if not rows:
                print("read_db_current_inventory: No inventory snapshot available.")
                return []
            aggregated_items = {}
            columns = ['snapshot_time', 'id', 'price', 'description', 'quantity']
            for row in rows:
                row_dict = dict(zip(columns, row))
                stackSize = int(row_dict['quantity'])
                if stackSize > 1:
                    key = (f"{row_dict['description']}", stackSize, row_dict['price'])
                else:
                    key = (f"{row_dict['description']}", 1, row_dict['price'])
                if key not in aggregated_items:
                    aggregated_items[key] = 0
                aggregated_items[key] += 1
            sorted_items = categorize_and_sort_aggregated_items(aggregated_items)
            out_str = ""
            if not only_report_incorrect_inventory:
                out_str += "***WTS*** *(all available on vendors MM1 through MM8 at my shop a short walk southeast from Totem moongate*"
            for category_name, category_items in sorted_items.items(): 
                if len(category_items) == 0:
                    continue
                out_str += f"\n**{category_name}**:\n"
                for description, details in category_items.items():
                    trunc_name = discord_truncate(description)
                    inline_strings = []
                    check_arr = []
                    for stack_size, price, quantity in sorted(details): 
                        fprice = shorten_number(price)    
                        if stack_size == 1:
                            inline_strings.append(f"{quantity} @ {fprice}/item")
                        else:
                            ftotal = shorten_number(price * stack_size)
                            if quantity == 1:
                                inline_strings.append(f"1 set of {stack_size} @ {ftotal}/set ({fprice}/item)")
                            elif quantity != 0:
                                inline_strings.append(f"{quantity} sets of {stack_size} @ {ftotal}/set ({fprice}/item)")
                            else:
                                inline_strings.append(f"({fprice}/item)")

                        check_arr.append((stack_size,quantity))
                    result = f"{trunc_name}: {' & '.join(inline_strings)}"

                    if category_name == "Skill Mastery Scrolls" and ((1,2) not in check_arr or (10,2) not in check_arr):
                        out_str += f"--{result}   \n"
                    elif category_name == "Cores" and ((20,1) not in check_arr or (5,2) not in check_arr or (1,2) not in check_arr): 
                        out_str += f"--{result}   \n"
                    elif category_name == "Distils" and ((5,2) not in check_arr or (1,2) not in check_arr): 
                        out_str += f"--{result}   \n"
                    elif not only_report_incorrect_inventory:
                        out_str += f"\t{result}\n"

            new_window = tk.Toplevel(self.root)
            new_window.wm_attributes("-topmost", 1)
            new_window.title("Restock Info")
            self.scrollbar = tk.Scrollbar(new_window, orient="vertical")
            textbox = tk.Text(new_window, yscrollcommand=self.scrollbar.set, width=160, height=50, font=("Consolas", 11))
            self.scrollbar.config(command=textbox.yview)
            self.scrollbar.pack(side="right", fill="y")
            textbox.pack(side="left", fill="both", expand=True)
            textbox.insert(tk.END, out_str)

            render_stock_script(sorted_items)
            if only_report_incorrect_inventory:
                return "break"
            return sorted_items
        except Exception as e:
            print(f"read_db_current_inventory: An error occurred: {e}")
            return []
        
    #------------------------------ GUI Updates---------------------------
    def queue_daemon(self,event=None):
        try:
            data = self.queue_append.get_nowait()
            if isinstance(data,str):
                self.status_var.set(data)
                if 'Finished FAST' in data:
                    self.queue_emptyFastSort_flag = True
            elif data and len(data):
                for tuple in data:
                    self.append_to_tree(*tuple)
                self.queue_emptySort_flag = True
            self.root.after(10, self.queue_daemon)
        except queue.Empty:
            if self.queue_emptySort_flag or self.queue_emptyFastSort_flag:
                self.queue_emptySort_flag = False
                if self.queue_emptyFastSort_flag:
                    self.queue_emptyFastSort_flag = False
                    try:
                        self.sort_tree_quick()
                    except Exception as e:
                        print('queue_daemon: sort quick failed: ', e)
                elif self.search_sortmode.get() == 2:
                    try:
                        self.sort_column_tuple("Ratio", "Item", False, sort_key_tuple)
                    except Exception as e:
                        print('queue_daemon: sort failed: ', e)
            self.root.after(20, self.queue_daemon)
            
        except Exception as e:
            print(f"queue_daemon exception: {e}")
            self.root.after(20, self.queue_daemon)

    def clear_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

    #"Item", "Price","Ratio","#","Profit","Vendor","Location","Time"
    def append_to_tree(self,text1='',text2='',text3='',text4='',text5='',text6='',text7='',text8='',text9='',text10='',text11='',text12='',text13=''):
        if len(text3):
            ratio = float(text3)
            if ratio == 1001:
                item = self.tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9, text10, text11, text12, text13), tags=("mistake",))
            elif ratio < 0.6:
                item = self.tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9, text10, text11, text12, text13), tags=("ultra",))
            elif ratio <= 0.7:
                item = self.tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9, text10, text11, text12, text13), tags=("high",))
            elif ratio <= 0.8:
                item = self.tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9, text10, text11, text12, text13), tags=("med",))
            elif ratio <= 0.9:
                item = self.tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9, text10, text11, text12, text13), tags=("low",))
            elif ratio < 0.95:
                item = self.tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9, text10, text11, text12, text13), tags=("verylow",))
            elif ratio >= 0.95 and ratio <= 1.0:
                item = self.tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9, text10, text11, text12, text13), tags=("base",))
            else:
                item = self.tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9, text10, text11, text12, text13))
        elif text1:
            item = self.tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9, text10, text11, text12, text13))
        #self.tree.see(item)

    def sort_column(self, col, reverse, key=None):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        l.sort(key=key,reverse=reverse)
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
        self.tree.heading(col, command=lambda _col=col: self.sort_column(_col, not reverse, key))

    def sort_column_tuple(self, col,secondary_col,reverse, key=None):
        tree_children = self.tree.get_children("")
        if(len(tree_children) == 0):
            return
        l = [(self.tree.set(k, col), self.tree.set(k, secondary_col), k) for k in tree_children]
        try:
            l.sort(key=lambda x: (key(x,col,secondary_col)[0] if key else x[0], key(x,col,secondary_col)[1]) if key else x[1], reverse=reverse)
        except Exception as e:
            print('sort_column_tuple: Exception:', e)
        for index, (_, _, k) in enumerate(l):
            self.tree.move(k, '', index)
        self.tree.heading(col, command=lambda _col=col,_secondary_col = secondary_col: self.sort_column_tuple(_col, _secondary_col, not reverse, key))
        self.tree.see(l[0][2])

    def sort_tree_density(self, event=None):
        data = []
        tree_children = self.tree.get_children("")          
        if(len(tree_children) == 0):
            return
        for child in tree_children:
            row_data = {}
            for col in self.tree["columns"]:
                row_data[col] = self.tree.set(child, col)
            data.append(row_data)
        rows_by_location = defaultdict(list)
        for item in data:
            rows_by_location[item['Location'].split('\t')[1]].append(item)
        data_by_location = []
        for location, items in rows_by_location.items():
            profit_sum = 0
            ctp_sum = 0
            margin_sum = 0
            total_items_at_location = 0
            for item in items:
                price_col_string = item['Price']
                price_col_split = price_col_string.split('/')
                my_cost = int(float(price_col_split[0]))
                sale_price = int(float(price_col_split[1]))
                quantity_int = int(item['#'])
                ctp_ratio_float = float(item['Ratio'])
                try:
                    profit_margin = round((sale_price - my_cost) / my_cost,2)
                except ZeroDivisionError:
                    profit_margin = 1
                potential_profit = (sale_price - my_cost) * quantity_int
                if ctp_ratio_float > 0.9 or profit_margin < 0.1:
                    continue
                total_items_at_location += 1
                profit_sum += potential_profit
                ctp_sum += ctp_ratio_float
                margin_sum += profit_margin
            total_profit = profit_sum
            profit_per_item = round(profit_sum / total_items_at_location) if total_items_at_location else 1
            ctp_ratio_average = round((ctp_sum / total_items_at_location) * 10) / 10 if total_items_at_location else 1
            profit_margin_average = round((margin_sum / total_items_at_location) * 10) / 10 if total_items_at_location else 0
            loc_data = {
                "Profit": total_profit,
                "Profit_Per_Item": profit_per_item,
                "CTP_Average": ctp_ratio_average,
                "Margin_Average": profit_margin_average,
            }
            data_by_location.append((location,loc_data))
        loc_data_sorted = sorted(data_by_location,key=lambda x: (-x[1]["Profit"],x[1]["CTP_Average"],-x[1]["Margin_Average"]))
        loc_sorted = []
        for loc,data in loc_data_sorted:
            loc_sorted.append(loc)

        loc_id_list = [(self.tree.set(k, 'Location'),self.tree.set(k, 'Ratio'), k) for k in tree_children]
        loc_id_list_sorted = sorted(loc_id_list,key=lambda x: (loc_sorted.index(x[0].split("\t")[1]), float(x[1])))
        for index, (_, _, k) in enumerate(loc_id_list_sorted):
            self.tree.move(k, '', index)
        self.tree.see(loc_id_list_sorted[0][2])
        #print(f"Total Profit: {total_profit}\tCTP Ratio Average: {ctp_ratio_average}\t\tProfit Margin Average: {profit_margin_average}\n")

    def sort_tree_quick(self, event=None):
        data = []
        tree_children = self.tree.get_children("")          
        if(len(tree_children) == 0):
            return
        for child in tree_children:
            row_data = {}
            for col in self.tree["columns"]:
                row_data[col] = self.tree.set(child, col)
            data.append(row_data)
        data = [row for row in data if row.get("Price","999/0") != "999/0"]
        if len(data) == 0:
            return
        rows_by_location = defaultdict(list)
        items_by_vendor = defaultdict(lambda: defaultdict(str))
        vendors_by_location = defaultdict(lambda: defaultdict(str))
        for row in data:
            rows_by_location[row['Location'].split('\t')[1]].append(row)
            value_to_copy_raw = row["#9"]
            serial_match = re.search(r'\?(\d+)(?:\?(\d+))(?:\?(\d+))?#', value_to_copy_raw) #'https://www.exploreoutlands.com/?471890?1251126567?312345125#pos:869,1381,13'
            if serial_match:
                vendor_serial = serial_match.group(1)
            else:
                second_try = re.search(r'\?(\d+)\?', value_to_copy_raw)
                vendor_serial = second_try.group(1) if second_try else 0
            item_id = serial_match.group(2) if serial_match else 0
            item_price = serial_match.group(3) if serial_match else 0
            str_price = format_with_commas(item_price)
            if str_price == "999":
                continue
            total_cost = int(float(row["#11"]))
            total_cost_str = format_with_commas(total_cost)
            item_description_sans_price = row["#12"]
            item_description_compare = f"Price: {total_cost_str} {item_description_sans_price}"
            items_by_vendor[vendor_serial][item_description_compare] = item_id
            vendors_by_location[row['Location'].split('\t')[1]][row["Vendor"]] = vendor_serial
        data_by_location = []
        for location, rows in rows_by_location.items():
            profit_sum = 0
            ctp_sum = 0
            margin_sum = 0
            total_items_at_location = 0
            loc_time = ""
            for row in rows:
                price_col_string = row['Price']
                price_col_split = price_col_string.split('/')
                my_cost = int(float(price_col_split[0]))
                sale_price = int(float(price_col_split[1]))
                quantity_int = int(row['#'])
                ctp_ratio_float = float(row['Ratio'])
                try:
                    profit_margin = round((sale_price - my_cost) / my_cost,2)
                except ZeroDivisionError:
                    profit_margin = 1
                potential_profit = (sale_price - my_cost) * quantity_int
                # if ctp_ratio_float > 0.93 or profit_margin < 0.07:
                #     continue
                total_items_at_location += 1
                profit_sum += potential_profit
                ctp_sum += ctp_ratio_float
                margin_sum += profit_margin
                loc_time = row["Time"]
            total_profit = profit_sum
            ctp_ratio_average = round((ctp_sum / total_items_at_location) * 10) / 10 if total_items_at_location else 1
            profit_margin_average = round((margin_sum / total_items_at_location) * 10) / 10 if total_items_at_location else 0
            loc_data = {
                "Profit": total_profit,
                "CTP_Average": ctp_ratio_average,
                "Margin_Average": profit_margin_average,
                "Time": get_seconds_from_string(loc_time)
            }
            data_by_location.append((location,loc_data))

        #loc_data_sorted = sorted(data_by_location,key=lambda x: (-x[1]["Profit"],x[1]["CTP_Average"],-x[1]["Margin_Average"]))
        loc_data_sorted = sorted(data_by_location,key=lambda x: (x[1]["Time"],-x[1]["Profit"],x[1]["CTP_Average"]))
        loc_sorted = []
        for loc, data in loc_data_sorted:
            loc_sorted.append(loc)

        loc_id_list = [(self.tree.set(k, 'Location'), self.tree.set(k, 'Ratio'), k) for k in tree_children if self.tree.set(k, "Price") != "999/0"]
        loc_id_list_sorted = sorted(loc_id_list,key=lambda x: (loc_sorted.index(x[0].split("\t")[1]), float(x[1])))
        locationIndex = []
        for index, (l, r, k) in enumerate(loc_id_list_sorted):
            self.tree.move(k, '', index)
            capsule_loc_name = l.split("\t")[1]
            if capsule_loc_name not in locationIndex and int(float(r) != 1001):
                locationIndex.append(capsule_loc_name)
        self.tree.see(loc_id_list_sorted[0][2])
        self.root.update()

        #Generate razor script
        scriptString = '@setvar! "timeout" 650'
        for location in locationIndex:
            location_data = my_locations[location][2]
            location_character = location_data[0]
            book_hue = location_data[1]
            location_recall_code = location_data[2]
            location_button_code = location_data[3]
            vendors = vendors_by_location[location]
            vendor_one_name,vendor_one_serial = next(iter(vendors.items()))
            scriptString += f"""
if find {vendor_one_serial} ground any any 20
    overhead {vendor_one_name}
else
    @setvar! "myTome" 0
    for 3
        if findtype "runetome" backpack {book_hue} as "tome"
            @setvar! "myTome" "tome"
            break
        endif
        dclick backpack
        wait "timeout"
    endfor

    if "myTome" = 0
        overhead "NO TOME" 33
        stop
    endif
    if findtype "bank deposit safe" ground -1 -1 14 as "safe"
        getlabel "safe" "label"
        overhead "label"
        sysmsg "label"
    endif
    overhead "recalling to spot {location} in {location_character}'s book" 1159
    dclick "myTome"
    waitforgump 167090027 1000
    if not gumpexists 167090027
        dclick "myTome"
        waitforgump 167090027 2000
    endif
    gumpresponse {location_recall_code} 167090027
    waitforgump 167090027 2000
    gumpresponse {location_button_code} 167090027
    wait 500
endif

while not dead
    if hidden or cooldown "skill" > 0
        break
    endif
    skill "hiding"
    wait 200
    if insysmsg "You must be a friend of this house, or have a rental vendor, in order to hide here."
        break
    endif
endwhile
        
        """
            vendors = vendors_by_location[location]
            for vendor_name, vendor_serial in vendors.items():
                scriptString += f"""

removelist "itemDescriptions"
createlist "itemDescriptions"
clearignore

"""
                items = items_by_vendor[vendor_serial]
                
                for item_description_compare, item_serial in items.items():
                    scriptString += f"""
pushlist "itemDescriptions" "{item_description_compare}"

"""
                    
                scriptString += f"""
while not dead
    if find {vendor_serial} ground any any 20
        overhead "● ▼▼ HERE ▼▼ ●" 88 {vendor_serial}
        if findtype 3701 {vendor_serial} 0 0 0 as "mainBackpack"
            @setvar! "searching" 0
            dclick "mainBackpack"
            wait "timeout"
            @ignore "mainBackpack"

            while findtype "book|recall rune" "mainBackpack" as "decoys"
                @ignore "decoys"
            endwhile 
            if hidden
            else
                skill "hiding"
            endif
            while findtype 55390|2463|2594|2595|2596|2597|3203|3204|3206|3207|3211|3214|3215|3217|3219|3220|3221|3222|3223|3224|3225|3226|3227|3228|3229|3230|3231|3232|3233|3234|3235|3237|3238|3239|3240|3241|3242|3243|3255|3256|3257|3258|3259|3262|3263|3268|3271|3272|3273|3288|3302|3305|3306|3307|3308|3309|3310|3311|3312|3313|3314|3320|3323|3326|3329|3332|3340|3341|3342|3343|3344|3345|3346|3347|3348|3365|3366|3367|3368|3370|3372|3374|3376|3377|3381|3383|3391|3392|3492|3496|3519|3527|3528|3529|3531|3569|3591|3656|3657|3658|3659|3700|3714|3720|3722|3735|3736|3737|3738|3741|3764|3827|3835|3836|3837|3838|3839|3840|3841|3842|3843|3844|3856|3859|3861|3862|3865|3873|3877|3878|3885|3898|3910|3916|3918|3919|3936|3939|3985|3999|4201|4225|4226|4248|4249|4250|4251|4252|4253|4254|4255|4256|4257|4258|4259|4277|5039|5041|5043|5050|5114|5116|5118|5120|5122|5124|5126|5176|5178|5183|5186|5190|5191|5355|5356|5359|5360|5361|5362|5363|5364|5366|5374|5376|5377|5378|5379|5416|5418|5421|5661|5662|5899|5900|5901|5902|5903|5904|5905|5906|5981|5982|5983|5984|5985|5986|5987|5988|7116|7127|7128|7129|7130|7131|7132|7139|7140|7141|7142|7143|7144|7145|7146|7147|7148|7149|7150|7151|7152|7153|7154|7155|7156|7157|7158|7159|7160|7161|7162|7732|7866|8417|8438|8454|8455|8478|8479|8480|8481|8484|8501|8502|8503|8750|8751|8752|8753|8826|10247|10324|10527|10827|11761|11762|11763|11764|12282|12320|12321|12322|12323|12324|12686|13278|13290|13291|13292|13297|13298|13299|13300|13301|13305|13307|13308|13309|13310|13311|13312|13313|13314|13316|13318|13319|13320|13321|13328|13330|13335|13336|14428|14442|14444|14448|14450|14451|14454|14456|14458|14470|14484|14490|14496|14506|14512|14514|14520|14522|14530|14536|14538|14542|14544|14562|14568|14571|14574|14594|15178|15293|15294|15295|15296|15297|15298|15577|15580|15635|15638|16898|17083|17087|17686|18218|18233|18282|18283|18400|18652 "mainBackpack" as "foundItem"
                getlabel "foundItem" "desc"
                if inlist "itemDescriptions" "desc"
                    menu "foundItem" 0
                    waitforgump 4274928655 1000
                    gumpresponse 1
                    wait 100
                    if findtype "bank deposit safe" ground -1 -1 14 as "safe"
                        getlabel "safe" "label"
                        overhead "label"
                    endif
                    wait 100
                endif
                @ignore "foundItem"
            endwhile
            while findtype 18653|18658|18704|19199|19226|19227|19228|19229|19230|19231|19232|19234|19235|19236|19237|19238|19239|19240|19241|19242|19246|19247|19248|19249|19250|19251|19252|19253|19254|19256|19370|19372|19508|19512|19513|19520|19521|19522|19524|19525|19532|20501|20374|20375|20376|20377|20378|20379|20381|20383|20384|20385|20391|20392|20466|20467|20495|20496|21397|21398|21399|21400|21401|21402|21403|21404|21405|21780|21781|21783|21784|21785|21786|21787|21788|21789|21790|21791|21797|21798|21799|21800|21801|21803|21804|21805|21806|21807|21808|21809|21810|21814|21818|21824|21826|21827|21828|21829|21830|21831|21835|21836|21838|21840|21841|21842|21843|21844|21845|21847|21848|21849|21852|21853|21856|21859|21860|21861|21862|21863|21864|21865|21866|21867|21868|21870|21871|21872|21873|21874|21875|21876|21877|21878|21879|21880|21881|21882|21883|21884|21885|21886|21889|21891|21893|21894|21895|21896|21897|21898|21899|21901|21902|21904|21905|21906|21907|21908|21909|21911|21917|21918|21921|21923|21924|21925|21926|21927|21929|21931|21933|21934|21935|21936|21937|21938|21939|21940|21942|21943|21944|21945|21947|21948|21949|21950|21951|21953|21954|21956|21957|21960|21962|21963|21964|21969|21978|21981|21988|21996|21997|21998|21999|22151|22152|22153|22154|22155|22157|22158|22163|22164|22165|22166|22167|22168|22169|22170|22171|22172|22173|22174|22175|22177|22178|22179|22180|22181|22182|22183|22184|22185 "mainBackpack" as "foundItem"
                getlabel "foundItem" "desc"
                if inlist "itemDescriptions" "desc"
                    menu "foundItem" 0
                    waitforgump 4274928655 1000
                    gumpresponse 1
                    wait 100
                    if findtype "bank deposit safe" ground -1 -1 14 as "safe"
                        getlabel "safe" "label"
                        overhead "label"
                    endif
                    wait 100
                endif
                @ignore "foundItem"
            endwhile
            while findtype 22186|22188|22189|22190|22191|22192|22193|22194|22195|22196|22197|22199|22261|22264|22272|22285|22286|22287|22288|22289|22290|22291|22292|22293|22294|22295|22296|22297|22298|22336|22417|22418|22419|22420|22421|22422|22423|22426|22427|22428|22429|22430|22431|22432|22433|22434|22435|22436|22437|22438|22439|22440|22441|22442|22443|22444|22445|22449|22451|22453|22455|22456|23009|23034|23035|23774|23996|23997|24175|24179|24181|24182|24183|24184|24187|24188|24190|24191|24193|24195|24196|24197|24199|24246|24382|24383|24384|24385|24386|24387|24388|24389|24390|24391|24392|24393|24394|24395|24396|24397|24398|24399|24400|24401|24402|24403|24404|24405|24406|24407|24408|24409|24410|24411|24412|24413|24414|24415|24416|24417|24418|24419|24420|24421|24422|24423|24424|24425|24426|24427|24428|24429|24430|24431|24432|24433|24434|25647|25759|26640|26664|26669|26670|26671|26672|26688|26689|26693|26700|26701|26719|26720|26721|26724|26732|26734|26735|26736|26737|27561|27562|27563|27564|27565|27577|27580|27584|27611|27612|27640|27642|28760|28765|28768|28775|28795|28799|28803|28908|28909|28910|28911|28924|28994|28995|29024|29025|29026|29027|29028|29029|29031|29032|29033|29034|29035|29036|29037|29038|29040|29104|29106|29107|29108|29142|29350|29030|29352|29354|29355|29421|29382|29425|29428|29430|29431|29463|29495|29497|29498|29502 "mainBackpack" as "foundItem"
                getlabel "foundItem" "desc"
                if inlist "itemDescriptions" "desc"
                    menu "foundItem" 0
                    waitforgump 4274928655 1000
                    gumpresponse 1
                    wait 100
                    if findtype "bank deposit safe" ground -1 -1 14 as "safe"
                        getlabel "safe" "label"
                        overhead "label"
                    endif
                    wait 100
                endif
                @ignore "foundItem"
            endwhile
            while findtype 30561|30562|30563|30564|30565|30566|30567|30568|30573|30574|30575|30576|30577|30578|30579|30580|30582|30583|30586|30587|30588|30589|30590|30591|30592|30596|30599|30601|30602|30603|30604|30608|30609|30610|30611|30612|30613|30614|30615|30617|30618|30621|30622|30623|30624|30625|30626|30627|30628|30629|30630|30631|30632|30633|30634|30635|30636|30637|30638|30639|30640|30641|30642|30643|30644|30645|30646|30647|30648|30649|30650|30651|30652|30653|30655|30657|30658|30659|30660|30661|30662|30663|30766|30767|30768|30769|30770|30771|30772|30773|30775|30776|30778|30818|30819|30821|30822|30823|30825|30826|30827|30828|30829|30850|30851|30852|30853|30854|30855|30856|30857|30858|30859|30860|30866|30867|30868|30869|30870|30871|30872|30878|30967|30969|30970|30971|30972|30973|30974|30975|30976|30977|30978|30979|30980|30981|30982|30983|30984|30985|30986|36752|39264|39343|39344|39345|39346|39347|39348|39349|39350|39351|39352|39353 "mainBackpack" as "foundItem"
                getlabel "foundItem" "desc"
                if inlist "itemDescriptions" "desc"
                    menu "foundItem" 0
                    waitforgump 4274928655 1000
                    gumpresponse 1
                    wait 100
                    if findtype "bank deposit safe" ground -1 -1 14 as "safe"
                        getlabel "safe" "label"
                        overhead "label"
                    endif
                    wait 100
                endif
                @ignore "foundItem"
            endwhile
            while findtype 41459|41460|41461|41462|41510|42227|42239|42240|42242|42243|42244|42517|42574|42665|43159|43160|43161|43162|43163|43164|43165|43166|43167|43168|43169|43170|43171|43172|43173|43174|43175|43176|43177|43178|43179|43180|43181|43182|43206|43207|43208|43209|43210|43277|43279|43320|44310|44312|44314|44795|44796|44797|44798|44799|44800|44801|44804|44805|44808|44810|44986|45002|45120|45156|45157|45182|45193|45208|45211|45214|45216|45218|45220|45222|45235|45236|45238|45239|45241|45242|45246|45247|45248|45250|45251|45252|45254|45255|45257|45281|45282|45300|45315|45316|45371|45372|45373|45374|45375|45376|45377|45378|45379|45380|45381|45382|45383|45384|45385|45386|45387|45388|45389|45390|45391|45392|45393|45394|45395|45396|45397|45398|45399|45400|45401|45402|45403|45404|45405|45406|45407|45408|45409|45410|45411|45412|45413|45414|45415|45416|45417|45418|45419|45420|45421|45422|45423|45424|45425|45426|45427|45428|45429|45430|45828|45830|47107|47109|47111|48357|48358|48359|48360|48361|48362|48363|48364|48365|48366|48367|48368|48369|48370|48371|48372|48373|48374|48375|48376|48377|48378|48379|48380|48381|48382|48383|48384|48385|48386|48387|48388|48389|48390|48391|48392|48393|48394|48395|48396|48397|48398|48399|48400|48401|48402|48403|48404|48405|48406|48407|50298|50308|50675|51078|51094|51098|51100|51200|51201|51202|51203|51204|51205|51206|51207|51208|51209|51210|51211|51212|51213|51214 "mainBackpack" as "foundItem"
                getlabel "foundItem" "desc"
                if inlist "itemDescriptions" "desc"
                    menu "foundItem" 0
                    waitforgump 4274928655 1000
                    gumpresponse 1
                    wait 100
                    if findtype "bank deposit safe" ground -1 -1 14 as "safe"
                        getlabel "safe" "label"
                        overhead "label"
                    endif
                    wait 100
                endif
                @ignore "foundItem"
            endwhile
            while findtype 51215|51216|51217|51218|51219|51220|51221|51222|51223|51224|51225|51226|51227|51228|51229|51230|51231|51232|51233|51234|51235|51236|51237|51238|51239|51240|51241|51242|51243|51244|51245|51246|51247|51248|51249|51250|51251|51252|51253|51254|51255|51256|51257|51258|51259|51260|51261|51262|51263|51264|51265|51266|51267|51268|51269|51270|51271|51272|51273|51274|51275|51276|51277|51278|51279|51280|51281|51282|51283|51284|51285|51286|51287|51288|51289|51290|51291|51292|51293|51294|51295|51296|51297|51298|51299|51300|51301|51302|51303|51304|51305|51306|51307|51308|51309|51310|51311|51312|51313|51314|51315|51316|51317|51318|51319|51320|51321|51322|51323|51324|51325|51326|51327|51328|51329|51330|51331|51332|51333|51334|51335|51336|51337|51338|51339|51340|51341|51342|51343|51344|51345|51346|51347|51348|51349|51350|51351|51352|51353|51354|51355|51356|51357|51358|51359|51360|51361|51362|51363|51364|51365|51366|51367|51368|51369|51370|51371|51372|51373|51374|51375|51400|51401|51402|51403|51404|51405|51406|51407|51408|51409|51430|51431|51432|51433|51434|51435|51436|51437|51438|51439|51440|51441|51442|51443|51444|51445|51446|51447|51448|51449|51470|51471|51472|51473|51474|51475|51476|51477|51478|51479|53547|53548|53549|53550|53551|53552|53553|53554|53555|53556|53557|53558|53559|53560|53561|53562|53563|53564|53565|53566|53567|53568|53569|53570|53571|53572|53573|53574|53575|53576|53577|53578|53579|53580|53581|53582|53583|53584|53585|53586|53587|53588|53589|53590|53591|53592|53593|53594|53595|53596|53597|53598|53599|53600|53601|53602|53603|53604|53605|53606|53607|53608|53609|53610|53611 "mainBackpack" as "foundItem"
                getlabel "foundItem" "desc"
                if inlist "itemDescriptions" "desc"
                    menu "foundItem" 0
                    waitforgump 4274928655 1000
                    gumpresponse 1
                    wait 100
                    if findtype "bank deposit safe" ground -1 -1 14 as "safe"
                        getlabel "safe" "label"
                        overhead "label"
                    endif
                    wait 100
                endif
                @ignore "foundItem"
            endwhile

            while findtype 2472|2473|2474|2475|2476|2480|2481|2482|2604|2605|2606|2607|2608|2609|2610|2611|2612|2613|2614|2615|2616|2617|2618|2619|2620|2621|2622|2623|2624|2625|2626|2627|2628|2629|2630|2631|2632|2633|2634|2635|2636|2637|2638|2639|2640|2641|2642|2643|2711|2712|2713|2714|2715|2716|2717|2718|3644|3645|3646|3647|3648|3649|3650|3651|3701|3702|3703|3704|3705|3706|3708|3709|3710|3711|3712|7808|7809|9002|9003|11010|11011|12657|29833|29832 "mainBackpack" as "subContainer"
                @ignore "subContainer"
                getlabel "subContainer" "desc"
                if "Price: Not for sale" in "desc"
                    dclick "subContainer"
                    wait "timeout"
                    @setvar! "searching" 1
                endif
                if hidden
                else
                    skill "hiding"
                endif
            endwhile

            if "searching" == 1
                while findtype "book|recall rune" "mainBackpack" as "decoys"
                    @ignore "decoys"
                endwhile 
                if hidden
                else
                    skill "hiding"
                endif
                while findtype 55390|2463|2594|2595|2596|2597|3203|3204|3206|3207|3211|3214|3215|3217|3219|3220|3221|3222|3223|3224|3225|3226|3227|3228|3229|3230|3231|3232|3233|3234|3235|3237|3238|3239|3240|3241|3242|3243|3255|3256|3257|3258|3259|3262|3263|3268|3271|3272|3273|3288|3302|3305|3306|3307|3308|3309|3310|3311|3312|3313|3314|3320|3323|3326|3329|3332|3340|3341|3342|3343|3344|3345|3346|3347|3348|3365|3366|3367|3368|3370|3372|3374|3376|3377|3381|3383|3391|3392|3492|3496|3519|3527|3528|3529|3531|3569|3591|3656|3657|3658|3659|3700|3714|3720|3722|3735|3736|3737|3738|3741|3764|3827|3835|3836|3837|3838|3839|3840|3841|3842|3843|3844|3856|3859|3861|3862|3865|3873|3877|3878|3885|3898|3910|3916|3918|3919|3936|3939|3985|3999|4201|4225|4226|4248|4249|4250|4251|4252|4253|4254|4255|4256|4257|4258|4259|4277|5039|5041|5043|5050|5114|5116|5118|5120|5122|5124|5126|5176|5178|5183|5186|5190|5191|5355|5356|5359|5360|5361|5362|5363|5364|5366|5374|5376|5377|5378|5379|5416|5418|5421|5661|5662|5899|5900|5901|5902|5903|5904|5905|5906|5981|5982|5983|5984|5985|5986|5987|5988|7116|7127|7128|7129|7130|7131|7132|7139|7140|7141|7142|7143|7144|7145|7146|7147|7148|7149|7150|7151|7152|7153|7154|7155|7156|7157|7158|7159|7160|7161|7162|7732|7866|8417|8438|8454|8455|8478|8479|8480|8481|8484|8501|8502|8503|8750|8751|8752|8753|8826|10247|10324|10527|10827|11761|11762|11763|11764|12282|12320|12321|12322|12323|12324|12686|13278|13290|13291|13292|13297|13298|13299|13300|13301|13305|13307|13308|13309|13310|13311|13312|13313|13314|13316|13318|13319|13320|13321|13328|13330|13335|13336|14428|14442|14444|14448|14450|14451|14454|14456|14458|14470|14484|14490|14496|14506|14512|14514|14520|14522|14530|14536|14538|14542|14544|14562|14568|14571|14574|14594|15178|15293|15294|15295|15296|15297|15298|15577|15580|15635|15638|16898|17083|17087|17686|18218|18233|18282|18283|18400|18652 "mainBackpack" as "foundItem"
                    getlabel "foundItem" "desc"
                    if inlist "itemDescriptions" "desc"
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 100
                        if findtype "bank deposit safe" ground -1 -1 14 as "safe"
                            getlabel "safe" "label"
                            overhead "label"
                        endif
                        wait 100
                    else
                        @ignore "foundItem"
                    endif
                endwhile
                while findtype 18653|18658|18704|19199|19226|19227|19228|19229|19230|19231|19232|19234|19235|19236|19237|19238|19239|19240|19241|19242|19246|19247|19248|19249|19250|19251|19252|19253|19254|19256|19370|19372|19508|19512|19513|19520|19521|19522|19524|19525|19532|20501|20374|20375|20376|20377|20378|20379|20381|20383|20384|20385|20391|20392|20466|20467|20495|20496|21397|21398|21399|21400|21401|21402|21403|21404|21405|21780|21781|21783|21784|21785|21786|21787|21788|21789|21790|21791|21797|21798|21799|21800|21801|21803|21804|21805|21806|21807|21808|21809|21810|21814|21818|21824|21826|21827|21828|21829|21830|21831|21835|21836|21838|21840|21841|21842|21843|21844|21845|21847|21848|21849|21852|21853|21856|21859|21860|21861|21862|21863|21864|21865|21866|21867|21868|21870|21871|21872|21873|21874|21875|21876|21877|21878|21879|21880|21881|21882|21883|21884|21885|21886|21889|21891|21893|21894|21895|21896|21897|21898|21899|21901|21902|21904|21905|21906|21907|21908|21909|21911|21917|21918|21921|21923|21924|21925|21926|21927|21929|21931|21933|21934|21935|21936|21937|21938|21939|21940|21942|21943|21944|21945|21947|21948|21949|21950|21951|21953|21954|21956|21957|21960|21962|21963|21964|21969|21978|21981|21988|21996|21997|21998|21999|22151|22152|22153|22154|22155|22157|22158|22163|22164|22165|22166|22167|22168|22169|22170|22171|22172|22173|22174|22175|22177|22178|22179|22180|22181|22182|22183|22184|22185 "mainBackpack" as "foundItem"
                    getlabel "foundItem" "desc"
                    if inlist "itemDescriptions" "desc"
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 100
                        if findtype "bank deposit safe" ground -1 -1 14 as "safe"
                            getlabel "safe" "label"
                            overhead "label"
                        endif
                        wait 100
                    endif
                    @ignore "foundItem"
                endwhile
                while findtype 22186|22188|22189|22190|22191|22192|22193|22194|22195|22196|22197|22199|22261|22264|22272|22285|22286|22287|22288|22289|22290|22291|22292|22293|22294|22295|22296|22297|22298|22336|22417|22418|22419|22420|22421|22422|22423|22426|22427|22428|22429|22430|22431|22432|22433|22434|22435|22436|22437|22438|22439|22440|22441|22442|22443|22444|22445|22449|22451|22453|22455|22456|23009|23034|23035|23774|23996|23997|24175|24179|24181|24182|24183|24184|24187|24188|24190|24191|24193|24195|24196|24197|24199|24246|24382|24383|24384|24385|24386|24387|24388|24389|24390|24391|24392|24393|24394|24395|24396|24397|24398|24399|24400|24401|24402|24403|24404|24405|24406|24407|24408|24409|24410|24411|24412|24413|24414|24415|24416|24417|24418|24419|24420|24421|24422|24423|24424|24425|24426|24427|24428|24429|24430|24431|24432|24433|24434|25647|25759|26640|26664|26669|26670|26671|26672|26688|26689|26693|26700|26701|26719|26720|26721|26724|26732|26734|26735|26736|26737|27561|27562|27563|27564|27565|27577|27580|27584|27611|27612|27640|27642|28760|28765|28768|28775|28795|28799|28803|28908|28909|28910|28911|28924|28994|28995|29024|29025|29026|29027|29028|29029|29031|29032|29033|29034|29035|29036|29037|29038|29040|29104|29106|29107|29108|29142|29350|29030|29352|29354|29355|29421|29382|29425|29428|29430|29431|29463|29495|29497|29498|29502 "mainBackpack" as "foundItem"
                    getlabel "foundItem" "desc"
                    if inlist "itemDescriptions" "desc"
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 100
                        if findtype "bank deposit safe" ground -1 -1 14 as "safe"
                            getlabel "safe" "label"
                            overhead "label"
                        endif
                        wait 100
                    endif
                    @ignore "foundItem"
                endwhile
                while findtype 30561|30562|30563|30564|30565|30566|30567|30568|30573|30574|30575|30576|30577|30578|30579|30580|30582|30583|30586|30587|30588|30589|30590|30591|30592|30596|30599|30601|30602|30603|30604|30608|30609|30610|30611|30612|30613|30614|30615|30617|30618|30621|30622|30623|30624|30625|30626|30627|30628|30629|30630|30631|30632|30633|30634|30635|30636|30637|30638|30639|30640|30641|30642|30643|30644|30645|30646|30647|30648|30649|30650|30651|30652|30653|30655|30657|30658|30659|30660|30661|30662|30663|30766|30767|30768|30769|30770|30771|30772|30773|30775|30776|30778|30818|30819|30821|30822|30823|30825|30826|30827|30828|30829|30850|30851|30852|30853|30854|30855|30856|30857|30858|30859|30860|30866|30867|30868|30869|30870|30871|30872|30878|30967|30969|30970|30971|30972|30973|30974|30975|30976|30977|30978|30979|30980|30981|30982|30983|30984|30985|30986|36752|39264|39343|39344|39345|39346|39347|39348|39349|39350|39351|39352|39353 "mainBackpack" as "foundItem"
                    getlabel "foundItem" "desc"
                    if inlist "itemDescriptions" "desc"
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 100
                        if findtype "bank deposit safe" ground -1 -1 14 as "safe"
                            getlabel "safe" "label"
                            overhead "label"
                        endif
                        wait 100
                    endif
                    @ignore "foundItem"
                endwhile
                while findtype 41459|41460|41461|41462|41510|42227|42239|42240|42242|42243|42244|42517|42574|42665|43159|43160|43161|43162|43163|43164|43165|43166|43167|43168|43169|43170|43171|43172|43173|43174|43175|43176|43177|43178|43179|43180|43181|43182|43206|43207|43208|43209|43210|43277|43279|43320|44310|44312|44314|44795|44796|44797|44798|44799|44800|44801|44804|44805|44808|44810|44986|45002|45120|45156|45157|45182|45193|45208|45211|45214|45216|45218|45220|45222|45235|45236|45238|45239|45241|45242|45246|45247|45248|45250|45251|45252|45254|45255|45257|45281|45282|45300|45315|45316|45371|45372|45373|45374|45375|45376|45377|45378|45379|45380|45381|45382|45383|45384|45385|45386|45387|45388|45389|45390|45391|45392|45393|45394|45395|45396|45397|45398|45399|45400|45401|45402|45403|45404|45405|45406|45407|45408|45409|45410|45411|45412|45413|45414|45415|45416|45417|45418|45419|45420|45421|45422|45423|45424|45425|45426|45427|45428|45429|45430|45828|45830|47107|47109|47111|48357|48358|48359|48360|48361|48362|48363|48364|48365|48366|48367|48368|48369|48370|48371|48372|48373|48374|48375|48376|48377|48378|48379|48380|48381|48382|48383|48384|48385|48386|48387|48388|48389|48390|48391|48392|48393|48394|48395|48396|48397|48398|48399|48400|48401|48402|48403|48404|48405|48406|48407|50298|50308|50675|51078|51094|51098|51100|51200|51201|51202|51203|51204|51205|51206|51207|51208|51209|51210|51211|51212|51213|51214 "mainBackpack" as "foundItem"
                    getlabel "foundItem" "desc"
                    if inlist "itemDescriptions" "desc"
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 100
                        if findtype "bank deposit safe" ground -1 -1 14 as "safe"
                            getlabel "safe" "label"
                            overhead "label"
                        endif
                        wait 100
                    endif
                    @ignore "foundItem"
                endwhile
                while findtype 51215|51216|51217|51218|51219|51220|51221|51222|51223|51224|51225|51226|51227|51228|51229|51230|51231|51232|51233|51234|51235|51236|51237|51238|51239|51240|51241|51242|51243|51244|51245|51246|51247|51248|51249|51250|51251|51252|51253|51254|51255|51256|51257|51258|51259|51260|51261|51262|51263|51264|51265|51266|51267|51268|51269|51270|51271|51272|51273|51274|51275|51276|51277|51278|51279|51280|51281|51282|51283|51284|51285|51286|51287|51288|51289|51290|51291|51292|51293|51294|51295|51296|51297|51298|51299|51300|51301|51302|51303|51304|51305|51306|51307|51308|51309|51310|51311|51312|51313|51314|51315|51316|51317|51318|51319|51320|51321|51322|51323|51324|51325|51326|51327|51328|51329|51330|51331|51332|51333|51334|51335|51336|51337|51338|51339|51340|51341|51342|51343|51344|51345|51346|51347|51348|51349|51350|51351|51352|51353|51354|51355|51356|51357|51358|51359|51360|51361|51362|51363|51364|51365|51366|51367|51368|51369|51370|51371|51372|51373|51374|51375|51400|51401|51402|51403|51404|51405|51406|51407|51408|51409|51430|51431|51432|51433|51434|51435|51436|51437|51438|51439|51440|51441|51442|51443|51444|51445|51446|51447|51448|51449|51470|51471|51472|51473|51474|51475|51476|51477|51478|51479|53547|53548|53549|53550|53551|53552|53553|53554|53555|53556|53557|53558|53559|53560|53561|53562|53563|53564|53565|53566|53567|53568|53569|53570|53571|53572|53573|53574|53575|53576|53577|53578|53579|53580|53581|53582|53583|53584|53585|53586|53587|53588|53589|53590|53591|53592|53593|53594|53595|53596|53597|53598|53599|53600|53601|53602|53603|53604|53605|53606|53607|53608|53609|53610|53611 "mainBackpack" as "foundItem"
                    getlabel "foundItem" "desc"
                    if inlist "itemDescriptions" "desc"
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 100
                        if findtype "bank deposit safe" ground -1 -1 14 as "safe"
                            getlabel "safe" "label"
                            overhead "label"
                        endif
                        wait 100
                    else
                        @ignore "foundItem"
                    endif
                endwhile
            endif
        endif
        break
    else
        wait "timeout"
    endif
endwhile"""
        self.root.clipboard_clear()
        self.root.clipboard_append(scriptString)
        self.root.update()

def catch_assistant_handles():
    windows = pywinauto.Desktop(backend="win32").windows()
    assistant_windows = [window for window in windows if window.is_visible() and "([None])" in window.window_text()]
    assistant_list = list()
    for window in assistant_windows:
        char_name_search = re.search(r"(?:-\s)?([\w\s]+)\s\(\[",window.window_text())
        char_name = char_name_search.group(1) if char_name_search else ""
        assistant_list.append((char_name, window.handle))
    return assistant_list

def Check_Razor_Assistant(hWnd=329188):
    try:
        app = pywinauto.Application().connect(handle=hWnd)
        window = app.window(handle=hWnd)
    except Exception as e:
        print(f"Check_Razor_Assistant: Window not found. Error: {e}")
        return None
    script_editor = window.child_window(auto_id="scriptEditor", control_type="FastColoredTextBoxNS.FastColoredTextBox")
    if script_editor.is_enabled():
        return False
    else:
        return True

async def fetch(session, url, headers, cookies):
    async with session.get(url, headers=headers, cookies=cookies) as response:
        return await response.content.read()
    
async def fetch_with_extra_data(session, url, headers, cookies, extra_data):
    content = await fetch(session, url, headers, cookies)
    return {"content": content, "url": url, "extra_data": extra_data}

async def request_gen_simple():
    string_list = [
        ("survival gear OR chromatic OR ankh token OR battle commendation OR mastercrafting diagram OR skill mastery orb OR plant chemicals OR arcane scroll OR (skill mastery scroll OR aspect core) AND (chivalry OR inscription OR tailoring OR peacemaking OR taste id OR arcane OR eldritch OR void OR poison aspect core OR shadow OR air aspect core OR artisan OR harvest)", 0.8),
        ("research materials OR prevalia coins OR an emote deed OR clothing bless deed OR strongbox customization OR treasure undeciphered", 0.9),
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    cookies = RequestsCookieJar()
    cookies.set("app", user_config["outlands_cookie"])

    quick_prices = collate_price_dicts(core_prices,distil_prices,tmap_prices,scroll_prices,misc_crafting_prices,misc_hp_prices,misc_lp_prices,deed_prices)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for item in string_list:
            searchString, price_ratio = item
            page_url = "https://outlandmalls.com/?item=" + quote_plus(searchString) + "&search_category_id=0"
            tasks.append(fetch_with_extra_data(session, page_url, headers, cookies,price_ratio))
        
        responses = await asyncio.gather(*tasks)

        return [(response["content"], quick_prices, response["url"], 60, 1, response["extra_data"]) for response in responses]

class AssMonGui:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("AssMon")
        self.top.minsize(180,60)
        self.top.maxsize(210,60)
        self.top.attributes('-topmost', True)
        self.handles_to_monitor = catch_assistant_handles()
        self.monitoring = True
        self.top.protocol("WM_DELETE_WINDOW", self.on_close)

        self.char1 = self.handles_to_monitor[0]
        self.char2 = self.handles_to_monitor[1]
        self.char3 = self.handles_to_monitor[2]

        self.bool1 = tk.BooleanVar()
        self.bool2 = tk.BooleanVar()
        self.bool3 = tk.BooleanVar()

        self.prev_state1 = False
        self.prev_state2 = False
        self.prev_state3 = False

        self.label1 = tk.Label(self.top, text=self.char1[0])
        self.label1.pack()
        self.label2 = tk.Label(self.top, text=self.char2[0])
        self.label2.pack()
        self.label3 = tk.Label(self.top, text=self.char3[0])
        self.label3.pack()

    def update_booleans(self, bool_values):
        self.label1.config(text=f"{self.char1[0]}: {'Running' if bool_values.get('bool1', False) else 'Not Running'}",
                        bg="green" if bool_values.get('bool1', False) else "red")
        self.label2.config(text=f"{self.char2[0]}: {'Running' if bool_values.get('bool2', False) else 'Not Running'}",
                        bg="green" if bool_values.get('bool2', False) else "red")
        self.label3.config(text=f"{self.char3[0]}: {'Running' if bool_values.get('bool3', False) else 'Not Running'}",
                        bg="green" if bool_values.get('bool3', False) else "red")

        self.prev_state1 = bool_values.get('bool1')
        self.prev_state2 = bool_values.get('bool2')
        self.prev_state3 = bool_values.get('bool3')

    def monitor_daemon(self):
        while self.monitoring:
            bool_values = defaultdict(bool)
            bool_values['bool1'] = Check_Razor_Assistant(self.char1[1])
            bool_values['bool2'] = Check_Razor_Assistant(self.char2[1])
            bool_values['bool3'] = Check_Razor_Assistant(self.char3[1])
            self.top.after(0, lambda: self.update_booleans(bool_values))
            time.sleep(1)

    def on_close(self):
        self.monitoring = False  # This will stop the monitor_daemon loop
        self.top.destroy()  # Destroy the Toplevel window

    def start_monitoring(self):
        self.monitor_thread = threading.Thread(target=self.monitor_daemon, daemon=True)
        self.monitor_thread.start()

def start_purchase_script():
    append_recall_home_script()
    #mouse_pos = win32api.GetCursorPos()
    window = None
    active_window = gw.getActiveWindow()
    active_title = active_window.title
    regex_client = r"UO - ([\w\s]+) - ClassicUO"
    regex_assistant = r"(?:\] - )?([\w\s]+) \(\[None\]\)"
    match_client = re.search(regex_client, active_title)
    match_assistant = re.search(regex_assistant, active_title)
    if match_client: #if focus is on client, switch to assistant and set it as target
        original = connect_to_window(active_window._hWnd)
        if not original:
            print("start_purchase_script 1: Something went wrong when selecting original window")
            return
        extracted_name = match_client.group(1)
        try:
            window = focus_named_assistant(extracted_name)
        except Exception as e:
            print(f"start_purchase_script 22: Error: {e}")
    elif match_assistant: #if focus is on assistant, set assistant as target
        extracted_name = match_assistant.group(1)
        for window in gw.getAllWindows():
            if extracted_name in window.title and window != active_window:
                original = connect_to_window(window._hWnd)
                break
        if not original:
            print("start_purchase_script 3: Something went wrong when selecting original window")
            return
        window = connect_to_window(active_window._hWnd)
    else:
        print("start_purchase_script 4: No match found in the active window's title.")
        return
    if not window:
        print("start_purchase_script 5: Error connecting to window")
        return False
    tab_control = window.TabControl
    if tab_control.get_selected_tab() != 9:
        tab_control.select("TabControlScripts")
    tree = window.TreeView
    node = tree.get_item(['aaaTempScript'])
    if not node.is_selected():
        node.select()
    try:
        script_editor = window.child_window(auto_id="scriptEditor", control_type="FastColoredTextBoxNS.FastColoredTextBox")
        scripts_tab = window.child_window(title="Scripts", auto_id="subScripts", control_type="System.Windows.Forms.TabPage")
        if scripts_tab.exists():
            scripts_tab.click()
            time.sleep(.01)
        if script_editor.is_enabled():
            script_editor.set_focus()
            time.sleep(.01)
            script_editor.type_keys("^a")
            time.sleep(.01)
            script_editor.type_keys("^v")
            time.sleep(.01)
            play_button = window.child_window(title="Scripts", auto_id="subScripts", control_type="System.Windows.Forms.TabPage")\
                .child_window(auto_id="tableLayoutPanel1", control_type="System.Windows.Forms.TableLayoutPanel")\
                .child_window(auto_id="tableLayoutPanel2", control_type="System.Windows.Forms.TableLayoutPanel")\
                .child_window(title="Play", auto_id="playScript", control_type="System.Windows.Forms.Button")
            if play_button.exists():
                play_button.click()
                time.sleep(.01)
                original.set_focus()
            else:
                print('start_purchase_script 6: Play button missing!')
                return
        else:
            stop_button = window.child_window(title="Scripts", auto_id="subScripts", control_type="System.Windows.Forms.TabPage")\
                .child_window(auto_id="tableLayoutPanel1", control_type="System.Windows.Forms.TableLayoutPanel")\
                .child_window(auto_id="tableLayoutPanel2", control_type="System.Windows.Forms.TableLayoutPanel")\
                .child_window(title="Stop", auto_id="playScript", control_type="System.Windows.Forms.Button")
            if stop_button.exists():
                stop_button.click()
                time.sleep(.01)
                original.set_focus()
            else:
                print('start_purchase_script 7: Stop button missing!')
                return
    except Exception as e:
        print(f"start_purchase_script 8: Error: {e}")
    #win32api.SetCursorPos(mouse_pos)
        
def append_recall_home_script():
    try:
        current_content = root_ghost.root.clipboard_get()
        append_string = """
wait 1000
script 'AliRoom'
"""
        new_content = current_content + append_string
        pyperclip.copy(new_content)

    except Exception as e:
        print(f"append_recall_home_script: Error: {e}")


user_config = {}
root_ghost = False
def main():
    global user_config
    global root_ghost
    user_config = load_config()
    print(user_config)
    keyboard.add_hotkey("ctrl+alt+c", start_purchase_script)
    keyboard.add_hotkey("ctrl+alt+`", switch_focus)
    keyboard.add_hotkey("alt+shift+`", lambda: focus_scraper())
    root = tk.Tk()
    root_ghost = AliApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()