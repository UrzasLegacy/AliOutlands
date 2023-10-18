#resource maps, cloth, boat stuff (crew, upgrades)
import os
import glob
import math
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
import pygetwindow as gw
import keyboard
import win32api
import pywinauto
from pywinauto import Application
import json

core_prices = { #exact string MATTERS
    "Blood Aspect Core": 3000,
    "Holy Aspect Core": 4000,
    "Earth Aspect Core": 3000,
    "War Aspect Core": 3000,
    "Death Aspect Core": 4000,
    "Water Aspect Core": 10000,
    "Gadget Aspect Core": 4000,
    "Shadow Aspect Core": 10000,
    "Void Aspect Core": 20000,
    "Fire Aspect Core": 10000,
    "Discipline Aspect Core": 8000,
    "Lyric Aspect Core": 19000,
    "Poison Aspect Core": 29000,
    "Eldritch Aspect Core": 31000,
    "Fortune Aspect Core": 50000,
    "Command Aspect Core": 130000,
    "Artisan Aspect Core": 60000,
    "Air Aspect Core": 40000,
    "Harvest Aspect Core": 130000,
}

extract_prices = { #exact string MATTERS
    "Blood Aspect Extract": 2000,
    "Holy Aspect Extract": 2000,
    "Earth Aspect Extract": 2000,
    "Death Aspect Extract": 2000,
    "Water Aspect Extract": 4000,
    "Gadget Aspect Extract": 2000,
    "Shadow Aspect Extract": 4000,
    "Void Aspect Extract": 4000,
    "Fire Aspect Extract": 2000,
    "Discipline Aspect Extract": 4000,
    "Lyric Aspect Extract": 5000,
    "Poison Aspect Extract": 6000,
    "Eldritch Aspect Extract": 8000,
    "Fortune Aspect Extract": 7000,
    "Command Aspect Extract": 8000,
    "Artisan Aspect Extract": 4000,
    "Air Aspect Extract": 7000,
    "Harvest Aspect Extract": 10000,
}

distil_prices = { #exact string MATTERS
    "Blood Aspect Distillation": 2000,
    "Holy Aspect Distillation": 2000,
    "Earth Aspect Distillation": 2000,
    "Death Aspect Distillation": 2000,
    "Water Aspect Distillation": 4000,
    "Gadget Aspect Distillation": 2000,
    "Shadow Aspect Distillation": 4000,
    "Void Aspect Distillation": 4000,
    "Fire Aspect Distillation": 2000,
    "Discipline Aspect Distillation": 4000,
    "Lyric Aspect Distillation": 5000,
    "War Aspect Distillation": 2000,
    "Poison Aspect Distillation": 6000,
    "Eldritch Aspect Distillation": 8000,
    "Fortune Aspect Distillation": 7000,
    "Command Aspect Distillation": 8000,
    "Artisan Aspect Distillation": 4000,
    "Air Aspect Distillation": 7000,
    "Harvest Aspect Distillation": 10000,
}

map_prices = { #exact string MATTERS
    "plainly drawn treasure map: level 1 (undeciphered)": 5000,
    "expertly drawn treasure map: level 2 (undeciphered)": 10000,
    "adeptly drawn treasure map: level 3 (undeciphered)": 25000,
    "cleverly drawn treasure map: level 4 (undeciphered)": 32000,
    "deviously drawn treasure map: level 5 (undeciphered)": 45000,
    "ingeniously drawn treasure map: level 6 (undeciphered)": 75000,
    "diabolically drawn treasure map: level 7 (undeciphered)": 100000,
    "legendarily drawn treasure map: level 8 (undeciphered)": 300000,

    "avarscale fishing map (undeciphered)": 13000,

    "verewood lumber map (undeciphered)": 25000,
    "valewood lumber map (undeciphered)": 45000,
    "avarwood lumber map (undeciphered)": 80000,

    "verehide skinning map (undeciphered)": 10000,
    "valehide skinning map (undeciphered)": 15000,
    "avarhide skinning map (undeciphered)": 20000,
    
    "copper ore map (undeciphered)": 3000,
    "bronze ore map (undeciphered)": 6000,
    "gold ore map (undeciphered)": 12000,
    "agapite ore map (undeciphered)": 20000,
    "verite ore map (undeciphered)": 40000,
    "valorite ore map (undeciphered)": 50000,
    "avarite ore map (undeciphered)": 80000,
}

ingot_prices = {
    "iron ingot": 15,
    "dull copper ingot": 17,
    "shadow iron ingot": 23,
    "copper ingot": 31,
    "bronze ingot": 73,
    "gold ingot": 115,
    "agapite ingot": 170,
    "verite ingot": 330,
    "valorite ingot": 400,
    "avarite ingot": 870,
    "iron ingot commodity (5,000 total)": 75000,
    "dull copper ingot commodity (2,500 total)": 42500,
    "shadow iron ingot commodity (2,500 total)": 57500,
    "copper ingot commodity (2,500 total)": 77500,
    "bronze ingot commodity (2,500 total)": 182500,
    "gold ingot commodity (2,500 total)": 287500,
    "agapite ingot commodity (2,500 total)": 425000,
    "verite ingot commodity (2,500 total)": 825000,
    "valorite ingot commodity (2,500 total)": 1000000,
    "avarite ingot commodity (2,500 total)": 2175000,
    "stack of ingots (harvest antiquity)": 150000,
}

board_prices = {
    "board": 14,
    "dullwood board": 30,
    "shadowwood board": 80,
    "copperwood board": 23,
    "bronzewood board": 60,
    "goldenwood board": 70,
    "rosewood board": 75,
    "verewood board": 220,
    "valewood board": 500,
    "avarwood board": 1000,
    "board commodity (5,000 total)": 70000,
    "dullwood commodity (2,500 total)": 75000,
    "shadowwood commodity (2,500 total)": 200000,
    "copperwood commodity (2,500 total)": 57500,
    "bronzewood commodity (2,500 total)": 150000,
    "goldenwood commodity (2,500 total)": 175000,
    "rosewood commodity (2,500 total)": 187500,
    "verewood commodity (2,500 total)": 550000,
    "valewood commodity (2,500 total)": 1250000,
    "avarwood commodity (2,500 total)": 2500000,
}

leather_prices = { #https://outlandmalls.com/?item=&search_category_id=1&search_sub_category_id=28
    "leather": 1,
    "dullhide": 3,
    "shadowhide": 16,
    "copperhide": 20,
    "bronzehide": 38,
    "goldenhide": 60,
    "rosehide": 75,
    "verehide": 100,
    "valehide": 150,
    "avarhide": 340,
    "leather commodity (5,000 total)": 6000,
    "dullhide commodity (2,500 total)": 7500,
    "shadowhide commodity (2,500 total)": 40000,
    "copperhide commodity (2,500 total)": 50000,
    "bronzehide commodity (2,500 total)": 95000,
    "goldenhide commodity (2,500 total)": 150000,
    "rosehide commodity (2,500 total)": 187500,
    "verehide commodity (2,500 total)": 250000,
    "valehide commodity (2,500 total)": 375000, 
    "avarhide commodity (2,500 total)": 850000,
}

scroll_prices = { #exact string MATTERS
    "alchemy skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 25000, #alchemy skill mastery scroll : 3 (used to increase a player's skill cap for a skill by 1)
    "animal lore skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 17500,
    "animal taming skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 17500,
    "carpentry skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "arms lore skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "begging skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "blacksmithy skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "camping skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "cartography skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "chivalry skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 22000,
    "cooking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "detect hidden skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 11000,
    "lockpicking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 16000,
    "discordance skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "fishing skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 11000,
    "forensic eval skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 9000,
    "herding skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 17500,
    "inscription skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 20000,
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
    "tailoring skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 38000,
    "taste id skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "tinkering skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "tracking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 8000,
    "veterinary skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 17500,
}

link_prices = { #exact chain type string MATTERS
    "Melee Accuracy": [100000,600000,2700000], #Melee Accuracy/Defense
    "Melee Defense": [100000,600000,2700000], #Melee Accuracy/Defense
    "Melee Accuracy/Defense": [100000,600000,2700000],
    "Melee Special Chance/Special Damage": [90000,710000,2700000],
    "Melee Special Chance": [90000,710000,2700000], #Melee Special Chance/Special Damage
    "Melee Swing Speed": [100000,600000,2700000],
    "Melee Damage": [60000,500000,2300000], #Melee Damage/Ignore Armor Chance
    "Melee Ignore Armor Chance": [60000,500000,2300000], #Melee Damage/Ignore Armor Chance
    "Melee Damage/Ignore Armor Chance": [60000,500000,2300000],
    "Melee Aspect Effect Modifier": [60000,600000,2600000],
    "Melee Aspect Effect Chance": [100000,600000,2700000],
    "Spell Damage": [60000,500000,2300000], #Spell Damage/Ignore Resist Chance
    "Spell Damage When No Followers":   [60000,500000,2300000],
    "Spell Ignore Resist Chance": [60000,500000,2300000], #Spell Damage/Ignore Resist Chance
    "Spell Damage/Ignore Resist Chance": [60000,500000,2300000],
    "Spell Charged Chance": [60000,500000,2300000], #Spell Charged Chance/Charged Damage
    "Spell Charged Damage": [60000,500000,2300000], #Spell Charged Chance/Charged Damage
    "Spell Charged Chance/Charged Damage": [60000,500000,2300000],
    "Meditation Rate": [60000,500000,2300000], #Meditation Rate/Spell Disrupt Avoid Chance
    "Spell Disrupt Avoid Chance": [60000,500000,2300000], #Meditation Rate/Spell Disrupt Avoid Chance, Spell Damage When No Followers
    "Meditation Rate/Disrupt Avoid Chance": [60000,500000,2300000], #Spell Damage When No Followers
    "Spell Aspect Effect Modifier": [60000,500000,2300000],
    "Spell Aspect Special Chance": [130000,700000,2500000],
    "Damage to Beastial Creatures": [75000,600000,2500000], #Nusero Damage
    "Damage to Construct Creatures": [75000,600000,2500000], #Mausoleum Damage
    "Damage to Daemonic Creatures": [100000,600000,2500000], #Inferno Damage
    "Damage to Elemental Creatures": [75000,600000,2500000], #Mount Petram Damage
    "Damage to Humanoid Creatures": [75000,600000,2500000], #Aegis Keep Damage
    "Damage to Monstrous Creatures": [75000,600000,2500000], #Cavernam Damage
    "Damage to Nature Creatures": [75000,600000,2500000], #Darkmire Temple Damage
    "Damage to Undead Creatures": [75000,600000,2500000], #Ossuary Damage
    "Nusero Damage": [80000,600000,2500000],
    "Mausoleum Damage": [80000,600000,2500000],
    "Inferno Damage": [90000,600000,2500000],
    "Mount Petram Damage": [80000,600000,2500000],
    "Aegis Keep Damage": [80000,600000,2500000],
    "Cavernam Damage": [80000,600000,2500000],
    "Darkmire Temple Damage": [80000,600000,2500000],
    "Ossuary Damage": [80000,600000,2500000],
    "Pulma Damage": [80000,600000,2500000],
    "Shadowspire Cathedral Damage": [90000,600000,2500000],
    "Wilderness Damage": [100000,600000,2500000],
    "Follower Damage": [140000,700000,2700000],
    "Damage to Barded Creatures": [110000,600000,2700000],
    "Damage to Poisoned Creatures": [120000,600000,2700000],
    "Poison Damage/Resist Ignore": [60000,500000,2300000],
    "Backstab Damage": [100000,600000,2500000],
    "Trap Damage": [100000,600000,2700000],
    "Damage to Bosses": [80000,600000,2600000],
    "Damage on Ships": [125000,600000,2600000],
    "Ship Cannon Damage": [120000,600000,2600000],
    "Damage to Creatures Above 66% HP": [60000,500000,2300000], #Damage Dealt By Player
    "Damage to Creatures Below 33% HP": [60000,500000,2300000], #Damage Dealt By Player
    "Damage Dealt By Player": [60000,500000,2300000],
    "Physical Damage Resistance": [60000,500000,2300000], #Damage Resistance
    "Spell Damage Resistance": [60000,500000,2300000], #Damage Resistance
    "Follower Damage Resistance": [150000,600000,2700000], #Alchemy/Healing/Veterinary Skill, Follower Attack Speed
    "Effective Parrying Skill": [60000,500000,2300000], #Damage Resistance
    "Effective Magic Resist Skill": [60000,500000,2300000], #Damage Resistance
    "Healing Received": [60000,500000,2300000], #Effective Alchemy/Healing/Veterinary Skill
    "Follower Attack Speed": [130000,600000,2700000],
    "Follower Healing Received": [130000,600000,2700000], #Effective Alchemy/Healing/Veterinary Skill, Follower Attack Speed
    "Boss Damage Resistance": [60000,500000,2300000], #Damage Resistance
    "Damage Resistance on Ships": [60000,500000,2300000], #Damage Resistance
    "Damage Resistance": [60000,500000,2300000],
    "Chest Success Chances/Progress": [90000,600000,2600000],
    "Effective Skill on Chests": [90000,600000,2600000],
    "Alchemy/Healing/Veterinary": [60000,500000,2300000],
    "Effective Lockpicking Skill": [90000,600000,2600000], #Chest Success Chances/Progress
    "Effective Poisoning Skill": [60000,500000,2300000], #Poison Damage/Resist Ignore
    "Effective Barding Skill": [110000,600000,2700000], #Bard Reset/Break Ignore Chance
    "Chivalry Skill": [60000,500000,2300000], 
    "Necromancy Skill": [140000,750000,2700000], #Follower Damage, Follower Damage Resistance
    "Barding Effect Durations": [60000,600000,2600000], #Bard Reset/Break Ignore Chance
    "Bard Reset/Break Ignore Chance": [60000,600000,2600000],
    "Spirit Speak/Inscription": [140000,750000,2700000], #Follower Damage, Follower Damage Resistance
    "Chance on Stealth For 5 Extra Steps": [100000,675000,2600000],
    "Gold/Doubloon Drop Increase": [60000,500000,2300000],
    "Special/Rare Loot Chance": [60000,500000,2300000],
    "reforging tool": [85000,180000,350000],
}

hue_list = {
    'Shimmer Oxide':         {'rare cloth': 175000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 750000, 'facial hair dye': 750000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1483},
    'Shimmer Cardinal':      {'rare cloth': 125000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 750000, 'facial hair dye': 750000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1476},
    'Shimmer Evergreen':     {'rare cloth': 125000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 750000, 'facial hair dye': 750000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1479},
    'Shimmer Valentine':     {'rare cloth': 150000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 750000, 'facial hair dye': 750000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2916},
    'Shimmer Periwinkle':    {'rare cloth': 175000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 750000, 'facial hair dye': 750000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2251},
    'Shimmer Shamrock':      {'rare cloth': 175000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 750000, 'facial hair dye': 750000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2664},
    'Shimmer Lunar':         {'rare cloth': 150000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 750000, 'facial hair dye': 750000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2342},
    'Shimmer Solstice':      {'rare cloth': 75000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 500000, 'facial hair dye': 500000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1967},
    'Shimmer Dahlia':        {'rare cloth': 125000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1956},
    'Shimmer Paradox':       {'rare cloth': 600000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 1000000, 'facial hair dye': 1000000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2346},
    'Shimmer Redux':         {'rare cloth': 300000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1957},
    'Shimmer Spice':         {'rare cloth': 500000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1557},
    'Shimmer Garnet':        {'rare cloth': 500000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 1000000, 'facial hair dye': 1000000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1571},
    'Shimmer Equinox':       {'rare cloth': 100000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1574},
    'Shimmer Moonlight':     {'rare cloth': 150000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2284},
    'Shimmer Gala':          {'rare cloth': 100000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2074},
    'Shimmer Spirit':        {'rare cloth': 100000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1181},
    'Shimmer Tempest':       {'rare cloth': 125000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1180},
    'Shimmer Borealis':      {'rare cloth': 60000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1179},
    'Shimmer Passion':       {'rare cloth': 60000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1184},
    'Shimmer Celestial':     {'rare cloth': 60000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1186},
    'Shimmer Nightfall':     {'rare cloth': 60000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2260},
    'Shimmer Toil':          {'rare cloth': 40000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1499},
    'Shimmer Crystal':       {'rare cloth': 40000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1059},
    'Shimmer Aurora':        {'rare cloth': 40000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1063},
    'Shimmer Candy':         {'rare cloth': 40000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1188},
    'Shimmer Fen':           {'rare cloth': 40000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1400},
    'Shimmer Blossom':       {'rare cloth': 40000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1070},
    'Shimmer Mirage':        {'rare cloth': 35000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1575},
    'Shimmer Gore':          {'rare cloth': 40000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1069},
    'Shimmer Flora':         {'rare cloth': 30000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1071},
    'Shimmer Rime':          {'rare cloth': 30000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1074},
    'Shimmer Serenity':      {'rare cloth': 30000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1081},
    'Shimmer Zephyr':        {'rare cloth': 30000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1480},
    'Shimmer Bloom':         {'rare cloth': 30000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1577},
    'Shimmer Tidal':         {'rare cloth': 30000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1083},
    'Shimmer Comet':         {'rare cloth': 30000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1099},
    'Arena Black':           {'rare cloth': 500000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2056},
    'Strangelands':          {'rare cloth': 40000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2752},
    'Thief':                 {'rare cloth': 80000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1067},
    'Order Cloth':           {'rare cloth': 50000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2452},
    'Chaos Cloth':           {'rare cloth': 50000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2719},
    'Freedom Cloth':         {'rare cloth': 50000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2944},
    'Corpse Creek Contest':  {'rare cloth': 80000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1197},
    'Stygian Rifts':         {'rare cloth': 150000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1198},
    'Town Struggles':        {'rare cloth': 80000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1199},
    'Dungeon Flashpoints':   {'rare cloth': 80000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1200},
    'Prevalia Faction':      {'rare cloth': 1000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1076},
    'Andaria Faction':       {'rare cloth': 1000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1078},
    'Terran Faction':        {'rare cloth': 1000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1086},
    'Cambria Faction':       {'rare cloth': 1000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1088},
    'Monster Hunter':        {'rare cloth': 50000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 250000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2817},
    'Adventurer Lodge':      {'rare cloth': 50000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 250000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1918},
    'Tradesman Union':       {'rare cloth': 50000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 250000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2765},
    'Order of Armorers':     {'rare cloth': 50000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 250000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2915},
    'Seafarer League':       {'rare cloth': 50000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 250000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2906},
    'Artificer\'s Enclave':  {'rare cloth': 50000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 250000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2875},
    'Aegis Keep':            {'rare cloth': 5000, 'runebook dye': 20000, 'accessory dye': 1000, 'headwear dye': 30000, 'carpet dye': 4000, 'furniture dye': 20000, 'hair dye': 60000, 'facial hair dye': 60000, 'backpack dye': 40000, 'mount gear dye': 5000,  'hue': 1779},
    'Inferno':               {'rare cloth': 5000, 'runebook dye': 20000, 'accessory dye': 1000, 'headwear dye': 20000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 40000, 'facial hair dye': 30000, 'backpack dye': 75000, 'mount gear dye': 10000,  'hue': 1909},
    'Ossuary':               {'rare cloth': 5000, 'runebook dye': 20000, 'accessory dye': 1000, 'headwear dye': 20000, 'carpet dye': 500, 'furniture dye': 20000, 'hair dye': 20000, 'facial hair dye': 20000, 'backpack dye': 50000, 'mount gear dye': 5000,  'hue': 2091},
    'Darkmire Temple':       {'rare cloth': 5000, 'runebook dye': 20000, 'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 25000, 'facial hair dye': 20000, 'backpack dye': 50000, 'mount gear dye': 5000,  'hue': 2099},
    'Pulma':                 {'rare cloth': 5000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 90000, 'facial hair dye': 90000, 'backpack dye': 50000, 'mount gear dye': 5000,  'hue': 2085},
    'The Mausoleum':         {'rare cloth': 5000, 'runebook dye': 20000, 'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 60000, 'facial hair dye': 60000, 'backpack dye': 50000, 'mount gear dye': 5000,  'hue': 2092},
    'Mount Petram':          {'rare cloth': 4000, 'runebook dye': 15000, 'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 40000, 'facial hair dye': 40000, 'backpack dye': 50000, 'mount gear dye': 5000,  'hue': 2089},
    'Nusero':                {'rare cloth': 4000, 'runebook dye': 15000, 'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 500, 'furniture dye': 20000, 'hair dye': 20000, 'facial hair dye': 20000, 'backpack dye': 50000, 'mount gear dye': 5000,  'hue': 2796},
    'Cavernam':              {'rare cloth': 18000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 300000, 'facial hair dye': 300000, 'backpack dye': 50000, 'mount gear dye': 10000,  'hue': 2338},
    'Shadowspire Cathedral': {'rare cloth': 13000, 'runebook dye': 15000, 'accessory dye': 1250, 'headwear dye': 30000, 'carpet dye': 14000, 'furniture dye': 80000, 'hair dye': 40000, 'facial hair dye': 40000, 'backpack dye': 50000, 'mount gear dye': 10000,  'hue': 2093},
    'Wilderness':            {'rare cloth': 5000, 'runebook dye': 15000, 'accessory dye': 1000, 'headwear dye': 20000, 'carpet dye': 100, 'furniture dye': 15000, 'hair dye': 15000, 'facial hair dye': 15000, 'backpack dye': 50000, 'mount gear dye': 5000,  'hue': 1182},
    'Ocean':                 {'rare cloth': 12500, 'runebook dye': 150000, 'accessory dye': 2000, 'headwear dye': 50000, 'carpet dye': 4000, 'furniture dye': 120000, 'hair dye': 100000, 'facial hair dye': 100000, 'backpack dye': 100000, 'mount gear dye': 4000,  'hue': 1183},
    'Metallic Cherry':       {'rare cloth': 50000, 'runebook dye': 40000, 'accessory dye': 10000, 'headwear dye': 200000, 'carpet dye': 4000, 'furniture dye': 50000, 'hair dye': 100000, 'facial hair dye': 100000, 'backpack dye': 100000, 'mount gear dye': 600000,  'hue': 2380},
    'Metallic Orange':       {'rare cloth': 10000, 'runebook dye': 30000, 'accessory dye': 6000, 'headwear dye': 50000, 'carpet dye': 3000, 'furniture dye': 40000, 'hair dye': 100000, 'facial hair dye': 100000, 'backpack dye': 100000, 'mount gear dye': 600000,  'hue': 1989},
    'Metallic Amber':        {'rare cloth': 7000, 'runebook dye': 25000, 'accessory dye': 1000, 'headwear dye': 30000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 50000, 'facial hair dye': 50000, 'backpack dye': 50000, 'mount gear dye': 600000,  'hue': 1990},
    'Metallic Lemon-Lime':   {'rare cloth': 5000, 'runebook dye': 25000, 'accessory dye': 1000, 'headwear dye': 30000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 40000, 'facial hair dye': 30000, 'backpack dye': 50000, 'mount gear dye': 600000,  'hue': 2653},
    'Metallic Olive':        {'rare cloth': 3000, 'runebook dye': 25000, 'accessory dye': 1000, 'headwear dye': 30000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 20000, 'facial hair dye': 20000, 'backpack dye': 50000, 'mount gear dye': 600000,  'hue': 2398},
    'Metallic Pickle':       {'rare cloth': 9000, 'runebook dye': 30000, 'accessory dye': 5000, 'headwear dye': 30000, 'carpet dye': 3000, 'furniture dye': 20000, 'hair dye': 50000, 'facial hair dye': 50000, 'backpack dye': 50000, 'mount gear dye': 600000,  'hue': 2828},
    'Metallic Juniper':      {'rare cloth': 3000, 'runebook dye': 25000, 'accessory dye': 1000, 'headwear dye': 30000, 'carpet dye': 500, 'furniture dye': 2000, 'hair dye': 10000, 'facial hair dye': 7000, 'backpack dye': 50000, 'mount gear dye': 600000,  'hue': 2845},
    'Metallic Mint':         {'rare cloth': 3000, 'runebook dye': 25000, 'accessory dye': 1000, 'headwear dye': 30000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 30000, 'facial hair dye': 30000, 'backpack dye': 50000, 'mount gear dye': 600000,  'hue': 2827},
    'Metallic Sky':          {'rare cloth': 4000, 'runebook dye': 25000, 'accessory dye': 2000, 'headwear dye': 30000, 'carpet dye': 2000, 'furniture dye': 20000, 'hair dye': 40000, 'facial hair dye': 30000, 'backpack dye': 50000, 'mount gear dye': 600000,  'hue': 2826},
    'Metallic Sapphire':     {'rare cloth': 8000, 'runebook dye': 30000, 'accessory dye': 2000, 'headwear dye': 30000, 'carpet dye': 1000, 'furniture dye': 30000, 'hair dye': 40000, 'facial hair dye': 30000, 'backpack dye': 50000, 'mount gear dye': 600000,  'hue': 2379},
    'Metallic Cerulean':     {'rare cloth': 8000, 'runebook dye': 40000, 'accessory dye': 1000, 'headwear dye': 30000, 'carpet dye': 1000, 'furniture dye': 30000, 'hair dye': 40000, 'facial hair dye': 30000, 'backpack dye': 50000, 'mount gear dye': 600000,  'hue': 1484},
    'Metallic Eggplant':     {'rare cloth': 13000, 'runebook dye': 40000, 'accessory dye': 5000, 'headwear dye': 70000, 'carpet dye': 5000, 'furniture dye': 20000, 'hair dye': 100000, 'facial hair dye': 100000, 'backpack dye': 150000, 'mount gear dye': 600000,  'hue': 2898},
    'Metallic Raspberry':    {'rare cloth': 6000, 'runebook dye': 25000, 'accessory dye': 2000, 'headwear dye': 30000, 'carpet dye': 2000, 'furniture dye': 20000, 'hair dye': 40000, 'facial hair dye': 30000, 'backpack dye': 50000, 'mount gear dye': 600000,  'hue': 1489},
    'Metallic Wine':         {'rare cloth': 6000, 'runebook dye': 25000, 'accessory dye': 2000, 'headwear dye': 30000, 'carpet dye': 1000, 'furniture dye': 30000, 'hair dye': 40000, 'facial hair dye': 30000, 'backpack dye': 50000, 'mount gear dye': 600000,  'hue': 1995},
    'Metallic Pewter':       {'rare cloth': 3000, 'runebook dye': 25000, 'accessory dye': 1000, 'headwear dye': 30000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 10000, 'facial hair dye': 10000, 'backpack dye': 25000, 'mount gear dye': 600000,  'hue': 2167},
    'Metallic Chalk':        {'rare cloth': 3000, 'runebook dye': 25000, 'accessory dye': 1000, 'headwear dye': 30000, 'carpet dye': 500, 'furniture dye': 20000, 'hair dye': 40000, 'facial hair dye': 30000, 'backpack dye': 50000, 'mount gear dye': 600000,  'hue': 2928},
    'Metallic Umber':        {'rare cloth': 3000, 'runebook dye': 25000, 'accessory dye': 2000, 'headwear dye': 30000, 'carpet dye': 500, 'furniture dye': 20000, 'hair dye': 20000, 'facial hair dye': 20000, 'backpack dye': 25000, 'mount gear dye': 600000,  'hue': 1470},
    'Dark Coffee':           {'rare cloth': 60000, 'runebook dye': 50000, 'accessory dye': 2000, 'headwear dye': 100000, 'carpet dye': 5000, 'furniture dye': 75000, 'hair dye': 70000, 'facial hair dye': 70000, 'backpack dye': 200000, 'mount gear dye': 600000,  'hue': 1467},
    'Dark Rust':             {'rare cloth': 3000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 20000, 'carpet dye': 1000, 'furniture dye': 30000, 'hair dye': 25000, 'facial hair dye': 25000, 'backpack dye': 40000, 'mount gear dye': 600000,  'hue': 2807},
    'Dark Crimson':          {'rare cloth': 5000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 20000, 'carpet dye': 1000, 'furniture dye': 30000, 'hair dye': 30000, 'facial hair dye': 30000, 'backpack dye': 40000, 'mount gear dye': 600000,  'hue': 1939},
    'Dark Blood':            {'rare cloth': 10000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 20000, 'carpet dye': 4000, 'furniture dye': 30000, 'hair dye': 40000, 'facial hair dye': 30000, 'backpack dye': 40000, 'mount gear dye': 600000,  'hue': 1465},
    'Dark Salmon':           {'rare cloth': 4000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 20000, 'carpet dye': 500, 'furniture dye': 30000, 'hair dye': 15000, 'facial hair dye': 15000, 'backpack dye': 40000, 'mount gear dye': 600000,  'hue': 2174},
    'Dark Forest':           {'rare cloth': 3000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 20000, 'carpet dye': 1000, 'furniture dye': 30000, 'hair dye': 20000, 'facial hair dye': 20000, 'backpack dye': 40000, 'mount gear dye': 600000,  'hue': 2804},
    'Dark Peacock':          {'rare cloth': 3000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 20000, 'carpet dye': 3000, 'furniture dye': 30000, 'hair dye': 25000, 'facial hair dye': 25000, 'backpack dye': 40000, 'mount gear dye': 600000,  'hue': 2226},
    'Dark Denim':            {'rare cloth': 3000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 100000, 'carpet dye': 1000, 'furniture dye': 30000, 'hair dye': 25000, 'facial hair dye': 25000, 'backpack dye': 40000, 'mount gear dye': 600000,  'hue': 2801},
    'Dark Blueberry':        {'rare cloth': 3000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 20000, 'carpet dye': 1000, 'furniture dye': 30000, 'hair dye': 25000, 'facial hair dye': 25000, 'backpack dye': 40000, 'mount gear dye': 600000,  'hue': 1156},
    'Dark Jam':              {'rare cloth': 50000, 'runebook dye': 50000, 'accessory dye': 12000, 'headwear dye': 200000, 'carpet dye': 20000, 'furniture dye': 100000, 'hair dye': 150000, 'facial hair dye': 150000, 'backpack dye': 200000, 'mount gear dye': 600000,  'hue': 2230},
    'Powder Ruby':           {'rare cloth': 110000, 'runebook dye': 80000, 'accessory dye': 30000, 'headwear dye': 600000, 'carpet dye': 20000, 'furniture dye': 250000, 'hair dye': 400000, 'facial hair dye': 400000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2227},
    'Powder Coral':          {'rare cloth': 20000, 'runebook dye': 30000, 'accessory dye': 7000, 'headwear dye': 150000, 'carpet dye': 9000, 'furniture dye': 100000, 'hair dye': 100000, 'facial hair dye': 100000, 'backpack dye': 150000, 'mount gear dye': 600000,  'hue': 1495},
    'Powder Peach':          {'rare cloth': 15000, 'runebook dye': 30000, 'accessory dye': 10000, 'headwear dye': 150000, 'carpet dye': 2000, 'furniture dye': 100000, 'hair dye': 150000, 'facial hair dye': 150000, 'backpack dye': 150000, 'mount gear dye': 600000,  'hue': 1496},
    'Powder Lemon':          {'rare cloth': 65000, 'runebook dye': 50000, 'accessory dye': 15000, 'headwear dye': 500000, 'carpet dye': 8000, 'furniture dye': 100000, 'hair dye': 300000, 'facial hair dye': 300000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1382},
    'Powder Pistachio':      {'rare cloth': 20000, 'runebook dye': 30000, 'accessory dye': 10000, 'headwear dye': 150000, 'carpet dye': 4000, 'furniture dye': 100000, 'hair dye': 75000, 'facial hair dye': 75000, 'backpack dye': 150000, 'mount gear dye': 600000,  'hue': 1494},
    'Powder Seafoam':        {'rare cloth': 30000, 'runebook dye': 30000, 'accessory dye': 15000, 'headwear dye': 150000, 'carpet dye': 4000, 'furniture dye': 100000, 'hair dye': 300000, 'facial hair dye': 300000, 'backpack dye': 150000, 'mount gear dye': 600000,  'hue': 2246},
    'Powder Spring':         {'rare cloth': 30000, 'runebook dye': 30000, 'accessory dye': 15000, 'headwear dye': 150000, 'carpet dye': 9000, 'furniture dye': 100000, 'hair dye': 300000, 'facial hair dye': 300000, 'backpack dye': 150000, 'mount gear dye': 600000,  'hue': 1381},
    'Powder Lapis':          {'rare cloth': 55000, 'runebook dye': 80000, 'accessory dye': 15000, 'headwear dye': 500000, 'carpet dye': 5000, 'furniture dye': 100000, 'hair dye': 400000, 'facial hair dye': 400000, 'backpack dye': 150000, 'mount gear dye': 600000,  'hue': 2255},
    'Powder Cyan':           {'rare cloth': 40000, 'runebook dye': 30000, 'accessory dye': 15000, 'headwear dye': 150000, 'carpet dye': 5000, 'furniture dye': 100000, 'hair dye': 100000, 'facial hair dye': 100000, 'backpack dye': 150000, 'mount gear dye': 600000,  'hue': 2877},
    'Powder Azure':          {'rare cloth': 175000, 'runebook dye': 80000, 'accessory dye': 30000, 'headwear dye': 1200000, 'carpet dye': 8000, 'furniture dye': 100000, 'hair dye': 800000, 'facial hair dye': 800000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1384},
    'Powder Orchid':         {'rare cloth': 55000, 'runebook dye': 30000, 'accessory dye': 15000, 'headwear dye': 500000, 'carpet dye': 5000, 'furniture dye': 100000, 'hair dye': 200000, 'facial hair dye': 200000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1462},
    'Powder Iris':           {'rare cloth': 400000, 'runebook dye': 100000, 'accessory dye': 50000, 'headwear dye': 1300000, 'carpet dye': 20000, 'furniture dye': 250000, 'hair dye': 800000, 'facial hair dye': 800000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2173},
    'Powder Cloud':          {'rare cloth': 200000, 'runebook dye': 80000, 'accessory dye': 40000, 'headwear dye': 600000, 'carpet dye': 9000, 'furniture dye': 100000, 'hair dye': 800000, 'facial hair dye': 800000, 'backpack dye': 800000, 'mount gear dye': 600000,  'hue': 2903},
    'Powder Blush':          {'rare cloth': 35000, 'runebook dye': 30000, 'accessory dye': 15000, 'headwear dye': 150000, 'carpet dye': 5000, 'furniture dye': 100000, 'hair dye': 100000, 'facial hair dye': 100000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2808},
    'Powder Bubblegum':      {'rare cloth': 125000, 'runebook dye': 50000, 'accessory dye': 40000, 'headwear dye': 400000, 'carpet dye': 18000, 'furniture dye': 250000, 'hair dye': 600000, 'facial hair dye': 600000, 'backpack dye': 800000, 'mount gear dye': 600000,  'hue': 1952},
}

def alter_hue_dict(self_parse=False, item_type="rare cloth"):
    shoe_list = ['cloth shoes', 'shoes', 'cloth boots', 'cloth thigh boots', 'cloth sandals']
    out_dict = defaultdict(int)
    if self_parse:
        for hue_name, hue_data in hue_list.items():
            lower = hue_name.lower()
            if item_type == 'rare cloth':
                new_k = f"{item_type} (hue {hue_data['hue']}: {lower})"
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
    print(json.dumps(out_dict, indent=4))

misc_crafting_prices = { #https://outlandmalls.com/?item=&search_category_id=21&search_sub_category_id=98
    "pristine lumber": 32000, 
    "immaculate stone": 32000,
    "an arcane scroll": 1000,
    "research materials (double-click to research)": 35000,
    "mastercrafting diagram": 15500,
    "cleansing brew": 1500,
    "amber": 50,
    "amethyst": 62,
    "citrine": 25,
    "diamond": 125,
    "emerald": 100,
    "ruby": 75,
    "sapphire": 87,
    "star sapphire": 112,
    "tourmaline": 37,
}

misc_prices = { #exact string matters
    "pristine lumber": 32000, 
    "immaculate stone": 32000,
    "an arcane scroll": 1000,
    "research materials (double-click to research)": 35000,
    "mastercrafting diagram": 15500,
    "a skill mastery orb (used to increase a player's total skill cap by 1)": 15000, #a skill mastery orb : 3 (used to increase a player's total skill cap by 1)
    "plant chemicals": 2000,
    #"supremely potent magic spellbook": 13000,
    "an ankh token":9000,
    "prevalia coins [blessed]":17800, #prevalia coins : 5 [blessed]
    #"exceedingly potent magic spellbook": 3500,
    "arcane essence": 30,
    "a message in a bottle": 19000, 
    "an emote deed": 200000,
    #"a battle commendation (double-click to consume and receive reward item)": 10000,
    "invulnerability leather cap": 100000,
    "dyeable gilded gold carpet tile": 20000
}

misc_hp_prices = { #exact string matters
    # "research materials (double-click to research)": 35000,
    # "mastercrafting diagram": 15500,
    # "a skill mastery orb (used to increase a player's total skill cap by 1)": 15000, #a skill mastery orb : 3 (used to increase a player's total skill cap by 1)
    "plant chemicals": 2000,
    "prevalia coins [blessed]":17800, #prevalia coins : 5 [blessed]
}

misc_lp_prices = { #exact string matters
    # "pristine lumber": 32000, 
    # "immaculate stone": 32000,
    # "an arcane scroll": 1000,
    #"exceedingly potent magic spellbook": 3500,
    #"supremely potent magic spellbook": 13000,
    "an ankh token":9000,
    "arcane essence": 30,
    "a message in a bottle": 19000, 
    "an emote deed": 200000,
    #"a battle commendation (double-click to consume and receive reward item)": 10000,
    "invulnerability leather cap": 100000,
    "dyeable gilded gold carpet tile": 20000
}

my_locations = {
    # Vendor Police
    "N Prevalia Sandbar": (1657,1320),
    "N Prev Clearing N": (1592,1388),
    "N Prev Clearing E": (1629,1421),
    "N Prev Clearing Mid": (1596,1419),
    "N Prev Clearing S": (1585,1439),
    "N Prev Clearing SW": (1554,1439),
    "N Prev Clearing W": (1555,1404),
    "E of Prev": (2036,1463),
    "Khal SE Prev": (2002,1795),
    "S Prev Xroad N": (1569,1729),
    "S Prev Xroad E": (1647,1745),
    "S Prev Xroad S": (1545,1772),
    "S Prev Xroad Far S": (1531,1833),
    "S Prev Xroad W": (1499,1757),
    "SW Prev Clearing SE": (1547,1653),
    "SW Prev Clearing NE": (1544,1623),
    "SW Prev Clearing SW": (1510,1657),
    "SW Prev Clearing NW": (1486,1588),
    "Prev Gate": (1475,1488),
    "N of Anchor's Rest": (3756,347),
    "W of Prev Gate": (1425,1483),
    "S of Anchor's Rest": (3757,740),
    "S of Anchor's Rest 2": (3752,671),
    "Far S Anchor's Rest": (3715, 872),
    "E of GH": (3981,854),

    # a lost girl
    "N Cambria Gate": (1706,3129),
    "SE Cambria Gate": (1753,3176),
    "S Cambria Gate": (1709,3182),
    "SW Cambria Gate": (1669,3177),
    "NW Cambria Gate": (1670,3138),
    "N Outpost Gate": (2980,579),
    "N Outpost Gate 2": (2975,547),
    "N Outpost Gate 3": (3001,496),
    "NW Outpost Gate": (2940,563),
    "NW Outpost Gate Far": (2982,500),
    "NE Outpost Close": (3387,377),
    "NE Outpost Far": (3398,178),
    "NE Outpost Far NW": (3250,296),
    "Frost Forest": (3622,447),
    "Frozen Ruins SE":(1612,780),
    "Frozen Ruins SW":(1546,753),
    "W Andaria Gate": (2315,639),
    "N Andaria Gate": (2334,591),
    "Minotaur Island": (3967,1736),
    "Minotaur Island E": (4067,1766),
    "N Terran Clearing": (869,1381),
    "S Terran Clearing": (927,1471),
    "SW Terran Clearing": (893,1517),
    "TRT":(1756,2341),
    "S of TRT": (1779,2388),

    # Aproctoflecticus
    "Mine": (4008,477),
    "AR0": (3962,477),
    "AR1": (3961,559),
    "AR2": (3961,477),
    "AR3": (4002,554),
    "AR4": (4020,515),
    "AR5": (4050,540),
    "AR6": (4050,508), 
    "AR7": (4055,463),
    "S of Pulma": (1780,1048),
    "W of SSC": (3267,689),
    "Cedar Island Mall":(3985,349),
    "Cedar Island Center":(4025,305),
    "Shelter Haven": (1588,2550),
    "MyKruelz":(1634,1136),
    "Western Camp Island": (3495,1467),
    "Pwnstar":(4218,1090),
    "Far S Prev W":(1765,1740),
    "Far S Prev SW":(1730,1782),
    "81a Xroad":(1262,1907),
    "E Andaria Gate":(2398,648),
    "Winterspire":(3571,198),
    "W of Urukton":(1899,1163),
    "N Prev Sandbar W":(1551,1315),

    # Unassigned
    "SOF Island Mall": (3571,198),
}

def is_junk(item_name,item_quantity):
    # Check if the 'forbidden_words_set' attribute exists. If not, create it.
    item_name = item_name.lower()
    if not hasattr(is_junk, "general_forbidden"):
        is_junk.general_forbidden = {
        "potion keg","common plant","common seed","unidentified"," phylactery","durable ","substantial ","massive ","fortified ","exceptional ","accurate ",
        "ruin ","might ","force ","slaying ","mastercrafted "," defense ","guarding ","hardening ","fortification ","potent ","melodious ","boarding rope",
        "blank map","large ship bomb","(delectable)","skinning knife","fishing pole","fishing map"," uses remaining)","cannon shot","recall scroll","hops seed","a disguise kit",
        "veterinary supplies","fertility serum","AAAAAAAAAAA","AAAAAAAAAAA","AAAAAAAAAAA","AAAAAAAAAAA","AAAAAAAAAAA","AAAAAAAAAAA","AAAAAAAAAAA","AAAAAAAAAAA","AAAAAAAAAAA","AAAAAAAAAAA"
        }

    if not hasattr(is_junk, "strict_forbidden"):
        is_junk.strict_forbidden = [
        "bow","buckler","crossbow","kryss","martial manual","platemail chest","quarter staff","shepherd's crook","war mace","longsword"
        ]
        
    if not hasattr(is_junk, "singleton_forbidden"):
        is_junk.singleton_forbidden = {
        "ingot","board","leather","gems","bottle","blank scroll",
        }
    #singleton_check
    # if item_quantity == 1 and any(word in item_name for word in is_junk.singleton_forbidden):
    #     pass #TODO
    if item_name in is_junk.strict_forbidden: #returns true if item is junk
        return True 
    general_check = any(word in item_name for word in is_junk.general_forbidden) #returns true if item is junk
    return general_check

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
        page_url = "https://outlandmalls.com/?item=&search_category_id=21&search_sub_category_id=98"
    else:
        page_url = "https://outlandmalls.com/?item=" + quote_plus(item) + "&search_category_id=0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(page_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage: {item}. Status code: {response.status_code}")
        return (None,None)
    soup = BeautifulSoup(response.content, 'lxml')
    if soup:
        table = soup.find('table', id="item-search-results")
        if not table:
            print('Table not found')
            return
        out_data = []
        rows = table.tbody.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            time_cell = cells[7]
            time_string = time_cell.text.strip().lower()  # Convert to lowercase for consistent comparison
            if is_time_recent_multi(time_string,time_frame):
                vendor_cell = cells[1]
                location_cell = cells[2]
                name_cell = cells[3]
                quantity_cell = cells[4]
                price_cell = cells[6]
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
                    x2, y2 = map(int,tuple_loc)
                    distance = get_distance(x1,y1,x2,y2)
                    if distance < check_dist:
                        check_dist = distance
                        closest = location_name
                location_name = closest if closest else 'N/A'
                formatted_location_link = f"{location_link_split[0]}?{vendor_serial}?{item_serial}?{item_price}#{location_link_split[1]}"
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
                    cost_to_price_ratio = round(price / threshold,2)
                elif price == 999 and not is_junk(name_string,quantity_string):
                    cost_to_price_ratio = 1001
                else:
                    cost_to_price_ratio = 1000
                if cost_to_price_ratio != 1001 and cost_to_price_ratio > cutoff_threshold and price_depth != 2:
                    continue
                if(price <= threshold or price_depth == 2): #self.search_pricedepth.get()
                    format_url = "https://outlandmalls.com/?item=" + quote_plus(name_string) + "&search_category_id=0"
                    out_data.append((f"{name_string}",f"{price}/{threshold}",f"{cost_to_price_ratio}",f"{quantity_string}",f"{vendor_string}",f"{location_coordinates}\t{closest}",f"{time_string}",f"{formatted_location_link}",f"{format_url}"))
        #print(f"out_data length: {len(out_data)}")
        #for tuple in out_data:
        return (item,out_data)
        #self.queue_append.put(out_data)

def multi_parse_hue(in_tuple): #TODO
    pass

def multi_parse_misc(in_tuple):
    html = in_tuple[0]
    #print(f'html:{len(html)}')
    searchPrice = in_tuple[1]
    page_url = in_tuple[2]
    time_frame = in_tuple[3]
    price_depth = in_tuple[4]
    cutoff_threshold = in_tuple[5]
    soup = BeautifulSoup(html, 'lxml')
    #print(f"soup: {time.time() - misc_start_time}")
    if soup:
        # Find the table with the specific id
        table = soup.find('table', id="item-search-results")
        #print(f'table:{table}')
        if not table:
            print(page_url)
            return False
        # Extract all rows from the table body
        rows = table.tbody.find_all('tr')
        out_data = []
        for row in rows[:7]:
            cells = row.find_all('td')
            time_cell = cells[7]
            time_string = time_cell.text.strip().lower()  # Convert to lowercase for consistent comparison
            if is_time_recent_multi(time_string,time_frame):
                price_cell = cells[6]
                price = float(price_cell.text.strip().replace(',', ''))  # Convert price to float
                ratio = round(price / searchPrice,2)
                if ratio > cutoff_threshold and price_depth != 2:
                        continue
                if price <= searchPrice or price_depth == 2:
                    vendor_cell = cells[1]
                    location_cell = cells[2]
                    name_cell = cells[3]
                    quantity_cell = cells[4]
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
                        x2, y2 = map(int,tuple_loc)
                        distance = get_distance(x1,y1,x2,y2)
                        if distance < check_dist:
                            check_dist = distance
                            closest = location_name
                    location_name = closest if closest else 'N/A'
                    formatted_location_link = f"{location_link_split[0]}?{vendor_serial}?{item_serial}?{item_price}#{location_link_split[1]}"
                    quantity_string = quantity_cell.text.strip()
                    name_string = name_cell.text.strip()
                    out_data.append((f"{name_string}",f"{price}/{searchPrice}",f"{ratio}",f"{quantity_string}",f"{vendor_string}",f"{location_coordinates}\t{closest}",f"{time_string}",f"{formatted_location_link}",f"{page_url}"))
        #for tuple in out_data:
        return out_data
        #collected_data.append(out_data)

def is_time_recent_multi(time_string,seconds_threshold):
    #print(seconds_threshold)
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

def sort_key_tuple(item):
    primary_val, secondary_val = item[0], item[1]  # Extract the values from the tuple
    #print(f"primary_val:{primary_val}, secondary_val:{secondary_val}")
    primary_key = 1000.0
    secondary_key = 1000.0
    # Handling the primary value 
    try:
        if len(primary_val) == 0:
            #print('primary: no length')
            pass
        else:
            try:
                result = get_seconds_from_string(primary_val)
                if result:
                    primary_key = float(result)
                else:
                    primary_key = float(primary_val)
                    if primary_key > 10000.0:
                        print(f'Vendor name convertable to float in primary check {primary_val}:{primary_key}:{result}')
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
            #print('secondary: no length')
            pass
        else:
            try:
                result = get_seconds_from_string(secondary_val)
                if result:
                    primary_key = float(result)
                else:
                    secondary_key = float(secondary_val)
                    if secondary_key > 10000.0:
                        print(f'Vendor name convertable to float in secondary check {secondary_val}:{secondary_key}:{result}')
                        raise Exception('Vendor name convertable to float')
                    #print(primary_key)
            except Exception as e:
                #print(f"Couldn't parse seconds from string: {e}")
                secondary_key = secondary_val.lower()
    except Exception as e:
        print(f"Unexpected error for secondary column: {e}")
    #print(f"primary_key:{primary_key}, secondary_key:{secondary_key}")
    return (primary_key, secondary_key)  # Return a tuple for multi-level sorting

def delete_most_recent_log(event=None):
    file = get_most_recent_log()
    os.remove(file)

def get_most_recent_log():
    folder_path = "C:\\Program Files (x86)\\Ultima Online Outlands\\ClassicUO\Data\Client\\JournalLogs\\"
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
    my_vendors = [4342004,1888935,3097786]
    vendors = {}
    current_vendor = None
    latest_log = get_most_recent_log()
    if not latest_log:
        return False
    character_name = None
    pass_flag = False
    my_vendor_objs = []
    with open(latest_log, 'r', encoding='utf-8') as lines:
        # Iterate through each line

        for line in lines:
            if "System: Welcome" in line:
                match = re.search(r'System: Welcome (.+)!', line)
                character_name = match.group(1) if match else 'Invalid Name'
                pass
            elif "…item" in line and current_vendor is not None:
                if "Not for sale" in line:
                    continue
                #item_id = re.search(r'ID:(\d+) (.+?)(?: : (\d+)(.*))?$', line)
                match = re.search(r'ID:(\d+) Price: (\d+) (.+?)(?: : (\d+)(.*))?$', line)
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
                        x2, y2 = map(int,tuple_loc)
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
        self.root.title("Ali's OutlandMalls Scraper")
        self.root.geometry("1160x870")  # Initial size
        self.root.minsize(1160, 870)  # Minimum size
        #self.root.maxsize(900, 700)  # Maximum size
        self.root.bind("<Return>", self.ParseMostRecentJournalLog)
        self.root.bind("<Control-Return>", self.ScrapeOutlandMall)
        self.root.bind("<F1>", self.sort_tree_density)
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
        self.tree = ttk.Treeview(self.tree_frame, columns=("Item", "Price","Ratio","#","Vendor","Location","Time"),show='headings')
        self.tree.heading("Item", text="Item", command=lambda _col="Item",_col2 ="Ratio": self.sort_column_tuple(_col, _col2, False, sort_key_tuple))
        self.tree.heading("Price", text="Price")
        self.tree.heading("Ratio", text="%", command=lambda _col="Ratio",_col2 ="Item": self.sort_column_tuple(_col, _col2, False, sort_key_tuple))
        self.tree.heading("#", text="#")
        self.tree.heading("Vendor", text="Vendor", command=lambda _col="Vendor",_col2 ="Item": self.sort_column_tuple(_col, _col2, False, sort_key_tuple))
        #self.tree.heading("Location", text="Location", command=lambda _col="Location",_col2 ="Ratio": self.sort_column_tuple(_col, _col2, False, sort_key_tuple))
        self.tree.heading("Location", text="Location", command=self.sort_tree_density)
        self.tree.heading("Time", text="Time", command=lambda _col="Time",_col2 ="Ratio": self.sort_column_tuple(_col, _col2, False, sort_key_tuple))
        self.tree.column("Item", width=300)
        self.tree.column("Price", width=100)
        self.tree.column("Ratio", width=25)
        self.tree.column("#", width=15)
        self.tree.column("Vendor", width=125)
        self.tree.column("Location", width=205)
        self.tree.column("Time", width=100)
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
        #self.check_misc_var = tk.BooleanVar(self.root)
        self.check_hp_misc_var = tk.BooleanVar(self.root)
        self.check_lp_misc_var = tk.BooleanVar(self.root)
        self.check_cloth_var = tk.BooleanVar(self.root)
        self.check_dye_var = tk.BooleanVar(self.root)
        self.check_misc_crafting_var = tk.BooleanVar(self.root)
        self.check_ingot_var = tk.BooleanVar(self.root)
        self.check_board_var = tk.BooleanVar(self.root)
        self.check_leather_var = tk.BooleanVar(self.root) 

        self.set_hp_checkboxes()

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

        # self.check_misc_search = ttk.Checkbutton(self.checkbox_frame, text="Search Misc", variable=self.check_misc_var)
        # self.check_misc_search.grid(row=6, column=0,sticky='w')
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
        self.btn_hp_checkboxes = ttk.Button(self.checkbox_frame, text="HP", command=self.set_hp_checkboxes)
        self.btn_hp_checkboxes.grid(row=13, column=0, sticky='ew', padx=(0,2), pady=(10,2))
        self.btn_lp_checkboxes = ttk.Button(self.checkbox_frame, text="LP", command=self.set_lp_checkboxes)
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
        self.cutoff_slider.set(0.9)
        self.label_sortmode = ttk.Label(self.radio_frame,text='Sort Mode:')
        self.label_sortmode.grid(row=3,column=0,columnspan=2,pady=(5,0))
        self.radio5 = ttk.Radiobutton(self.radio_frame, text="Indexed", variable=self.search_sortmode, value=1)
        self.radio6 = ttk.Radiobutton(self.radio_frame, text="Best Ratio", variable=self.search_sortmode, value=2)
        self.radio5.grid(row=4, column=0,sticky='w')
        self.radio6.grid(row=4, column=1,sticky='w')
        self.btn_locations = ttk.Button(self.radio_frame, text="Locations", command=self.scrape_vendor_updates)
        self.btn_locations.grid(row=5, column=0, sticky='ew', padx=10, pady=(15,5), columnspan=2)
        self.btn_visit_web = ttk.Button(self.radio_frame, text="Open Website", command=lambda: webbrowser.open("https://outlandmalls.com/"))
        self.btn_visit_web.grid(row=6, column=0, sticky='ew', padx=10, pady=5, columnspan=2)
        self.btn_open_folder = ttk.Button(self.radio_frame, text="Open Folder", command=lambda: os.system('explorer "C:\\Program Files (x86)\\Ultima Online Outlands\\ClassicUO\Data\\Client\\JournalLogs"'))
        self.btn_open_folder.grid(row=7, column=0, sticky='ew', padx=10, pady=5, columnspan=2)
        self.btn_inventory = ttk.Button(self.radio_frame, text="Inventory", command=self.read_db_current_inventory)
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

        self.queue_append = queue.Queue()
        self.queue_flag = False
        self.queue_daemon()
        self.queue_append.put("Idle") 
    
    def set_hp_checkboxes(self):
        self.check_core_var.set(True)
        self.check_extract_var.set(False)
        self.check_distil_var.set(False)
        self.check_tmaps_var.set(True)
        self.check_skillscrolls_var.set(True)
        self.check_chainlinks_var.set(False)
        #self.check_misc_var.set(True)
        self.check_lp_misc_var.set(False)
        self.check_hp_misc_var.set(True)
        self.check_cloth_var.set(False)
        self.check_dye_var.set(False)
        self.check_misc_crafting_var.set(True)
        self.check_ingot_var.set(False)
        self.check_board_var.set(False)
        self.check_leather_var.set(False)

    def set_lp_checkboxes(self):
        self.check_core_var.set(False)
        self.check_extract_var.set(True)
        self.check_distil_var.set(True)
        self.check_tmaps_var.set(False)
        self.check_skillscrolls_var.set(False)
        self.check_chainlinks_var.set(True)
        #self.check_misc_var.set(True)
        self.check_lp_misc_var.set(True)
        self.check_hp_misc_var.set(False)
        self.check_cloth_var.set(True)
        self.check_dye_var.set(True)
        self.check_misc_crafting_var.set(False)
        self.check_ingot_var.set(True)
        self.check_board_var.set(True)
        self.check_leather_var.set(True)

    def set_all_checkboxes(self):
        self.check_core_var.set(True)
        self.check_extract_var.set(True)
        self.check_distil_var.set(True)
        self.check_tmaps_var.set(True)
        self.check_skillscrolls_var.set(True)
        self.check_chainlinks_var.set(True)
        #self.check_misc_var.set(True)
        self.check_lp_misc_var.set(True)
        self.check_hp_misc_var.set(True)
        self.check_cloth_var.set(True)
        self.check_dye_var.set(True)
        self.check_misc_crafting_var.set(True)
        self.check_ingot_var.set(True)
        self.check_board_var.set(True)
        self.check_leather_var.set(True)

    def set_none_checkboxes(self):
        self.check_core_var.set(False)
        self.check_extract_var.set(False)
        self.check_distil_var.set(False)
        self.check_tmaps_var.set(False)
        self.check_skillscrolls_var.set(False)
        self.check_chainlinks_var.set(False)
        #self.check_misc_var.set(False)
        self.check_lp_misc_var.set(False)
        self.check_hp_misc_var.set(False)
        self.check_cloth_var.set(False)
        self.check_dye_var.set(False)
        self.check_misc_crafting_var.set(False)
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
        
        if(len(self.tree.item(row_id,'values')) > 1 and self.tree.item(row_id,'values')[1]):
            if col_id == "#1":
                url = self.tree.item(row_id, "values")[8]
            else:
                url = self.tree.item(row_id, "values")[7]

            value_to_copy_raw = self.tree.item(row_id, "values")[7]
            serial_match = re.search(r'\?(\d+)(?:\?(\d+))(?:\?(\d+))?#', value_to_copy_raw) #'https://www.exploreoutlands.com/?471890?1251126567?312345125#pos:869,1381,13'
            vendor_serial = serial_match.group(1) if serial_match else 0
            item_serial = serial_match.group(2) if serial_match else 0
            item_price = serial_match.group(3) if serial_match else 0
            scriptString = f"""@setvar! timeout 650
@setvar! vendorID {vendor_serial}
@clearignore
while not dead
    if find vendorID ground -1 -1 20
        skill 'hiding'
        overhead "● ▼▼ HERE ▼▼ ●" 88 vendorID
        if findtype 3701 vendorID as pack
            dclick pack
            wait timeout
            @setvar! foundItem 0
            if find {item_serial} pack as item
                @setvar! foundItem item
            else
                while findtype 2472|2473|2474|2475|2476|2480|2481|2482|2604|2605|2606|2607|2608|2609|2610|2611|2612|2613|2614|2615|2616|2617|2618|2619|2620|2621|2622|2623|2624|2625|2626|2627|2628|2629|2630|2631|2632|2633|2634|2635|2636|2637|2638|2639|2640|2641|2642|2643|2711|2712|2713|2714|2715|2716|2717|2718|3644|3645|3646|3647|3648|3649|3650|3651|3701|3702|3703|3704|3705|3706|3708|3709|3710|3711|3712|7808|7809|9002|9003|11010|11011|12657|29833|29832 pack as subContainer
                @ignore subContainer
                dclick subContainer
                wait timeout
                if find {item_serial} pack as item
                    @setvar! foundItem item
                    break
                endif
                endwhile
                clearignore
            endif
            if foundItem != 0
                getlabel foundItem foundItemLabel
                sysmsg "FOUND {{{{foundItemLabel}}}}"
                if "Description: " in foundItemLabel
                elseif "Price: {int(item_price)} " in foundItemLabel
                sysmsg "opening buy menu"
                menu foundItem 0
                else
                overhead "BEWARE PRICE CHANGE" 33
                sysmsg "BEWARE PRICE CHANGE" 33
                endif
            else
                sysmsg "Could not find item for sale"
            endif
        endif
        stop
    endif
    wait 500
endwhile"""
            # split = value_to_copy_raw.(', ')
            # value_to_copy = ">waypoint " + split[0] + " " + split[1]
            self.root.clipboard_clear()
            self.root.clipboard_append(scriptString)
            self.root.update()
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
        value_to_copy_raw = row_values[7] #'https://www.exploreoutlands.com/?471890?1251126567#pos:869,1381,13'
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
        location_raw = self.tree.item(row_id, "values")[5].split('\t')
        location_split = location_raw[0].split(',')
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
        value_to_copy_raw = self.tree.item(row_id, "values")[7]
        serial_match = re.search(r'\?(\d+)(?:\?(\d+))(?:\?(\d+))?#', value_to_copy_raw) #'https://www.exploreoutlands.com/?471890?1251126567?312345125#pos:869,1381,13'
        vendor_serial = serial_match.group(1) if serial_match else 0
        item_id = serial_match.group(2) if serial_match else 0
        item_price = serial_match.group(3) if serial_match else 0
        scriptString = f"""@setvar! timeout 650
@setvar! vendorID {vendor_serial}
@clearignore
while not dead
    if find vendorID ground -1 -1 20
        skill 'hiding'
        overhead "● ▼▼ HERE ▼▼ ●" 88 vendorID
        if findtype 3701 vendorID as pack
            dclick pack
            wait timeout
            @setvar! foundItem 0
            if find {item_id} pack as item
                @setvar! foundItem item
            else
                while findtype 2472|2473|2474|2475|2476|2480|2481|2482|2604|2605|2606|2607|2608|2609|2610|2611|2612|2613|2614|2615|2616|2617|2618|2619|2620|2621|2622|2623|2624|2625|2626|2627|2628|2629|2630|2631|2632|2633|2634|2635|2636|2637|2638|2639|2640|2641|2642|2643|2711|2712|2713|2714|2715|2716|2717|2718|3644|3645|3646|3647|3648|3649|3650|3651|3701|3702|3703|3704|3705|3706|3708|3709|3710|3711|3712|7808|7809|9002|9003|11010|11011|12657|29833|29832 pack as subContainer
                @ignore subContainer
                dclick subContainer
                wait timeout
                if find {item_id} pack as item
                    @setvar! foundItem item
                    break
                endif
                endwhile
                clearignore
            endif
            if foundItem != 0
                getlabel foundItem foundItemLabel
                sysmsg "FOUND {{{{foundItemLabel}}}}"
                if "Description: " in foundItemLabel
                elseif "Price: {int(item_price)} " in foundItemLabel
                sysmsg "opening buy menu"
                menu foundItem 0
                else
                overhead "BEWARE PRICE CHANGE" 33
                sysmsg "BEWARE PRICE CHANGE" 33
                endif
            else
                sysmsg "Could not find item for sale"
            endif
        endif
        stop
    endif
    wait 500
endwhile"""
        self.root.clipboard_clear()
        self.root.clipboard_append(scriptString)
        self.root.update()
        self.tree.selection_set(row_id)
        #self.context_menu.post(event.x_self.root, event.y_self.root)
        self.queue_append.put(location_name)

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
                elapsed_time = time.time() - start_time
                self.queue_append.put(f"{searchString}")
                #misc_start_time = time.time()  # Record the current time
                page_url = "https://outlandmalls.com/?item=" + quote_plus(searchString) + "&search_category_id=0"
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                response = requests.get(page_url, headers=headers)

                if response.status_code != 200:
                    print(f"Failed to retrieve the webpage: {searchString}. Status code: {response.status_code}")
                    continue
                print(f"start request: {searchString}: {elapsed_time}")
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
            ["Aspect Extract", extract_prices, self.check_extract_var.get()],
            ["Aspect Distillation", distil_prices, self.check_distil_var.get()],
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
        num_cores = cpu_count()
        with Pool(num_cores) as pool:
            for result in pool.imap_unordered(multi_parse_wide,tuple_list):
                self.queue_append.put(result[0])
                self.queue_append.put(result[1])
        time.sleep(.2)
        elapsed_time = round(time.time() - start_time,2)
        print(f"multi wide: {elapsed_time}")
        self.queue_append.put(f"Complete: {elapsed_time}s")

    def ScrapeOutlandMall(self,event=''):
        self.clear_tree()
        async_bot = threading.Thread(target=self.async_scraping)
        async_bot.start()

    def search_self_parse_obj(self,parse_obj):
        corrupted_link_price_threshold = 200000
        cutoff_threshold = self.cutoff_threshold.get()
        price_depth = self.search_pricedepth.get()
        bools = [
            (self.check_core_var.get(), core_prices),
            (self.check_extract_var.get(), extract_prices),
            (self.check_distil_var.get(), distil_prices),
            (self.check_tmaps_var.get(), map_prices),
            (self.check_skillscrolls_var.get(), scroll_prices),
            (self.check_chainlinks_var.get(), link_prices),
            (self.check_cloth_var.get(), 'cloth'), #todo
            #(True, 'cloth'), #todo
            (self.check_dye_var.get(), 'dyes'),
            #(True, 'dyes'), #todo
            #(self.check_misc_var.get(), misc_prices),
            (self.check_hp_misc_var.get(), misc_hp_prices),
            (self.check_lp_misc_var.get(), misc_lp_prices),
            
            (self.check_misc_crafting_var.get(), misc_crafting_prices),
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
                    format_url = "https://outlandmalls.com/?item=" + quote_plus(name_string) + "&search_category_id=0"
                    location_link = f"https://www.exploreoutlands.com/#pos:{location_coordinates_cleaned},13"
                    location_link_split = location_link.split('#')
                    formatted_location_link = f"{location_link_split[0]}?{vendor_id}?{item['id']}?{int(price * quantity_int)}#{location_link_split[1]}"
                    out_data.append((f"{name_string}",f"{price}/{threshold}",f"{cost_to_price_ratio}",f"{quantity_int}",f"{vendor_string}",f"{location_coordinates}\t{location_name}",f"{out_string}",f"{formatted_location_link}",f"{format_url}"))
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
        
    def read_db_current_inventory(self):
        try:
            rows = get_most_recent_inventory_snapshot()
            if not rows:
                print("No inventory snapshot available.")
                return []
            #snapshot_time = rows[0][0]
            #print(f'-Inventory Report- {snapshot_time}')
            inventory_window = tk.Toplevel(self.root)
            inventory_window.title("Inventory")
            self.scrollbar = tk.Scrollbar(inventory_window, orient="vertical")
            listbox = tk.Listbox(inventory_window, yscrollcommand=self.scrollbar.set, width=60, height=20)
            self.scrollbar.config(command=listbox.yview)
            self.scrollbar.pack(side="right", fill="y")
            listbox.pack(side="left", fill="both", expand=True)
            columns = ['snapshot_time', 'id', 'price', 'description', 'quantity']
            for row in rows:
                row_dict = dict(zip(columns, row))
                total_price = row_dict['price'] * row_dict['quantity']
                result = f"ID:{row_dict['id']}, {row_dict['description']}: {row_dict['quantity']}x @ {row_dict['price']} = {total_price}"
                listbox.insert(tk.END, result)
                #print(result)
            #print("-End Report-")
        except Exception as e:
            print(f"An error occurred: {e}")
            return []
    #------------------------------ GUI Updates---------------------------
    def queue_daemon(self,event=None):
        cases = {

        }
        try:
            data = self.queue_append.get_nowait()
            if isinstance(data,str):
                self.status_var.set(data)
            elif data:
                for tuple in data:
                    self.append_to_tree(*tuple)
                self.queue_flag = True
            self.root.after(50, self.queue_daemon)  # check again after 100ms
        except queue.Empty:
            if self.queue_flag:
                self.queue_flag = False
                if self.search_sortmode.get() == 2:
                    self.sort_column_tuple("Ratio", "Item", False, sort_key_tuple)
            self.root.after(100, self.queue_daemon)  # if queue is empty, check again after a longer delay

    def clear_tree(self):
        # Clear the Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)
#"Item", "Price","Ratio","#","Vendor","Location","Time"
    def append_to_tree(self,text1='',text2='',text3='',text4='',text5='',text6='',text7='',text8='',text9='',text10=''):
        if len(text3):
            ratio = float(text3)
            if ratio == 1001:
                item = self.tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9, text10), tags=("mistake",))
            elif ratio < 0.6:
                item = self.tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9, text10), tags=("ultra",))
            elif ratio <= 0.7:
                item = self.tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9, text10), tags=("high",))
            elif ratio <= 0.8:
                item = self.tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9, text10), tags=("med",))
            elif ratio <= 0.9:
                item = self.tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9, text10), tags=("low",))
            elif ratio < 0.95:
                item = self.tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9, text10), tags=("verylow",))
            elif ratio >= 0.95 and ratio <= 1.0:
                item = self.tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9, text10), tags=("base",))
            else:
                item = self.tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9, text10))
        else:
            item = self.tree.insert("", "end", values=(text1, text2, text3, text4,text5, text6, text7, text8, text9, text10))
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
        l.sort(key=lambda x: (key(x)[0] if key else x[0], key(x)[1] if key else x[1]), reverse=reverse)
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
        items_by_location = defaultdict(list)
        for item in data:
            items_by_location[item['Location'].split('\t')[1]].append(item)
        data_by_location = []
        for location, items in items_by_location.items():
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
                profit_margin = round((sale_price - my_cost) / my_cost,2)
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


def start_purchase_script():
    mouse_pos = win32api.GetCursorPos()

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
        window = focus_named_assistant(extracted_name)
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
    win32api.SetCursorPos(mouse_pos)

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
    window.set_focus()
    win32api.SetCursorPos(mouse_pos)

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
        return
    assistant = connect_to_window(assistant_window._hWnd)
    if not assistant:
        print("Couldn't connect to assistant app!")
        return
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
    client = connect_to_window(client_window._hWnd)
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
        return
    except pywinauto.timings.TimeoutError as e:
        print(f"Operation timed out: {e}")
        return
    except Exception as e:
        print(f"Unexpected error: {e}")
        return
    return connection

#print(f"Press ctrl+alt+` to find the Client/Assistant window for the active window...")
keyboard.add_hotkey("ctrl+alt+c", start_purchase_script)
keyboard.add_hotkey("ctrl+alt+`", switch_focus)
keyboard.add_hotkey("ctrl+alt+1", lambda: focus_named_assistant('a lost girl'))
keyboard.add_hotkey("ctrl+alt+2", lambda: focus_named_assistant('Vendor Police'))
keyboard.add_hotkey("ctrl+alt+3", lambda: focus_named_assistant('Aproctoflecticus'))

def main():
    root = tk.Tk()
    AliApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()