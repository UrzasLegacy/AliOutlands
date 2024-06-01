from collections import defaultdict
import re
import sqlite3
from contextlib import contextmanager
from OutlandsDicts import *
import json

# Custom function to handle the specific indentation
def custom_json_dumps(data, indent=4, depth=0):
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
    
def read_db_current_inventory(switch=None):
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
        restock_dict = {}
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
        # self.root.clipboard_clear()
        # self.root.clipboard_append(out_str)
        #print("-End Report-")
        return sorted_items
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
        
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
    
def fetch_query(query, params=()):
    with connect_db() as conn:
        c = conn.cursor()
        c.execute(query, params)
        return c.fetchall()
    
@contextmanager
def connect_db():
    conn = sqlite3.connect('inventory.db')
    try:
        yield conn
    finally:
        conn.close()

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
    category_name = "Skill Mastery Scrolls"
    price_dict = scroll_prices
    for item,data in price_dict.items():
        if item not in category_dict[category_name]:
            category_dict[category_name][item] = []
            category_dict[category_name][item].append((0, data, 0))
            #print(item)    
    category_name = "Cores"
    price_dict = core_prices
    for item,data in price_dict.items():
        if item not in category_dict[category_name]:
            category_dict[category_name][item] = []
            category_dict[category_name][item].append((0, data, 0))
            #print(item)
    category_name = "Distils"
    price_dict = distil_prices
    for item,data in price_dict.items():
        if item not in category_dict[category_name]:
            category_dict[category_name][item] = []
            category_dict[category_name][item].append((0, data, 0))
            #print(item)
    category_name = "Misc"
    misc_crafting_prices.update(misc_hp_prices)
    price_dict = get_misc_price_list()
    for item,data in price_dict.items():
        if item not in category_dict[category_name]:
            category_dict[category_name][item] = []
            category_dict[category_name][item].append((0, data, 0))
            #print(item)



    sorted_category_dict = defaultdict(dict)
    for category, _v in categories.items(): 
        descriptions = category_dict.get(category, {}) #category_dict[category]
        sorted_descriptions = {k: v for k, v in sorted(descriptions.items(), key=lambda item: item[0])}
        sorted_category_dict[category] = sorted_descriptions
    print(custom_json_dumps(sorted_category_dict,2))

    return sorted_category_dict

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


def full_restocker():
    categories = {
        'Misc': ('research material', 'an arcane scroll','mastercrafting diagram','skill mastery orb','plant chemicals'),
        'Cores': ['aspect core'],
        'Distils': ['aspect distillation'],
        'Skill Mastery Scrolls': ['skill mastery scroll'], 
        }
    out_dict = defaultdict(dict)
    inventory = read_db_current_inventory()
    for category_name, category_items in inventory.items(): 
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