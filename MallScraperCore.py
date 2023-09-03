#foci/weapon oil/ammo bundle/chainlinks
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote_plus
import time
import tkinter as tk
from tkinter import ttk
import webbrowser

def scrape_wide_page(item, prices_obj, chain_link_mode=False):
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
                print(search_pricedepth.get())
                if chain_link_mode:
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
                    ratio = ''
                if(price <= threshold):
                    format_url = "https://outlandmalls.com/?item=" + quote_plus(name_string) + "&search_category_id=0"
                    out_data.append((f"{name_string}",f"{price}/{threshold}",f"{ratio}",f"{quantity_string}",f"{vendor_string}",f"{location_string}",f"{time_string}",f"{formatted_location_link}",f"{format_url}"))
                elif search_pricedepth.get() == 2:
                    format_url = "https://outlandmalls.com/?item=" + quote_plus(name_string) + "&search_category_id=0"
                    out_data.append((f"{name_string}",f"{price}/{threshold}",f"{ratio}",f"{quantity_string}",f"{vendor_string}",f"{location_string}",f"{time_string}",f"{formatted_location_link}",f"{format_url}"))
        for tuple in out_data:
            append_to_tree(*tuple)
    #print(f'end: {time.time() - start_time}')
    sleep_time = 0.3 - elapsed_time
    if sleep_time > 0:
        time.sleep(sleep_time)

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
            item = tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9), tags=("high",))
        elif ratio < 0.75:
            item = tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9), tags=("med",))
        elif ratio < 0.9:
            item = tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9), tags=("low",))
        else:
            item = tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9))
    else:
        item = tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9))
    tree.see(item)

def is_time_recentOLD(time_string):
    patterns = [
        r'\b\d+\ssecond',  # Matches any number of seconds
        r'\babout a minute',
        r'\b[2-5]\sminutes'  # Matches any number from 1 to 4 followed by the word "minutes"
    ]
    #patterns.append(r'\b[1-3]?[1-9]\sminutes')
    return any(re.search(pattern, time_string) for pattern in patterns)

def is_time_recent(time_string):
    if search_timeframe.get() == 2:
        return True
    parse = str(time_string)
    if 'second' in parse:
        return True
    if 'minute' in parse:
        if 'about' in parse:
            return True
        split = parse.split(' minute')
        number = int(split[0])
        if number <= 5:
            return True
    # if 'hour' in parse:
    #     return True
    return False

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
        # The last click was on a header, so don't perform the item click action
        return
    # Get the row and column clicked
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
    try:
        return float(val)
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 0.0  # Default to 0 if conversion fails

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
    start_time = time.time()
    clear_tree()
    if check_core_var.get():
        status_var.set("Cores")
        yield
        core_prices = { #exact string MATTERS
            "Blood Aspect Core": 4000,
            "Holy Aspect Core": 4000,
            "Earth Aspect Core": 4000,
            "War Aspect Core": 3000,
            "Death Aspect Core": 4000,
            "Water Aspect Core": 6000,
            "Gadget Aspect Core": 4000,
            "Shadow Aspect Core": 7000,
            "Void Aspect Core": 8000,
            "Fire Aspect Core": 7000,
            "Discipline Aspect Core": 7000,
            "Lyric Aspect Core": 10000,
            "Poison Aspect Core": 17000,
            "Eldritch Aspect Core": 26000,
            "Fortune Aspect Core": 30000,
            "Command Aspect Core": 38000,
            "Artisan Aspect Core": 38000,
            "Air Aspect Core": 38000,
            "Harvest Aspect Core": 100000,
        }
        scrape_wide_page("Aspect Core",core_prices)

    if check_extract_var.get():
        status_var.set("Extracts")
        yield
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
        scrape_wide_page("Aspect Extract",extract_prices)

    if check_distil_var.get():
        status_var.set("Distils")
        yield
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
        scrape_wide_page("Aspect Distillation",distil_prices)

    if check_tmaps_var.get():
        status_var.set("Tmaps")
        yield
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
        scrape_wide_page("Treasure Map",map_prices)

    if check_skillscrolls_var.get():
        status_var.set("Skill Scrolls")
        yield
        scroll_prices = { #exact string MATTERS
            "alchemy skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 25000,
            "animal lore skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 13000,
            "animal taming skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 13000,
            "carpentry skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 7000,
            "arms lore skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 7000,
            "begging skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 7000,
            "blacksmithy skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 7000,
            "camping skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 7000,
            "cartography skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 7000,
            "chivalry skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 22000,
            "cooking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 7000,
            "detect hidden skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 10000,
            "lockpicking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 10000,
            "discordance skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 7000,
            "fishing skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 13000,
            "forensic eval skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 7000,
            "herding skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 7000,
            "inscription skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 15000,
            "item id skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 7000,
            "lumberjacking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 7000,
            "mining skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 7000,
            "musicianship skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 7000,
            "necromancy skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 25000,
            "peacemaking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 7000,
            "poisoning skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 7000,
            "provocation skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 7000,
            "spirit speak skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
            "stealth skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 10000,
            "tailoring skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 33000,
            "taste id skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 7000,
            "tinkering skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 7000,
            "tracking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 7000,
            "veterinary skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 13000,

        }
        scrape_wide_page("skill mastery scroll",scroll_prices)
 

    #dexxer: Melee Accuracy/Defense>, Melee Special Chance/Special Damage, Melee Swing Speed, Slayers
    #dex tamer: Melee Aspect Chance>, Follower Damage, Follower Attack Speed
    #mage tamer: Follower Damage, Follower Attack Speed
    #necro summoner: Spell Aspect Special Chance
    #dps mage: Spell Aspect Special Chance>, Slayers
    #poison: Damage to Poisoned Creatures>
    #bard: Effective Barding>, Damage to Barded Creatures
    #stealther: Chance on Stealth For 5 Extra Steps>, Backstab Damage
    #boating: Damage on Ships>, Ship Cannon Damage>

    if check_chainlinks_var.get():
        status_var.set("Chain Links")
        yield
        link_prices = { #exact string MATTERS
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
        scrape_wide_page("Mastery Chain Link",link_prices,True)


    if check_misc_var.get():
        misc_list = [ #exact string doesnt matter
            ["an ankh token",10000],
            ["prevalia coins [blessed]",18000],
            ["a random spell hue deed", 17000],
            ["research guide (25 uses remaining)",17000],
            ["Research Materials", 26000],
            ["Mastercrafting Diagram", 13000],
            ["Aspect Kit", 19000],
            ["Skill Mastery Orb", 13000],
            ["Arcane Scroll", 700],
            ["Arcane Essence", 20],
            ["Plant Chemicals", 1000],
            ["Iron Ingot Commodity", 72000],
            ["Board Commodity", 65000],
            ["Leather Commodity", 8500],
            ["Message in a Bottle", 15000],
            ["Pristine Lumber", 34000],
            ["Immaculate Stone", 34000],
        ]

        for searchItem in misc_list:
            searchString = searchItem[0]
            status_var.set(f"{searchString}")
            yield
            searchPrice = searchItem[1]
            misc_start_time = time.time()  # Record the current time
            page_url = "https://outlandmalls.com/?item=" + quote_plus(searchString) + "&search_category_id=0"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(page_url, headers=headers)
            #print(f"get: {time.time() - misc_start_time}")
            if response.status_code != 200:
                append_to_tree(f"Failed to retrieve the webpage: {searchString}. Status code: {response.status_code}")
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
                        if price <= searchPrice:
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
                        elif search_pricedepth.get() == 2:
                            out_data.append((f"{name_string}",f"{price}/{searchPrice}",f"{ratio}",f"{quantity_string}",f"{vendor_string}",f"{location_string}",f"{time_string}",f"{formatted_location_link}",f"{page_url}"))
                for tuple in out_data:
                    append_to_tree(*tuple)
            misc_elapsed_time = time.time() - misc_start_time
            #print(f"end: {misc_elapsed_time}")
            sleep_time = 0.5 - misc_elapsed_time
            if sleep_time > 0:
                time.sleep(sleep_time)
    elapsed_time = round(time.time() - start_time,2)
    status_var.set(f"Complete: {elapsed_time}s")
    #append_to_tree(f"Finished in {elapsed_time} seconds")

gen = step_scraping()
def execute_next_step(event=''):
    try:
        next(gen)
        root.after(25, execute_next_step)  # Schedule the next iteration
    except StopIteration:
        reset_generator()

def reset_generator():
    global gen
    gen = step_scraping()

def clear_tree():
    # Clear the Treeview
    for row in tree.get_children():
        tree.delete(row)

root = tk.Tk()
root.title("Ali's Outland Malls Scraper")
root.geometry("1000x700")  # Initial size
root.minsize(920, 350)  # Minimum size
#root.maxsize(900, 700)  # Maximum size
root.bind("<Return>", execute_next_step)
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
tree.tag_configure("high", background="#FF0000")
tree.tag_configure("med", background="#FFD700")
tree.tag_configure("low", background="#00BFFF")
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
search_timeframe = tk.IntVar()
search_timeframe.set(1)
search_pricedepth = tk.IntVar()
search_pricedepth.set(1)
label_timeframe = ttk.Label(radio_frame,text='Time Frame:')
label_timeframe.grid(row=0,column=0,columnspan=2)
radio1 = ttk.Radiobutton(radio_frame, text="Recent", variable=search_timeframe, value=1)
radio1.grid(row=1, column=0,sticky='w')
radio2 = ttk.Radiobutton(radio_frame, text="All Time", variable=search_timeframe, value=2)
radio2.grid(row=1, column=1,sticky='w')
label_pricedepth = ttk.Label(radio_frame,text='Price Depth:')
label_pricedepth.grid(row=2,column=0,columnspan=2)
radio3 = ttk.Radiobutton(radio_frame, text="Show Deals", variable=search_pricedepth, value=1)
radio3.grid(row=3, column=0,sticky='w')
radio4 = ttk.Radiobutton(radio_frame, text="Show All", variable=search_pricedepth, value=2)
radio4.grid(row=3, column=1,sticky='w')

# Create a frame for the buttons
button_frame = tk.Frame(root)
button_frame.grid(row=1, column=0,pady=10)
button_frame.columnconfigure(0,weight=1)
button_frame.columnconfigure(1,weight=1)
btn_start = ttk.Button(button_frame, text="Start", command=execute_next_step)
btn_start.grid(row=0, column=1, sticky='ew', padx=10)  # Pack to the left side of the button_frame

btn_reset = ttk.Button(button_frame, text="Clear", command=clear_tree)
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
update_label = tk.Label(status_frame, textvariable=status_var)
update_label.grid(row=1,column=0,pady=(0,12))

root.mainloop()