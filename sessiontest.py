#foci/weapon oil/ammo bundle/chainlinks
import requests
from bs4 import BeautifulSoup, SoupStrainer
import re
from urllib.parse import quote_plus
import time
import tkinter as tk
from tkinter import Button, Toplevel, Text, ttk
import webbrowser

root = tk.Tk()
root.title("Ali's Outland Malls Scraper")
# Create a frame to hold the Text widget and the Scrollbar
frame = tk.Frame(root)
frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Create the Treeview with two columns f"{time_string}",f"{location_string}",f"{location_link}",f"{format_url}",f"{vendor_serial}"))
tree = ttk.Treeview(frame, columns=("Item", "Price","Ratio","#","Vendor","Location","Time"),show='headings')
tree.heading("#1", text="Item")
tree.heading("#2", text="Price")
tree.heading("#3", text="Ratio")
tree.heading("#4", text="#")
tree.heading("#5", text="Vendor")
tree.heading("#6", text="Location")
tree.heading("#7", text="Time")
tree.column("#1", width=250)  # Set the width of the "Item" column
tree.column("#2", width=100)  # Set the width of the "Price" column
tree.column("#3", width=40)  # Set the width of the "Ratio" column
tree.column("#4", width=30)  # Set the width of the "Quantity" column
tree.column("#5", width=150)  # Set the width of the "Vendor" column
tree.column("#6", width=80)  # Set the width of the "Time" column
tree.column("#7", width=100)  # Set the width of the "Location" column
tree.configure(height=20)
# Create a Scrollbar and associate it with the Text widget
scrollbar = tk.Scrollbar(frame,orient='vertical', command=tree.yview)
# Link the Text widget's yscrollcommand to the Scrollbar's set method
tree.config(yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.pack(padx=10, pady=1,fill=tk.BOTH, expand=True)
tree.tag_configure("high", background="#FF0000")
tree.tag_configure("med", background="#FFD700")
tree.tag_configure("low", background="#00BFFF")
only_table = SoupStrainer(id="item-search-results")
def scrape_misc(misc_list):
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    with requests.Session() as session:
        session.headers.update(headers)  # Set headers for the session
        for searchItem in misc_list:
            searchString = searchItem[0]
            searchPrice = searchItem[1]
            start_time = time.time()  # Record the current time
            page_url = "https://outlandmalls.com/?item=" + quote_plus(searchString) + "&search_category_id=0"
            response = session.get(page_url)
            print(f"get: {time.time() - start_time}")
            if response.status_code != 200:
                print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
                return None
            soup = BeautifulSoup(response.content, 'lxml',parse_only=only_table)
            print(f"soup: {time.time() - start_time}")
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
                for tuple in out_data:
                    append_to_widget(*tuple)
            elapsed_time = time.time() - start_time
            print(f"end: {elapsed_time}")
            sleep_time = 0.5 - elapsed_time
            if sleep_time > 0:
                time.sleep(sleep_time)

def scrape_wide_page(item,prices_obj):
    start_time = time.time()  # Record the current time
    page_url = "https://outlandmalls.com/?item=" + quote_plus(item) + "&search_category_id=0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(page_url, headers=headers)
    elapsed_time = time.time() - start_time  # Calculate the elapsed time
    #print(f'get: {elapsed_time}')
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return None
    soup = BeautifulSoup(response.content, 'lxml',parse_only=only_table)
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
                name_string = name_cell.text.strip()
                quantity_string = quantity_cell.text.strip()
                threshold = float(prices_obj.get(name_string, 0))
                price = float(price_cell.text.strip().replace(',', ''))  # Convert price to integer
                if threshold > 0:
                    ratio = round(price / threshold,2)
                else:
                    ratio = ''
                if(price <= threshold):
                    format_url = "https://outlandmalls.com/?item=" + quote_plus(name_string) + "&search_category_id=0"
                    out_data.append((f"{name_string}",f"{price}/{threshold}",f"{ratio}",f"{quantity_string}",f"{vendor_string}",f"{location_string}",f"{time_string}",f"{formatted_location_link}",f"{format_url}"))
        for tuple in out_data:
            append_to_widget(*tuple)
    #print(f'end: {time.time() - start_time}')
    sleep_time = 0.3 - elapsed_time
    if sleep_time > 0:
        time.sleep(sleep_time)

def append_to_widget(text1='',text2='',text3='',text4='',text5='',text6='',text7='',text8='',text9=''):
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
    # Get the row and column clicked
    row_id = tree.identify_row(event.y)
    col_id = tree.identify_column(event.x)
    
    # If the URL column is clicked
    #if col_id == "#6":
    if(len(tree.item(row_id,'values')) > 1 and tree.item(row_id,'values')[1]):
        if col_id == "#1":
            url = tree.item(row_id, "values")[8]
        else:
            url = tree.item(row_id, "values")[7]

        value_to_copy_raw = tree.item(row_id, "values")[5]
        split = value_to_copy_raw.split(', ')
        value_to_copy = ">waypoint " + split[0] + " " + split[1]
        # Copy the value to the clipboard
        root.clipboard_clear()
        root.clipboard_append(value_to_copy)
        root.update()
        webbrowser.open(url)
tree.bind("<Button-1>", on_treeview_click)

def step_scraping():
    #--------------------------------------------------------------------------------------------------------------------------------------------
    start_time = time.time()
    clear_tree()
    append_to_widget("-------Cores:-------")
    core_prices = { #exact string MATTERS
        "Blood Aspect Core": 3000,
        "Holy Aspect Core": 3000,
        "Earth Aspect Core": 2500,
        "War Aspect Core": 3000,
        "Death Aspect Core": 4000,
        "Water Aspect Core": 5000,
        "Gadget Aspect Core": 5000,
        "Shadow Aspect Core": 6000,
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
    yield

    append_to_widget("-------Extracts:-------")
    extract_prices = { #exact string MATTERS
        "Blood Aspect Extract": 3000,
        "Holy Aspect Extract": 3000,
        "Earth Aspect Extract": 3000,
        "Death Aspect Extract": 4000,
        "Water Aspect Extract": 5000,
        "Gadget Aspect Extract": 3000,
        "Shadow Aspect Extract": 5000,
        "Void Aspect Extract": 5000,
        "Fire Aspect Extract": 5000,
        "Discipline Aspect Extract": 5000,
        "Lyric Aspect Extract": 5000,
        "Poison Aspect Extract": 8000,
        "Eldritch Aspect Extract": 8000,
        "Fortune Aspect Extract": 7000,
        "Command Aspect Extract": 8000,
        "Artisan Aspect Extract": 5000,
        "Air Aspect Extract": 7000,
        "Harvest Aspect Extract": 11000,
    }
    scrape_wide_page("Aspect Extract",extract_prices)
    yield

    append_to_widget("-------Distils:-------")
    distil_prices = { #exact string MATTERS
        "Blood Aspect Distillation": 3000,
        "Holy Aspect Distillation": 3000,
        "Earth Aspect Distillation": 3000,
        "Death Aspect Distillation": 4000,
        "Water Aspect Distillation": 5000,
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
    yield

    append_to_widget("-------Tmaps:-------")
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
    yield

    append_to_widget("-------Skill Scrolls:-------")
    scroll_prices = { #exact string MATTERS
        "alchemy skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 25000,
        "animal Lore skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 13000,
        "animal taming skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 13000,
        "arms lore skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 6000,
        "begging skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 6000,
        "blacksmithy skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 6000,
        "camping skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 6000,
        "cartography skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 6000,
        "chivalry skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 22000,
        "cooking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 6000,
        "detect hidden skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 10000,
        "discordance skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 6000,
        "fishing skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 13000,
        "forensic eval skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 6000,
        "herding skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 6000,
        "inscription skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 15000,
        "item id skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 6000,
        "lumberjacking skill mastery scroll skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 6000,
        "mining skill mastery scroll skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 6000,
        "musicianship skill mastery scroll skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 6000,
        "necromancy skill mastery scroll skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 25000,
        "peacemaking skill mastery scroll skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 6000,
        "poisoning skill mastery scroll skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 6000,
        "provocation skill mastery scroll skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 6000,
        "spirit speak skill mastery scroll skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
        "stealth skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 10000,
        "tailoring skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 33000,
        "taste id skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 6000,
        "tinkering skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 6000,
        "tracking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 6000,
        "veterinary skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 13000,

    }
    scrape_wide_page("skill mastery scroll",scroll_prices)
    yield

    append_to_widget("-------Chain Links:-------")
    link_prices = { #exact string MATTERS
        "a bronze mastery chain link reforging tool": 100000,
        "a silver mastery chain link reforging tool": 100000,
        "a gold mastery chain link reforging tool": 100000,

    }
    scrape_wide_page("Mastery Chain Link",link_prices)
    yield

    append_to_widget("-------Misc:-------")
    misc_list = [ #exact string doesnt matter
        ["an ankh token",11000],
        ["prevalia coins [blessed]",17000],
        ["a random spell hue deed", 17000],
        ["research guide (25 uses remaining)",17000],
        ["Research Materials", 26000],
        ["Mastercrafting Diagram", 13000],
        ["Aspect Kit", 19000],
        ["Skill Mastery Orb", 12000],
        ["Arcane Scroll", 700],
        ["Arcane Essence", 20],
        ["Iron Ingot Commodity", 72000],
        ["Board Commodity", 65000],
        ["Leather Commodity", 8500],
        ["Message in a Bottle", 15000],
        ["Pristine Lumber", 35000],
        ["Immaculate Stone", 35000],
    ]
    scrape_misc(misc_list)
    elapsed_time = round(time.time() - start_time,2)
    append_to_widget(f"Finished in {elapsed_time} seconds")

gen = step_scraping()
def execute_next_step(event=''):
    try:
        next(gen)
        root.after(50, execute_next_step)  # Schedule the next iteration
    except StopIteration:
        reset_generator()

root.bind("<Return>", execute_next_step)

def reset_generator():
    global gen
    gen = step_scraping()

def clear_tree():
    # Clear the Treeview
    for row in tree.get_children():
        tree.delete(row)
        

# Create a frame for the buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

btn_start = ttk.Button(button_frame, text="Start", command=execute_next_step)
btn_start.pack(side=tk.LEFT, padx=5)  # Pack to the left side of the button_frame

btn_reset = ttk.Button(button_frame, text="Clear", command=clear_tree)
btn_reset.pack(side=tk.LEFT, padx=5)  # Pack to the left side of the button_frame, right next to btn_start

root.mainloop()