from collections import defaultdict
import time
import requests
import pygetwindow as gw
from pywinauto import Application
import pywinauto
import win32api
import pyperclip
import json
from OutlandsDicts import *

def alter_hue_dict(self_parse=False, item_type="rare cloth"):
    shoe_list = ['cloth shoes', 'shoes', 'cloth boots', 'cloth thigh boots', 'cloth sandals']
    out_dict = defaultdict(int)
    if self_parse:
        for hue_name, hue_data in hue_list.items():
            lower = hue_name.lower()
            if item_type == 'rare cloth':
                new_k = f"{item_type} (hue {hue_data['hue']}: {lower})" #rare cloth (hue 1074: shimmer rime)
                out_dict[new_k] = hue_data[item_type]
                new_k = f"{lower} cloth (hue {hue_data['hue']}: {lower})" #shimmer rime cloth (hue 1074: shimmer rime)
                out_dict[new_k] = hue_data[item_type]
                shoe_price = hue_data['rare cloth'] * 6
                for shoe in shoe_list:
                    new_k = f"{lower} {shoe} (hue {hue_data['hue']})"
                    out_dict[new_k] = shoe_price
            else:
                new_k = f"{item_type} (hue {hue_data['hue']}: {lower})"
                out_dict[new_k] = hue_data[item_type]
                if 'hair dye' in item_type:
                    out_dict[f"rare {new_k}"] = hue_data[item_type]
    else:
        for hue_name, hue_data in hue_list.items():
            lower = hue_name.lower()
            if "metallic lemon-lime" in lower:
                new_k = f"{item_type} (hue {hue_data['hue']}: {lower})"
            else:
                new_k = f"{lower} {item_type}"
            out_dict[new_k] = hue_data[item_type]
            if 'hair dye' in item_type:
                out_dict[f"rare {new_k}"] = hue_data[item_type]
    return out_dict
    #print(json.dumps(out_dict, indent=4))

def is_junk(item_name,item_quantity):
    item_name = item_name.lower()

    #auto include
    if not hasattr(is_junk, "auto_include"):
        is_junk.auto_include = {
        "supremely potent", "invulnerability", "greater daemon slaying"
        }
    if any(word in item_name for word in is_junk.auto_include): #returns false if item name contains any string in auto include list
        return False
    
    if not hasattr(is_junk, "general_forbidden"):
        is_junk.general_forbidden = {
        "potion keg","common plant","common seed","unidentified","durable ","substantial ","massive ","fortified ","exceptional ","accurate ",
        "ruin ","might ","force "," power","slaying ","mastercrafted "," defense ","guarding ","hardening ","fortification ","potent ","melodious ","boarding rope",
        "blank map","large ship bomb","(delectable)","skinning knife","fishing pole","fishing map"," uses remaining)","cannon shot","recall scroll","hops seed","a disguise kit",
        "veterinary supplies","fertility serum","poison charges)","bottle of grog","(700 base doubloon cost)","carpet dye","(double click to place)","common black goods","(meagre)"
        }

    if not hasattr(is_junk, "strict_forbidden"):
        is_junk.strict_forbidden = {
        "bow","buckler","crossbow","kryss","martial manual","platemail chest","quarter staff","shepherd's crook","war mace","longsword","katana","metal kite shield",
        "beverage bottle it's full.","wooden chest","dullhide skinning map (undeciphered)","shadowhide skinning map (undeciphered)","cutlass","raw fish","doubloons",
        "gold coin","magic mushroom","dyes","blank recall rune"
        }
        
    if not hasattr(is_junk, "singleton_general_forbidden"):
        is_junk.singleton_general_forbidden = {
            "potion"
            }
        
    if not hasattr(is_junk, "singleton_strict_forbidden"): #for ignoring stackables of quantity 1
        is_junk.singleton_strict_forbidden = {
            "avarhide","verehide", "valehide", "rosehide", "goldenhide", "bronzehide","copperhide", "shadowhide", "dullhide","leather",
            "avarite ingot","valorite ingot","verite ingot","agapite ingot", "gold ingot", "bronze ingot","copper ingot", "shadow iron ingot", "dull copper ingot","iron ingot",
            "avarwood board","valewood board", "rosewood board", "goldenwood board", "bronzewood board","copperwood board", "shadowwood board", "dullwood board","board",
            "board","amethyst","citrine","diamond","emerald","ruby","sapphire","star sapphire","tourmaline","bottle","blank scroll","black pearl","bloodmoss","garlic","ginseng",
            "mandrake root", "nightshade", "spider's silk", "sulfurous ash", "an arcane scroll"
            }

    if item_quantity == 1: 
        if any(word in item_name for word in is_junk.singleton_general_forbidden):  #returns true if item quantity is 1 and item name contains any string in singleton forbidden list
            return True
        if item_name in is_junk.singleton_strict_forbidden: #returns true if item quantity is 1 and item name is in singleton strict forbidden list
            return True
    if item_name in is_junk.strict_forbidden: #returns true if item name is in strict forbidden list
        return True 
    if any(word in item_name for word in is_junk.general_forbidden): #returns true if item name contains any string in general forbidden list
        return True
    
def format_ingame_name(name_string, quantity_string):
    if quantity_string != '1':
        if "skill mastery scroll" in name_string:
            name_string = name_string.replace("(used to increase a player's skill cap for a skill by 1)",f": {quantity_string}")
        elif "prevalia coins" in name_string:
            name_string = name_string.replace("[blessed]",f": {quantity_string} [blessed]")
        elif "research materials" in name_string:
            name_string = name_string.replace("(double-click to research)",f": {quantity_string} (double-click to research)")
        elif "a skill mastery orb" in name_string:
            name_string = name_string.replace("(used to increase a player's total skill cap by 1)",f": {quantity_string} (used to increase a player's total skill cap by 1)")
        else:
            name_string += f" : {quantity_string}"
    return name_string

def format_with_commas(number_string):
    try:
        number = float(number_string)
        if number.is_integer():
            formatted_number = "{:,.0f}".format(number)
        else:
            formatted_number = "{:,}".format(number)
        return formatted_number
    except ValueError:
        return "Invalid input"

def is_time_recent_multi(time_string,seconds_threshold):
    if seconds_threshold == 'All Time':
        return True
    time_seconds = get_seconds_from_string(time_string)
    if not time_seconds:
        time_seconds = 1000000
    return time_seconds <= seconds_threshold

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

def get_seconds_from_string(time_string):
    parse = str(time_string)
    time_seconds = 0
    try:
        if 's' in parse:
            split = parse.split('s')
            seconds = int(split[0])
            if seconds:
                time_seconds += seconds
        elif 'm' in parse:
            split = parse.split('m')
            minutes = int(split[0])
            if minutes:
                time_seconds += minutes * 60
        elif 'h' in parse:
            split = parse.split('h')
            hours = int(split[0])
            if hours:
                time_seconds += hours * 3600
        elif 'd' in parse:
            time_seconds = 1000000
        else:
            return False
        return time_seconds
    except Exception as e:
        print(f"Error: {e}: {parse}")

def get_vendor_seconds_from_string(time_string):
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
            time_seconds += 59
        else:
            split = parse.split(' minute')
            minutes = int(split[0])
            if minutes:
                time_seconds += minutes * 60
    elif 'hour ago' in parse or 'hours ago' in parse:
        if 'about' in parse:
            time_seconds += 3540
        else:
            split = parse.split(' hour')
            hours = int(split[0])
            if hours:
                time_seconds += hours * 3600
    elif 'day ago' in parse or 'days ago' in parse:
        time_seconds = 1000000
    else:
        return False
    return time_seconds

def get_distance(x1, y1, x2, y2):
    return round(math.sqrt((x2 - x1)**2 + (y2 - y1)**2))

def get_distance_squared(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    return dx * dx + dy * dy

def send_to_discord(content):
    webhook_url = "https://discord.com/api/webhooks/1145494637180633240/AR6iXN2MfdTOsldgTUcCSu_d6sCScan2vdp8zb0LwovDlB4DNq7nLcN-N_AnMHwVlIhp"
    data = {
        "content": content
    }
    response = requests.post(webhook_url, json=data)
    time.sleep(0.2)

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

def sort_key_tuple(item,column1,column2):
    def handle_value(value, column):
        if column == 'Item':
            return value.lower()
        elif column == "Ratio":
            return float(value)
        elif column == "Vendor":
            return value.lower()
        elif column == "Time":
            return get_seconds_from_string(value)
        elif column == "Profit":
            return float(value)
        else:
            print('waduhek')
            return
    primary_val, secondary_val = item[0], item[1]
    primary_key = handle_value(primary_val,column1)
    secondary_key = handle_value(secondary_val,column2)
    #print(f"\nprimary_key:{primary_key}, type: {type(primary_key)}\nsecondary_key:{secondary_key}, type: {type(secondary_key)}\n")
    return (primary_key, secondary_key)  # Return a tuple for multi-level sorting

def shorten_number(num):
    num = round(num,2)
    if num >= 1000000:
        short_num = f"{num / 1000000:.1f}"
    elif num >= 1000:
        short_num = f"{num / 1000:.1f}"
    else:
        return str(num)
    return short_num.rstrip('0').rstrip('.') + ('m' if num >= 1000000 else 'k')

def categorize_and_sort_aggregated_items(aggregated_items):
    categories = {
        'Links': ['chain link'],
        'Misc': ('research material', 'an arcane scroll','mastercrafting diagram','skill mastery orb','plant chemicals'),
        'Boards': ['board'],
        'Ingots': ['ingot'],
        'Leather': ['leather','dullhide', 'shadowhide', 'copperhide', 'bronzehide', 'goldenhide', 'rosehide', 'verehide', 'valehide', 'avarhide'],
        'Cores': ['aspect core'],
        'Extract': ['aspect extract'],
        'Distils': ['aspect distillation'],
        'Skill Mastery Scrolls': ['skill mastery scroll'], 
        'Cloth': ['rare cloth'],
        'Dyes': ['dye'],
        }
    category_dict = defaultdict(dict)
    for (description, stack_size, price), quantity in aggregated_items.items():
        flagged = False
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword.lower() in description.lower():
                    if description not in category_dict[category]:
                        category_dict[category][description] = []
                    category_dict[category][description].append((stack_size, price, quantity))
                    flagged = True
                    break
        if not flagged:
            if description not in category_dict['Misc']:
                category_dict['Misc'][description] = []
            category_dict['Misc'][description].append((stack_size, price, quantity))
    for scroll,data in scroll_prices.items():
        if scroll not in category_dict["Skill Mastery Scrolls"]:
            category_dict["Skill Mastery Scrolls"][scroll] = []
            category_dict["Skill Mastery Scrolls"][scroll].append((0, data, 0))
    for core,data in core_prices.items():
        if core not in category_dict["Cores"]:
            category_dict["Cores"][core] = []
            category_dict["Cores"][core].append((0, data, 0))
    for distil,data in distil_prices.items():
        if distil not in category_dict["Distils"]:
            category_dict["Distils"][distil] = []
            category_dict["Distils"][distil].append((0, data, 0))
    for misc,data in get_misc_price_list().items():
        if misc not in category_dict["Misc"]:
            category_dict["Misc"][misc] = []
            category_dict["Misc"][misc].append((0, data, 0))



    sorted_category_dict = defaultdict(dict)
    for category, _v in categories.items(): 
        descriptions = category_dict.get(category, {}) #category_dict[category]
        sorted_descriptions = {k: v for k, v in sorted(descriptions.items(), key=lambda item: item[0])}
        for item_name,tuples in sorted_descriptions.items():
            tuples.sort(key=lambda x: x[0],reverse=True)
        sorted_category_dict[category] = sorted_descriptions
    #pretty_print(sorted_category_dict)

    return sorted_category_dict
    #sorted_category_dict["Cores"]["Air Aspect Core"] = [(20, 15000, 1), (5, 15000, 2), (1, 15000, 2)]

def pretty_print(data, indent=0):
    if isinstance(data, dict):
        for key, value in data.items():
            print(' ' * indent + str(key) + ':')
            pretty_print(value, indent + 4)
    elif isinstance(data, list) and all(isinstance(i, list) for i in data):
        print(' ' * indent + '[\n' + ',\n'.join(' ' * (indent + 4) + str(sublist) for sublist in data) + '\n' + ' ' * indent + ']')
    else:
        print(' ' * indent + str(data))

def discord_truncate(s):
    transformer = {
        'Aspect Core': (' Aspect Core',''),
        'Aspect Extract': (' Aspect Extract',''),
        'Aspect Distillation': (' Aspect Distillation',''), 
        'skill mastery orb': ("a skill mastery orb \(used to increase a player's total skill cap by 1\)",'skill mastery orb'), #a skill mastery orb (used to increase a player's total skill cap by 1)
        'skill mastery scroll': (" skill mastery scroll \(used to increase a player's skill cap for a skill by 1\)",""), 
        'mastery chain link': (r'(\w)\w+ mastery chain link (.+) \(.+\)',r'\1. \2'),
        'rare cloth': (r'rare cloth \(hue \d+: ([\w\s-]+)\)',r'\1'),
        'an arcane scroll': ('an ', ''),
        ' dye ': (r' dye \(hue \d+: ([\w\s-]+)\)', r': \1'),
        ' board': (' board', ''), 
        ' ingot': (' ingot', ''),
        'research materials': ('double-click to research','RM'), 
        'mastercrafting diagram': ('diagram','diagram (MCD)'), 
        }
    for key_string, re_tuple in transformer.items():
        if key_string in s:
            search_pattern, replace_pattern = re_tuple
            s = re.sub(search_pattern, replace_pattern, s)
    return s

def switch_focus():
    mouse_pos = win32api.GetCursorPos()

    active_window = gw.getActiveWindow()
    active_title = active_window.title
    regex_client = r"UO - ([\w\s]+) - ClassicUO"
    regex_assistant = r"(?:\] - )?([\w\s]+) \(\[None\]\)"
    match_client = re.search(regex_client, active_title)
    match_assistant = re.search(regex_assistant, active_title)
    if match_client: #if focus is on client, switch to assistant
        extracted_name = match_client.group(1)
        target_window = None
        for window in gw.getAllWindows():
            if extracted_name in window.title and window != active_window:
                target_window = window
                break
        if target_window is not None:
            window = connect_to_window(target_window._hWnd)
        else:
            print("No other window found with the extracted string in its title")
    elif match_assistant: #if focus is on assistant, swtich to client
        extracted_name = match_assistant.group(1)
        target_window = None
        for window in gw.getAllWindows():
            if extracted_name in window.title and window != active_window:
                target_window = window
                break
        window = connect_to_window(target_window._hWnd)
    else:
        print("No match found in the active window's title.")
        return
    if not window:
        print("Error connecting to window")
    try:
        window.set_focus()
    except Exception as e:
        print(f"Failed: {e}")
    win32api.SetCursorPos(mouse_pos)

def focus_scraper():
    window_name = rf"Ali's OutlandMalls Scraper"
    scraper_window = None
    for window in gw.getAllWindows():
        if window_name in window.title:
            scraper_window = window
            break
    if not scraper_window:
        print("Couldn't find scraper window!")
        return
    scraper = connect_to_window(scraper_window._hWnd)
    if not scraper:
        print("Couldn't connect to scraper app!")
        return
    scraper.set_focus()

def focus_named_assistant(name):
    # Save the current mouse position
    regex_assistant = rf"(?:\] - )?{name} \(\[None\]\)"
    assistant_window = None
    for window in gw.getAllWindows():
        if re.search(regex_assistant, window.title):
            assistant_window = window
            break
    if not assistant_window:
        print("Couldn't find assistant window!")
        return False
    try:
        assistant = connect_to_window(assistant_window._hWnd)
    except Exception as e:
        print(f'Error connecting to assistant app! {e}')
        return False
    if not assistant:
        print("Couldn't connect to assistant app!")
        return False
    assistant.set_focus()
    return assistant

def focus_named_client(name):
    mouse_pos = win32api.GetCursorPos()
    regex_client = rf"UO - {name} - ClassicUO"
    client_window = None
    for window in gw.getAllWindows():
        if re.search(regex_client, window.title):
            client_window = window
            break
    if not client_window:
        print("Couldn't find client window!")
        return
    try:
        client = connect_to_window(client_window._hWnd)
    except Exception as e:
        print(f'Error connecting to client app! {e}')
        return False
    if not client:
        print("Couldn't connect to client app!")
        return
    client.set_focus()
    win32api.SetCursorPos(mouse_pos)
    return client

def connect_to_window(hWnd):
    try:
        app = Application().connect(handle=hWnd)
        connection = app.window(handle=hWnd)
    except pywinauto.findwindows.ElementNotFoundError as e:
        print(f"Window not found: {e}")
        return False
    except pywinauto.timings.TimeoutError as e:
        print(f"Operation timed out: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    return connection

def custom_json_dumps(data, indent=4, depth=0):
    # Custom function to handle the specific indentation

    if isinstance(data, dict):
        items = []
        for key, value in data.items():
            items.append(f'{" " * (depth * indent)}"{key}": {custom_json_dumps(value, indent, depth + 1)}')
        return "{\n" + ",\n".join(items) + f'\n{" " * ((depth - 1) * indent)}}}'
    elif isinstance(data, list):
        if depth == 2:  # Specific depth where you want to customize the indentation
            items = [json.dumps(item) for item in data]
            return "[\n" + ",\n".join(f'{" " * (depth * indent)}{item}' for item in items) + f'\n{" " * ((depth - 1) * indent)}]'
        else:
            items = [custom_json_dumps(item, indent, depth + 1) for item in data]
            return "[\n" + ",\n".join(f'{" " * (depth * indent)}{item}' for item in items) + f'\n{" " * ((depth - 1) * indent)}]'
    else:
        return json.dumps(data)
    
def PipedListDiffer(before, after):
    before_set = set(before.split("|"))
    after_set = set(after.split("|"))
    dif_set = after_set - before_set

    dif_list = list(dif_set)
    dif_list_sorted = sorted(dif_list, key= int)
    dif_string = f"{'|'.join(dif_list_sorted)}"

    print(f"Difference: {dif_string}\nDif Len: {len(dif_list)}")

    return dif_string

def PipedListSubtract(list1, list2):
    list1_set = set(list1.split("|"))
    list2_set = set(list2.split("|"))
    dif_set = list1_set - list2_set

    sub_list = list(dif_set)
    sub_list_sorted = sorted(sub_list, key= int)
    sub_string = f"{'|'.join(sub_list_sorted)}"

    print(f"Subtracted: {sub_string}\nSub Len: {len(sub_string)}")

    return sub_string

def PipedListConcatenator(before, after):
    before_set = set(before.split("|"))
    after_set = set(after.split("|"))
    concat_set = after_set | before_set

    concat_list = [string for string in concat_set if string] #list(concat_set)
    concat_list_sorted = sorted(concat_list, key= int)
    concat_string = f"{'|'.join(concat_list_sorted)}"

    print(f"Concat Len: {len(concat_list)}")

    return concat_string

def PipedListSplitter(piped_list_string,chunk_size):
    piped_list = piped_list_string.split("|")
    
    chunk_list = []
    for i in range(0, len(piped_list), chunk_size):
        chunk_list.append(piped_list[i:i + chunk_size])

    template_string = """
                    while findtype $%$% "container" as foundItem
                        getlabel foundItem desc
                        sysmsg "…item ID:{{foundItem}} {{desc}}" 1159
                        @ignore foundItem
                    endwhile
"""

    out_string = ""
    for chunk in chunk_list:
        chunk_string = "|".join(chunk)
        out_string += template_string.replace("$%$%",chunk_string)

    print(f"Chunks: {len(chunk_list)}")

    return out_string
