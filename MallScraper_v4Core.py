#TODO clothes,boat stuff (crew, upgrades), jugglin torches n shit
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
import tkinter as tk
from tkinter import ttk
from multiprocessing import Pool, cpu_count
from bs4 import BeautifulSoup
from contextlib import contextmanager
from urllib.parse import quote_plus
from collections import defaultdict
import keyboard
import pywinauto
import numpy as np
import json
import pyautogui
import socket
from OutlandsDicts import *
from OutlandsUtils import *

logging.basicConfig(
    level=logging.DEBUG,  # Set the minimum log level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Format for log messages
    datefmt='%Y-%m-%d %H:%M:%S',  # Format for timestamps
    handlers=[
        logging.StreamHandler(),  # Output logs to console
        logging.FileHandler('app.log')  # Output logs to a file
    ]
)
logger = logging.getLogger('my_logger')

clipboard_ghost = ""

def multi_parse_wide(in_tuple):
    item = in_tuple[0]
    price_depth = in_tuple[1]
    time_frame = in_tuple[2]
    cutoff_threshold = in_tuple[3]
    corrupted_link_price_threshold = 200000
    steps = {
        "Aspect Core": core_prices,
        "Aspect Extract": extract_prices,
        "Aspect Distillation": distil_prices,
        "Undeciphered": map_prices,
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
    failsafe = 0 #todo: decide on whether to retry if time out
    process_id = os.getpid()
    print(f'start: {process_id}: {item}')
    
    while i < 10:
        #print(i)
        time.sleep(1)
        if i > 0:
            temp_url = f"{page_url}&page={i}"
        else:
            temp_url = page_url
        #print(temp_url)
        cookie = {"app": "MTcxNzkxMTY0NXxyMy1fUlZXNkswcGRXZEhXNWpZOXdHY1FQMHhSQ1Z4VUp0MnFlNkQxdWlKMnExdUNyRDFtaFBBSmpJNGRZUXZjYkdndFhFNWRFaFZDQXJ0emg3VjJfTllSd2FmZWdXOW1kTEF4MHNsdHJEQUJHYlU9fGerm92O8uhh1zqXUJc5DO5U3HJ2gx6aQKYCEwXjuI9S"}
        response = requests.get(temp_url, headers=headers, cookies=cookie)
        if response.status_code != 200:
            print(f"Failed to retrieve the webpage: {item}. Status code: {response.status_code}")
            if failsafe == 0:
                break
            failsafe = 0
            time.sleep(.3)
            continue
        # result = None
        soup = BeautifulSoup(response.content, 'lxml')
        if soup:
            # results_table = soup.find('table',style="display: block; border: none;")
            # if results_table:
            #     results = results_table.find_all('em')
            #     if len(results):
            #         result = results[0].text.strip().replace(',', '')
            #         try:
            #             result = int(result)
            #         except Exception as e:
            #             print(f"Error: {e}. {temp_url}:{results[0].text.strip()}")
            # else:
            #     print('summit went awry, results table missing')
            #     print(temp_url)
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

    print(f'end: {process_id}: {item}')
    out_data = []
    for row in agg_rows:
        cells = row.find_all('td')
        time_cell = cells[8]
        time_string = time_cell.text.strip().lower()  # Convert to lowercase for consistent comparison
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
            check_dist = float('inf')
            closest = None
            for location_name, tuple_loc in my_locations.items():
                x2 = int(tuple_loc[0])
                y2 = int(tuple_loc[1])
                distance = get_distance(x1,y1,x2,y2)
                if distance < check_dist:
                    check_dist = distance
                    closest = location_name
            location_name = closest if closest else 'N/A'
            formatted_location_link = f"{location_link_split[0]}?{vendor_serial}?{item_serial}?{item_price}#{location_link_split[1]}"
            quantity_string = quantity_cell.text.strip()
            name_string = name_cell.text.strip()
            name_check_string = format_ingame_name(name_string, quantity_string)
            try:
                price_cell_sanitized = re.sub(r"\D",'',price_cell.text)
                price = float(price_cell_sanitized)
            except Exception as e:
                print(f"{name_string}:{location_name}:{vendor_string}:{price_cell.text.strip()}")
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
                out_data.append((f"{name_string}",f"{price}/{threshold}",f"{cost_to_price_ratio}",f"{quantity_string}",f"{total_profit}",f"{vendor_string}",f"{location_coordinates}\t{closest}",f"{time_string}",f"{formatted_location_link}",f"{format_url}",f"{total_cost}",f"{name_check_string}"))
    #print(f"out_data length: {len(out_data)}")
    #for tuple in out_data:
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
        "Undeciphered": map_prices,
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
    failsafe = 0 #todo: decide on whether to retry if time out
    process_id = os.getpid()
    print(f'start: {process_id}: {item}')
    
    while i < 10:
        #print(i)
        if i > 0:
            temp_url = f"{page_url}&page={i}"
        else:
            temp_url = page_url
        #print(temp_url)
        cookie = {"app": "MTcxNzkxMTY0NXxyMy1fUlZXNkswcGRXZEhXNWpZOXdHY1FQMHhSQ1Z4VUp0MnFlNkQxdWlKMnExdUNyRDFtaFBBSmpJNGRZUXZjYkdndFhFNWRFaFZDQXJ0emg3VjJfTllSd2FmZWdXOW1kTEF4MHNsdHJEQUJHYlU9fGerm92O8uhh1zqXUJc5DO5U3HJ2gx6aQKYCEwXjuI9S"}
        response = requests.get(temp_url, headers=headers, cookies=cookie)
        if response.status_code != 200:
            print(f"Failed to retrieve the webpage: {item}. Status code: {response.status_code}")
            if failsafe == 0:
                break
            failsafe = 0
            time.sleep(.3)
            continue
        # result = None
        soup = BeautifulSoup(response.content, 'lxml')
        if soup:
            # results_table = soup.find('table',style="display: block; border: none;")
            # if results_table:
            #     results = results_table.find_all('em')
            #     if len(results):
            #         result = results[0].text.strip()
            #         result = int(result)
            # else:
            #     print('summit went awry, results table missing')
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

    print(f'end: {process_id}: {item}')
    out_data = []
    for row in agg_rows:
        cells = row.find_all('td')
        time_cell = cells[8]
        time_string = time_cell.text.strip().lower()  # Convert to lowercase for consistent comparison
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
            check_dist = float('inf')
            closest = None
            for location_name, tuple_loc in my_locations.items():
                x2 = int(tuple_loc[0])
                y2 = int(tuple_loc[1])
                distance = get_distance(x1,y1,x2,y2)
                if distance < check_dist:
                    check_dist = distance
                    closest = location_name
            location_name = closest if closest else 'N/A'
            formatted_location_link = f"{location_link_split[0]}?{vendor_serial}?{item_serial}?{item_price}#{location_link_split[1]}"
            quantity_string = quantity_cell.text.strip()
            name_string = name_cell.text.strip()
            name_check_string = format_ingame_name(name_string, quantity_string)
            try:
                price_cell_sanitized = re.sub(r"\D",'',price_cell.text)
                price = float(price_cell_sanitized)
            except Exception as e:
                print(f"{name_string}:{location_name}:{vendor_string}:{price_cell.text.strip()}")
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
                out_data.append((f"{name_string}",f"{price}/{threshold}",f"{cost_to_price_ratio}",f"{quantity_string}",f"{total_profit}",f"{vendor_string}",f"{location_coordinates}\t{closest}",f"{time_string}",f"{formatted_location_link}",f"{format_url}",f"{total_cost}",f"{name_check_string}"))
    #print(f"out_data length: {len(out_data)}")
    #for tuple in out_data:
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
    soup = BeautifulSoup(html, 'lxml')
    #print(f"soup: {time.time() - misc_start_time}")
    if soup:
        table = soup.find('table', id="item-search-results")
        if not table:
            print(f"No table: {page_url}")
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
                    check_dist = float('inf')
                    closest = None
                    for location_name, tuple_loc in my_locations.items():
                        x2 = int(tuple_loc[0])
                        y2 = int(tuple_loc[1])
                        distance = get_distance(x1,y1,x2,y2)
                        if distance < check_dist:
                            check_dist = distance
                            closest = location_name
                    location_name = closest if closest else 'N/A'
                    formatted_location_link = f"{location_link_split[0]}?{vendor_serial}?{item_serial}?{item_price}#{location_link_split[1]}"
                    quantity_string = quantity_cell.text.strip()
                    name_string = name_cell.text.strip()
                    name_check_string = format_ingame_name(name_string,quantity_string)
                    total_cost = round(price * int(quantity_string),0)
                    total_profit = round(searchPrice * int(quantity_string) - total_cost,0)
                    out_data.append((f"{name_string}",f"{price}/{searchPrice}",f"{ratio}",f"{quantity_string}",f"{total_profit}",f"{vendor_string}",f"{location_coordinates}\t{closest}",f"{time_string}",f"{formatted_location_link}",f"{page_url}",f"{total_cost}",f"{name_check_string}"))
        return out_data

def simple_parse_narrow(in_tuple): #(response.content,searchPrices,page_url,60,1,.93)
    # print("parse start")
    html = in_tuple[0]
    searchPrices = in_tuple[1]
    page_url = in_tuple[2]
    time_frame = in_tuple[3]
    price_depth = in_tuple[4]
    cutoff_threshold = in_tuple[5]
    soup = BeautifulSoup(html, 'lxml')
    #print(f"soup: {time.time() - misc_start_time}")
    if soup:
        table = soup.find('table', id="item-search-results")
        if not table:
            print(f"No table: {page_url}")
            return False
        rows = table.tbody.find_all('tr')
        out_data = []
        for row in rows:
            cells = row.find_all('td')
            name_cell = cells[4]
            name_string = name_cell.text.strip()
            searchPrice = float(searchPrices.get(name_string, 0))
            time_cell = cells[8]
            time_string = time_cell.text.strip().lower()
            if is_time_recent_multi(time_string,time_frame):
                price_cell = cells[7]

                price_cell_sanitized = re.sub(r"[^\d.]",'',price_cell.text)

                price = float(price_cell_sanitized)
                ratio = round(price / searchPrice,2)
                if ratio > cutoff_threshold and price_depth != 2:
                    continue
                if price <= searchPrice or price_depth == 2:
                    vendor_cell = cells[1]
                    location_cell = cells[2]
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
                    check_dist = float('inf')
                    closest = None
                    for location_name, tuple_loc in my_locations.items():
                        x2 = int(tuple_loc[0])
                        y2 = int(tuple_loc[1])
                        distance = get_distance(x1,y1,x2,y2)
                        if distance < check_dist:
                            check_dist = distance
                            closest = location_name
                    location_name = closest if closest else 'N/A'
                    formatted_location_link = f"{location_link_split[0]}?{vendor_serial}?{item_serial}?{item_price}#{location_link_split[1]}"
                    quantity_string = quantity_cell.text.strip()
                    name_check_string = format_ingame_name(name_string,quantity_string)
                    total_cost = round(price * int(quantity_string),0)
                    total_profit = round(searchPrice * int(quantity_string) - total_cost,0)
                    out_data.append((f"{name_string}",f"{price}/{searchPrice}",f"{ratio}",f"{quantity_string}",f"{total_profit}",f"{vendor_string}",f"{location_coordinates}\t{closest}",f"{time_string}",f"{formatted_location_link}",f"{page_url}",f"{total_cost}",f"{name_check_string}"))
        # print("parse end")
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
        print(f"Unexpected error when accessing {folder_path}: {str(e)}")
        latest_file = False
    #print('latest: ' + latest_file)
    return latest_file

def check_accessibility(file_path):
    try:
        with open(file_path):  # Using with ensures the file is closed after this block
            pass
        return True
    except Exception as e:
        #print(f"2! Unexpected error when accessing {file_path}: {str(e)}")
        return False

def parse_log_to_object():
    #my_vendors = [4342004, 3097786, 1598057, 4205843, 3756258, 3749795]
    my_vendors = ["MM1","MM2","MM3","MM4","MM5","MM6"]
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
                        # print(item_description)
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
                    print('missing: ' + line)
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
                if current_vendor['name'] in my_vendors:
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
                #print('Previous snapshot is identical')
                return previous_snapshot
    except Exception as e:
        print(f"Exception in take_snapshot: {e}")

# Function to get the sales from the database
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
    
# Function to get the most recent snapshot from the database
def get_most_recent_inventory_snapshot():
    try:
        fetches = fetch_query("SELECT MAX(snapshot_time) FROM inventory_snapshots") #returns fetchall
        if len(fetches):
            most_recent_time = fetches[0][0]
            return fetch_query("SELECT * FROM inventory_snapshots WHERE snapshot_time=?", (most_recent_time,))
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def get_most_recent_sales_time():
    try:
        fetches = fetch_query("SELECT MAX(snapshot_time) FROM sales_history") #returns fetchall
        if len(fetches):
            most_recent_time = fetches[0][0]
            return most_recent_time
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
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
        #print('same length')
        return False
    for item1, item2 in zip(sorted_snap1, sorted_snap2):
        # Compare all fields except the timestamp (assuming timestamp is at index 0)
        if item1 != item2:
            #print('item1:',item1)
            #print('item2:',item2)
            return False
    return True

def update_snapshots(inventory_items):
    snapshot1 = get_most_recent_inventory_snapshot()
    if len(snapshot1) == 0:
        take_snapshot(inventory_items)
        return    
    if snapshots_are_identical(snapshot1, inventory_items):
        #print("The snapshots are identical, no changes detected.")
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
            #print(f"Item {id} exists in the first snapshot but not in the second. All {quantity1} units may have been sold or removed.")
            sold_items[id] = item_info  # Or some other logic
    for id, item_info in sold_items.items():
        price, description, quantity = item_info
        record_sale(snapshot_time,id,price,description,quantity)
    return sold_items

def record_sale(snapshot_time, id, price, description, quantity):
    try:
        existing_records = fetch_query("SELECT * FROM sales_history WHERE id = ?", (id,))
        # Insert a new sale record
        if len(existing_records) == 0:
            execute_query("INSERT INTO sales_history (snapshot_time, id, price, description, quantity) VALUES (?, ?, ?, ?, ?)",
                    (snapshot_time, id, price, description, quantity))
            #total_price = price * quantity
            #print(f"Recorded sale: {quantity} of item {description} at {price} each, for a total price of {total_price}.")
        #else:
         #   print(f"Item with ID {id} already exists in sales_history. Skipping insert.")
    except Exception as e:
        print(f"An error occurred: {e}")



class AliApp:
    def __init__(self,root):
        self.root = root
        self.root.title("Ali's OutlandMalls Scraper v4.2")
        self.root.geometry("1160x870")  # Initial size
        self.root.minsize(1300, 870)  # Minimum size
        #self.root.maxsize(900, 700)  # Maximum size
        self.root.bind("<Return>", self.ParseMostRecentJournalLog)
        self.root.bind("<Control-Return>", self.ScrapeOutlandMall)
        self.root.bind("<Control-Alt-Return>", self.PriorityScrapeOutlandMall)
        self.root.bind("<KeyPress-3>", self.set_all_checkboxes)
        self.root.bind("<KeyPress-4>", self.set_none_checkboxes)
        self.root.bind("<Alt-Return>", self.set_hp_variables)
        self.root.bind("<KeyPress-1>", self.set_hp_variables)
        self.root.bind("<Shift-Return>", self.set_lp_variables)
        self.root.bind("<KeyPress-2>", self.set_lp_variables)
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

        # Create the Treeview with several columns
        self.tree = ttk.Treeview(self.tree_frame, columns=("Item", "Price","Ratio","#","Profit","Vendor","Location","Time","#9","#10","#11","#12"),show='headings') #todo add profit column
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
        self.tree.column("#9", width=0,stretch=False) #todo
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
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label='Insert To Sales History', command=self.on_treeview_select)
        #self.context_menu.add_command(label='Option 2', command=lambda: print("Option 2 clicked"))
        # Bind right-click event
        self.tree.bind('<Button-3>', self.show_context_menu)

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
        self.btn_locations = ttk.Button(self.radio_frame, text="Locations", command=self.scrape_vendor_updates)
        self.btn_locations.grid(row=5, column=0, sticky='ew', padx=10, pady=5, columnspan=2)
        self.btn_visit_web = ttk.Button(self.radio_frame, text="Open Website", command=lambda: webbrowser.open("https://outlandmalls.com/"))
        self.btn_visit_web.grid(row=6, column=0, sticky='ew', padx=10, pady=5, columnspan=2)
        self.btn_open_folder = ttk.Button(self.radio_frame, text="Open Folder", command=lambda: os.system('explorer "C:\\Program Files (x86)\\Ultima Online Outlands\\ClassicUO\\Data\\Client\\JournalLogs"'))
        self.btn_open_folder.grid(row=7, column=0, sticky='ew', padx=10, pady=5, columnspan=2)
        self.btn_inventory = ttk.Button(self.radio_frame, text="Inventory", command=lambda: self.read_db_current_inventory())
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

    def draw_transparent_rectangle(self,x,y,width,height):
        region = (x, y, width, height)
        overlay = tk.Toplevel(self.root)
        overlay.attributes('-alpha', 0.1)  # Make the window fully transparent
        overlay.geometry(f'{region[2]}x{region[3]}+{region[0]}+{region[1]}')
        overlay.overrideredirect(True)  # Remove window decorations
        overlay.attributes('-topmost', True)  # Keep window on top
        border_color = 'cyan'
        border_width = 4
        canvas = tk.Canvas(overlay, highlightthickness=0, bg='black')
        canvas.pack(fill='both', expand=True)
        canvas.create_rectangle(border_width // 2, border_width // 2, region[2] - border_width // 2, region[3] - border_width // 2, outline=border_color, width=border_width, fill='')

    def detect_notification(self): #todo
        def images_are_equal(img1, img2):
            arr1 = np.array(img1)
            arr2 = np.array(img2)
            return np.array_equal(arr1, arr2)
        def send_udp_message(message, target_ip, target_port):
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(message.encode(), (target_ip, target_port))
        x, y, width, height = 715, 1150, 782, 135  # Update these values
        time_stamp = time.time()
        initial_screenshot = pyautogui.screenshot(region=(x, y, width, height))
        while True:
            new_screenshot = pyautogui.screenshot(region=(x, y, width, height))
            if time.time() > time_stamp and not images_are_equal(new_screenshot, initial_screenshot):
                time_stamp = time.time() + 5
                send_udp_message("Triggered", "10.0.0.61", 8080)  # Update IP and port
            initial_screenshot = new_screenshot
            time.sleep(0.2)

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
        self.cutoff_threshold.set(0.93)
        self.search_pricedepth.set(1)
        self.search_combobox_timeframe.set("1 Minute")
        self.check_core_var.set(True)
        self.check_extract_var.set(False)
        self.check_distil_var.set(False)
        self.check_tmaps_var.set(True)
        self.check_skillscrolls_var.set(True)
        self.check_chainlinks_var.set(False)
        self.check_lp_misc_var.set(False)
        self.check_hp_misc_var.set(False)
        self.check_cloth_var.set(False)
        self.check_dye_var.set(False)
        self.check_ingot_var.set(False)
        self.check_board_var.set(False)
        self.check_leather_var.set(False)

    def set_lp_variables(self,event=None):
        self.cutoff_threshold.set(0.93)
        self.search_pricedepth.set(1)
        self.search_combobox_timeframe.set("5 Minutes")
        self.check_core_var.set(False)
        self.check_extract_var.set(False)
        self.check_distil_var.set(False)
        self.check_tmaps_var.set(False)
        self.check_skillscrolls_var.set(False)
        self.check_chainlinks_var.set(True)
        self.check_lp_misc_var.set(True)
        self.check_hp_misc_var.set(True)
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
        start_time = time.time()
        headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        url = "https://outlandmalls.com/vendors/"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve the webpage: {url}. Status code: {response.status_code}")
            self.queue_append.put('Vendor Page Failed')
            return
        self.queue_append.put(f"Scanning Locations")
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
                #print(f"{vendor_name}: {update_time}")
                if sec_since_scan < min_time:
                    min_time = sec_since_scan
                    closest = (update_time,x2,y2,vendor_name)
            scan_time_string = closest[0] if closest else 'Not Scanned'
            scan_x = closest[1] if closest else '0'
            scan_y = closest[2] if closest else '0'
            scan_name = closest[3] if closest else 'No Name!'
            out_arr.append((location_name,scan_time_string,min_time,scan_x,scan_y,scan_name))
            #print(f"{location_name}: {scan_time_string}")
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
        elapsed_time = round(time.time() - start_time,2)
        #print(f"end: {elapsed_time}")
        self.queue_append.put("Idle")

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
    
    def on_treeview_click(self, event):
        if self.tree.identify_region(event.x, event.y) == "heading":
            return
        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        url = None
        if(len(self.tree.item(row_id,'values')) > 1 and self.tree.item(row_id,'values')[1]):
            if col_id == "#1":
                url = self.tree.item(row_id, "values")[9]
            elif col_id == "#7":
                url = self.tree.item(row_id, "values")[8]                
            #print(url)
            # value_to_copy_raw = self.tree.item(row_id, "values")[8]
            # serial_match = re.search(r'\?(\d+)(?:\?(\d+))(?:\?(\d+))?#', value_to_copy_raw) #'https://www.exploreoutlands.com/?471890?1251126567?312345125#pos:869,1381,13'
            # vendor_serial = serial_match.group(1) if serial_match else 0
            # item_serial = serial_match.group(2) if serial_match else 0
            # item_price = serial_match.group(3) if serial_match else 0
            location_raw = self.tree.item(row_id, "values")[6].split('\t')
            location_split = location_raw[0].split(',')
            x1, y1 = map(int,location_split)
            check_dist = float('inf')
            closest = None
            for location_name, tuple_loc in my_locations.items():
                x2 = int(tuple_loc[0])
                y2 = int(tuple_loc[1])
                distance = get_distance(x1,y1,x2,y2)
                if distance < check_dist:
                    check_dist = distance
                    closest = location_name
            location_name = closest if closest else 'Not found'
            if not closest:
                print("Somehow 'closest' is None")
                return
            if my_locations.get(closest) is None:
                print(f"No match in dictionary for location name: {closest}")
                return
            location_data = my_locations[closest][2]
            location_character = location_data[0]
            book_hue = location_data[1]
            location_recall_code = location_data[2]
            location_button_code = location_data[3]
            value_to_copy_raw = self.tree.item(row_id, "values")[8]
            serial_match = re.search(r'\?(\d+)(?:\?(\d+))(?:\?(\d+))?#', value_to_copy_raw) #'https://www.exploreoutlands.com/?471890?1251126567?312345125#pos:869,1381,13'
            second_try = re.search(r'\?(\d+)\?', value_to_copy_raw)
            print(value_to_copy_raw)
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
                    elseif "Price: {total_cost_str} " in "foundItemLabel"
                        sysmsg "opening buy menu" 1159
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
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
            # split = value_to_copy_raw.(', ')
            # value_to_copy = ">waypoint " + split[0] + " " + split[1]
            self.root.clipboard_append(scriptString)
            # global clipboard_ghost
            # clipboard_ghost = scriptString
            self.root.update()
            if url:
                webbrowser.open(url)

    def on_treeview_select(self):
        item = self.tree.selection()[0]
        row_values = self.tree.item(item,'values')
        #snapshot_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        description = row_values[0]
        price_string = row_values[1] #80000.0/80000.0
        left_side_price = price_string.split('/')[0]
        price = int(float(left_side_price))
        quantity = row_values[3] #80000.0/80000.0
        value_to_copy_raw = row_values[8] #'https://www.exploreoutlands.com/?471890?1251126567#pos:869,1381,13'
        number_match = re.search(r'\?(\d+)(?:\?(\d+))?#', value_to_copy_raw)
        vendor_serial = number_match.group(1) if number_match else 0
        id = number_match.group(2) if number_match else 0
        # execute_query("INSERT INTO sales_history (snapshot_time, id, price, description, quantity) VALUES (?, ?, ?, ?, ?)",
        #                        (snapshot_time, id, price, description, quantity))
        #print(f"You selected item: {snapshot_time}, {id}, {price}, {description}, {quantity}")

    def show_context_menu(self,event=None):
        if self.tree.identify_region(event.x, event.y) == "heading":
            return
        row_id = self.tree.identify_row(event.y)
        try:
            location_raw = self.tree.item(row_id, "values")[6].split('\t')
        except:
            return
        location_split = location_raw[0].split(',')
        x1, y1 = map(int,location_split)
        check_dist = float('inf')
        closest = None
        for location_name, tuple_loc in my_locations.items():
            x2 = int(tuple_loc[0])
            y2 = int(tuple_loc[1])
            distance = get_distance(x1,y1,x2,y2)
            if distance < check_dist:
                check_dist = distance
                closest = location_name
        location_name = closest if closest else 'Not found'
        if not closest:
            print("Somehow 'closest' is None")
            return
        if my_locations.get(closest) is None:
            print(f"No match in dictionary for location name: {closest}")
            return
        location_data = my_locations[closest][2]
        location_character = location_data[0]
        book_hue = location_data[1]
        location_recall_code = location_data[2]
        location_button_code = location_data[3]
        value_to_copy_raw = self.tree.item(row_id, "values")[8]
        serial_match = re.search(r'\?(\d+)(?:\?(\d+))(?:\?(\d+))?#', value_to_copy_raw) #'https://www.exploreoutlands.com/?471890?1251126567?312345125#pos:869,1381,13'
        second_try = re.search(r'\?(\d+)\?', value_to_copy_raw)
        print(value_to_copy_raw)
        vendor_serial = serial_match.group(1) if serial_match else second_try.group(1) if second_try else 0
        item_id = serial_match.group(2) if serial_match else 0
        item_price = format_with_commas(serial_match.group(3)) if serial_match else 0
        str_price = format_with_commas(item_price)
        total_cost = int(float(self.tree.item(row_id, "values")[10]))
        total_cost_str = format_with_commas(total_cost)
        item_description = self.tree.item(row_id, "values")[11]
        print(item_description)
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
                    elseif "Price: {total_cost_str} " in "foundItemLabel"
                        sysmsg "opening buy menu" 1159
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
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
        # global clipboard_ghost
        # clipboard_ghost = scriptString
        self.tree.selection_set(row_id)
        #self.context_menu.post(event.x_self.root, event.y_self.root)

    def quick_scrape(self):
        start_time = time.time()
        def request_gen_simple():
            price_list = [
                # ("https://outlandmalls.com/?item=core&search_category_id=0",core_prices),
                # ("https://outlandmalls.com/?item=core&search_category_id=0&page=1",core_prices),
                # ("https://outlandmalls.com/?item=core&search_category_id=0&page=2",core_prices),
                #("https://outlandmalls.com/?item=core&search_category_id=0&page=3",core_prices), 
                # ("https://outlandmalls.com/?item=core&search_category_id=0&page=4",core_prices),
                # ("https://outlandmalls.com/?item=core&search_category_id=0&page=5",core_prices),
                ("treasure undeciphered",map_prices),
                ("research materials",misc_crafting_prices),
                ("prevalia coins",misc_hp_prices),
            ]

            for searchString, searchPrices in price_list:
                request_time = time.time()
                res = re.search(r"https://outlandmalls\.com/\?item=(\w*)&",searchString)
                match = res.group(1) if res else None
                printable_name = match if match else searchString
                print(f"{printable_name}: start")
                page_url = searchString if match else "https://outlandmalls.com/?item=" + quote_plus(printable_name) + "&search_category_id=0"
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                cookie = {"app": "MTcxNzkxMTY0NXxyMy1fUlZXNkswcGRXZEhXNWpZOXdHY1FQMHhSQ1Z4VUp0MnFlNkQxdWlKMnExdUNyRDFtaFBBSmpJNGRZUXZjYkdndFhFNWRFaFZDQXJ0emg3VjJfTllSd2FmZWdXOW1kTEF4MHNsdHJEQUJHYlU9fGerm92O8uhh1zqXUJc5DO5U3HJ2gx6aQKYCEwXjuI9S"}
                response = requests.get(page_url, headers=headers, cookies=cookie)
                if response.status_code != 200:
                    print(f"Failed to retrieve the webpage: {searchString}. Status code: {response.status_code}")
                    continue
                #self.queue_append.put(f"{printable_name}")
                elapsed_time = round(time.time() - request_time,2)
                print(f"{searchString}: {elapsed_time}")
                try:
                    yield (response.content,searchPrices,page_url,60,1,.90)
                except Exception as e:
                    print(f"yield error: {e}")
        num_cores = cpu_count()
        # print('quicktest1')
        with Pool(num_cores) as pool:
            try:
                for result in pool.imap_unordered(simple_parse_narrow,request_gen_simple()):
                    #print(f"inpool: {result}")
                    self.queue_append.put(result)
            except Exception as e:
                print(f"Pool failed: {e}")
        # print('quicktest2')
        elapsed_time = round(time.time() - start_time,2)
        self.queue_append.put(f"Finished FAST:{elapsed_time}")
        # print('quicktest3')


    def async_scraping(self):
        start_time = time.time()
        seconds_threshold = self.parse_combobox()
        price_depth = self.search_pricedepth.get()
        cutoff_threshold = self.cutoff_threshold.get()
        
        def request_gen():
            #tuple_list = []
            bools = [
                (self.check_lp_misc_var.get(), misc_lp_prices),
                (self.check_hp_misc_var.get(), misc_hp_prices),
            ]
            gathered_misc_prices = {}
            for bool, prices in bools:
                if bool:
                    gathered_misc_prices.update(prices)
            for searchString, searchPrice in gathered_misc_prices.items():
                #elapsed_time = time.time() - start_time
                self.queue_append.put(f"{searchString}")
                #misc_start_time = time.time()  # Record the current time
                page_url = "https://outlandmalls.com/?item=" + quote_plus(searchString) + "&search_category_id=0"
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                time.sleep(1)
                cookie = {"app": "MTcxNzkxMTY0NXxyMy1fUlZXNkswcGRXZEhXNWpZOXdHY1FQMHhSQ1Z4VUp0MnFlNkQxdWlKMnExdUNyRDFtaFBBSmpJNGRZUXZjYkdndFhFNWRFaFZDQXJ0emg3VjJfTllSd2FmZWdXOW1kTEF4MHNsdHJEQUJHYlU9fGerm92O8uhh1zqXUJc5DO5U3HJ2gx6aQKYCEwXjuI9S"}
                response = requests.get(page_url, headers=headers, cookies=cookie)

                if response.status_code != 200:
                    print(f"Failed to retrieve the webpage: {searchString}. Status code: {response.status_code}")
                    continue
                #print(f"start misc request: {searchString}: {elapsed_time}")
                yield (response.content,searchPrice,page_url,seconds_threshold,price_depth,cutoff_threshold)


        if self.check_lp_misc_var.get() or self.check_hp_misc_var.get():
            elapsed_time = round(time.time() - start_time,2)
            print(f"misc request: {elapsed_time}")
            num_cores = cpu_count()
            with Pool(num_cores) as pool:
                for result in pool.imap_unordered(multi_parse_misc,request_gen()):
                    self.queue_append.put(result)

        elapsed_time = round(time.time() - start_time,2)
        print(f"multi misc: {elapsed_time}")
        steps = [
            ["Aspect Core", core_prices, self.check_core_var.get()],
            #["Aspect Extract", extract_prices, self.check_extract_var.get()],
            #["Aspect Distillation", distil_prices, self.check_distil_var.get()],
            ["Undeciphered", map_prices, self.check_tmaps_var.get()],
            ["Skill Mastery Scroll", scroll_prices, self.check_skillscrolls_var.get()],
            ["Mastery Chain Link", link_prices, self.check_chainlinks_var.get()],
            ["Misc Crafting", misc_crafting_prices, self.check_hp_misc_var.get()],
        ]
        
        price_depth = self.search_pricedepth.get()
        seconds_threshold = self.parse_combobox()
        cutoff_threshold = self.cutoff_threshold.get()
        tuple_list = []
        for step in steps:
            bool = step[2]
            if not bool:
                continue
            name = step[0]
            tuple_list.append((name,price_depth,seconds_threshold,cutoff_threshold))

        elapsed_time = round(time.time() - start_time,2)
        print(f"wide request: {elapsed_time}")
        self.queue_append.put("Searching Wide")
        num_cores = cpu_count()
        with Pool(num_cores) as pool:
            for result in pool.imap_unordered(multi_parse_wide,tuple_list):
                self.queue_append.put(result[0])
        elapsed_time = round(time.time() - start_time,2)
        print(f"multi wide: {elapsed_time}")
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
        self_parse_extra_misc = self.check_hp_misc_var.get()
        bools = [
            (self.check_core_var.get(), core_prices),
            (self.check_extract_var.get(), extract_prices),
            (self.check_distil_var.get(), distil_prices),
            (self.check_tmaps_var.get(), map_prices),
            (self.check_skillscrolls_var.get(), scroll_prices),
            (self.check_chainlinks_var.get(), link_prices),
            (self.check_cloth_var.get(), 'cloth'),
            (self.check_dye_var.get(), 'dyes'),
            (self.check_hp_misc_var.get(), misc_hp_prices),
            (self_parse_extra_misc, self_parse_extra_prices),
            (self_parse_extra_misc, commodity_2500_prices),
            (self_parse_extra_misc, commodity_5000_prices),
            (self_parse_extra_misc, deed_prices),
            (self.check_lp_misc_var.get(), misc_lp_prices),
            (self.check_hp_misc_var.get(), misc_crafting_prices),
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
        #self_parse_prices = {**core_prices, **extract_prices, **distil_prices, **map_prices, **scroll_prices, **link_prices, **misc_prices}
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
                name_string = item['description']
                full_description = item['full_description']
                price = round(item['price'],4)
                if 'chain link' in name_string:
                    if name_string.startswith('a '):
                        name_string = name_string[2:]
                    chain_name = clean_chainlink_string(name_string)
                    if name_string.startswith('bronze mastery chain link'):
                        threshold = float(self_parse_prices.get(chain_name,[0,0,0])[0])
                    elif name_string.startswith('silver mastery chain link'):
                        threshold = float(self_parse_prices.get(chain_name,[0,0,0])[1])
                    elif name_string.startswith('gold mastery chain link'):
                        threshold = float(self_parse_prices.get(chain_name,[0,0,0])[2])
                    elif name_string.startswith('corrupted mastery chain link'):
                        threshold = float(self_parse_prices.get("corrupted_link_price_threshold",0))
                    else:
                        threshold = 0
                elif "invulnerability" in name_string and ("bone" in name_string or "platemail" in name_string or "studded" in name_string) and not ("skirt" in name_string or "cap" in name_string):
                    threshold = 5000.0
                elif self_parse_extra_misc and "tome" in name_string and not "summoner's tome" in name_string and not "a rune tome" in name_string:
                    threshold = float(self_parse_extra_aliases['tome'])
                elif self_parse_extra_misc and "mount token" in name_string:
                    threshold =  float(self_parse_extra_aliases['mount token'])
                elif self_parse_extra_misc and 'a lore page' in name_string:
                    if "of 15)" in name_string:
                        threshold = float(self_parse_extra_aliases['lore page /15'])
                    else:
                        threshold = float(self_parse_extra_aliases['lore page /10'])
                else:
                    threshold = float(self_parse_prices.get(name_string, 0))
                if threshold > 0:
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
        print(f"items: {len(out_data)}")
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

    def PriorityParseMostRecentJournalLog(self,event=''):
        self.clear_tree()
        self.set_hp_variables()
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
        headers = {'Authorization': '9ec321b8-6c45-4869-aa01-c15cfc7d38be'}
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
            #print('-Sales Report-')
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
                #print(result)
            rev_string = f"Total Revenue: {total_revenue}"
            listbox.insert(tk.END, rev_string)
            #print(f"{rev_string}\n-End Report-")
            return rows
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def read_db_recent_sales(self):
        try:
            with connect_db() as conn:
                c = conn.cursor()
                c.execute("SELECT MAX(snapshot_time) FROM sales_history")
                entries = c.fetchall()
                #if len(entries) == 0:
                    #print('No recent sales')
                most_recent_time = entries[0][0]
                c.execute("SELECT * FROM sales_history WHERE snapshot_time=?",(most_recent_time,))
                rows = c.fetchall()
                columns = [desc[0] for desc in c.description]
            #print('-Sales Report-')
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
                #result = f"{row_dict['description']}: {row_dict['quantity']}x @ {row_dict['price']} = {total_price}"
                listbox.insert(tk.END, result)
                #print(result)
            rev_string = f"Total Revenue: {total_revenue}"
            listbox.insert(tk.END, rev_string)
            #print(f"{rev_string}\n-End Report-")
            return rows
        except Exception as e:
            print(f"An error occurred: {e}")
            return []
        
    def read_db_current_inventory(self,switch=None):
        try:
            rows = get_most_recent_inventory_snapshot()
            if not rows:
                print("No inventory snapshot available.")
                return []
            # inventory_window = tk.Toplevel(self.root)
            # inventory_window.title("Inventory")
            # self.scrollbar = tk.Scrollbar(inventory_window, orient="vertical")
            # listbox = tk.Listbox(inventory_window, yscrollcommand=self.scrollbar.set, width=60, height=20)
            # self.scrollbar.config(command=listbox.yview)
            # self.scrollbar.pack(side="right", fill="y")
            # listbox.pack(side="left", fill="both", expand=True)
            aggregated_items = {}
            columns = ['snapshot_time', 'id', 'price', 'description', 'quantity']
            for row in rows:
                row_dict = dict(zip(columns, row))
                stackSize = int(row_dict['quantity'])
                if stackSize > 1:
                    key = (f"{row_dict['description']}", stackSize, row_dict['price'])  # Create a unique key for each item type at a given price
                else:
                    key = (f"{row_dict['description']}", 1, row_dict['price'])  # Create a unique key for each item type at a given price
                if key not in aggregated_items:
                    aggregated_items[key] = 0
                aggregated_items[key] += 1
            sorted_items = categorize_and_sort_aggregated_items(aggregated_items)
            #pretty_print(check_dict)
            #Animal Lore Scroll: 11 @ 18k each | 2 sets of 10 @ 180k/set
            out_str = "***WTS*** *(all available on vendors MM1, MM2, MM3 and MM4 at Chopper's Shop (4008, 477) directly north of Anchor's Rest moongate*"
            for category_name, category_items in sorted_items.items(): 
                if len(category_items) == 0:
                    continue
                out_str += f"\n**{category_name}**:\n"
                for description, details in category_items.items():
                    #total_price = int(price) * int(quantity)
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

                        if category_name == "Skill Mastery Scrolls":
                            check_arr.append((stack_size,quantity))
                    result = f"{trunc_name}: {' & '.join(inline_strings)}"

                    #listbox.insert(tk.END, result)
                    if category_name == "Skill Mastery Scrolls" and ((1,2) not in check_arr or (10,2) not in check_arr):
                        out_str += f"--{result}   \n"
                    else:
                        out_str += f"\t{result}\n"


                    #print(result)
            #print(out_str)
            
            #self.root.clipboard_clear()
            #self.root.clipboard_append(out_str)
                        
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
            #print("-End Report-")
            
            return sorted_items
        except Exception as e:
            print(f"An error occurred: {e}")
            return []
        
    #------------------------------ GUI Updates---------------------------
    def queue_daemon(self,event=None):
        try:
            #print('queue_daemon_init')
            data = self.queue_append.get_nowait()
            #print(f"queue_daemon_start: {data}")
            if isinstance(data,str):
                self.status_var.set(data)
                if 'Finished FAST' in data:
                    #print(f"queue_daemon_1a")
                    self.queue_emptyFastSort_flag = True
            elif data and len(data):
                for tuple in data:
                    self.append_to_tree(*tuple)
                #print(f"queue_daemon_1b")
                self.queue_emptySort_flag = True
            self.root.after(10, self.queue_daemon)
        except queue.Empty:
            if self.queue_emptySort_flag or self.queue_emptyFastSort_flag:
                self.queue_emptySort_flag = False
                if self.queue_emptyFastSort_flag:
                    print(f"queue_daemon_2")
                    self.queue_emptyFastSort_flag = False
                    try:
                        #print('quicksort')
                        self.sort_tree_quick()
                    except Exception as e:
                        print('sort quick failed: ', e)
                elif self.search_sortmode.get() == 2:
                    try:
                        #print(f"queue_daemon_2")
                        self.sort_column_tuple("Ratio", "Item", False, sort_key_tuple)
                    except Exception as e:
                        print('sort failed: ', e)
            self.root.after(20, self.queue_daemon)
        except Exception as e:
            print(f"queue_daemon exception: {e}")
            self.root.after(20, self.queue_daemon)
        #print("daemon_queue_end")

    def clear_tree(self):
        # Clear the Treeview
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
            print('lsort e:', e)
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
        print(loc_data_sorted)

        loc_id_list = [(self.tree.set(k, 'Location'),self.tree.set(k, 'Ratio'), k) for k in tree_children]
        loc_id_list_sorted = sorted(loc_id_list,key=lambda x: (loc_sorted.index(x[0].split("\t")[1]), float(x[1])))
        for index, (_, _, k) in enumerate(loc_id_list_sorted):
            self.tree.move(k, '', index)
        self.tree.see(loc_id_list_sorted[0][2])
        #print(f"Total Profit: {total_profit}\tCTP Ratio Average: {ctp_ratio_average}\t\tProfit Margin Average: {profit_margin_average}\n")

    def sort_tree_quick(self, event=None):
        data = []
        print("sort_tree_quick_test1")
        tree_children = self.tree.get_children("")          
        if(len(tree_children) == 0):
            #print("sort_tree_quick_test_early_exit")
            return
        for child in tree_children:
            row_data = {}
            for col in self.tree["columns"]:
                row_data[col] = self.tree.set(child, col)
            data.append(row_data)
        rows_by_location = defaultdict(list)
        items_by_vendor = defaultdict(lambda: defaultdict(str))
        vendors_by_location = defaultdict(lambda: defaultdict(str))
        #print("sort_tree_quick_test2")
        for row in data:
            rows_by_location[row['Location'].split('\t')[1]].append(row)
            value_to_copy_raw = row["#9"]
            #print('v', value_to_copy_raw)
            serial_match = re.search(r'\?(\d+)(?:\?(\d+))(?:\?(\d+))?#', value_to_copy_raw) #'https://www.exploreoutlands.com/?471890?1251126567?312345125#pos:869,1381,13'
            second_try = re.search(r'\?(\d+)\?', value_to_copy_raw)
            vendor_serial = serial_match.group(1) if serial_match else second_try.group(1) if second_try else 0
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
        #print("sort_tree_quick_test3")
        for location, rows in rows_by_location.items():
            profit_sum = 0
            ctp_sum = 0
            margin_sum = 0
            total_items_at_location = 0
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
            total_profit = profit_sum
            ctp_ratio_average = round((ctp_sum / total_items_at_location) * 10) / 10 if total_items_at_location else 1
            profit_margin_average = round((margin_sum / total_items_at_location) * 10) / 10 if total_items_at_location else 0
            loc_data = {
                "Profit": total_profit,
                "CTP_Average": ctp_ratio_average,
                "Margin_Average": profit_margin_average,
            }
            data_by_location.append((location,loc_data))
        #print("sort_tree_quick_test4")

        loc_data_sorted = sorted(data_by_location,key=lambda x: (-x[1]["Profit"],x[1]["CTP_Average"],-x[1]["Margin_Average"]))
        loc_sorted = []
        for loc,data in loc_data_sorted:
            loc_sorted.append(loc)
        #print(loc_data_sorted)

        loc_id_list = [(self.tree.set(k, 'Location'), self.tree.set(k, 'Ratio'), k) for k in tree_children]
        loc_id_list_sorted = sorted(loc_id_list,key=lambda x: (loc_sorted.index(x[0].split("\t")[1]), float(x[1])))
        locationIndex = []
        for index, (l, r, k) in enumerate(loc_id_list_sorted):
            self.tree.move(k, '', index)
            capsule_loc_name = l.split("\t")[1]
            if capsule_loc_name not in locationIndex and int(float(r) != 1001):
                locationIndex.append(capsule_loc_name)
        #print("sort_tree_quick_test5")
        self.tree.see(loc_id_list_sorted[0][2])
        self.root.update()
        #print("sort_tree_quick_test6")
        #Generate razor script
        scriptString = '@setvar! "timeout" 650'
        for location in locationIndex:
            location_data = my_locations[location][2]
            location_character = location_data[0]
            book_hue = location_data[1]
            location_recall_code = location_data[2]
            location_button_code = location_data[3]
            scriptString += f"""
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

while not dead
    if hidden or cooldown "skill" > 0
        break
    endif
    skill "hiding"
    wait 200
endwhile
        
        """ # todo initialize and recall portion
            vendors = vendors_by_location[location]
            for vendor_name, vendor_serial in vendors.items():
                scriptString += f"""

removelist "itemDescriptions"
createlist "itemDescriptions"
clearignore

""" # find vendor and open backpack
                items = items_by_vendor[vendor_serial]
                
                for item_description_compare, item_serial in items.items():
                    print(item_description_compare,item_serial,vendor_serial,vendor_name)
                    scriptString += f"""
pushlist "itemDescriptions" "{item_description_compare}"

"""
                scriptString += f"""
while not dead
    if find {vendor_serial} ground any any 20
        overhead "● ▼▼ {vendor_name} ▼▼ ●" 88 {vendor_serial}
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
                    wait 250
                endif
                @ignore "foundItem"
            endwhile
            while findtype 18653|18658|18704|19199|19226|19227|19228|19229|19230|19231|19232|19234|19235|19236|19237|19238|19239|19240|19241|19242|19246|19247|19248|19249|19250|19251|19252|19253|19254|19256|19370|19372|19508|19512|19513|19520|19521|19522|19524|19525|19532|20501|20374|20375|20376|20377|20378|20379|20381|20383|20384|20385|20391|20392|20466|20467|20495|20496|21397|21398|21399|21400|21401|21402|21403|21404|21405|21780|21781|21783|21784|21785|21786|21787|21788|21789|21790|21791|21797|21798|21799|21800|21801|21803|21804|21805|21806|21807|21808|21809|21810|21814|21818|21824|21826|21827|21828|21829|21830|21831|21835|21836|21838|21840|21841|21842|21843|21844|21845|21847|21848|21849|21852|21853|21856|21859|21860|21861|21862|21863|21864|21865|21866|21867|21868|21870|21871|21872|21873|21874|21875|21876|21877|21878|21879|21880|21881|21882|21883|21884|21885|21886|21889|21891|21893|21894|21895|21896|21897|21898|21899|21901|21902|21904|21905|21906|21907|21908|21909|21911|21917|21918|21921|21923|21924|21925|21926|21927|21929|21931|21933|21934|21935|21936|21937|21938|21939|21940|21942|21943|21944|21945|21947|21948|21949|21950|21951|21953|21954|21956|21957|21960|21962|21963|21964|21969|21978|21981|21988|21996|21997|21998|21999|22151|22152|22153|22154|22155|22157|22158|22163|22164|22165|22166|22167|22168|22169|22170|22171|22172|22173|22174|22175|22177|22178|22179|22180|22181|22182|22183|22184|22185 "mainBackpack" as "foundItem"
                getlabel "foundItem" "desc"
                if inlist "itemDescriptions" "desc"
                    menu "foundItem" 0
                    waitforgump 4274928655 1000
                    gumpresponse 1
                    wait 250
                endif
                @ignore "foundItem"
            endwhile
            while findtype 22186|22188|22189|22190|22191|22192|22193|22194|22195|22196|22197|22199|22261|22264|22272|22285|22286|22287|22288|22289|22290|22291|22292|22293|22294|22295|22296|22297|22298|22336|22417|22418|22419|22420|22421|22422|22423|22426|22427|22428|22429|22430|22431|22432|22433|22434|22435|22436|22437|22438|22439|22440|22441|22442|22443|22444|22445|22449|22451|22453|22455|22456|23009|23034|23035|23774|23996|23997|24175|24179|24181|24182|24183|24184|24187|24188|24190|24191|24193|24195|24196|24197|24199|24246|24382|24383|24384|24385|24386|24387|24388|24389|24390|24391|24392|24393|24394|24395|24396|24397|24398|24399|24400|24401|24402|24403|24404|24405|24406|24407|24408|24409|24410|24411|24412|24413|24414|24415|24416|24417|24418|24419|24420|24421|24422|24423|24424|24425|24426|24427|24428|24429|24430|24431|24432|24433|24434|25647|25759|26640|26664|26669|26670|26671|26672|26688|26689|26693|26700|26701|26719|26720|26721|26724|26732|26734|26735|26736|26737|27561|27562|27563|27564|27565|27577|27580|27584|27611|27612|27640|27642|28760|28765|28768|28775|28795|28799|28803|28908|28909|28910|28911|28924|28994|28995|29024|29025|29026|29027|29028|29029|29031|29032|29033|29034|29035|29036|29037|29038|29040|29104|29106|29107|29108|29142|29350|29030|29352|29354|29355|29421|29382|29425|29428|29430|29431|29463|29495|29497|29498|29502 "mainBackpack" as "foundItem"
                getlabel "foundItem" "desc"
                if inlist "itemDescriptions" "desc"
                    menu "foundItem" 0
                    waitforgump 4274928655 1000
                    gumpresponse 1
                    wait 250
                endif
                @ignore "foundItem"
            endwhile
            while findtype 30561|30562|30563|30564|30565|30566|30567|30568|30573|30574|30575|30576|30577|30578|30579|30580|30582|30583|30586|30587|30588|30589|30590|30591|30592|30596|30599|30601|30602|30603|30604|30608|30609|30610|30611|30612|30613|30614|30615|30617|30618|30621|30622|30623|30624|30625|30626|30627|30628|30629|30630|30631|30632|30633|30634|30635|30636|30637|30638|30639|30640|30641|30642|30643|30644|30645|30646|30647|30648|30649|30650|30651|30652|30653|30655|30657|30658|30659|30660|30661|30662|30663|30766|30767|30768|30769|30770|30771|30772|30773|30775|30776|30778|30818|30819|30821|30822|30823|30825|30826|30827|30828|30829|30850|30851|30852|30853|30854|30855|30856|30857|30858|30859|30860|30866|30867|30868|30869|30870|30871|30872|30878|30967|30969|30970|30971|30972|30973|30974|30975|30976|30977|30978|30979|30980|30981|30982|30983|30984|30985|30986|36752|39264|39343|39344|39345|39346|39347|39348|39349|39350|39351|39352|39353 "mainBackpack" as "foundItem"
                getlabel "foundItem" "desc"
                if inlist "itemDescriptions" "desc"
                    menu "foundItem" 0
                    waitforgump 4274928655 1000
                    gumpresponse 1
                    wait 250
                endif
                @ignore "foundItem"
            endwhile
            while findtype 41459|41460|41461|41462|41510|42227|42239|42240|42242|42243|42244|42517|42574|42665|43159|43160|43161|43162|43163|43164|43165|43166|43167|43168|43169|43170|43171|43172|43173|43174|43175|43176|43177|43178|43179|43180|43181|43182|43206|43207|43208|43209|43210|43277|43279|43320|44310|44312|44314|44795|44796|44797|44798|44799|44800|44801|44804|44805|44808|44810|44986|45002|45120|45156|45157|45182|45193|45208|45211|45214|45216|45218|45220|45222|45235|45236|45238|45239|45241|45242|45246|45247|45248|45250|45251|45252|45254|45255|45257|45281|45282|45300|45315|45316|45371|45372|45373|45374|45375|45376|45377|45378|45379|45380|45381|45382|45383|45384|45385|45386|45387|45388|45389|45390|45391|45392|45393|45394|45395|45396|45397|45398|45399|45400|45401|45402|45403|45404|45405|45406|45407|45408|45409|45410|45411|45412|45413|45414|45415|45416|45417|45418|45419|45420|45421|45422|45423|45424|45425|45426|45427|45428|45429|45430|45828|45830|47107|47109|47111|48357|48358|48359|48360|48361|48362|48363|48364|48365|48366|48367|48368|48369|48370|48371|48372|48373|48374|48375|48376|48377|48378|48379|48380|48381|48382|48383|48384|48385|48386|48387|48388|48389|48390|48391|48392|48393|48394|48395|48396|48397|48398|48399|48400|48401|48402|48403|48404|48405|48406|48407|50298|50308|50675|51078|51094|51098|51100|51200|51201|51202|51203|51204|51205|51206|51207|51208|51209|51210|51211|51212|51213|51214 "mainBackpack" as "foundItem"
                getlabel "foundItem" "desc"
                if inlist "itemDescriptions" "desc"
                    menu "foundItem" 0
                    waitforgump 4274928655 1000
                    gumpresponse 1
                    wait 250
                endif
                @ignore "foundItem"
            endwhile
            while findtype 51215|51216|51217|51218|51219|51220|51221|51222|51223|51224|51225|51226|51227|51228|51229|51230|51231|51232|51233|51234|51235|51236|51237|51238|51239|51240|51241|51242|51243|51244|51245|51246|51247|51248|51249|51250|51251|51252|51253|51254|51255|51256|51257|51258|51259|51260|51261|51262|51263|51264|51265|51266|51267|51268|51269|51270|51271|51272|51273|51274|51275|51276|51277|51278|51279|51280|51281|51282|51283|51284|51285|51286|51287|51288|51289|51290|51291|51292|51293|51294|51295|51296|51297|51298|51299|51300|51301|51302|51303|51304|51305|51306|51307|51308|51309|51310|51311|51312|51313|51314|51315|51316|51317|51318|51319|51320|51321|51322|51323|51324|51325|51326|51327|51328|51329|51330|51331|51332|51333|51334|51335|51336|51337|51338|51339|51340|51341|51342|51343|51344|51345|51346|51347|51348|51349|51350|51351|51352|51353|51354|51355|51356|51357|51358|51359|51360|51361|51362|51363|51364|51365|51366|51367|51368|51369|51370|51371|51372|51373|51374|51375|51400|51401|51402|51403|51404|51405|51406|51407|51408|51409|51430|51431|51432|51433|51434|51435|51436|51437|51438|51439|51440|51441|51442|51443|51444|51445|51446|51447|51448|51449|51470|51471|51472|51473|51474|51475|51476|51477|51478|51479|53547|53548|53549|53550|53551|53552|53553|53554|53555|53556|53557|53558|53559|53560|53561|53562|53563|53564|53565|53566|53567|53568|53569|53570|53571|53572|53573|53574|53575|53576|53577|53578|53579|53580|53581|53582|53583|53584|53585|53586|53587|53588|53589|53590|53591|53592|53593|53594|53595|53596|53597|53598|53599|53600|53601|53602|53603|53604|53605|53606|53607|53608|53609|53610|53611 "mainBackpack" as "foundItem"
                getlabel "foundItem" "desc"
                if inlist "itemDescriptions" "desc"
                    menu "foundItem" 0
                    waitforgump 4274928655 1000
                    gumpresponse 1
                    wait 250
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
                        wait 250
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
                        wait 250
                    endif
                    @ignore "foundItem"
                endwhile
                while findtype 22186|22188|22189|22190|22191|22192|22193|22194|22195|22196|22197|22199|22261|22264|22272|22285|22286|22287|22288|22289|22290|22291|22292|22293|22294|22295|22296|22297|22298|22336|22417|22418|22419|22420|22421|22422|22423|22426|22427|22428|22429|22430|22431|22432|22433|22434|22435|22436|22437|22438|22439|22440|22441|22442|22443|22444|22445|22449|22451|22453|22455|22456|23009|23034|23035|23774|23996|23997|24175|24179|24181|24182|24183|24184|24187|24188|24190|24191|24193|24195|24196|24197|24199|24246|24382|24383|24384|24385|24386|24387|24388|24389|24390|24391|24392|24393|24394|24395|24396|24397|24398|24399|24400|24401|24402|24403|24404|24405|24406|24407|24408|24409|24410|24411|24412|24413|24414|24415|24416|24417|24418|24419|24420|24421|24422|24423|24424|24425|24426|24427|24428|24429|24430|24431|24432|24433|24434|25647|25759|26640|26664|26669|26670|26671|26672|26688|26689|26693|26700|26701|26719|26720|26721|26724|26732|26734|26735|26736|26737|27561|27562|27563|27564|27565|27577|27580|27584|27611|27612|27640|27642|28760|28765|28768|28775|28795|28799|28803|28908|28909|28910|28911|28924|28994|28995|29024|29025|29026|29027|29028|29029|29031|29032|29033|29034|29035|29036|29037|29038|29040|29104|29106|29107|29108|29142|29350|29030|29352|29354|29355|29421|29382|29425|29428|29430|29431|29463|29495|29497|29498|29502 "mainBackpack" as "foundItem"
                    getlabel "foundItem" "desc"
                    if inlist "itemDescriptions" "desc"
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 250
                    endif
                    @ignore "foundItem"
                endwhile
                while findtype 30561|30562|30563|30564|30565|30566|30567|30568|30573|30574|30575|30576|30577|30578|30579|30580|30582|30583|30586|30587|30588|30589|30590|30591|30592|30596|30599|30601|30602|30603|30604|30608|30609|30610|30611|30612|30613|30614|30615|30617|30618|30621|30622|30623|30624|30625|30626|30627|30628|30629|30630|30631|30632|30633|30634|30635|30636|30637|30638|30639|30640|30641|30642|30643|30644|30645|30646|30647|30648|30649|30650|30651|30652|30653|30655|30657|30658|30659|30660|30661|30662|30663|30766|30767|30768|30769|30770|30771|30772|30773|30775|30776|30778|30818|30819|30821|30822|30823|30825|30826|30827|30828|30829|30850|30851|30852|30853|30854|30855|30856|30857|30858|30859|30860|30866|30867|30868|30869|30870|30871|30872|30878|30967|30969|30970|30971|30972|30973|30974|30975|30976|30977|30978|30979|30980|30981|30982|30983|30984|30985|30986|36752|39264|39343|39344|39345|39346|39347|39348|39349|39350|39351|39352|39353 "mainBackpack" as "foundItem"
                    getlabel "foundItem" "desc"
                    if inlist "itemDescriptions" "desc"
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 250
                    endif
                    @ignore "foundItem"
                endwhile
                while findtype 41459|41460|41461|41462|41510|42227|42239|42240|42242|42243|42244|42517|42574|42665|43159|43160|43161|43162|43163|43164|43165|43166|43167|43168|43169|43170|43171|43172|43173|43174|43175|43176|43177|43178|43179|43180|43181|43182|43206|43207|43208|43209|43210|43277|43279|43320|44310|44312|44314|44795|44796|44797|44798|44799|44800|44801|44804|44805|44808|44810|44986|45002|45120|45156|45157|45182|45193|45208|45211|45214|45216|45218|45220|45222|45235|45236|45238|45239|45241|45242|45246|45247|45248|45250|45251|45252|45254|45255|45257|45281|45282|45300|45315|45316|45371|45372|45373|45374|45375|45376|45377|45378|45379|45380|45381|45382|45383|45384|45385|45386|45387|45388|45389|45390|45391|45392|45393|45394|45395|45396|45397|45398|45399|45400|45401|45402|45403|45404|45405|45406|45407|45408|45409|45410|45411|45412|45413|45414|45415|45416|45417|45418|45419|45420|45421|45422|45423|45424|45425|45426|45427|45428|45429|45430|45828|45830|47107|47109|47111|48357|48358|48359|48360|48361|48362|48363|48364|48365|48366|48367|48368|48369|48370|48371|48372|48373|48374|48375|48376|48377|48378|48379|48380|48381|48382|48383|48384|48385|48386|48387|48388|48389|48390|48391|48392|48393|48394|48395|48396|48397|48398|48399|48400|48401|48402|48403|48404|48405|48406|48407|50298|50308|50675|51078|51094|51098|51100|51200|51201|51202|51203|51204|51205|51206|51207|51208|51209|51210|51211|51212|51213|51214 "mainBackpack" as "foundItem"
                    getlabel "foundItem" "desc"
                    if inlist "itemDescriptions" "desc"
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 250
                    endif
                    @ignore "foundItem"
                endwhile
                while findtype 51215|51216|51217|51218|51219|51220|51221|51222|51223|51224|51225|51226|51227|51228|51229|51230|51231|51232|51233|51234|51235|51236|51237|51238|51239|51240|51241|51242|51243|51244|51245|51246|51247|51248|51249|51250|51251|51252|51253|51254|51255|51256|51257|51258|51259|51260|51261|51262|51263|51264|51265|51266|51267|51268|51269|51270|51271|51272|51273|51274|51275|51276|51277|51278|51279|51280|51281|51282|51283|51284|51285|51286|51287|51288|51289|51290|51291|51292|51293|51294|51295|51296|51297|51298|51299|51300|51301|51302|51303|51304|51305|51306|51307|51308|51309|51310|51311|51312|51313|51314|51315|51316|51317|51318|51319|51320|51321|51322|51323|51324|51325|51326|51327|51328|51329|51330|51331|51332|51333|51334|51335|51336|51337|51338|51339|51340|51341|51342|51343|51344|51345|51346|51347|51348|51349|51350|51351|51352|51353|51354|51355|51356|51357|51358|51359|51360|51361|51362|51363|51364|51365|51366|51367|51368|51369|51370|51371|51372|51373|51374|51375|51400|51401|51402|51403|51404|51405|51406|51407|51408|51409|51430|51431|51432|51433|51434|51435|51436|51437|51438|51439|51440|51441|51442|51443|51444|51445|51446|51447|51448|51449|51470|51471|51472|51473|51474|51475|51476|51477|51478|51479|53547|53548|53549|53550|53551|53552|53553|53554|53555|53556|53557|53558|53559|53560|53561|53562|53563|53564|53565|53566|53567|53568|53569|53570|53571|53572|53573|53574|53575|53576|53577|53578|53579|53580|53581|53582|53583|53584|53585|53586|53587|53588|53589|53590|53591|53592|53593|53594|53595|53596|53597|53598|53599|53600|53601|53602|53603|53604|53605|53606|53607|53608|53609|53610|53611 "mainBackpack" as "foundItem"
                    getlabel "foundItem" "desc"
                    if inlist "itemDescriptions" "desc"
                        menu "foundItem" 0
                        waitforgump 4274928655 1000
                        gumpresponse 1
                        wait 250
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
        print("sort_tree_quick_test7")
        self.root.clipboard_clear()
        self.root.clipboard_append(scriptString)
        self.root.update()
        print("sort_tree_quick_test_done")

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
        print(f"Window not found. Error: {e}")
        return None
    script_editor = window.child_window(auto_id="scriptEditor", control_type="FastColoredTextBoxNS.FastColoredTextBox")
    if script_editor.is_enabled():
        return False #script editor is enabled and editable so script isnt running
    else:
        return True  #script editor is disabled and not editable so script is running



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
        # Update label text and colors based on status
        self.label1.config(text=f"{self.char1[0]}: {'Running' if bool_values.get('bool1', False) else 'Not Running'}",
                        bg="green" if bool_values.get('bool1', False) else "red")
        self.label2.config(text=f"{self.char2[0]}: {'Running' if bool_values.get('bool2', False) else 'Not Running'}",
                        bg="green" if bool_values.get('bool2', False) else "red")
        self.label3.config(text=f"{self.char3[0]}: {'Running' if bool_values.get('bool3', False) else 'Not Running'}",
                        bg="green" if bool_values.get('bool3', False) else "red")

        # Update previous states
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
            print("Something went wrong when selecting original window")
            return
        extracted_name = match_client.group(1)
        try:
            window = focus_named_assistant(extracted_name)
        except Exception as e:
            print(f"Purchase Script Error: {e}")
    elif match_assistant: #if focus is on assistant, set assistant as target
        extracted_name = match_assistant.group(1)
        for window in gw.getAllWindows():
            if extracted_name in window.title and window != active_window:
                original = connect_to_window(window._hWnd)
                break
        if not original:
            print("Something went wrong when selecting original window")
            return
        window = connect_to_window(active_window._hWnd)
    else:
        print("No match found in the active window's title.")
        return
    if not window:
        print("Error connecting to window")
        return False
    tab_control = window.TabControl
    if tab_control.get_selected_tab() != 9:
        tab_control.select("TabControlScripts")
    tree = window.TreeView
    node = tree.get_item(['aaaaab'])
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
                print('Play button missing!')
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
                print('Stop button missing!')
                return
    except Exception as e:
        print(f"error: {e}")
    #win32api.SetCursorPos(mouse_pos)
        
def append_recall_home_script():
    try:
        current_content = root_ghost.root.clipboard_get()

        print(current_content)
        append_string = """
wait 1000
script 'AliRoom'
"""
        new_content = current_content + append_string
        pyperclip.copy(new_content)

    except Exception as e:
        print(f"Err: {e}")

#print(f"Press ctrl+alt+` to find the Client/Assistant window for the active window...")
keyboard.add_hotkey("ctrl+alt+c", start_purchase_script)
keyboard.add_hotkey("ctrl+alt+`", switch_focus)
keyboard.add_hotkey("ctrl+alt+1", lambda: focus_named_assistant('a lost girl'))
keyboard.add_hotkey("ctrl+alt+2", lambda: focus_named_assistant('Vendor Police'))
keyboard.add_hotkey("ctrl+alt+3", lambda: focus_named_assistant('Aproctoflecticus'))
keyboard.add_hotkey("alt+shift+`", lambda: focus_scraper())




root_ghost = False
def main():
    root = tk.Tk()
    global root_ghost
    root_ghost = AliApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()