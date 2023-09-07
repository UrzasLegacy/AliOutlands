#foci/weapon oil/ammo bundle/chainlinks
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote_plus
import time
import tkinter as tk
from tkinter import ttk
import webbrowser
import os
import glob
import pyautogui

core_prices = { #exact string MATTERS
    "Blood Aspect Core": 4000,
    "Holy Aspect Core": 4000,
    "Earth Aspect Core": 4000,
    "War Aspect Core": 3000,
    "Death Aspect Core": 4000,
    "Water Aspect Core": 6000,
    "Gadget Aspect Core": 4000,
    "Shadow Aspect Core": 7000,
    "Void Aspect Core": 10000,
    "Fire Aspect Core": 10000,
    "Discipline Aspect Core": 7000,
    "Lyric Aspect Core": 10000,
    "Poison Aspect Core": 25000,
    "Eldritch Aspect Core": 26000,
    "Fortune Aspect Core": 30000,
    "Command Aspect Core": 38000,
    "Artisan Aspect Core": 38000,
    "Air Aspect Core": 38000,
    "Harvest Aspect Core": 130000,
}

extract_prices = { #exact string MATTERS
    "Blood Aspect Extract": 3000,
    "Holy Aspect Extract": 3000,
    "Earth Aspect Extract": 3000,
    "Death Aspect Extract": 3000,
    "Water Aspect Extract": 5000,
    "Gadget Aspect Extract": 3000,
    "Shadow Aspect Extract": 5000,
    "Void Aspect Extract": 5000,
    "Fire Aspect Extract": 5000,
    "Discipline Aspect Extract": 4000,
    "Lyric Aspect Extract": 4000,
    "Poison Aspect Extract": 8000,
    "Eldritch Aspect Extract": 8000,
    "Fortune Aspect Extract": 5000,
    "Command Aspect Extract": 8000,
    "Artisan Aspect Extract": 5000,
    "Air Aspect Extract": 7000,
    "Harvest Aspect Extract": 11000,
}

distil_prices = { #exact string MATTERS
    "Blood Aspect Distillation": 3000,
    "Holy Aspect Distillation": 3000,
    "Earth Aspect Distillation": 3000,
    "Death Aspect Distillation": 4000,
    "Water Aspect Distillation": 6000,
    "Gadget Aspect Distillation": 3000,
    "Shadow Aspect Distillation": 5000,
    "Void Aspect Distillation": 5000,
    "Fire Aspect Distillation": 5000,
    "Discipline Aspect Distillation": 5000,
    "Lyric Aspect Distillation": 5000,
    "War Aspect Distillation": 5000,
    "Poison Aspect Distillation": 8000,
    "Eldritch Aspect Distillation": 8000,
    "Fortune Aspect Distillation": 7000,
    "Command Aspect Distillation": 8000,
    "Artisan Aspect Distillation": 5000,
    "Air Aspect Distillation": 7000,
    "Harvest Aspect Distillation": 11000,
}

map_prices = { #exact string MATTERS
    "plainly drawn treasure map: level 1 (undeciphered)": 3000,
    "plainly drawn treasure map: level 1 [100.0% estimated accuracy]": 3000,
    "expertly drawn treasure map: level 2 (undeciphered)": 5000,
    "expertly drawn treasure map: level 2 [100.0% estimated accuracy]": 5000,
    "adeptly drawn treasure map: level 3 (undeciphered)": 12000,
    "adeptly drawn treasure map: level 3 [100.0% estimated accuracy]": 12000,
    "cleverly drawn treasure map: level 4 (undeciphered)": 23000,
    "cleverly drawn treasure map: level 4 [100.0% estimated accuracy]": 23000,
    "deviously drawn treasure map: level 5 (undeciphered)": 35000,
    "deviously drawn treasure map: level 5 [100.0% estimated accuracy]": 35000,
    "ingeniously drawn treasure map: level 6 (undeciphered)": 60000,
    "ingeniously drawn treasure map: level 6 [100.0% estimated accuracy]": 60000,
    "diabolically drawn treasure map: level 7 (undeciphered)": 100000,
    "diabolically drawn treasure map: level 7 [100.0% estimated accuracy]": 100000,
    "legendarily drawn treasure map: level 8 (undeciphered)": 275000,
    "legendarily drawn treasure map: level 8 [100.0% estimated accuracy]": 275000,
}
scroll_prices = { #exact string MATTERS
    "alchemy skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 25000, #alchemy skill mastery scroll : 3 (used to increase a player's skill cap for a skill by 1)
    "animal lore skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 13000,
    "animal taming skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 13000,
    "carpentry skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "arms lore skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "begging skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "blacksmithy skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "camping skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "cartography skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "chivalry skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 23000,
    "cooking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "detect hidden skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 10000,
    "lockpicking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 10000,
    "discordance skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "fishing skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 13000,
    "forensic eval skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "herding skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "inscription skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 15000,
    "item id skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "lumberjacking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "mining skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "musicianship skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "necromancy skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 25000,
    "peacemaking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "poisoning skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "provocation skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "spirit speak skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "stealth skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 10000,
    "tailoring skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 33000,
    "taste id skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "tinkering skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "tracking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "veterinary skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 13000,
}

link_prices = { #exact chain type string MATTERS
    "Melee Accuracy": [110000,650000,2800000], #Melee Accuracy/Defense
    "Melee Defense": [110000,650000,2800000], #Melee Accuracy/Defense
    "Melee Accuracy/Defense": [110000,650000,2800000],
    "Melee Special Chance/Special Damage": [90000,710000,2800000],
    "Melee Special Chance": [90000,710000,2800000], #Melee Special Chance/Special Damage
    "Melee Swing Speed": [140000,700000,2800000],
    "Melee Damage": [70000,500000,2300000], #Melee Damage/Ignore Armor Chance
    "Melee Ignore Armor Chance": [70000,500000,2300000], #Melee Damage/Ignore Armor Chance
    "Melee Damage/Ignore Armor Chance": [70000,500000,2300000],
    "Melee Aspect Effect Modifier": [100000,725000,2700000],
    "Melee Aspect Effect Chance": [130000,700000,2800000],
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
    "Spell Aspect Effect Modifier": [90000,600000,2500000],
    "Spell Aspect Special Chance": [125000,750000,2500000],
    "Damage to Beastial Creatures": [90000,625000,2500000], #Nusero Damage
    "Damage to Construct Creatures": [90000,625000,2500000], #Mausoleum Damage
    "Damage to Daemonic Creatures": [90000,625000,2500000], #Inferno Damage
    "Damage to Elemental Creatures": [90000,625000,2500000], #Mount Petram Damage
    "Damage to Humanoid Creatures": [90000,625000,2500000], #Aegis Keep Damage
    "Damage to Monstrous Creatures": [90000,625000,2500000], #Cavernam Damage
    "Damage to Nature Creatures": [90000,625000,2500000], #Darkmire Temple Damage
    "Damage to Undead Creatures": [90000,625000,2500000], #Ossuary Damage
    "Nusero Damage": [90000,625000,2500000],
    "Mausoleum Damage": [90000,625000,2500000],
    "Inferno Damage": [90000,625000,2500000],
    "Mount Petram Damage": [90000,625000,2500000],
    "Aegis Keep Damage": [90000,625000,2500000],
    "Cavernam Damage": [90000,625000,2500000],
    "Darkmire Temple Damage": [90000,625000,2500000],
    "Ossuary Damage": [90000,625000,2500000,1111111111],
    "Pulma Damage": [90000,625000,2500000],
    "Shadowspire Cathedral Damage": [90000,625000,2500000],
    "Wilderness Damage": [90000,625000,2500000],
    "Follower Damage": [150000,750000,2800000],
    "Damage to Barded Creatures": [130000,650000,2800000],
    "Damage to Poisoned Creatures": [130000,650000,2800000],
    "Poison Damage/Resist Ignore": [70000,500000,2300000],
    "Backstab Damage": [120000,600000,2500000],
    "Trap Damage": [130000,700000,2800000],
    "Damage to Bosses": [90000,600000,2600000],
    "Damage on Ships": [135000,650000,2600000],
    "Ship Cannon Damage": [135000,650000,2600000],
    "Damage to Creatures Above 66% HP": [70000,500000,2300000], #Damage Dealt By Player
    "Damage to Creatures Below 33% HP": [70000,500000,2300000], #Damage Dealt By Player
    "Damage Dealt By Player": [70000,500000,2300000],
    "Physical Damage Resistance": [70000,500000,2300000], #Damage Resistance
    "Spell Damage Resistance": [70000,500000,2300000], #Damage Resistance
    "Follower Damage Resistance": [150000,700000,2800000], #Alchemy/Healing/Veterinary Skill, Follower Attack Speed
    "Effective Parrying Skill": [70000,500000,2300000], #Damage Resistance
    "Effective Magic Resist Skill": [70000,500000,2300000], #Damage Resistance
    "Healing Received": [70000,500000,2300000], #Effective Alchemy/Healing/Veterinary Skill
    "Follower Attack Speed": [150000,700000,2800000],
    "Follower Healing Received": [150000,700000,2800000], #Effective Alchemy/Healing/Veterinary Skill, Follower Attack Speed
    "Boss Damage Resistance": [70000,500000,2300000], #Damage Resistance
    "Damage Resistance on Ships": [70000,500000,2300000], #Damage Resistance
    "Damage Resistance": [70000,500000,2300000],
    "Chest Success Chances/Progress": [100000,650000,2700000],
    "Effective Skill on Chests": [100000,650000,2700000],
    "Alchemy/Healing/Veterinary": [70000,500000,2300000],
    "Effective Lockpicking Skill": [100000,650000,2700000], #Chest Success Chances/Progress
    "Effective Poisoning Skill": [70000,500000,2300000], #Poison Damage/Resist Ignore
    "Effective Barding Skill": [120000,650000,2800000], #Bard Reset/Break Ignore Chance
    "Chivalry Skill": [70000,500000,2300000], 
    "Necromancy Skill": [140000,750000,2800000], #Follower Damage, Follower Damage Resistance
    "Barding Effect Durations": [90000,650000,2600000], #Bard Reset/Break Ignore Chance
    "Bard Reset/Break Ignore Chance": [90000,650000,2600000],
    "Spirit Speak/Inscription": [140000,750000,2800000], #Follower Damage, Follower Damage Resistance
    "Chance on Stealth For 5 Extra Steps": [150000,750000,2800000],
    "Gold/Doubloon Drop Increase": [70000,500000,2300000],
    "Special/Rare Loot Chance": [70000,500000,2300000],
    "reforging tool": [85000,190000,350000],
}

misc_prices = { #exact string matters
    "exceedingly potent magic spellbook": 3500,
    "supremely potent magic spellbook": 15000,
    "an ankh token":10000,
    "prevalia coins [blessed]":18000, #prevalia coins : 5 [blessed]
    "a random spell hue deed": 17000,
    "research guide (25 uses remaining)":17000,
    "research materials (double-click to research)": 31000,
    "mastercrafting diagram": 15000,
    "aspect kit": 22000,
    "a skill mastery orb (used to increase a player's total skill cap by 1)": 15000, #a skill mastery orb : 3 (used to increase a player's total skill cap by 1)
    "an arcane scroll": 900,
    "arcane essence": 30,
    "plant chemicals": 2000,
    "iron ingot commodity (5,000 total)": 80000,
    "board commodity (5,000 total)": 65000,
    "leather commodity (5,000 total)": 9000,
    "a message in a bottle": 17000, 
    "pristine lumber": 33000, 
    "immaculate stone": 33000, 
    "an emote deed": 250000,
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
        for tuple in out_data:
            append_to_tree(*tuple)
        if search_sortmode.get() == 2 and len(out_data):
            sort_column("Ratio", False, sort_floats_key)
    #print(f'end: {time.time() - start_time}')
    sleep_time = 0.3 - elapsed_time
    if sleep_time > 0:
        time.sleep(sleep_time)

def scrape_vendor_updates():
    urls = {
        "https://outlandmalls.com/vendors/1793084": ("S Terran Clearing"),
        "https://outlandmalls.com/vendors/89435": "N Prev Clearing SW",
        "https://outlandmalls.com/vendors/3878051": "N Prev Clearing W",
        "https://outlandmalls.com/vendors/4056785": "N Prev Clearing N",
        "https://outlandmalls.com/vendors/348328": "N Prev Clearing E",
        "https://outlandmalls.com/vendors/1548555": "S Cambria Gate",
        "https://outlandmalls.com/vendors/2038646": "SS & CORES ALL GOODS Outland Malls",
        "https://outlandmalls.com/vendors/40369": "West of SSC w190",
        "https://outlandmalls.com/vendors/1548555": "S Cambria Gate",
        "aaaaa": "aaaaa",
        "aaaaa": "aaaaa",
        "aaaaa": "aaaaa",
        "aaaaa": "aaaaa",
        "aaaaa": "aaaaa",
        "aaaaa": "aaaaa",
        "aaaaa": "aaaaa",
        "aaaaa": "aaaaa",
        "aaaaa": "aaaaa",
        "aaaaa": "aaaaa",
        "aaaaa": "aaaaa",
        "aaaaa": "aaaaa",
        "aaaaa": "aaaaa",
        "aaaaa": "aaaaa",
        "aaaaa": "aaaaa",
        "aaaaa": "aaaaa",
        "aaaaa": "aaaaa",
    }
    start_time = time.time()  # Record the current time
    status_var.set(f"Scanning Locations")
    for url, location in urls.items():
        misc_start_time = time.time()  # Record the current time
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve the webpage: {url}. Status code: {response.status_code}")
            continue
        soup = BeautifulSoup(response.content, 'lxml')
        if soup:
            table = soup.find('table', style="display: block; border: none;")
            # Extract all rows from the table body
            theaders = table.thead.find_all('th')
            scan_time = ' '.join(theaders[0].text.split()[2:])
            if not is_time_recent(scan_time,7200):
                print(f"{location}: {scan_time}") 
        misc_elapsed_time = time.time() - misc_start_time
        sleep_time = 0.5 - misc_elapsed_time
        if sleep_time > 0:
            time.sleep(sleep_time)
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
        elif ratio <= 1.0:
            item = tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9), tags=("base",))
        else:
            item = tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9))
    else:
        item = tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9))
    #tree.see(item)

def is_time_recent(time_string,seconds_threshold=300):
    if search_timeframe.get() == 2:
        return True
    parse = str(time_string)
    threshold_parse = int(seconds_threshold)
    time_seconds = 0
    if 'second' in parse:
        if 'about' in parse:
            time_seconds += 1
        else:
            split = parse.split(' second')
            seconds = int(split[0])
            if seconds:
                time_seconds += seconds
    elif 'minute' in parse:
        if 'about' in parse:
            time_seconds += 59 #about a minute
        else:
            split = parse.split(' minute')
            minutes = int(split[0])
            if minutes:
                time_seconds += minutes * 60
    elif 'hour' in parse:
        if 'about' in parse:
            time_seconds += 3540 #about an hour
        else:
            split = parse.split(' hour')
            hours = int(split[0])
            if hours:
                time_seconds += hours * 3600
    else:
        return False
    return time_seconds <= threshold_parse

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
        number_match = re.search(r'\?(\d+)#', value_to_copy_raw)
        number = number_match.group(1) if number_match else 0
        # split = value_to_copy_raw.(', ')
        # value_to_copy = ">waypoint " + split[0] + " " + split[1]
        # Copy the value to the clipboard
        root.clipboard_clear()
        root.clipboard_append(number)
        root.update()
        webbrowser.open(url)

def sort_floats_key(item):
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

def step_scraping():
    steps = [
        ["Aspect Core", core_prices, check_core_var.get()],
        ["Aspect Extract", extract_prices, check_extract_var.get()],
        ["Aspect Distillation", distil_prices, check_distil_var.get()],
        ["Treasure Map", map_prices, check_tmaps_var.get()],
        ["Skill Mastery Scroll", scroll_prices, check_skillscrolls_var.get()],
        ["Mastery Chain Link", link_prices, check_chainlinks_var.get()],
    ]
    start_time = time.time()
    clear_tree()
    for step in steps:
        bool = step[2]
        if not bool:
            continue
        name = step[0]
        prices = step[1]
        status_var.set(name)
        yield
        scrape_wide_page(name,prices)

    if check_misc_var.get():
        for searchString, searchPrice in misc_prices.items():
            status_var.set(f"{searchString}")
            yield
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
                for tuple in out_data:
                    append_to_tree(*tuple)
                if search_sortmode.get() == 2 and len(out_data):
                    sort_column("Ratio", False, sort_floats_key)
            misc_elapsed_time = time.time() - misc_start_time
            #print(f"end: {misc_elapsed_time}")
            sleep_time = 0.5 - misc_elapsed_time
            if sleep_time > 0:
                time.sleep(sleep_time)
    elapsed_time = round(time.time() - start_time,2)
    status_var.set(f"Complete: {elapsed_time}s")

def ScrapeOutlandMall(event=''):
    try:
        next(scraping_generator)
        root.after(25, ScrapeOutlandMall)  # Schedule the next iteration
    except StopIteration:
        reset_generator()

scraping_generator = step_scraping()

def reset_generator():
    global scraping_generator
    scraping_generator = step_scraping()

def get_most_recent_log():
    print('get_most_recent_log')
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
    print('latest: ' + latest_file)
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
    print('parse_log_to_object')
    vendors = {}
    current_vendor = None
    latest_log = get_most_recent_log()
    if not latest_log:
        return False
    pass_flag = False
    with open(latest_log, 'r', encoding='utf-8') as lines:
        # Iterate through each line

        for line in lines:
            if "…item" in line and current_vendor is not None:
                # Extract the item details
                # if "[blessed]" in line:
                #     line = line.replace(" [blessed]","")
                #     print(line)
                match = re.search(r'Price: (\d+) (.+?)(?: : (\d+)(.*))?$', line)
                # If a match is found
                #print(match.group())
                if match:
                    item_price = int(match.group(1))
                    item_description = match.group(2)
                    #print(item_description)
                    item_quantity = int(match.group(3)) if match.group(3) else 1
                    item_suffix = match.group(4) if match.group(4) else ''
                    if(item_suffix):
                        item_description += item_suffix
                    item_unitprice = round(item_price / item_quantity,1)
                    # If a match was found, return the matched number as an integer
                    item = {
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
                vendor_id = parts[4]
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
                current_vendor = None
            elif "System: Current location is" in line:
                match = re.search(r'Current location is \((\d+), (\d+)', line)
                if match:
                    location = f"{match.group(1)},{match.group(2)},13"
                else:
                    location = "0,0,13"
        if pass_flag:
            return vendors, latest_log
    return latest_log
    
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
    #start_time = time.time()  # Record the current time
    #elapsed_time = time.time() - start_time  # Calculate the elapsed time
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
                formatted_location_link = f"{location_split[0]}?{vendor_id}#{location_split[1]}"
                out_data.append((f"{name_string}",f"{price}/{threshold}",f"{ratio}",f"{quantity_string}",f"{vendor_string}",f"{location_string[:-3]}",f"{out_string}",f"{formatted_location_link}",f"{format_url}"))
    for tuple in out_data:
        append_to_tree(*tuple)
    if search_sortmode.get() == 2 and len(out_data):
        sort_column("Ratio", False, sort_floats_key)

def ParseMostRecentJournalLog():
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

def clear_tree():
    # Clear the Treeview
    for row in tree.get_children():
        tree.delete(row)

root = tk.Tk()
root.title("Ali's Outland Malls Scraper")
root.geometry("1000x700")  # Initial size
root.minsize(920, 350)  # Minimum size
#root.maxsize(900, 700)  # Maximum size
root.bind("<Return>", ScrapeOutlandMall)
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
# Create the Treeview with two columns f"{time_string}",f"{location_string}",f"{location_link}",f"{format_url}",f"{vendor_serial}"))
tree = ttk.Treeview(tree_frame, columns=("Item", "Price","Ratio","#","Vendor","Location","Time"),show='headings')
tree.heading("Item", text="Item")
tree.heading("Price", text="Price")
tree.heading("Ratio", text="Ratio", command=lambda _col="Ratio": sort_column(_col, False, sort_floats_key))
tree.heading("#", text="#")
tree.heading("Vendor", text="Vendor")
tree.heading("Location", text="Location")
tree.heading("Time", text="Time", command=lambda _col="Time": sort_column(_col, False, sort_timestring_key))
tree.column("Item", width=250)
tree.column("Price", width=100)
tree.column("Ratio", width=40)
tree.column("#", width=30)
tree.column("Vendor", width=150)
tree.column("Location", width=80)
tree.column("Time", width=100)
tree.configure(height=20)
tree.grid(row=0, column=0,sticky='nsew')
tree.tag_configure("ultra", background="#FF0000")
tree.tag_configure("high", background="#FFA500")
tree.tag_configure("med", background="#FFD700")
tree.tag_configure("low", background="#00FF00")
tree.tag_configure("base", background="#00BFFF")
tree.bind("<Button-1>", on_treeview_click)

# Create a Scrollbar and associate it with the Text widget
scrollbar = tk.Scrollbar(tree_frame,orient='vertical', command=tree.yview)
scrollbar.grid(row=0, column=1, sticky='ns')
tree.config(yscrollcommand=scrollbar.set)

config_frame = tk.Frame(root)#,bg='green')
config_frame.grid(row=0, column=2,pady=10,padx=(0,10),sticky='nesw')
config_frame.grid_rowconfigure(0, weight=1)
config_frame.grid_rowconfigure(1, weight=1)
config_frame.grid_columnconfigure(0, weight=1)

# Define the checkboxes
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

# Define the radio buttons
radio_frame = tk.Frame(config_frame)#,bg='yellow')
radio_frame.grid(row=1, column=0)
radio_frame.grid_columnconfigure(0, weight=0)
radio_frame.grid_columnconfigure(1, weight=0)
radio_frame.grid_rowconfigure(0, weight=1)
radio_frame.grid_rowconfigure(1, weight=1)
radio_frame.grid_rowconfigure(2, weight=1)
radio_frame.grid_rowconfigure(3, weight=1)
radio_frame.grid_rowconfigure(4, weight=1)
radio_frame.grid_rowconfigure(5, weight=1)
radio_frame.grid_rowconfigure(6, weight=1)
search_timeframe = tk.IntVar()
search_timeframe.set(1)
search_pricedepth = tk.IntVar()
search_pricedepth.set(1)
search_sortmode = tk.IntVar()
search_sortmode.set(2)
label_timeframe = ttk.Label(radio_frame,text='Time Frame:')
label_timeframe.grid(row=0,column=0,columnspan=2,pady=5)
radio1 = ttk.Radiobutton(radio_frame, text="Recent", variable=search_timeframe, value=1)
radio1.grid(row=1, column=0,sticky='w')
radio2 = ttk.Radiobutton(radio_frame, text="All Time", variable=search_timeframe, value=2)
radio2.grid(row=1, column=1,sticky='w')
label_pricedepth = ttk.Label(radio_frame,text='Price Depth:')
label_pricedepth.grid(row=2,column=0,columnspan=2,pady=5)
radio3 = ttk.Radiobutton(radio_frame, text="Show Deals", variable=search_pricedepth, value=1)
radio3.grid(row=3, column=0,sticky='w')
radio4 = ttk.Radiobutton(radio_frame, text="Show All", variable=search_pricedepth, value=2)
radio4.grid(row=3, column=1,sticky='w')
label_sortmode = ttk.Label(radio_frame,text='Sort Mode:')
label_sortmode.grid(row=4,column=0,columnspan=2,pady=5)
radio5 = ttk.Radiobutton(radio_frame, text="Indexed", variable=search_sortmode, value=1)
radio6 = ttk.Radiobutton(radio_frame, text="Best Ratio", variable=search_sortmode, value=2)
radio5.grid(row=5, column=0,sticky='w')
radio6.grid(row=5, column=1,sticky='w')
btn_start = ttk.Button(radio_frame, text="Locations", command=scrape_vendor_updates)
btn_start.grid(row=6, column=0, sticky='ew', padx=10, pady=10, columnspan=2)

def clicker():
    # Move the mouse to a specific location; coordinates x=100, y=100
    pyautogui.moveTo(100, 100)

    # Perform a mouse click
    pyautogui.click()

# Create a frame for the buttons
button_frame = tk.Frame(root,bg='blue')
button_frame.grid(row=1, column=0,pady=10)
button_frame.columnconfigure(0,weight=1)
button_frame.columnconfigure(1,weight=1)
btn_start = ttk.Button(button_frame, text="OutlandMalls", command=ScrapeOutlandMall)
btn_start.grid(row=0, column=1, sticky='ew', padx=10)  # Pack to the left side of the button_frame

btn_reset = ttk.Button(button_frame, text="Journal Log", command=ParseMostRecentJournalLog)
btn_reset.grid(row=0, column=0, sticky='ew', padx=10)  # Pack to the left side of the button_frame, right next to btn_start

status_frame = tk.Frame(root)
status_frame.grid(row=1, column=2,sticky='nesw')
status_frame.grid_rowconfigure(0, weight=1)
status_frame.grid_rowconfigure(1, weight=1)
status_frame.grid_columnconfigure(0, weight=1)
status_frame.grid_propagate(False)
# Step 2: Create a Label widget tied to the StringVar
status_label = tk.Label(status_frame, text='Status:')
status_label.grid(row=0,column=0,pady=(3,0))
status_var = tk.StringVar()
status_var.set("Idle")
update_label = tk.Label(status_frame, textvariable=status_var, font=("Arial", 10))
update_label.grid(row=1,column=0,pady=(0,10))

root.mainloop()