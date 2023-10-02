#foci/weapon oil/ammo bundle
import os
import glob
import math
import requests
import re
import time
import datetime
import webbrowser
import pyautogui
import sqlite3
import threading
import queue
import tkinter as tk
from tkinter import ttk
from bs4 import BeautifulSoup
from contextlib import contextmanager
from urllib.parse import quote_plus
core_prices = { #exact string MATTERS
    "Blood Aspect Core": 3000,
    "Holy Aspect Core": 3000,
    "Earth Aspect Core": 3000,
    "War Aspect Core": 3000,
    "Death Aspect Core": 4000,
    "Water Aspect Core": 8000,
    "Gadget Aspect Core": 3000,
    "Shadow Aspect Core": 10000,
    "Void Aspect Core": 13000,
    "Fire Aspect Core": 10000,
    "Discipline Aspect Core": 8000,
    "Lyric Aspect Core": 14000,
    "Poison Aspect Core": 28000,
    "Eldritch Aspect Core": 35000,
    "Fortune Aspect Core": 45000,
    "Command Aspect Core": 95000,
    "Artisan Aspect Core": 60000,
    "Air Aspect Core": 40000,
    "Harvest Aspect Core": 130000,
}

extract_prices = { #exact string MATTERS
    "Blood Aspect Extract": 2000,
    "Holy Aspect Extract": 2000,
    "Earth Aspect Extract": 2000,
    "Death Aspect Extract": 2000,
    "Water Aspect Extract": 5000,
    "Gadget Aspect Extract": 3000,
    "Shadow Aspect Extract": 5000,
    "Void Aspect Extract": 5000,
    "Fire Aspect Extract": 3000,
    "Discipline Aspect Extract": 4000,
    "Lyric Aspect Extract": 5000,
    "Poison Aspect Extract": 8000,
    "Eldritch Aspect Extract": 8000,
    "Fortune Aspect Extract": 7000,
    "Command Aspect Extract": 8000,
    "Artisan Aspect Extract": 5000,
    "Air Aspect Extract": 7000,
    "Harvest Aspect Extract": 10000,
}

distil_prices = { #exact string MATTERS
    "Blood Aspect Distillation": 2000,
    "Holy Aspect Distillation": 2000,
    "Earth Aspect Distillation": 2000,
    "Death Aspect Distillation": 3000,
    "Water Aspect Distillation": 5000,
    "Gadget Aspect Distillation": 2000,
    "Shadow Aspect Distillation": 5000,
    "Void Aspect Distillation": 5000,
    "Fire Aspect Distillation": 3000,
    "Discipline Aspect Distillation": 5000,
    "Lyric Aspect Distillation": 5000,
    "War Aspect Distillation": 2000,
    "Poison Aspect Distillation": 8000,
    "Eldritch Aspect Distillation": 8000,
    "Fortune Aspect Distillation": 7000,
    "Command Aspect Distillation": 8000,
    "Artisan Aspect Distillation": 5000,
    "Air Aspect Distillation": 7000,
    "Harvest Aspect Distillation": 10000,
}

map_prices = { #exact string MATTERS
    "plainly drawn treasure map: level 1 (undeciphered)": 4000,
    "plainly drawn treasure map: level 1 [100.0% estimated accuracy]": 4000,
    "expertly drawn treasure map: level 2 (undeciphered)": 9000,
    "expertly drawn treasure map: level 2 [100.0% estimated accuracy]": 9000,
    "adeptly drawn treasure map: level 3 (undeciphered)": 20000,
    "adeptly drawn treasure map: level 3 [100.0% estimated accuracy]": 20000,
    "cleverly drawn treasure map: level 4 (undeciphered)": 25000,
    "cleverly drawn treasure map: level 4 [100.0% estimated accuracy]": 25000,
    "deviously drawn treasure map: level 5 (undeciphered)": 35000,
    "deviously drawn treasure map: level 5 [100.0% estimated accuracy]": 35000,
    "ingeniously drawn treasure map: level 6 (undeciphered)": 45000,
    "ingeniously drawn treasure map: level 6 [100.0% estimated accuracy]": 45000,
    "diabolically drawn treasure map: level 7 (undeciphered)": 60000,
    "diabolically drawn treasure map: level 7 [100.0% estimated accuracy]": 60000,
    "legendarily drawn treasure map: level 8 (undeciphered)": 275000,
    "legendarily drawn treasure map: level 8 [100.0% estimated accuracy]": 275000,
}
scroll_prices = { #exact string MATTERS
    "alchemy skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 29000, #alchemy skill mastery scroll : 3 (used to increase a player's skill cap for a skill by 1)
    "animal lore skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 18000,
    "animal taming skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 18000,
    "carpentry skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "arms lore skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "begging skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "blacksmithy skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "camping skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "cartography skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "chivalry skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 21000,
    "cooking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "detect hidden skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 13000,
    "lockpicking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 18000,
    "discordance skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "fishing skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 13000,
    "forensic eval skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "herding skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 18000,
    "inscription skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 19000,
    "item id skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "lumberjacking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "mining skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "musicianship skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "necromancy skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 24000,
    "peacemaking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "poisoning skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "provocation skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "spirit speak skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "stealth skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 14000,
    "tailoring skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 40000,
    "taste id skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "tinkering skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "tracking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "veterinary skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 18000,
}

link_prices = { #exact chain type string MATTERS
    "Melee Accuracy": [100000,650000,2800000], #Melee Accuracy/Defense
    "Melee Defense": [100000,650000,2800000], #Melee Accuracy/Defense
    "Melee Accuracy/Defense": [100000,650000,2800000],
    "Melee Special Chance/Special Damage": [100000,710000,2800000],
    "Melee Special Chance": [100000,710000,2800000], #Melee Special Chance/Special Damage
    "Melee Swing Speed": [130000,700000,2800000],
    "Melee Damage": [70000,500000,2300000], #Melee Damage/Ignore Armor Chance
    "Melee Ignore Armor Chance": [70000,500000,2300000], #Melee Damage/Ignore Armor Chance
    "Melee Damage/Ignore Armor Chance": [70000,500000,2300000],
    "Melee Aspect Effect Modifier": [70000,700000,2700000],
    "Melee Aspect Effect Chance": [100000,700000,2800000],
    "Spell Damage": [70000,500000,2300000], #Spell Damage/Ignore Resist Chance
    "Spell Damage When No Followers": [70000,500000,2300000],
    "Spell Ignore Resist Chance": [70000,500000,2300000], #Spell Damage/Ignore Resist Chance
    "Spell Damage/Ignore Resist Chance": [70000,500000,2300000],
    "Spell Charged Chance": [70000,500000,2300000], #Spell Charged Chance/Charged Damage
    "Spell Charged Damage": [70000,500000,2300000], #Spell Charged Chance/Charged Damage
    "Spell Charged Chance/Charged Damage": [70000,500000,2300000],
    "Meditation Rate": [70000,500000,2300000], #Meditation Rate/Spell Disrupt Avoid Chance
    "Spell Disrupt Avoid Chance": [70000,500000,2300000], #Meditation Rate/Spell Disrupt Avoid Chance, Spell Damage When No Followers
    "Meditation Rate/Disrupt Avoid Chance": [70000,500000,2300000], #Spell Damage When No Followers
    "Spell Aspect Effect Modifier": [70000,600000,2500000],
    "Spell Aspect Special Chance": [135000,750000,2500000],
    "Damage to Beastial Creatures": [80000,625000,2500000], #Nusero Damage
    "Damage to Construct Creatures": [80000,625000,2500000], #Mausoleum Damage
    "Damage to Daemonic Creatures": [80000,625000,2500000], #Inferno Damage
    "Damage to Elemental Creatures": [80000,625000,2500000], #Mount Petram Damage
    "Damage to Humanoid Creatures": [80000,625000,2500000], #Aegis Keep Damage
    "Damage to Monstrous Creatures": [80000,625000,2500000], #Cavernam Damage
    "Damage to Nature Creatures": [80000,625000,2500000], #Darkmire Temple Damage
    "Damage to Undead Creatures": [80000,625000,2500000], #Ossuary Damage
    "Nusero Damage": [80000,625000,2500000],
    "Mausoleum Damage": [80000,625000,2500000],
    "Inferno Damage": [80000,625000,2500000],
    "Mount Petram Damage": [80000,625000,2500000],
    "Aegis Keep Damage": [80000,625000,2500000],
    "Cavernam Damage": [80000,625000,2500000],
    "Darkmire Temple Damage": [80000,625000,2500000],
    "Ossuary Damage": [80000,625000,2500000],
    "Pulma Damage": [80000,625000,2500000],
    "Shadowspire Cathedral Damage": [90000,625000,2500000],
    "Wilderness Damage": [90000,625000,2500000],
    "Follower Damage": [160000,750000,2800000],
    "Damage to Barded Creatures": [110000,650000,2800000],
    "Damage to Poisoned Creatures": [120000,650000,2800000],
    "Poison Damage/Resist Ignore": [70000,500000,2300000],
    "Backstab Damage": [100000,600000,2500000],
    "Trap Damage": [100000,700000,2800000],
    "Damage to Bosses": [80000,600000,2600000],
    "Damage on Ships": [125000,650000,2600000],
    "Ship Cannon Damage": [125000,650000,2600000],
    "Damage to Creatures Above 66% HP": [70000,500000,2300000], #Damage Dealt By Player
    "Damage to Creatures Below 33% HP": [70000,500000,2300000], #Damage Dealt By Player
    "Damage Dealt By Player": [70000,500000,2300000],
    "Physical Damage Resistance": [70000,500000,2300000], #Damage Resistance
    "Spell Damage Resistance": [70000,500000,2300000], #Damage Resistance
    "Follower Damage Resistance": [150000,700000,2800000], #Alchemy/Healing/Veterinary Skill, Follower Attack Speed
    "Effective Parrying Skill": [70000,500000,2300000], #Damage Resistance
    "Effective Magic Resist Skill": [70000,500000,2300000], #Damage Resistance
    "Healing Received": [70000,500000,2300000], #Effective Alchemy/Healing/Veterinary Skill
    "Follower Attack Speed": [140000,700000,2800000],
    "Follower Healing Received": [140000,700000,2800000], #Effective Alchemy/Healing/Veterinary Skill, Follower Attack Speed
    "Boss Damage Resistance": [70000,500000,2300000], #Damage Resistance
    "Damage Resistance on Ships": [70000,500000,2300000], #Damage Resistance
    "Damage Resistance": [70000,500000,2300000],
    "Chest Success Chances/Progress": [100000,650000,2700000],
    "Effective Skill on Chests": [100000,650000,2700000],
    "Alchemy/Healing/Veterinary": [70000,500000,2300000],
    "Effective Lockpicking Skill": [100000,650000,2700000], #Chest Success Chances/Progress
    "Effective Poisoning Skill": [70000,500000,2300000], #Poison Damage/Resist Ignore
    "Effective Barding Skill": [110000,650000,2800000], #Bard Reset/Break Ignore Chance
    "Chivalry Skill": [70000,500000,2300000], 
    "Necromancy Skill": [140000,750000,2800000], #Follower Damage, Follower Damage Resistance
    "Barding Effect Durations": [70000,650000,2600000], #Bard Reset/Break Ignore Chance
    "Bard Reset/Break Ignore Chance": [70000,650000,2600000],
    "Spirit Speak/Inscription": [140000,750000,2800000], #Follower Damage, Follower Damage Resistance
    "Chance on Stealth For 5 Extra Steps": [110000,720000,2700000],
    "Gold/Doubloon Drop Increase": [70000,500000,2300000],
    "Special/Rare Loot Chance": [70000,500000,2300000],
    "reforging tool": [85000,180000,350000],
}

misc_prices = { #exact string matters
    "research materials (double-click to research)": 35000,
    "mastercrafting diagram": 15500,
    "a skill mastery orb (used to increase a player's total skill cap by 1)": 15000, #a skill mastery orb : 3 (used to increase a player's total skill cap by 1)
    "an arcane scroll": 1000,
    "plant chemicals": 1750,
    "supremely potent magic spellbook": 13000,
    "an ankh token":9000,
    "prevalia coins [blessed]":17500, #prevalia coins : 5 [blessed]
    #"a random spell hue deed": 17000,
    #"research guide (25 uses remaining)":15000,
    #"aspect kit": 22000,
    #"exceedingly potent magic spellbook": 3500,
    "arcane essence": 30,
    "iron ingot commodity (5,000 total)": 75000,
    "board commodity (5,000 total)": 65000,
    "leather commodity (5,000 total)": 8500,
    "a message in a bottle": 19000, 
    "pristine lumber": 32000, 
    "immaculate stone": 32000,
    "an emote deed": 200000,
    "a battle commendation (double-click to consume and receive reward item)": 10000,
    "invulnerability leather cap": 100000,
}



def scrape_wide_page(item, prices_obj):
    corrupted_link_price_threshold = 200000
    start_time = time.time()  # Record the current time
    page_url = "https://outlandmalls.com/?item=" + quote_plus(item) + "&search_category_id=0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(page_url, headers=headers)
    elapsed_time = time.time() - start_time  # Calculate the elapsed time
    #print(f'get: {elapsed_time}')
    if response.status_code != 200:
        append_to_tree(f"Failed to retrieve the webpage: {item}. Status code: {response.status_code}")
        return None
    soup = BeautifulSoup(response.content, 'lxml')
    #print(f'soup: {time.time() - start_time}')
    if soup:
        # Find the table with the specific id
        table = soup.find('table', id="item-search-results")
        if not table:
            return
        # Extract all rows from the table body
        out_data = []
        rows = table.tbody.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            time_cell = cells[7]
            time_string = time_cell.text.strip().lower()  # Convert to lowercase for consistent comparison
            if is_time_recent(time_string):
                vendor_cell = cells[1]
                location_cell = cells[2]
                name_cell = cells[3]
                quantity_cell = cells[4]
                price_cell = cells[6]
                vendor_string = vendor_cell.text.strip()
                vendor_serial = vendor_cell.find('a')['href'].split('/')[-1]
                location_string = location_cell.text.strip()
                location_link = location_cell.find('a')['href']
                location_split = location_link.split('#')
                formatted_location_link = f"{location_split[0]}?{vendor_serial}#{location_split[1]}"
                quantity_string = quantity_cell.text.strip()
                name_string = name_cell.text.strip()
                price = float(price_cell.text.strip().replace(',', ''))  # Convert price to float
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
                    ratio = round(price / threshold,2)
                else:
                    ratio = 1000
                if(price <= threshold or search_pricedepth.get() == 2):
                    format_url = "https://outlandmalls.com/?item=" + quote_plus(name_string) + "&search_category_id=0"
                    out_data.append((f"{name_string}",f"{price}/{threshold}",f"{ratio}",f"{quantity_string}",f"{vendor_string}",f"{location_string}",f"{time_string}",f"{formatted_location_link}",f"{format_url}"))
        print(f"out_data length: {len(out_data)}")
        #for tuple in out_data:
        data_queue_appendcommand.put(out_data)
    #print(f'end: {time.time() - start_time}')
    sleep_time = 0.3 - elapsed_time
    if sleep_time > 0:
        time.sleep(sleep_time)

def scrape_vendor_updates():
    my_locations = {
        #"location name": (x,y),
        "S Terran Clearing": (927,1471),
        "N Terran Clearing": (869,1381),
        "Minotaur Island": (3967,1736),
        "Minotaur Island E": (4067,1766),
        "N Prev Clearing SW": (1560,1438),
        "N Prev Clearing S": (1589,1430),
        "N Prev Clearing W": (1555,1404),
        "N Prev Clearing N": (1576,1389),
        "N Prev Clearing E": (1629,1421),
        "Prevalia Gate": (1475,1488),
        "West of Prev Gate": (1425,1483),
        "S Cambria Gate": (1709,3182),
        "SW Cambria Gate": (1669,3177),
        "N Cambria Gate": (1706,3129),
        "NW Cambria Gate": (1670,3138),
        "West of SSC": (3267,689),
        "NE Outpost Close": (3387,377),
        "NE Outpost Far": (3398,178),
        "NE Outpost Far NW": (3250,296),
        "S of Anchor's Rest": (3757,740),
        "Far South of Anchor's Rest": (3715, 872),
        "S Prevalia Xroad": (1546,1751),
        "N Prevalia Sandbar": (1657,1320),
        "Frost Forest": (3622,447),
        "Khal": (2002,1795),
        "Mine": (4008,477),
        "AR0": (3947,504),
        "AR1": (3961,559),
        "AR2": (3961,477),
        "AR3": (4002,554),
        "AR4": (4020,515),
        "AR5": (4050,540),
        "AR6": (4050,508), 
        "AR7": (4055,463),
        "SW Prevalia Clearing SE": (1547,1653),
        "SW Prevalia Clearing NE": (1544,1623),
        "SW Prevalia Clearing SW": (1510,1657),
        "W Andaria Gate": (2315,639),
        "N Andaria Gate": (2334,591),
        "South of Pulma": (1780,1048),
        "Western Camp Island": (3495,1467),
        "TRT":(1756,2341),
        "South of TRT": (1779,2388),
        "South of GH": (3981,854),
        "SOF Island Mall": (3498,3748),
        "NW Outpost Gate": (2940,563),
        "NW Outpost Gate Far": (2982,500),
        "N Outpost Gate": (2980,579),
        "N Outpost Gate 2": (2975,547),
        "N Outpost Gate 3": (3001,496),
        "Cedar Island Mall":(3975,355),
        "Cedar Island Center":(4025,305),
        "Pwnstar":(4218,1090),
        "Frozen Ruins SE":(1612,780),
        "Frozen Ruins SW":(1546,753),
    }
    start_time = time.time()  # Record the current time
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    url = "https://outlandmalls.com/vendors/"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage: {url}. Status code: {response.status_code}")
        status_var.set('Vendor Page Failed')
        return
    status_var.set(f"Scanning Locations")
    soup = BeautifulSoup(response.content, 'lxml')
    if not soup:
        status_var.set('Vendor Page Soup Failed')
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
        x1, y1 = map(int,tuple_loc)
        closest = None
        min_distance = 20
        min_time = 1000000
        for update_time, list_loc,vendor_name in found_locations:
            x2, y2 = map(int,list_loc)
            distance = get_distance(x1,y1,x2,y2)
            if distance > min_distance:
                continue
            sec_since_scan = get_seconds_from_string(update_time)
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
    new_window = tk.Toplevel(root)
    new_window.wm_attributes("-topmost", 1)
    new_window.title("Results")
    scrollbar = tk.Scrollbar(new_window, orient="vertical")
    listbox = tk.Listbox(new_window, yscrollcommand=scrollbar.set, width=60, height=20)
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side="right", fill="y")
    listbox.pack(side="left", fill="both", expand=True)
    for locName,scanString,minTime,x,y,name in out_arr:
        result = f"{locName}: {scanString}: {x},{y}"
        listbox.insert(tk.END, result)
    elapsed_time = round(time.time() - start_time,2)
    print(f"end: {elapsed_time}")

def clean_chainlink_string(string):
    prefixes = ['bronze mastery chain link ', 'silver mastery chain link ', 'gold mastery chain link ', 'corrupted mastery chain link ']
    for prefix in prefixes:
        if string.startswith(prefix):
            string = string[len(prefix):]
    if 'reforging tool' in string:
        return string
    if '%' in string:
        return string[:-9]
    return string[:-8]

flag = False
def check_queue_appendcommand():
    global flag
    try:
        data = data_queue_appendcommand.get_nowait()
        for tuple in data:
            append_to_tree(*tuple)
        flag = True
        root.after(100, check_queue_appendcommand)  # check again after 100ms
    except queue.Empty:
        if flag:
            flag = False
            if search_sortmode.get() == 2:
                sort_column_tuple("Ratio", "Item", False, sort_key_tuple)
        root.after(500, check_queue_appendcommand)  # if queue is empty, check again after a longer delay

# def check_queue_sortcommand():
#     if data_queue_appendcommand.empty() is False:
#         root.after(100, check_queue_sortcommand)
#     else:
#         try:
#             data = data_queue_sortcommand.get_nowait()
#             if data:
#                 if search_sortmode.get() == 2:
#                     sort_column_tuple("Ratio", "Item", False, sort_key_tuple)
#             root.after(100, check_queue_sortcommand)
#         except queue.Empty:
#             root.after(100, check_queue_sortcommand)

def append_to_tree(text1='',text2='',text3='',text4='',text5='',text6='',text7='',text8='',text9=''):
    if len(text3):
        ratio = float(text3)
        if ratio < 0.6:
            item = tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9), tags=("ultra",))
        elif ratio <= 0.7:
            item = tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9), tags=("high",))
        elif ratio <= 0.8:
            item = tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9), tags=("med",))
        elif ratio <= 0.9:
            item = tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9), tags=("low",))
        elif ratio < 0.95:
            item = tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9), tags=("verylow",))
        elif ratio >= 0.95 and ratio <= 1.0:
            item = tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9), tags=("base",))
        else:
            item = tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9))
    else:
        item = tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9))
    #tree.see(item)

def is_time_recent(time_string):
    seconds_threshold = parse_combobox()
    print(seconds_threshold)
    if seconds_threshold == 'All Time':
        return True
    time_seconds = get_seconds_from_string(time_string)
    if not time_seconds:
        time_seconds = 1000000
    return time_seconds <= seconds_threshold

def parse_combobox():
    option = search_combobox_timeframe.get()
    option_dict = {
        '30 Seconds': 30,
        '1 Minute': 60,
        '5 Minutes': 300,
        '30 Minutes': 1800,
        '1 Hour': 3600,
        'All Time': 'All Time'
    }
    return option_dict[option]

def get_seconds_from_string(time_string):
    parse = str(time_string)
    time_seconds = 0
    if 'second ago' in parse or 'seconds ago' in parse:
        if 'about' in parse:
            time_seconds += 1
        else:
            split = parse.split(' second')
            seconds = int(split[0])
            if seconds:
                time_seconds += seconds
    elif 'minute ago' in parse or 'minutes ago' in parse:
        if 'about' in parse:
            time_seconds += 59 #about a minute
        else:
            split = parse.split(' minute')
            minutes = int(split[0])
            if minutes:
                time_seconds += minutes * 60
    elif 'hour ago' in parse or 'hours ago' in parse:
        if 'about' in parse:
            time_seconds += 3540 #about an hour
        else:
            split = parse.split(' hour')
            hours = int(split[0])
            if hours:
                time_seconds += hours * 3600
    elif 'day ago' in parse or 'days ago' in parse:
        time_seconds = 1000000 #about an hour
    else:
        return False
    return time_seconds

def get_distance(x1, y1, x2, y2):
    return round(math.sqrt((x2 - x1)**2 + (y2 - y1)**2))

def send_to_discord(content):
    webhook_url = "https://discord.com/api/webhooks/1145494637180633240/AR6iXN2MfdTOsldgTUcCSu_d6sCScan2vdp8zb0LwovDlB4DNq7nLcN-N_AnMHwVlIhp"
    data = {
        "content": content
    }
    response = requests.post(webhook_url, json=data)
    time.sleep(0.2)
    return response.status_code

def on_treeview_click(event):
    if tree.identify_region(event.x, event.y) == "heading":
        return

    row_id = tree.identify_row(event.y)
    col_id = tree.identify_column(event.x)
    
    # If the URL column is clicked
    #if col_id == "Location":
    if(len(tree.item(row_id,'values')) > 1 and tree.item(row_id,'values')[1]):
        if col_id == "#1":
            url = tree.item(row_id, "values")[8]
        else:
            url = tree.item(row_id, "values")[7]

        value_to_copy_raw = tree.item(row_id, "values")[7]
        number_match = re.search(r'\?(\d+)(?:\?(\d+))?#',value_to_copy_raw)
        vendor_serial = number_match.group(1) if number_match else 0
        item_serial = number_match.group(2) if number_match else 0
        # split = value_to_copy_raw.(', ')
        # value_to_copy = ">waypoint " + split[0] + " " + split[1]
        # Copy the value to the clipboard
        root.clipboard_clear()
        root.clipboard_append(vendor_serial)
        root.update()
        webbrowser.open(url)

def on_treeview_select():
    item = tree.selection()[0]
    row_values = tree.item(item,'values')
    
    snapshot_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    description = row_values[0]
    price_string = row_values[1] #80000.0/80000.0
    left_side_price = price_string.split('/')[0]
    price = int(float(left_side_price))
    quantity = row_values[3] #80000.0/80000.0
    value_to_copy_raw = row_values[7] #'https://www.exploreoutlands.com/?471890?1251126567#pos:869,1381,13'
    number_match = re.search(r'\?(\d+)(?:\?(\d+))?#', value_to_copy_raw)
    vendor_serial = number_match.group(1) if number_match else 0
    id = number_match.group(2) if number_match else 0
    # execute_query("INSERT INTO sales_history (snapshot_time, id, price, description, quantity) VALUES (?, ?, ?, ?, ?)",
    #                        (snapshot_time, id, price, description, quantity))
    print(f"You selected item: {snapshot_time}, {id}, {price}, {description}, {quantity}")

def show_context_menu(event):
    if tree.identify_region(event.x, event.y) == "heading":
        return
    my_locations = {
        #"location name": (x,y),
        "S Terran Clearing": (927,1471),
        "N Terran Clearing": (869,1381),
        "Minotaur Island": (3967,1736),
        "Minotaur Island E": (4067,1766),
        "N Prev Clearing SW": (1560,1438),
        "N Prev Clearing S": (1589,1430),
        "N Prev Clearing W": (1555,1404),
        "N Prev Clearing N": (1576,1389),
        "N Prev Clearing E": (1629,1421),
        "Prevalia Gate": (1475,1488),
        "West of Prev Gate": (1425,1483),
        "S Cambria Gate": (1709,3182),
        "SW Cambria Gate": (1669,3177),
        "N Cambria Gate": (1706,3129),
        "NW Cambria Gate": (1670,3138),
        "West of SSC": (3267,689),
        "NE Outpost Close": (3387,377),
        "NE Outpost Far": (3398,178),
        "NE Outpost Far NW": (3250,296),
        "S of Anchor's Rest": (3757,740),
        "Far South of Anchor's Rest": (3715, 872),
        "S Prevalia Xroad": (1546,1751),
        "N Prevalia Sandbar": (1657,1320),
        "Frost Forest": (3622,447),
        "Khal": (2002,1795),
        "Mine": (4008,477),
        "AR0": (3947,504),
        "AR1": (3961,559),
        "AR2": (3961,477),
        "AR3": (4002,554),
        "AR4": (4020,515),
        "AR5": (4050,540),
        "AR6": (4050,508), 
        "AR7": (4055,463),
        "SW Prevalia Clearing SE": (1547,1653),
        "SW Prevalia Clearing NE": (1544,1623),
        "SW Prevalia Clearing SW": (1510,1657),
        "W Andaria Gate": (2315,639),
        "N Andaria Gate": (2334,591),
        "South of Pulma": (1780,1048),
        "Western Camp Island": (3495,1467),
        "TRT":(1756,2341),
        "South of TRT": (1779,2388),
        "South of GH": (3981,854),
        "SOF Island Mall": (3498,3748),
        "NW Outpost Gate": (2940,563),
        "NW Outpost Gate Far": (2982,500),
        "N Outpost Gate": (2980,579),
        "N Outpost Gate 2": (2975,547),
        "N Outpost Gate 3": (3001,496),
        "Cedar Island Mall":(3975,355),
        "Cedar Island Center":(4025,305),
        "Pwnstar":(4218,1090),
        "Frozen Ruins SE":(1612,780),
        "Frozen Ruins SW":(1546,753),
    }
    row_id = tree.identify_row(event.y)
    location_raw = tree.item(row_id, "values")[5]
    location_split = location_raw.split(',')
    x1, y1 = map(int,location_split)
    check_dist = float('inf')
    closest = None
    for location_name, tuple_loc in my_locations.items():
        x2, y2 = map(int,tuple_loc)
        distance = get_distance(x1,y1,x2,y2)
        if distance < check_dist:
            check_dist = distance
            closest = location_name
    location_name = closest if closest else 'Not found'
    value_to_copy_raw = tree.item(row_id, "values")[7]
    serial_match = re.search(r'\?(\d+)(?:\?(\d+))?#', value_to_copy_raw)
    #item_id = number_match.group(1) if number_match else 0
    vendor_serial = serial_match.group(1) if serial_match else 0
    root.clipboard_clear()
    root.clipboard_append(vendor_serial)
    root.update()
    tree.selection_set(row_id)
    #context_menu.post(event.x_root, event.y_root)
    status_var.set(location_name)

def sort_floats_key(item):
    #print('sort_floats_key')
    val = item[0]  # The value from the tuple
    if val == '':
        return 1000.0
    try:
        return float(val)
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1000.0  # Default to 1000 if conversion fails

def sort_timestring_key(item):
    val = item[0]  # The value from the tuple
    # Match the number in the string (if it exists)
    number_match = re.search(r'\d+', val)
    number = int(number_match.group()) if number_match else 1
    if 'second' in val:
        return number
    elif 'minute' in val:
        return number * 60
    elif 'hour' in val:
        return number * 3600
    elif 'day' in val:
        return number * 86400
    else:
        raise ValueError(f"Unknown time format: {val}")

def sort_column(col, reverse, key=None):
    l = [(tree.set(k, col), k) for k in tree.get_children("")]
    l.sort(key=key,reverse=reverse)
    for index, (val, k) in enumerate(l):
        tree.move(k, '', index)
    tree.heading(col, command=lambda _col=col: sort_column(_col, not reverse, key))

def sort_column_tuple(col,secondary_col,reverse, key=None):
    tree_children = tree.get_children("")
    if(len(tree_children) == 0):
        return
    l = [(tree.set(k, col), tree.set(k, secondary_col), k) for k in tree_children]
    l.sort(key=lambda x: (key(x)[0] if key else x[0], key(x)[1] if key else x[1]), reverse=reverse)
    for index, (_, _, k) in enumerate(l):
        tree.move(k, '', index)
    tree.heading(col, command=lambda _col=col,_secondary_col = secondary_col: sort_column_tuple(_col, _secondary_col, not reverse, key))

def sort_key_tuple(item):
    primary_val, secondary_val = item[0], item[1]  # Extract the values from the tuple
    #print(f"primary_val:{primary_val}, secondary_val:{secondary_val}")
    primary_key = 1000.0
    secondary_key = 1000.0
    # Handling the primary value 
    try:
        if len(primary_val) == 0:
            print('primary: no length')
            pass
        else:
            try:
                result = get_seconds_from_string(primary_val)
                if result:
                    primary_key = float(result)
                else:
                    primary_key = float(primary_val)
                    if primary_key > 10000.0:
                        print(f'Vendor name convertable to float {primary_val}:{primary_key}')
                        raise Exception('Vendor name convertable to float')
                    #print(primary_key)
            except Exception as e:
                #print(f"Couldn't parse seconds from string: {e}")
                primary_key = primary_val.lower()
    except Exception as e:
        print(f"Unexpected error for primary column: {e}")
    # Handling the secondary value
    try:
        if len(secondary_val) == 0:
            print('secondary: no length')
            pass
        else:
            try:
                result = get_seconds_from_string(secondary_val)
                if result:
                    primary_key = float(result)
                else:
                    secondary_key = float(secondary_val)
                    if secondary_key > 1000.0:
                        print(f'Vendor name convertable to float {secondary_val}:{secondary_key}')
                        raise Exception('Vendor name convertable to float')
                    #print(primary_key)
            except Exception as e:
                #print(f"Couldn't parse seconds from string: {e}")
                secondary_key = secondary_val.lower()
    except Exception as e:
        print(f"Unexpected error for secondary column: {e}")
    #print(f"primary_key:{primary_key}, secondary_key:{secondary_key}")
    return (primary_key, secondary_key)  # Return a tuple for multi-level sorting

def async_scraping():
    start_time = time.time()
    clear_tree()
    if check_misc_var.get():
        for searchString, searchPrice in misc_prices.items():
            status_var.set(f"{searchString}")
            #yield
            misc_start_time = time.time()  # Record the current time
            page_url = "https://outlandmalls.com/?item=" + quote_plus(searchString) + "&search_category_id=0"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(page_url, headers=headers)
            #print(f"get: {time.time() - misc_start_time}")
            if response.status_code != 200:
                print(f"Failed to retrieve the webpage: {searchString}. Status code: {response.status_code}")
                continue
            soup = BeautifulSoup(response.content, 'lxml')
            #print(f"soup: {time.time() - misc_start_time}")
            if soup:
                # Find the table with the specific id
                table = soup.find('table', id="item-search-results")
                if not table:
                    continue
                # Extract all rows from the table body
                rows = table.tbody.find_all('tr')
                out_data = []
                for row in rows[:7]:
                    cells = row.find_all('td')
                    time_cell = cells[7]
                    time_string = time_cell.text.strip().lower()  # Convert to lowercase for consistent comparison
                    if is_time_recent(time_string):
                        price_cell = cells[6]
                        price = float(price_cell.text.strip().replace(',', ''))  # Convert price to float
                        ratio = round(price / searchPrice,2)
                        if price <= searchPrice or search_pricedepth.get() == 2:
                            vendor_cell = cells[1]
                            location_cell = cells[2]
                            name_cell = cells[3]
                            quantity_cell = cells[4]
                            vendor_string = vendor_cell.text.strip()
                            vendor_serial = vendor_cell.find('a')['href'].split('/')[-1]
                            location_string = location_cell.text.strip()
                            location_link = location_cell.find('a')['href']
                            location_split = location_link.split('#')
                            formatted_location_link = f"{location_split[0]}?{vendor_serial}#{location_split[1]}"
                            quantity_string = quantity_cell.text.strip()
                            name_string = name_cell.text.strip()
                            out_data.append((f"{name_string}",f"{price}/{searchPrice}",f"{ratio}",f"{quantity_string}",f"{vendor_string}",f"{location_string}",f"{time_string}",f"{formatted_location_link}",f"{page_url}"))
                #for tuple in out_data:
                data_queue_appendcommand.put(out_data)
                #collected_data.append(out_data)
            misc_elapsed_time = time.time() - misc_start_time
            sleep_time = 0.5 - misc_elapsed_time
            if sleep_time > 0:
                time.sleep(sleep_time)
    #for data in collected_data:
    #    data_queue_appendcommand.put(data)

    steps = [
        ["Aspect Core", core_prices, check_core_var.get()],
        ["Aspect Extract", extract_prices, check_extract_var.get()],
        ["Aspect Distillation", distil_prices, check_distil_var.get()],
        ["Treasure Map", map_prices, check_tmaps_var.get()],
        ["Skill Mastery Scroll", scroll_prices, check_skillscrolls_var.get()],
        ["Mastery Chain Link", link_prices, check_chainlinks_var.get()],
    ]
    for step in steps:
        bool = step[2]
        if not bool:
            continue
        name = step[0]
        prices = step[1]
        status_var.set(name)
        scrape_wide_page(name,prices)
        
    elapsed_time = round(time.time() - start_time,2)
    status_var.set(f"Complete: {elapsed_time}s")

def ScrapeOutlandMall(event=''):
    async_bot = threading.Thread(target=async_scraping)
    async_bot.start()
    return
    try:
        next(scraping_generator)
        root.after(25, ScrapeOutlandMall)  # Schedule the next iteration
    except StopIteration:
        reset_generator()

#scraping_generator = step_scraping()
# def reset_generator():
#     global scraping_generator
#     scraping_generator = step_scraping()

def get_most_recent_log():
    folder_path = "C:\\Program Files (x86)\\Ultima Online Outlands\\ClassicUO\Data\Client\\JournalLogs\\"
    files = [f for f in glob.glob(os.path.join(folder_path, '*.txt')) if os.path.isfile(f)]
    sorted_files = sorted(files, key=os.path.getmtime, reverse=True)
    latest_files = sorted_files[:6]
    accessible_files = [f for f in latest_files if not is_inaccessible(f)]
    try:
        latest_file = max(accessible_files, key=os.path.getmtime)
    except Exception as e:
        print(f"1! Unexpected error when accessing {folder_path}: {str(e)}")
        latest_file = False
    #print('latest: ' + latest_file)
    return latest_file

def is_inaccessible(file_path):
    try:
        with open(file_path):  # Using with ensures the file is closed after this block
            pass
        return False
    except Exception as e:
        #print(f"2! Unexpected error when accessing {file_path}: {str(e)}")
        return True

# Initialize an empty dictionary to store the results
def parse_log_to_object():
    my_vendors = [4342004,1888935]
    vendors = {}
    current_vendor = None
    latest_log = get_most_recent_log()
    if not latest_log:
        return False
    pass_flag = False
    my_vendor_objs = []
    with open(latest_log, 'r', encoding='utf-8') as lines:
        # Iterate through each line

        for line in lines:
            if "…item" in line and current_vendor is not None:
                # Extract the item details
                # if "[blessed]" in line:
                #     line = line.replace(" [blessed]","")
                #     print(line)
                item_id = re.search(r'ID:(\d+) (.+?)(?: : (\d+)(.*))?$', line)
                match = re.search(r'ID:(\d+) Price: (\d+) (.+?)(?: : (\d+)(.*))?$', line)
                # If a match is found
                #print(match.group())
                if match:
                    item_id = int(match.group(1))
                    item_price = int(match.group(2))
                    item_description = match.group(3)
                    #print(item_description)
                    item_quantity = int(match.group(4)) if match.group(4) else 1
                    item_suffix = match.group(5) if match.group(5) else ''
                    if(item_suffix):
                        item_description += item_suffix
                    item_unitprice = round(item_price / item_quantity,1)
                    # If a match was found, return the matched number as an integer
                    item = {
                        'id': item_id,
                        "price": item_unitprice,
                        "description": item_description,
                        "quantity": item_quantity,
                        'location': location
                    }
                    pass_flag = True
                    current_vendor["items"].append(item)
                else:
                    print('missing: ' + line)
            elif "…vendorStart" in line:
                # Extract the vendor ID and name
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
                    location = f"{match.group(1)},{match.group(2)},13"
                else:
                    location = "0,0,13"
        if pass_flag:
            if len(my_vendor_objs):
                HandleMyVendors(my_vendor_objs)
            return vendors, latest_log
    return latest_log
    
def HandleMyVendors(vendor_obj_list):
    initialize_db()
    full_items = []
    for vendor_obj in vendor_obj_list:
        items = vendor_obj['items']
        for item in items:
            full_items.append(item)
    update_snapshots(full_items)

def search_self_parse_obj(parse_obj):
    corrupted_link_price_threshold = 200000
    bools = [
        (check_core_var.get(), core_prices),
        (check_extract_var.get(), extract_prices),
        (check_distil_var.get(), distil_prices),
        (check_tmaps_var.get(), map_prices),
        (check_skillscrolls_var.get(), scroll_prices),
        (check_chainlinks_var.get(), link_prices),
        (check_misc_var.get(), misc_prices),
    ]
    self_parse_prices = {}
    for bool, prices in bools:
        if bool:
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
            price = item['price']
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
                    threshold = float(corrupted_link_price_threshold)
                else:
                    threshold = 0
            else:
                threshold = float(self_parse_prices.get(name_string, 0))
            if threshold > 0:
                ratio = round(price / threshold,2)
            else:
                ratio = 1000
            if(price <= threshold or search_pricedepth.get() == 2):
                location_string = item['location']
                quantity_string = item['quantity']
                format_url = "https://outlandmalls.com/?item=" + quote_plus(name_string) + "&search_category_id=0"
                location_link = "https://www.exploreoutlands.com/#pos:" + location_string
                location_split = location_link.split('#')
                formatted_location_link = f"{location_split[0]}?{vendor_id}?{item['id']}#{location_split[1]}"
                out_data.append((f"{name_string}",f"{price}/{threshold}",f"{ratio}",f"{quantity_string}",f"{vendor_string}",f"{location_string[:-3]}",f"{out_string}",f"{formatted_location_link}",f"{format_url}"))
    data_queue_appendcommand.put(out_data)
    #data_queue_sortcommand.put(True)

def ParseMostRecentJournalLog(event=''):
    clear_tree()
    obj = parse_log_to_object()
    if type(obj) is str:
        file_info = obj.split('\\')[-1].split('_') #2023_09_02_17_07_16_journal.txt
        out_string_date = '/'.join(file_info[1:3])
        out_string_time = ':'.join(file_info[3:5])
        out_string = f"{out_string_date} {out_string_time}"
        status_var.set(f"Invalid: {out_string}")
        return
    search_self_parse_obj(obj)
    tree_children = tree.get_children()
    if tree_children:
        tree.see(tree_children[0])
    status_var.set('Recent Journal')
    root.update()

def PostJournalLog(event=''):
    url = 'https://outlandmalls.com/uploads'
    headers = {'Authorization': '9ec321b8-6c45-4869-aa01-c15cfc7d38be'}
    data = {'tz': 'America/New_York'}
    file_path = get_most_recent_log()
    if not file_path:
        status_var.set('POST failed')
        return
    with open(file_path, 'rb') as f:
        files = {'file': (file_path, f)}
        response = requests.post(url, headers=headers, files=files, data=data)
        status_var.set(f"{response}")

def clear_tree():
    # Clear the Treeview
    for row in tree.get_children():
        tree.delete(row)


# def connect_db():
#     return sqlite3.connect('inventory.db')
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

# def fetch_query(query, params=()):
#     conn = connect_db()
#     c = conn.cursor()
#     try:
#         c.execute(query, params)
#         result = c.fetchall()
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         result = []
#     finally:
#         c.close()
#         conn.close()
#     return result
    
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
                print('Previous snapshot is identical')
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
    
# Function to get the sales from the database
def read_db_total_sales():
    try:
        with connect_db() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM sales_history")
            rows = c.fetchall()
            columns = [desc[0] for desc in c.description]
        print('-Sales Report-')
        total_sales_window = tk.Toplevel(root)
        total_sales_window.title("Sales Report")
        scrollbar = tk.Scrollbar(total_sales_window, orient="vertical")
        listbox = tk.Listbox(total_sales_window, yscrollcommand=scrollbar.set, width=60, height=20)
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.pack(side="left", fill="both", expand=True)
        total_revenue = 0
        for row in rows:
            row_dict = dict(zip(columns, row))
            total_price = row_dict['price'] * row_dict['quantity']
            total_revenue += total_price
            result = f"{row_dict['snapshot_time']} ID:{row_dict['id']}, {row_dict['description']}: {row_dict['quantity']}x @ {row_dict['price']} = {total_price}"
            #result = f"{row_dict['description']}: {row_dict['quantity']}x @ {row_dict['price']} = {total_price}"
            
            listbox.insert(tk.END, result)
            print(result)
        rev_string = f"Total Revenue: {total_revenue}"
        listbox.insert(tk.END, rev_string)
        print(f"{rev_string}\n-End Report-")
        return rows
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def read_db_recent_sales():
    try:
        with connect_db() as conn:
            c = conn.cursor()
            c.execute("SELECT MAX(snapshot_time) FROM sales_history")
            entries = c.fetchall()
            if len(entries) == 0:
                print('No recent sales')
            most_recent_time = entries[0][0]
            c.execute("SELECT * FROM sales_history WHERE snapshot_time=?",(most_recent_time,))
            rows = c.fetchall()
            columns = [desc[0] for desc in c.description]
        print('-Sales Report-')
        sales_window = tk.Toplevel(root)
        sales_window.title("Sales Report")
        scrollbar = tk.Scrollbar(sales_window, orient="vertical")
        listbox = tk.Listbox(sales_window, yscrollcommand=scrollbar.set, width=60, height=20)
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.pack(side="left", fill="both", expand=True)
        total_revenue = 0
        for row in rows:
            row_dict = dict(zip(columns, row))
            total_price = row_dict['price'] * row_dict['quantity']
            total_revenue += total_price
            result = f"{row_dict['snapshot_time']} ID:{row_dict['id']}, {row_dict['description']}: {row_dict['quantity']}x @ {row_dict['price']} = {total_price}"
            #result = f"{row_dict['description']}: {row_dict['quantity']}x @ {row_dict['price']} = {total_price}"
            listbox.insert(tk.END, result)
            print(result)
        rev_string = f"Total Revenue: {total_revenue}"
        listbox.insert(tk.END, rev_string)
        print(f"{rev_string}\n-End Report-")
        return rows
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
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

def read_db_current_inventory():
    try:
        rows = get_most_recent_inventory_snapshot()
        if not rows:
            print("No inventory snapshot available.")
            return []
        snapshot_time = rows[0][0]
        print(f'-Inventory Report- {snapshot_time}')
        inventory_window = tk.Toplevel(root)
        inventory_window.title("Inventory")
        scrollbar = tk.Scrollbar(inventory_window, orient="vertical")
        listbox = tk.Listbox(inventory_window, yscrollcommand=scrollbar.set, width=60, height=20)
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.pack(side="left", fill="both", expand=True)
        columns = ['snapshot_time', 'id', 'price', 'description', 'quantity']
        for row in rows:
            row_dict = dict(zip(columns, row))
            total_price = row_dict['price'] * row_dict['quantity']
            result = f"ID:{row_dict['id']}, {row_dict['description']}: {row_dict['quantity']}x @ {row_dict['price']} = {total_price}"
            listbox.insert(tk.END, result)
            print(result)
        print("-End Report-")
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
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
        print('same length')
        return False
    for item1, item2 in zip(sorted_snap1, sorted_snap2):
        # Compare all fields except the timestamp (assuming timestamp is at index 0)
        if item1 != item2:
            print('item1:',item1)
            print('item2:',item2)
            return False
    return True

def update_snapshots(inventory_items):
    snapshot1 = get_most_recent_inventory_snapshot()
    if len(snapshot1) == 0:
        take_snapshot(inventory_items)
        return    
    if snapshots_are_identical(snapshot1, inventory_items):
        print("The snapshots are identical, no changes detected.")
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
            # Handle the case where the item exists in the first snapshot but not the second
            print(f"Item {id} exists in the first snapshot but not in the second. All {quantity1} units may have been sold or removed.")
            sold_items[id] = item_info  # Or some other logic
    for id, item_info in sold_items.items():
        price, description, quantity = item_info
        record_sale(snapshot_time,id,price,description,quantity)
    return sold_items

def record_sale(snapshot_time, id, price, description, quantity):
    try:
        # Check if the item ID already exists in sales_history
        existing_records = fetch_query("SELECT * FROM sales_history WHERE id = ?", (id,))
        # Insert a new sale record
        if len(existing_records) == 0:
            execute_query("INSERT INTO sales_history (snapshot_time, id, price, description, quantity) VALUES (?, ?, ?, ?, ?)",
                    (snapshot_time, id, price, description, quantity))
            total_price = price * quantity
            print(f"Recorded sale: {quantity} of item {description} at {price} each, for a total price of {total_price}.")
        else:
            print(f"Item with ID {id} already exists in sales_history. Skipping insert.")
    except Exception as e:
        print(f"An error occurred: {e}")

root = tk.Tk()
root.title("Ali's Outland Malls Scraper")
root.geometry("1000x700")  # Initial size
root.minsize(920, 450)  # Minimum size
#root.maxsize(900, 700)  # Maximum size
root.bind("<Return>", ParseMostRecentJournalLog)
root.bind("<F1>", PostJournalLog)
root.grid_columnconfigure(0, weight=10)
root.grid_columnconfigure(1, weight=0)
root.grid_columnconfigure(2, weight=0)
root.grid_rowconfigure(0, weight=15)
root.grid_rowconfigure(1, weight=0)

# Create a frame to hold the Tree widget and the Scrollbar
tree_frame = tk.Frame(root)
tree_frame.grid(row=0, column=0, sticky='nsew', padx=(10,0))
tree_frame.grid_columnconfigure(0, weight=10)
tree_frame.grid_columnconfigure(1, weight=0)
tree_frame.grid_rowconfigure(0, weight=1)
tree_frame.grid_rowconfigure(1, weight=0)

# Create the Treeview with several columns
tree = ttk.Treeview(tree_frame, columns=("Item", "Price","Ratio","#","Vendor","Location","Time"),show='headings')
tree.heading("Item", text="Item", command=lambda _col="Item",_col2 ="Ratio": sort_column_tuple(_col, _col2, False, sort_key_tuple))
tree.heading("Price", text="Price")
tree.heading("Ratio", text="%", command=lambda _col="Ratio",_col2 ="Item": sort_column_tuple(_col, _col2, False, sort_key_tuple))
tree.heading("#", text="#")
tree.heading("Vendor", text="Vendor", command=lambda _col="Vendor",_col2 ="Item": sort_column_tuple(_col, _col2, False, sort_key_tuple))
tree.heading("Location", text="Location", command=lambda _col="Location",_col2 ="Vendor": sort_column_tuple(_col, _col2, False, sort_key_tuple))
tree.heading("Time", text="Time", command=lambda _col="Time",_col2 ="Ratio": sort_column_tuple(_col, _col2, False, sort_key_tuple))
tree.column("Item", width=300)
tree.column("Price", width=100)
tree.column("Ratio", width=25)
tree.column("#", width=15)
tree.column("Vendor", width=125)
tree.column("Location", width=60)
tree.column("Time", width=100)
tree.configure(height=20)
tree.grid(row=0, column=0,sticky='nsew')
tree.tag_configure("ultra", background="#FF0000")
tree.tag_configure("high", background="#FFA500")
tree.tag_configure("med", background="#FFD700")
tree.tag_configure("low", background="#00FF00")
tree.tag_configure("verylow", background="#00BFFF")
tree.tag_configure("base", background="#ADD8E6")
tree.bind("<Button-1>", on_treeview_click)

# Create context menu
context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label='Insert To Sales History', command=on_treeview_select)
#context_menu.add_command(label='Option 2', command=lambda: print("Option 2 clicked"))
# Bind right-click event
tree.bind('<Button-3>', show_context_menu)

# Create a Scrollbar and associate it with the Tree widget
scrollbar = tk.Scrollbar(tree_frame,orient='vertical', command=tree.yview)
scrollbar.grid(row=0, column=1, sticky='ns')
tree.config(yscrollcommand=scrollbar.set)

config_frame = tk.Frame(root)#,bg='green')
config_frame.grid(row=0, column=2,pady=10,padx=(0,10),sticky='nesw')
config_frame.grid_rowconfigure(0, weight=1)
config_frame.grid_rowconfigure(1, weight=1)
config_frame.grid_columnconfigure(0, weight=1)

# Checkbox Panel
checkbox_frame = tk.Frame(config_frame)#,bg='blue')
checkbox_frame.grid(row=0, column=0)
#checkbox_frame.grid_rowconfigure(0, weight=1)
#checkbox_frame.grid_rowconfigure(1, weight=1)
check_core_var = tk.BooleanVar()
check_extract_var = tk.BooleanVar()
check_distil_var = tk.BooleanVar()
check_tmaps_var = tk.BooleanVar()
check_skillscrolls_var = tk.BooleanVar()
check_chainlinks_var = tk.BooleanVar()
check_misc_var = tk.BooleanVar()

check_core_var.set(True)
check_extract_var.set(False)
check_distil_var.set(False)
check_tmaps_var.set(True)
check_skillscrolls_var.set(True)
check_chainlinks_var.set(True)
check_misc_var.set(True)

checkbox_core_search = ttk.Checkbutton(checkbox_frame, text="Search Cores", variable=check_core_var)
checkbox_core_search.grid(row=0, column=0,sticky='w')
check_distil_search = ttk.Checkbutton(checkbox_frame, text="Search Extracts", variable=check_extract_var)
check_distil_search.grid(row=1, column=0,sticky='w')
check_extract_search = ttk.Checkbutton(checkbox_frame, text="Search Distils", variable=check_distil_var)
check_extract_search.grid(row=2, column=0,sticky='w')
check_tmaps_search = ttk.Checkbutton(checkbox_frame, text="Search Tmaps", variable=check_tmaps_var)
check_tmaps_search.grid(row=3, column=0,sticky='w')
check_skillscrolls_search = ttk.Checkbutton(checkbox_frame, text="Search Skill Scrolls", variable=check_skillscrolls_var)
check_skillscrolls_search.grid(row=4, column=0,sticky='w')
check_chainlinks_search = ttk.Checkbutton(checkbox_frame, text="Search Chain Links", variable=check_chainlinks_var)
check_chainlinks_search.grid(row=5, column=0,sticky='w')
check_misc_search = ttk.Checkbutton(checkbox_frame, text="Search Misc", variable=check_misc_var)
check_misc_search.grid(row=6, column=0,sticky='w')

# Combobox Panel
combobox_frame = tk.Frame(config_frame)#,bg='yellow')
combobox_frame.grid(row=1,column=0)
combobox_frame.grid_columnconfigure(0, weight=0)
combobox_frame.grid_rowconfigure(0, weight=1)
combobox_frame.grid_rowconfigure(1, weight=1)
options = ["30 Seconds", "1 Minute", "5 Minutes", "30 Minutes", "1 Hour", 
           "All Time"]
search_combobox_timeframe = tk.StringVar()
search_combobox_timeframe.set("30 Seconds")
label_timeframe = ttk.Label(combobox_frame,text='Time Frame:')
label_timeframe.grid(row=0,column=0,pady=(5,0))
combobox = ttk.Combobox(combobox_frame, values=options, textvariable=search_combobox_timeframe, state='readonly')
combobox.grid(row=1, column=0,sticky='nsew')

# Radio Panel
radio_frame = tk.Frame(config_frame)#,bg='yellow')
radio_frame.grid(row=2, column=0)
radio_frame.grid_columnconfigure(0, weight=0)
radio_frame.grid_columnconfigure(1, weight=0)
radio_frame.grid_rowconfigure(0, weight=1)
radio_frame.grid_rowconfigure(1, weight=1)
radio_frame.grid_rowconfigure(2, weight=1)
radio_frame.grid_rowconfigure(3, weight=1)
radio_frame.grid_rowconfigure(4, weight=1)
radio_frame.grid_rowconfigure(5, weight=1)
radio_frame.grid_rowconfigure(6, weight=1)
radio_frame.grid_rowconfigure(7, weight=1)
radio_frame.grid_rowconfigure(8, weight=1)
radio_frame.grid_rowconfigure(9, weight=1)
radio_frame.grid_rowconfigure(10, weight=1)
radio_frame.grid_rowconfigure(11, weight=1)
search_pricedepth = tk.IntVar()
search_pricedepth.set(1)
search_sortmode = tk.IntVar()
search_sortmode.set(2)

label_pricedepth = ttk.Label(radio_frame,text='Price Depth:')
label_pricedepth.grid(row=0,column=0,columnspan=2,pady=(5,0))
radio3 = ttk.Radiobutton(radio_frame, text="Show Deals", variable=search_pricedepth, value=1)
radio3.grid(row=1, column=0,sticky='w')
radio4 = ttk.Radiobutton(radio_frame, text="Show All", variable=search_pricedepth, value=2)
radio4.grid(row=1, column=1,sticky='w')
label_sortmode = ttk.Label(radio_frame,text='Sort Mode:')
label_sortmode.grid(row=2,column=0,columnspan=2,pady=(5,0))
radio5 = ttk.Radiobutton(radio_frame, text="Indexed", variable=search_sortmode, value=1)
radio6 = ttk.Radiobutton(radio_frame, text="Best Ratio", variable=search_sortmode, value=2)
radio5.grid(row=3, column=0,sticky='w')
radio6.grid(row=3, column=1,sticky='w')
btn_locations = ttk.Button(radio_frame, text="Locations", command=scrape_vendor_updates)
btn_locations.grid(row=4, column=0, sticky='ew', padx=10, pady=(15,5), columnspan=2)
btn_visit_web = ttk.Button(radio_frame, text="Open Website", command=lambda: webbrowser.open("https://outlandmalls.com/"))
btn_visit_web.grid(row=5, column=0, sticky='ew', padx=10, pady=5, columnspan=2)
btn_open_folder = ttk.Button(radio_frame, text="Open Folder", command=lambda: os.system('explorer "C:\\Program Files (x86)\\Ultima Online Outlands\\ClassicUO\Data\\Client\\JournalLogs"'))
btn_open_folder.grid(row=6, column=0, sticky='ew', padx=10, pady=5, columnspan=2)
btn_inventory = ttk.Button(radio_frame, text="Inventory", command=read_db_current_inventory)
btn_inventory.grid(row=7, column=0, sticky='ew', padx=10, pady=5, columnspan=2)
btn_recent_sales = ttk.Button(radio_frame, text="Sales", command=read_db_total_sales) # read_db_recent_sales
btn_recent_sales.grid(row=8, column=0, sticky='ew', padx=10, pady=5, columnspan=2)
btn_post_journal = ttk.Button(radio_frame, text="POST", command=PostJournalLog)
btn_post_journal.grid(row=9, column=0, sticky='ew', padx=10, pady=5, columnspan=2)

# Floor Panel
button_frame = tk.Frame(root)
button_frame.grid(row=1, column=0,pady=10)
button_frame.columnconfigure(0,weight=1)
button_frame.columnconfigure(1,weight=1)
btn_start = ttk.Button(button_frame, text="OutlandMalls", command=ScrapeOutlandMall)
btn_start.grid(row=0, column=1, sticky='ew', padx=10)
btn_reset = ttk.Button(button_frame, text="Journal Log", command=ParseMostRecentJournalLog)
btn_reset.grid(row=0, column=0, sticky='ew', padx=10)

# Status Panel
status_frame = tk.Frame(root)
status_frame.grid(row=1, column=2,sticky='nesw')
status_frame.grid_rowconfigure(0, weight=1)
status_frame.grid_rowconfigure(1, weight=1)
status_frame.grid_columnconfigure(0, weight=1)
status_frame.grid_propagate(False)
status_label = tk.Label(status_frame, text='Status:')
status_label.grid(row=0,column=0,pady=(3,0))
status_var = tk.StringVar()
status_var.set("Idle")
update_label = tk.Label(status_frame, textvariable=status_var, font=("Arial", 10))
update_label.grid(row=1,column=0,pady=(0,10))

data_queue_appendcommand = queue.Queue()
#data_queue_sortcommand = queue.Queue()
check_queue_appendcommand()
#check_queue_sortcommand()
root.mainloop()