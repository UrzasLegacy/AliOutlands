from collections import ChainMap,defaultdict
import pyperclip
import re
import math
import logging
import json
# Get the logger for this module

logger = logging.getLogger('OutlandsDicts')


def collate_master_price_dict():
    master_dict = {**core_prices,**distil_prices,**map_prices,**ingot_prices,**board_prices,**leather_prices,**commodity_2500_prices,**commodity_5000_prices,**scroll_prices,**link_prices,**misc_crafting_prices,**misc_hp_prices,**misc_lp_prices,**deed_prices}
    return master_dict

core_prices = { #exact string MATTERS
    "Air Aspect Core": 75000,
    "Arcane Aspect Core": 80000,
    "Artisan Aspect Core": 55000,
    "Blood Aspect Core": 9000,
    "Command Aspect Core": 80000,
    "Death Aspect Core": 12000,
    "Discipline Aspect Core": 8000,
    "Earth Aspect Core": 8000,
    "Eldritch Aspect Core": 75000,
    "Fire Aspect Core": 13000,
    "Frost Aspect Core": 17000,
    "Fortune Aspect Core": 70000,
    "Gadget Aspect Core": 10000,
    "Harvest Aspect Core": 80000,
    "Holy Aspect Core": 13000,
    "Lightning Aspect Core": 48000,
    "Lyric Aspect Core": 23000,
    "Madness Aspect Core": 75000,
    "Poison Aspect Core": 55000,
    "Shadow Aspect Core": 45000,
    "Void Aspect Core": 48000,
    "War Aspect Core": 7000,
    "Water Aspect Core": 9000,
}

extract_prices = {
    'Air Aspect Extract': 8000,
    "Arcane Aspect Extract": 11000,
    'Artisan Aspect Extract': 5000,
    'Blood Aspect Extract': 5000,
    'Command Aspect Extract': 9000,
    'Death Aspect Extract': 5000,
    'Discipline Aspect Extract': 5000,
    'Earth Aspect Extract': 5000,
    'Eldritch Aspect Extract': 8000,
    'Fire Aspect Extract': 5000,
    "Frost Aspect Extract": 7000,
    'Fortune Aspect Extract': 7000,
    'Gadget Aspect Extract': 5000,
    'Harvest Aspect Extract': 9000,
    'Holy Aspect Extract': 8000,
    "Lightning Aspect Extract": 9000,
    'Lyric Aspect Extract': 5000,
    "Madness Aspect Extract": 11000,
    'Poison Aspect Extract': 7000,
    'Shadow Aspect Extract': 17000,
    'Void Aspect Extract': 8000,
    'War Aspect Extract': 5000,
    'Water Aspect Extract': 5000,
}

distil_prices = {
    'Air Aspect Distillation': 8000,
    "Arcane Aspect Distillation": 11000,
    'Artisan Aspect Distillation': 5000,
    'Blood Aspect Distillation': 5000,
    'Command Aspect Distillation': 9000,
    'Death Aspect Distillation': 5000,
    'Discipline Aspect Distillation': 5000,
    'Earth Aspect Distillation': 5000,
    'Eldritch Aspect Distillation': 8000,
    'Fire Aspect Distillation': 5000,
    "Frost Aspect Distillation": 7000,
    'Fortune Aspect Distillation': 7000,
    'Gadget Aspect Distillation': 5000,
    'Harvest Aspect Distillation': 11000,
    'Holy Aspect Distillation': 8000,
    "Lightning Aspect Distillation": 9000,
    'Lyric Aspect Distillation': 5000,
    "Madness Aspect Distillation": 11000,
    'Poison Aspect Distillation': 9000,
    'Shadow Aspect Distillation': 17000,
    'Void Aspect Distillation': 8000,
    'War Aspect Distillation': 5000,
    'Water Aspect Distillation': 5000,
}

phylactery_prices = {
    "command phylactery": 10000,
    "fortune phylactery": 10000,
    "artisan phylactery": 10000,
    "eldritch phylactery": 10000,
    "harvest phylactery": 10000,
    "earth phylactery": 10000,
    "blood phylactery": 10000,
    "void phylactery": 10000,
    "air phylactery": 10000,
    "discipline phylactery": 10000,
    "fire phylactery": 10000,
    "death phylactery": 10000,
    "gadget phylactery": 10000,
    "holy phylactery": 10000,
    "lyric phylactery": 10000,
    "poison phylactery": 10000,
    "shadow phylactery": 10000,
    "harvest phylactery": 10000,
    "war phylactery": 10000,
    "water phylactery": 10000,
}

map_prices = { #exact string MATTERS
    "plainly drawn treasure map: level 1 (undeciphered)": 9500,
    "expertly drawn treasure map: level 2 (undeciphered)": 19500, #10000
    "adeptly drawn treasure map: level 3 (undeciphered)": 34000, #26000
    "cleverly drawn treasure map: level 4 (undeciphered)": 45000, #35000
    "deviously drawn treasure map: level 5 (undeciphered)": 54000, #45000
    "ingeniously drawn treasure map: level 6 (undeciphered)": 67000,
    "diabolically drawn treasure map: level 7 (undeciphered)": 80000,
    "legendarily drawn treasure map: level 8 (undeciphered)": 325000,

    "avarscale fishing map (undeciphered)": 13000,

    "verewood lumber map (undeciphered)": 15000,
    "valewood lumber map (undeciphered)": 38000,
    "avarwood lumber map (undeciphered)": 85000,

    "verehide skinning map (undeciphered)": 6000,
    "valehide skinning map (undeciphered)": 11000,
    "avarhide skinning map (undeciphered)": 16000,
    
    "copper ore map (undeciphered)": 2000,
    "bronze ore map (undeciphered)": 4000,
    "gold ore map (undeciphered)": 17000,
    "agapite ore map (undeciphered)": 20000,
    "verite ore map (undeciphered)": 27000,
    "valorite ore map (undeciphered)": 55000,
    "avarite ore map (undeciphered)": 100000,
}

ingot_prices = {
    "iron ingot": 16,
    "dull copper ingot": 23,
    "shadow iron ingot": 28,
    "copper ingot": 36,
    "bronze ingot": 60,
    "gold ingot": 110,
    "agapite ingot": 160,
    "verite ingot": 330,
    "valorite ingot": 420,
    "avarite ingot": 800,
    "iron ingot commodity (5,000 total)": 80000,
    "dull copper ingot commodity (2,500 total)": 55000,
    "shadow iron ingot commodity (2,500 total)": 70000,
    "copper ingot commodity (2,500 total)": 85000,
    "bronze ingot commodity (2,500 total)": 150000,
    "gold ingot commodity (2,500 total)": 285000,
    "agapite ingot commodity (2,500 total)": 400000,
    "verite ingot commodity (2,500 total)": 825000,
    "valorite ingot commodity (2,500 total)": 1000000,
    "avarite ingot commodity (2,500 total)": 2000000,
}

board_prices = {
    "board": 14,
    "dullwood board": 30,
    "shadowwood board": 45,
    "copperwood board": 35,
    "bronzewood board": 37,
    "goldenwood board": 55,
    "rosewood board": 100,
    "verewood board": 210,
    "valewood board": 550,
    "avarwood board": 1400,
    "board commodity (5,000 total)": 70000,
    "dullwood commodity (2,500 total)": 75000,
    "shadowwood commodity (2,500 total)": 100000,
    "copperwood commodity (2,500 total)": 85000,
    "bronzewood commodity (2,500 total)": 95000,
    "goldenwood commodity (2,500 total)": 140000,
    "rosewood commodity (2,500 total)": 250000,
    "verewood commodity (2,500 total)": 525000,
    "valewood commodity (2,500 total)": 1300000,
    "avarwood commodity (2,500 total)": 2750000,
}

leather_prices = { #https://outlandmalls.com/?item=&search_category_id=1&search_sub_category_id=28
    "leather": 1,
    "dullhide": 1,
    "shadowhide": 10,
    "copperhide": 14,
    "bronzehide": 32,
    "goldenhide": 45,
    "rosehide": 100,
    "verehide": 110,
    "valehide": 140,
    "avarhide": 340,
    "leather commodity (5,000 total)": 7000,
    "dullhide commodity (2,500 total)": 7000,
    "shadowhide commodity (2,500 total)": 22000,
    "copperhide commodity (2,500 total)": 30000,
    "bronzehide commodity (2,500 total)": 80000,
    "goldenhide commodity (2,500 total)": 125000,
    "rosehide commodity (2,500 total)": 250000,
    "verehide commodity (2,500 total)": 300000,
    "valehide commodity (2,500 total)": 400000, 
    "avarhide commodity (2,500 total)": 900000,
}

commodity_2500_prices = {
    "bottle commodity (500 total)": 2700,
    "blank scroll commodity (2,500 total)": 8500,
    "feather commodity (2,500 total)": 1500,
    "raw fish steak commodity (2,500 total)": 5000,
}

commodity_5000_prices = {
    "black pearl commodity (5,000 total)": 15000,
    "bloodmoss commodity (5,000 total)": 15000,
    "garlic commodity (5,000 total)": 15000,
    "ginseng commodity (5,000 total)": 15000,
    "mandrake root commodity (5,000 total)": 15000,
    "nightshade commodity (5,000 total)": 16000,
    "spiders silk commodity (5,000 total)": 16000,
    "sulfurous ash commodity (5,000 total)": 15000,
    "arrow commodity (5,000 total)": 11000,
    "bolt commodity (5,000 total)": 11000,
    "cannon shot commodity (5,000 total)": 12500,
}

scroll_prices = {
    "alchemy skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 38000,
    "animal lore skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 16000,#[:7]
    "animal taming skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 16000,#[:7]
    "arms lore skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 10000,
    "begging skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 9000,
    "blacksmithy skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 10000,
    "camping skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 15000,
    "carpentry skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 10000,#[:4]
    "cartography skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 13000,#[:4]
    "chivalry skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 35000,
    "cooking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 12000,
    "detect hidden skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 18000,
    "discordance skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 12000,
    "fishing skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 10000,
    "forensic eval skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 13000,#[:4]
    "herding skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 16000,
    "inscription skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 50000,
    "item id skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 13000,
    "lockpicking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 18000,
    "lumberjacking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 11000,
    "mining skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 10000,
    "musicianship skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 10000,
    "necromancy skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 28000,
    "peacemaking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 11000,#[:4]
    "poisoning skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 13000,
    "provocation skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 12000,
    "spirit speak skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 10000,
    "stealth skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 25000,#[:4]
    "tailoring skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 50000,
    "taste id skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 18000,
    "tinkering skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 12000,
    "tracking skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 10000,
    "veterinary skill mastery scroll (used to increase a player's skill cap for a skill by 1)": 13000,
}

link_prices = { #exact chain type string MATTERS
    "Melee Accuracy": [90000,600000,2700000], #Melee Accuracy/Defense
    "Melee Defense": [90000,600000,2700000], #Melee Accuracy/Defense
    "Melee Accuracy/Defense": [90000,600000,2700000],
    "Melee Special Chance/Special Damage": [90000,600000,2700000],
    "Melee Special Chance": [90000,600000,2700000], #Melee Special Chance/Special Damage
    "Melee Swing Speed": [100000,600000,2700000],
    "Melee Damage": [150000,650000,2600000], #Melee Damage/Ignore Armor Chance
    "Melee Ignore Armor Chance": [90000,600000,2400000], #Melee Damage/Ignore Armor Chance
    "Melee Damage/Ignore Armor Chance": [130000,550000,2400000],
    "Melee Aspect Effect Modifier": [90000,600000,2600000],
    "Melee Aspect Effect Chance": [130000,550000,2700000],
    "Spell Damage": [100000,500000,2400000], #Spell Damage/Ignore Resist Chance
    "Spell Damage When No Followers": [130000,600000,2500000],
    "Spell Ignore Resist Chance": [100000,600000,2400000], #Spell Damage/Ignore Resist Chance
    "Spell Damage/Ignore Resist Chance": [100000,600000,2400000],
    "Spell Charged Chance": [80000,550000,2400000], #Spell Charged Chance/Charged Damage
    "Spell Charged Damage": [80000,550000,2400000], #Spell Charged Chance/Charged Damage
    "Spell Charged Chance/Charged Damage": [80000,550000,2400000],
    "Meditation Rate": [90000,550000,2400000], #Meditation Rate/Spell Disrupt Avoid Chance
    "Spell Disrupt Avoid Chance": [130000,600000,2400000], #Meditation Rate/Spell Disrupt Avoid Chance, Spell Damage When No Followers
    "Meditation Rate/Disrupt Avoid Chance": [130000,600000,2500000], #Spell Damage When No Followers
    "Spell Aspect Effect Modifier": [90000,600000,2400000],
    "Spell Aspect Special Chance": [130000,650000,2500000],
    "Damage to Beastial Creatures": [75000,550000,2500000], #Nusero Damage
    "Damage to Construct Creatures": [75000,550000,2500000], #Mausoleum Damage
    "Damage to Daemonic Creatures": [95000,600000,2500000], #Inferno Damage
    "Damage to Elemental Creatures": [75000,550000,2500000], #Mount Petram Damage
    "Damage to Humanoid Creatures": [75000,550000,2500000], #Aegis Keep Damage
    "Damage to Monstrous Creatures": [75000,550000,2500000], #Cavernam Damage
    "Damage to Nature Creatures": [75000,550000,2500000], #Darkmire Temple Damage
    "Damage to Undead Creatures": [75000,550000,2500000], #Ossuary Damage
    "Nusero Damage": [75000,550000,2500000],
    "Mausoleum Damage": [75000,550000,2500000],
    "Inferno Damage": [75000,550000,2500000],
    "Mount Petram Damage": [75000,550000,2500000],
    "Aegis Keep Damage": [75000,550000,2500000],
    "Cavernam Damage": [75000,550000,2500000],
    "Darkmire Temple Damage": [75000,550000,2500000],
    "Ossuary Damage": [75000,550000,2500000],
    "Pulma Damage": [75000,550000,2500000],
    "Shadowspire Cathedral Damage": [90000,600000,2500000],
    "Wilderness Damage": [130000,600000,2500000],
    "Time Dungeon Damage": [130000,600000,2500000],
    "Netherzone Damage": [130000,600000,2500000],
    "Kraul Hive Damage": [130000,600000,2500000],
    "Follower Damage": [130000,600000,2600000],
    "Follower Accuracy/Defense": [130000,600000,2500000],
    "Damage to Barded Creatures": [100000,550000,2600000],
    "Damage to Poisoned Creatures": [140000,600000,2700000],
    "Damage to Diseased Creatures": [170000,670000,2700000],
    "Poison Damage/Resist Ignore": [90000,600000,2400000],
    "Backstab Damage": [180000,650000,2700000],
    "Trap Damage": [110000,550000,2600000],
    "Damage to Bosses": [90000,600000,2600000],
    "Damage on Ships": [110000,550000,2500000],
    "Ship Cannon Damage": [120000,550000,2600000],
    "Damage to Creatures Above 66% HP": [130000,600000,2500000], #Damage Dealt By Player
    "Damage to Creatures Below 33% HP": [100000,550000,2400000], #Damage Dealt By Player
    "Damage Dealt By Player": [90000,550000,2400000],
    "Physical Damage Resistance": [100000,550000,2400000], #Damage Resistance
    "Spell Damage Resistance": [100000,550000,2400000], #Damage Resistance
    "Follower Damage Resistance": [100000,600000,2400000], #Alchemy/Healing/Veterinary Skill, Follower Attack Speed
    "Effective Parrying Skill": [100000,550000,2400000], #Damage Resistance
    "Effective Magic Resist Skill": [100000,550000,2400000], #Damage Resistance
    "Healing Received": [90000,600000,2400000], #Effective Alchemy/Healing/Veterinary Skill
    "Follower Attack Speed": [100000,600000,2700000],
    "Follower Healing Received": [100000,600000,2700000], #Effective Alchemy/Healing/Veterinary Skill, Follower Attack Speed
    "Boss Damage Resistance": [100000,600000,2400000], #Damage Resistance
    "Damage Resistance on Ships": [100000,600000,2400000], #Damage Resistance
    "Damage Resistance": [100000,550000,2400000],
    "Crewmember Damage Resistance": [90000,550000,2400000],
    "Crewmember Damage": [90000,550000,2400000],
    "Chest Success Chances/Progress": [90000,550000,2600000],
    "Effective Skill on Chests": [100000,550000,2600000],
    "Alchemy/Healing/Veterinary": [90000,600000,2400000],
    "Effective Lockpicking Skill": [100000,550000,2600000], #Chest Success Chances/Progress
    "Effective Poisoning Skill": [130000,600000,2600000], #Poison Damage/Resist Ignore
    "Effective Barding Skill": [110000,550000,2500000], #Bard Reset/Break Ignore Chance
    "Exceptional Quality Chance": [130000,650000,2600000],
    "Effective Camping Skill": [120000,600000,2500000], 
    "Effective Harvest Skill": [160000,650000,2600000],
    "Effective Arms Lore Skill": [90000,550000,2400000], 
    "Chivalry Skill": [130000,600000,2500000], 
    "Necromancy Skill": [170000,670000,2700000], #Follower Damage, Follower Damage Resistance
    "Barding Effect Durations": [90000,550000,2400000], #Bard Reset/Break Ignore Chance
    "Bard Reset/Break Ignore Chance": [90000,550000,2400000],
    "Spirit Speak/Inscription": [140000,650000,2600000], #Follower Damage, Follower Damage Resistance
    "Chance on Stealth For 5 Extra Steps": [90000,550000,2600000],
    "Gold/Doubloon Drop Increase": [90000,600000,2400000],
    "Special/Rare Loot Chance": [120000,600000,2500000],
    "reforging tool": [110000,240000,450000],
    "corrupted_link_price_threshold": 620000,
}

hue_list = {
    'Shimmer Oxide':         {'hue': 1483, 'rare cloth': 175000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 1050000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 750000, 'facial hair dye': 750000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Shimmer Oxide
    'Shimmer Cardinal':      {'hue': 1476, 'rare cloth': 125000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 900000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 750000, 'facial hair dye': 750000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Shimmer Cardinal
    'Shimmer Evergreen':     {'hue': 1479, 'rare cloth': 125000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 900000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 750000, 'facial hair dye': 750000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Shimmer Evergreen
    'Shimmer Valentine':     {'hue': 2916, 'rare cloth': 150000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 1050000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 750000, 'facial hair dye': 750000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Shimmer Valentine
    'Shimmer Periwinkle':    {'hue': 2251, 'rare cloth': 175000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 1050000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 750000, 'facial hair dye': 750000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Shimmer Periwinkle
    'Shimmer Shamrock':      {'hue': 2664, 'rare cloth': 175000, 'runebook dye': 250000, 'accessory dye': 50000, 'headwear dye': 1050000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 650000, 'facial hair dye': 500000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Shimmer Shamrock
    'Shimmer Lunar':         {'hue': 2342, 'rare cloth': 150000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 900000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 750000, 'facial hair dye': 750000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Shimmer Lunar
    'Shimmer Solstice':      {'hue': 1967, 'rare cloth': 75000, 'runebook dye': 300000,  'accessory dye': 50000, 'headwear dye': 450000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 500000, 'facial hair dye': 500000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Shimmer Solstice
    'Shimmer Dahlia':        {'hue': 1956, 'rare cloth': 125000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 750000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Shimmer Dahlia
    'Shimmer Paradox':       {'hue': 2346, 'rare cloth': 600000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 3600000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 1000000, 'facial hair dye': 1000000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Shimmer Paradox
    'Shimmer Redux':         {'hue': 1957, 'rare cloth': 300000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 1900000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Shimmer Redux
    'Shimmer Spice':         {'hue': 1557, 'rare cloth': 500000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 3000000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Shimmer Spice
    'Shimmer Garnet':        {'hue': 1571, 'rare cloth': 500000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 3000000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 1000000, 'facial hair dye': 1000000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Shimmer Garnet
    'Shimmer Equinox':       {'hue': 1574, 'rare cloth': 100000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 600000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 500000}, #Shimmer Equinox
    'Shimmer Moonlight':     {'hue': 2284, 'rare cloth': 95000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 900000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 500000}, #Shimmer Moonlight
    'Shimmer Gala':          {'hue': 2074, 'rare cloth': 100000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 600000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 500000}, #Shimmer Gala
    'Shimmer Spirit':        {'hue': 1181, 'rare cloth': 100000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 600000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 500000}, #Shimmer Spirit
    'Shimmer Tempest':       {'hue': 1180, 'rare cloth': 125000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 700000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 500000}, #Shimmer Tempest
    'Shimmer Borealis':      {'hue': 1179, 'rare cloth': 60000, 'runebook dye': 300000,  'accessory dye': 50000, 'headwear dye': 360000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 500000}, #Shimmer Borealis
    'Shimmer Passion':       {'hue': 1184, 'rare cloth': 60000, 'runebook dye': 300000,  'accessory dye': 50000, 'headwear dye': 360000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 500000}, #Shimmer Passion
    'Shimmer Celestial':     {'hue': 1186, 'rare cloth': 60000, 'runebook dye': 250000,  'accessory dye': 50000, 'headwear dye': 360000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 300000, 'mount gear dye': 500000}, #Shimmer Celestial
    'Shimmer Nightfall':     {'hue': 2260, 'rare cloth': 60000, 'runebook dye': 200000,  'accessory dye': 50000, 'headwear dye': 360000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 500000}, #Shimmer Nightfall
    'Shimmer Toil':          {'hue': 1499, 'rare cloth': 40000, 'runebook dye': 300000,  'accessory dye': 50000, 'headwear dye': 240000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 500000}, #Shimmer Toil
    'Shimmer Crystal':       {'hue': 1059, 'rare cloth': 40000, 'runebook dye': 300000,  'accessory dye': 50000, 'headwear dye': 240000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 500000}, #Shimmer Crystal
    'Shimmer Aurora':        {'hue': 1063, 'rare cloth': 40000, 'runebook dye': 300000,  'accessory dye': 50000, 'headwear dye': 240000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 500000}, #Shimmer Aurora
    'Shimmer Candy':         {'hue': 1188, 'rare cloth': 40000, 'runebook dye': 300000,  'accessory dye': 50000, 'headwear dye': 240000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 500000}, #Shimmer Candy
    'Shimmer Fen':           {'hue': 1400, 'rare cloth': 40000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 240000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 500000}, #Shimmer Fen
    'Shimmer Blossom':       {'hue': 1070, 'rare cloth': 35000, 'runebook dye': 300000,  'accessory dye': 50000, 'headwear dye': 240000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 500000}, #Shimmer Blossom
    'Shimmer Mirage':        {'hue': 1575, 'rare cloth': 35000, 'runebook dye': 250000, 'accessory dye': 50000, 'headwear dye': 210000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 250000, 'mount gear dye': 500000}, #Shimmer Mirage
    'Shimmer Gore':          {'hue': 1069, 'rare cloth': 35000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 210000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 400000}, #Shimmer Gore
    'Shimmer Flora':         {'hue': 1071, 'rare cloth': 30000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 190000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 200000, 'facial hair dye': 150000, 'backpack dye': 300000, 'mount gear dye': 400000}, #Shimmer Flora
    'Shimmer Rime':          {'hue': 1074, 'rare cloth': 25000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 190000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 150000, 'mount gear dye': 400000}, #Shimmer Rime
    'Shimmer Serenity':      {'hue': 1081, 'rare cloth': 25000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 190000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 400000, 'mount gear dye': 400000}, #Shimmer Serenity
    'Shimmer Zephyr':        {'hue': 1480, 'rare cloth': 25000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 190000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 400000, 'mount gear dye': 400000}, #Shimmer Zephyr
    'Shimmer Bloom':         {'hue': 1577, 'rare cloth': 25000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 190000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 400000, 'mount gear dye': 400000}, #Shimmer Bloom
    'Shimmer Tidal':         {'hue': 1083, 'rare cloth': 25000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 190000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 400000, 'mount gear dye': 400000}, #Shimmer Tidal
    'Shimmer Comet':         {'hue': 1099, 'rare cloth': 25000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 190000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 400000, 'mount gear dye': 400000}, #Shimmer Comet
    'Shimmer Hex':           {'hue': 1299, 'rare cloth': 22500, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 150000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 400000, 'mount gear dye': 400000}, #Shimmer Hex
    'Shimmer Radiant':       {'hue': 1584, 'rare cloth': 22500, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 150000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 400000, 'mount gear dye': 400000}, #Shimmer Hex
    'Shimmer Clover':        {'hue': 1584, 'rare cloth': 22500, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 150000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 400000, 'mount gear dye': 400000}, #Shimmer Hex
    'Shimmer Nova':          {'hue': 1584, 'rare cloth': 22500, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 150000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 400000, 'mount gear dye': 400000}, #Shimmer Hex
    'Shimmer Selkie':        {'hue': 1572, 'rare cloth': 22500, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 150000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 400000, 'mount gear dye': 400000}, #Shimmer Hex
    'Lustrous Lavender':     {'hue': 4124, 'rare cloth': 200000, 'runebook dye': 500000, 'accessory dye': 50000, 'headwear dye': 1200000, 'carpet dye': 50000, 'furniture dye': 800000, 'hair dye': 500000, 'facial hair dye': 400000, 'backpack dye': 300000, 'mount gear dye': 300000}, #Lustrous Lavender
    'Lustrous Carmine':      {'hue': 4125, 'rare cloth': 200000, 'runebook dye': 500000, 'accessory dye': 50000, 'headwear dye': 1200000, 'carpet dye': 50000, 'furniture dye': 800000, 'hair dye': 500000, 'facial hair dye': 400000, 'backpack dye': 300000, 'mount gear dye': 300000}, #Lustrous Carmine
    'Lustrous Seagrass':     {'hue': 4126, 'rare cloth': 120000, 'runebook dye': 200000, 'accessory dye': 20000, 'headwear dye': 600000, 'carpet dye': 25000, 'furniture dye': 300000, 'hair dye': 200000, 'facial hair dye': 150000, 'backpack dye': 100000, 'mount gear dye': 100000}, #Lustrous Seagrass
    'Lustrous Grass':        {'hue': 4127, 'rare cloth': 200000, 'runebook dye': 500000, 'accessory dye': 50000, 'headwear dye': 1200000, 'carpet dye': 50000, 'furniture dye': 800000, 'hair dye': 500000, 'facial hair dye': 400000, 'backpack dye': 300000, 'mount gear dye': 300000}, #Lustrous Grass
    'Lustrous Bottleglass':  {'hue': 4128, 'rare cloth': 120000, 'runebook dye': 200000, 'accessory dye': 20000, 'headwear dye': 600000, 'carpet dye': 25000, 'furniture dye': 300000, 'hair dye': 200000, 'facial hair dye': 150000, 'backpack dye': 100000, 'mount gear dye': 100000}, #Lustrous Bottleglass
    'Lustrous Star':         {'hue': 4129, 'rare cloth': 400000, 'runebook dye': 800000, 'accessory dye': 80000, 'headwear dye': 2400000, 'carpet dye': 80000, 'furniture dye': 500000, 'hair dye': 2000000, 'facial hair dye': 1700000, 'backpack dye': 2000000, 'mount gear dye': 1500000}, #Lustrous Star
    'Lustrous Dream':        {'hue': 4130, 'rare cloth': 400000, 'runebook dye': 800000, 'accessory dye': 80000, 'headwear dye': 2400000, 'carpet dye': 80000, 'furniture dye': 500000, 'hair dye': 2000000, 'facial hair dye': 1700000, 'backpack dye': 2000000, 'mount gear dye': 1500000}, #Lustrous Dream
    'Lustrous Ecru':         {'hue': 4131, 'rare cloth': 200000, 'runebook dye': 500000, 'accessory dye': 50000, 'headwear dye': 1200000, 'carpet dye': 50000, 'furniture dye': 800000, 'hair dye': 500000, 'facial hair dye': 400000, 'backpack dye': 300000, 'mount gear dye': 300000}, #Lustrous Ecru
    'Lustrous Chartreuse':   {'hue': 4132, 'rare cloth': 400000, 'runebook dye': 800000, 'accessory dye': 80000, 'headwear dye': 2400000, 'carpet dye': 80000, 'furniture dye': 500000, 'hair dye': 2000000, 'facial hair dye': 1700000, 'backpack dye': 2000000, 'mount gear dye': 1500000}, #Lustrous Chartreuse
    'Lustrous Caramel':      {'hue': 4133, 'rare cloth': 120000, 'runebook dye': 200000, 'accessory dye': 20000, 'headwear dye': 600000, 'carpet dye': 25000, 'furniture dye': 300000, 'hair dye': 200000, 'facial hair dye': 150000, 'backpack dye': 100000, 'mount gear dye': 100000}, #Lustrous Caramel
    'Lustrous Steel':        {'hue': 4134, 'rare cloth': 200000, 'runebook dye': 500000, 'accessory dye': 50000, 'headwear dye': 1200000, 'carpet dye': 50000, 'furniture dye': 800000, 'hair dye': 500000, 'facial hair dye': 400000, 'backpack dye': 300000, 'mount gear dye': 300000}, #Lustrous Steel
    'Lustrous Slime':        {'hue': 4135, 'rare cloth': 400000, 'runebook dye': 800000, 'accessory dye': 80000, 'headwear dye': 2400000, 'carpet dye': 80000, 'furniture dye': 500000, 'hair dye': 2000000, 'facial hair dye': 1700000, 'backpack dye': 2000000, 'mount gear dye': 1500000}, #Lustrous Slime
    'Lustrous Flesh':        {'hue': 4136, 'rare cloth': 500000, 'runebook dye': 1000000, 'accessory dye': 100000, 'headwear dye': 3000000, 'carpet dye': 100000, 'furniture dye': 700000, 'hair dye': 3000000, 'facial hair dye': 2500000, 'backpack dye': 2500000, 'mount gear dye': 2500000}, #Lustrous Flesh
    'Lustrous Opal':         {'hue': 4137, 'rare cloth': 500000, 'runebook dye': 1000000, 'accessory dye': 100000, 'headwear dye': 3000000, 'carpet dye': 100000, 'furniture dye': 700000, 'hair dye': 3000000, 'facial hair dye': 2500000, 'backpack dye': 2500000, 'mount gear dye': 2500000}, #Lustrous Opal
    'Lustrous Ash':          {'hue': 4138, 'rare cloth': 120000, 'runebook dye': 200000, 'accessory dye': 20000, 'headwear dye': 600000, 'carpet dye': 25000, 'furniture dye': 300000, 'hair dye': 200000, 'facial hair dye': 150000, 'backpack dye': 100000, 'mount gear dye': 100000}, #Lustrous Ash
    'Lustrous Jade':         {'hue': 4139, 'rare cloth': 120000, 'runebook dye': 200000, 'accessory dye': 20000, 'headwear dye': 600000, 'carpet dye': 25000, 'furniture dye': 300000, 'hair dye': 200000, 'facial hair dye': 150000, 'backpack dye': 100000, 'mount gear dye': 100000}, #Lustrous Jade
    'Lustrous Bone':         {'hue': 4139, 'rare cloth': 120000, 'runebook dye': 200000, 'accessory dye': 20000, 'headwear dye': 600000, 'carpet dye': 25000, 'furniture dye': 300000, 'hair dye': 200000, 'facial hair dye': 150000, 'backpack dye': 100000, 'mount gear dye': 100000}, #Lustrous Bone
    'Lustrous Dewdrop':      {'hue': 4141, 'rare cloth': 200000, 'runebook dye': 500000, 'accessory dye': 50000, 'headwear dye': 1200000, 'carpet dye': 50000, 'furniture dye': 800000, 'hair dye': 1000000, 'facial hair dye': 700000, 'backpack dye': 500000, 'mount gear dye': 300000}, #Lustrous Dewdrop
    'Arena Black':           {'hue': 2056, 'rare cloth': 500000,'runebook dye': 1000,  'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Arena Black
    'Strangelands':          {'hue': 2752, 'rare cloth': 40000, 'runebook dye': 1000,  'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Strangelands
    'Thief':                 {'hue': 1067, 'rare cloth': 90000, 'runebook dye': 1000,  'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Thief
    'Order':                 {'hue': 2452, 'rare cloth': 50000, 'runebook dye': 1000,  'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Order
    'Chaos':                 {'hue': 2719, 'rare cloth': 50000, 'runebook dye': 1000,  'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Chaos
    'Freedom':               {'hue': 2944, 'rare cloth': 50000, 'runebook dye': 1000,  'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Freedom
    'Corpse Creek Contest':  {'hue': 1197, 'rare cloth': 80000, 'runebook dye': 1000,  'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Corpse Creek Contest
    'Stygian Rifts':         {'hue': 1198, 'rare cloth': 150000,'runebook dye': 1000,  'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Stygian Rifts
    'Town Struggle':         {'hue': 1199, 'rare cloth': 50000, 'runebook dye': 1000,  'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Town Struggle
    'Dungeon Flashpoints':   {'hue': 1200, 'rare cloth': 80000, 'runebook dye': 1000,  'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Dungeon Flashpoints
    'Prevalia Faction':      {'hue': 1076, 'rare cloth': 1000,  'runebook dye': 1000,  'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Prevalia Faction
    'Andaria Faction':       {'hue': 1078, 'rare cloth': 1000,  'runebook dye': 1000,  'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Andaria Faction
    'Terran Faction':        {'hue': 1086, 'rare cloth': 1000,  'runebook dye': 1000,  'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Terran Faction
    'Cambria Faction':       {'hue': 1088, 'rare cloth': 1000,  'runebook dye': 1000,  'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Cambria Faction
    'Monster Hunter':        {'hue': 2817, 'rare cloth': 50000, 'runebook dye': 1000,  'accessory dye': 1000, 'headwear dye': 250000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Monster Hunter
    'Adventurer Lodge':      {'hue': 1918, 'rare cloth': 50000, 'runebook dye': 1000,  'accessory dye': 1000, 'headwear dye': 250000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Adventurer Lodge
    'Tradesman Union':       {'hue': 2765, 'rare cloth': 50000, 'runebook dye': 1000,  'accessory dye': 1000, 'headwear dye': 250000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Tradesman Union
    'Order of Armorers':     {'hue': 2915, 'rare cloth': 45000, 'runebook dye': 1000,  'accessory dye': 1000, 'headwear dye': 250000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Order of Armorers
    'Seafarer League':       {'hue': 2906, 'rare cloth': 50000, 'runebook dye': 1000,  'accessory dye': 1000, 'headwear dye': 250000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000}, #Seafarer League
    "Artificer's Enclave":   {'hue': 2875, 'rare cloth': 50000,  'runebook dye': 1000,  'accessory dye': 1000, 'headwear dye': 250000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000}, #s Enclave
    'Aegis Keep':            {'hue': 1779, 'rare cloth': 4000,  'runebook dye': 20000, 'accessory dye': 1000, 'headwear dye': 30000, 'carpet dye': 3000, 'furniture dye': 20000, 'hair dye': 30000, 'facial hair dye': 20000, 'backpack dye': 40000, 'mount gear dye': 3000}, #Aegis Keep
    'Inferno':               {'hue': 1909, 'rare cloth': 4000,  'runebook dye': 20000, 'accessory dye': 1000, 'headwear dye': 20000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 30000, 'facial hair dye': 25000, 'backpack dye': 50000, 'mount gear dye': 3000}, #Inferno
    'Ossuary':               {'hue': 2091, 'rare cloth': 4000,  'runebook dye': 20000, 'accessory dye': 500, 'headwear dye': 20000, 'carpet dye': 500, 'furniture dye': 20000, 'hair dye': 20000, 'facial hair dye': 20000, 'backpack dye': 30000, 'mount gear dye': 1000}, #Ossuary
    'Darkmire Temple':       {'hue': 2099, 'rare cloth': 4000,  'runebook dye': 20000, 'accessory dye': 1000, 'headwear dye': 20000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 25000, 'facial hair dye': 20000, 'backpack dye': 15000, 'mount gear dye': 1000}, #Darkmire Temple
    'Pulma':                 {'hue': 2085, 'rare cloth': 4000,  'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 20000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 80000, 'facial hair dye': 70000, 'backpack dye': 40000, 'mount gear dye': 3000}, #Pulma
    'Mausoleum':             {'hue': 2092, 'rare cloth': 4000,  'runebook dye': 20000, 'accessory dye': 1000, 'headwear dye': 20000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 50000, 'facial hair dye': 40000, 'backpack dye': 50000, 'mount gear dye': 3000}, #Mausoleum
    'Mount Petram':          {'hue': 2089, 'rare cloth': 4000,  'runebook dye': 15000, 'accessory dye': 1000, 'headwear dye': 20000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 20000, 'facial hair dye': 20000, 'backpack dye': 40000, 'mount gear dye': 1000}, #Mount Petram
    'Nusero':                {'hue': 2796, 'rare cloth': 3500,  'runebook dye': 15000, 'accessory dye': 500, 'headwear dye': 15000, 'carpet dye': 500, 'furniture dye': 15000, 'hair dye': 10000, 'facial hair dye': 5000, 'backpack dye': 25000, 'mount gear dye': 1000}, #Nusero
    'Cavernam':              {'hue': 2338, 'rare cloth': 18000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 120000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 300000, 'facial hair dye': 300000, 'backpack dye': 50000, 'mount gear dye': 5000}, #Cavernam
    'Shadowspire Cathedral': {'hue': 2093, 'rare cloth': 19000, 'runebook dye': 15000, 'accessory dye': 1250, 'headwear dye': 100000, 'carpet dye': 10000, 'furniture dye': 50000, 'hair dye': 40000, 'facial hair dye': 35000, 'backpack dye': 50000, 'mount gear dye': 5000}, #Shadowspire Cathedral
    'Wilderness':            {'hue': 1182, 'rare cloth': 3000,  'runebook dye': 15000, 'accessory dye': 500, 'headwear dye': 18000, 'carpet dye': 100, 'furniture dye': 15000, 'hair dye': 15000, 'facial hair dye': 15000, 'backpack dye': 25000, 'mount gear dye': 1000}, #Wilderness
    'Ocean':                 {'hue': 1183, 'rare cloth': 10000, 'runebook dye': 55000, 'accessory dye': 2000, 'headwear dye': 50000, 'carpet dye': 4000, 'furniture dye': 100000, 'hair dye': 70000, 'facial hair dye': 60000, 'backpack dye': 60000, 'mount gear dye': 4000}, #Ocean
    'Kraul Hive':            {'hue': 2841, 'rare cloth': 4000,  'runebook dye': 15000, 'accessory dye': 1000, 'headwear dye': 20000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 20000, 'facial hair dye': 20000, 'backpack dye': 40000, 'mount gear dye': 1000}, #Kraul Hive
    'Netherzone':            {'hue': 1500, 'rare cloth': 80000, 'runebook dye': 200000,  'accessory dye': 30000, 'headwear dye': 480000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 200000, 'facial hair dye': 150000, 'backpack dye': 150000, 'mount gear dye': 150000}, #Netherzone
    'Metallic Cherry':       {'hue': 2380, 'rare cloth': 35000, 'runebook dye': 40000, 'accessory dye': 6000, 'headwear dye': 200000, 'carpet dye': 4000, 'furniture dye': 50000, 'hair dye': 60000, 'facial hair dye': 50000, 'backpack dye': 100000, 'mount gear dye': 6000}, #Metallic Cherry
    'Metallic Orange':       {'hue': 1989, 'rare cloth': 9000, 'runebook dye': 50000, 'accessory dye': 4000, 'headwear dye': 50000, 'carpet dye': 3000, 'furniture dye': 40000, 'hair dye': 55000, 'facial hair dye': 45000, 'backpack dye': 80000, 'mount gear dye': 6000}, #Metallic Orange
    'Metallic Amber':        {'hue': 1990, 'rare cloth': 4000,  'runebook dye': 20000, 'accessory dye': 1000, 'headwear dye': 30000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 40000, 'facial hair dye': 30000, 'backpack dye': 50000, 'mount gear dye': 6000}, #Metallic Amber
    'Metallic Lemon-Lime':   {'hue': 2653, 'rare cloth': 4000,  'runebook dye': 20000, 'accessory dye': 1000, 'headwear dye': 30000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 20000, 'facial hair dye': 25000, 'backpack dye': 45000, 'mount gear dye': 6000}, #Metallic Lemon-Lime
    'Metallic Olive':        {'hue': 2398, 'rare cloth': 3000,  'runebook dye': 20000, 'accessory dye': 1000, 'headwear dye': 18000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 10000, 'facial hair dye': 10000, 'backpack dye': 50000, 'mount gear dye': 6000}, #Metallic Olive
    'Metallic Pickle':       {'hue': 2828, 'rare cloth': 7000,  'runebook dye': 30000, 'accessory dye': 2000, 'headwear dye': 30000, 'carpet dye': 3000, 'furniture dye': 20000, 'hair dye': 35000, 'facial hair dye': 25000, 'backpack dye': 35000, 'mount gear dye': 6000}, #Metallic Pickle
    'Metallic Juniper':      {'hue': 2845, 'rare cloth': 3000,  'runebook dye': 20000, 'accessory dye': 1000, 'headwear dye': 18000, 'carpet dye': 500, 'furniture dye': 2000, 'hair dye': 7000, 'facial hair dye': 7000, 'backpack dye': 40000, 'mount gear dye': 6000}, #Metallic Juniper
    'Metallic Mint':         {'hue': 2827, 'rare cloth': 3000,  'runebook dye': 20000, 'accessory dye': 1000, 'headwear dye': 18000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 10000, 'facial hair dye': 10000, 'backpack dye': 50000, 'mount gear dye': 6000}, #Metallic Mint
    'Metallic Sky':          {'hue': 2826, 'rare cloth': 3000,  'runebook dye': 20000, 'accessory dye': 1000, 'headwear dye': 18000, 'carpet dye': 2000, 'furniture dye': 20000, 'hair dye': 10000, 'facial hair dye': 10000, 'backpack dye': 50000, 'mount gear dye': 6000}, #Metallic Sky
    'Metallic Sapphire':     {'hue': 2379, 'rare cloth': 7000,  'runebook dye': 30000, 'accessory dye': 1000, 'headwear dye': 30000, 'carpet dye': 1000, 'furniture dye': 30000, 'hair dye': 30000, 'facial hair dye': 20000, 'backpack dye': 50000, 'mount gear dye': 6000}, #Metallic Sapphire
    'Metallic Cerulean':     {'hue': 1484, 'rare cloth': 6000,  'runebook dye': 40000, 'accessory dye': 1000, 'headwear dye': 30000, 'carpet dye': 1000, 'furniture dye': 30000, 'hair dye': 30000, 'facial hair dye': 30000, 'backpack dye': 50000, 'mount gear dye': 6000}, #Metallic Cerulean
    'Metallic Eggplant':     {'hue': 2898, 'rare cloth': 13000, 'runebook dye': 40000, 'accessory dye': 2500, 'headwear dye': 70000, 'carpet dye': 5000, 'furniture dye': 20000, 'hair dye': 35000, 'facial hair dye': 20000, 'backpack dye': 150000, 'mount gear dye': 6000}, #Metallic Eggplant
    'Metallic Raspberry':    {'hue': 1489, 'rare cloth': 4000,  'runebook dye': 20000, 'accessory dye': 1000, 'headwear dye': 30000, 'carpet dye': 2000, 'furniture dye': 20000, 'hair dye': 30000, 'facial hair dye': 20000, 'backpack dye': 50000, 'mount gear dye': 6000}, #Metallic Raspberry
    'Metallic Wine':         {'hue': 1995, 'rare cloth': 4000,  'runebook dye': 20000, 'accessory dye': 1000, 'headwear dye': 30000, 'carpet dye': 1000, 'furniture dye': 30000, 'hair dye': 30000, 'facial hair dye': 30000, 'backpack dye': 50000, 'mount gear dye': 6000}, #Metallic Wine
    'Metallic Pewter':       {'hue': 2167, 'rare cloth': 3000,  'runebook dye': 20000, 'accessory dye': 500, 'headwear dye': 18000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 10000, 'facial hair dye': 10000, 'backpack dye': 25000, 'mount gear dye': 6000}, #Metallic Pewter
    'Metallic Chalk':        {'hue': 2928, 'rare cloth': 3000,  'runebook dye': 20000, 'accessory dye': 500, 'headwear dye': 18000, 'carpet dye': 500, 'furniture dye': 20000, 'hair dye': 20000, 'facial hair dye': 20000, 'backpack dye': 50000, 'mount gear dye': 6000}, #Metallic Chalk
    'Metallic Umber':        {'hue': 1470, 'rare cloth': 3000,  'runebook dye': 20000, 'accessory dye': 500, 'headwear dye': 18000, 'carpet dye': 500, 'furniture dye': 20000, 'hair dye': 10000, 'facial hair dye': 10000, 'backpack dye': 25000, 'mount gear dye': 6000}, #Metallic Umber
    'Dark Coffee':           {'hue': 1467, 'rare cloth': 45000, 'runebook dye': 25000, 'accessory dye': 2000, 'headwear dye': 240000, 'carpet dye': 5000, 'furniture dye': 60000, 'hair dye': 45000, 'facial hair dye': 40000, 'backpack dye': 200000, 'mount gear dye': 6000}, #Dark Coffee
    'Dark Rust':             {'hue': 2807, 'rare cloth': 2500,  'runebook dye': 20000, 'accessory dye': 500, 'headwear dye': 15000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 8000, 'facial hair dye': 7000, 'backpack dye': 40000, 'mount gear dye': 6000}, #Dark Rust
    'Dark Crimson':          {'hue': 1939, 'rare cloth': 2000,  'runebook dye': 20000, 'accessory dye': 1000, 'headwear dye': 20000, 'carpet dye': 1000, 'furniture dye': 30000, 'hair dye': 10000, 'facial hair dye': 10000, 'backpack dye': 40000, 'mount gear dye': 6000}, #Dark Crimson
    'Dark Blood':            {'hue': 1465, 'rare cloth': 4000,  'runebook dye': 20000, 'accessory dye': 1000, 'headwear dye': 20000, 'carpet dye': 4000, 'furniture dye': 30000, 'hair dye': 10000, 'facial hair dye': 10000, 'backpack dye': 40000, 'mount gear dye': 6000}, #Dark Blood
    'Dark Salmon':           {'hue': 2174, 'rare cloth': 3000,  'runebook dye': 20000, 'accessory dye': 500, 'headwear dye': 18000, 'carpet dye': 500, 'furniture dye': 20000, 'hair dye': 10000, 'facial hair dye': 10000, 'backpack dye': 40000, 'mount gear dye': 6000}, #Dark Salmon
    'Dark Forest':           {'hue': 2804, 'rare cloth': 3000,  'runebook dye': 20000, 'accessory dye': 500, 'headwear dye': 18000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 10000, 'facial hair dye': 10000, 'backpack dye': 40000, 'mount gear dye': 6000}, #Dark Forest
    'Dark Peacock':          {'hue': 2226, 'rare cloth': 3000,  'runebook dye': 20000, 'accessory dye': 500, 'headwear dye': 18000, 'carpet dye': 2500, 'furniture dye': 30000, 'hair dye': 10000, 'facial hair dye': 10000, 'backpack dye': 40000, 'mount gear dye': 6000}, #Dark Peacock
    'Dark Denim':            {'hue': 2801, 'rare cloth': 3000,  'runebook dye': 20000, 'accessory dye': 1000, 'headwear dye': 18000, 'carpet dye': 1000, 'furniture dye': 30000, 'hair dye': 6000, 'facial hair dye': 6000, 'backpack dye': 40000, 'mount gear dye': 6000}, #Dark Denim
    'Dark Blueberry':        {'hue': 1156, 'rare cloth': 3000,  'runebook dye': 20000, 'accessory dye': 500, 'headwear dye': 18000, 'carpet dye': 1000, 'furniture dye': 30000, 'hair dye': 10000, 'facial hair dye': 10000, 'backpack dye': 40000, 'mount gear dye': 6000}, #Dark Blueberry
    'Dark Jam':              {'hue': 2230, 'rare cloth': 40000, 'runebook dye': 50000, 'accessory dye': 4000, 'headwear dye': 260000, 'carpet dye': 15000, 'furniture dye': 80000, 'hair dye': 65000, 'facial hair dye': 60000, 'backpack dye': 120000, 'mount gear dye': 6000}, #Dark Jam
    'Powder Ruby':           {'hue': 2227, 'rare cloth': 70000,'runebook dye': 65000, 'accessory dye': 20000, 'headwear dye': 540000, 'carpet dye': 10000, 'furniture dye': 170000, 'hair dye': 200000, 'facial hair dye': 200000, 'backpack dye': 500000, 'mount gear dye': 6000}, #Powder Ruby
    'Powder Coral':          {'hue': 1495, 'rare cloth': 20000, 'runebook dye': 30000, 'accessory dye': 7000, 'headwear dye': 150000, 'carpet dye': 8000, 'furniture dye': 100000, 'hair dye': 50000, 'facial hair dye': 40000, 'backpack dye': 150000, 'mount gear dye': 6000}, #Powder Coral
    'Powder Peach':          {'hue': 1496, 'rare cloth': 14000, 'runebook dye': 30000, 'accessory dye': 8000, 'headwear dye': 150000, 'carpet dye': 2000, 'furniture dye': 100000, 'hair dye': 50000, 'facial hair dye': 40000, 'backpack dye': 140000, 'mount gear dye': 6000}, #Powder Peach
    'Powder Lemon':          {'hue': 1382, 'rare cloth': 65000, 'runebook dye': 50000, 'accessory dye': 15000, 'headwear dye': 500000, 'carpet dye': 8000, 'furniture dye': 100000, 'hair dye': 300000, 'facial hair dye': 200000, 'backpack dye': 500000, 'mount gear dye': 6000}, #Powder Lemon
    'Powder Pistachio':      {'hue': 1494, 'rare cloth': 20000, 'runebook dye': 30000, 'accessory dye': 5000, 'headwear dye': 120000, 'carpet dye': 4000, 'furniture dye': 100000, 'hair dye': 65000, 'facial hair dye': 55000, 'backpack dye': 100000, 'mount gear dye': 6000}, #Powder Pistachio
    'Powder Seafoam':        {'hue': 2246, 'rare cloth': 30000, 'runebook dye': 30000, 'accessory dye': 5000, 'headwear dye': 160000, 'carpet dye': 4000, 'furniture dye': 80000, 'hair dye': 65000, 'facial hair dye': 55000, 'backpack dye': 150000, 'mount gear dye': 6000}, #Powder Seafoam
    'Powder Spring':         {'hue': 1381, 'rare cloth': 30000, 'runebook dye': 30000, 'accessory dye': 15000, 'headwear dye': 160000, 'carpet dye': 9000, 'furniture dye': 100000, 'hair dye': 150000, 'facial hair dye': 200000, 'backpack dye': 150000, 'mount gear dye': 6000}, #Powder Spring
    'Powder Lapis':          {'hue': 2255, 'rare cloth': 55000, 'runebook dye': 80000, 'accessory dye': 15000, 'headwear dye': 330000, 'carpet dye': 5000, 'furniture dye': 100000, 'hair dye': 200000, 'facial hair dye': 150000, 'backpack dye': 150000, 'mount gear dye': 6000}, #Powder Lapis
    'Powder Cyan':           {'hue': 2877, 'rare cloth': 40000, 'runebook dye': 30000, 'accessory dye': 5000, 'headwear dye': 220000, 'carpet dye': 5000, 'furniture dye': 75000, 'hair dye': 100000, 'facial hair dye': 100000, 'backpack dye': 150000, 'mount gear dye': 6000}, #Powder Cyan
    'Powder Azure':          {'hue': 1384, 'rare cloth': 160000,'runebook dye': 80000, 'accessory dye': 20000, 'headwear dye': 1200000, 'carpet dye': 8000, 'furniture dye': 100000, 'hair dye': 550000, 'facial hair dye': 600000, 'backpack dye': 500000, 'mount gear dye': 6000}, #Powder Azure
    'Powder Orchid':         {'hue': 1462, 'rare cloth': 52000, 'runebook dye': 30000, 'accessory dye': 10000, 'headwear dye': 330000, 'carpet dye': 5000, 'furniture dye': 80000, 'hair dye': 160000, 'facial hair dye': 200000, 'backpack dye': 200000, 'mount gear dye': 6000}, #Powder Orchid
    'Powder Iris':           {'hue': 2173, 'rare cloth': 400000,'runebook dye': 100000,'accessory dye': 35000, 'headwear dye': 2400000, 'carpet dye': 20000, 'furniture dye': 200000, 'hair dye': 900000, 'facial hair dye': 900000, 'backpack dye': 500000, 'mount gear dye': 6000}, #Powder Iris
    'Powder Cloud':          {'hue': 2903, 'rare cloth': 190000,'runebook dye': 80000, 'accessory dye': 20000, 'headwear dye': 1000000, 'carpet dye': 9000, 'furniture dye': 100000, 'hair dye': 900000, 'facial hair dye': 900000, 'backpack dye': 900000, 'mount gear dye': 6000}, #Powder Cloud
    'Powder Blush':          {'hue': 2808, 'rare cloth': 35000, 'runebook dye': 30000, 'accessory dye': 13000, 'headwear dye': 190000, 'carpet dye': 5000, 'furniture dye': 80000, 'hair dye': 100000, 'facial hair dye': 100000, 'backpack dye': 500000, 'mount gear dye': 6000}, #Powder Blush
    'Powder Bubblegum':      {'hue': 1952, 'rare cloth': 100000,'runebook dye': 50000, 'accessory dye': 40000, 'headwear dye': 600000, 'carpet dye': 18000, 'furniture dye': 250000, 'hair dye': 550000, 'facial hair dye': 500000, 'backpack dye': 500000, 'mount gear dye': 6000}, #Powder Bubblegum
}

misc_crafting_prices = { #https://outlandmalls.com/?item=&search_category_id=21&search_sub_category_id=98
    "pristine lumber": 40000, 
    "immaculate stone": 50000,
    "an arcane scroll": 1000,
    "research materials (double-click to research)": 37000,
    "mastercrafting diagram": 20000,
    "cleansing brew": 1500,
    "amber": 48,
    "amethyst": 60,
    "citrine": 23,
    "diamond": 120,
    "emerald": 95,
    "ruby": 72,
    "sapphire": 84,
    "star sapphire": 109,
    "tourmaline": 34,
}

misc_hp_prices = { #exact string matters
    "a skill mastery orb (used to increase a player's total skill cap by 1)": 18000, #a skill mastery orb : 3 (used to increase a player's total skill cap by 1)
    "plant chemicals": 2500,
    "prevalia coins [blessed]": 17000, #prevalia coins : 5 [blessed]
    "a chromatic core": 75000,
    "chromatic distillation": 10000,
    "time dungeon lore page": 80000,

}

misc_lp_prices = { #exact string matters
    #"exceedingly potent magic spellbook": 3500,
    #"supremely potent magic spellbook": 13000,
    "an ankh token": 11000,
    "arcane essence": 37,
    "an emote deed": 200000,
    "redlightning bottle": 40000,
    "survival gear": 37000,
    "a battle commendation (double-click to consume and receive reward item)": 11000,
    "invulnerability leather cap": 95000,
    "dyeable gilded gold carpet tile": 23000,
    "Aspect Triumph": 1000000,
    "bloody skull pile": 400000,
    "a storage shelf": 400000,
    "a repair bench": 475000,
}

clothing_prices = { #TODO
    "butterfly colombina": 500000,
    "masquerade gown": 500000,
}

ship_upgrade_prices = { #TODO
    "destroyer outfitting": 600000,
    "dreadnought Outfitting": 600000,
    "explosive ammo lesser ability": 200000,
    "fearsome totem specialty item": 200000,
    "flak cannons greater ability": 1800000,
    "gorgon figurehead specialty item": 800000,
    "hellfire barrage greater ability": 500000,
    "icebreaker ammo greater ability": 1000000,
    "medium weaponry crew supplies": 800000,
    "powder carts specialty item": 700000,
    "powder specialty item ship": 700000,
    "powdersoak ammo regular ability": 200000,
    "routine maintenance specialty item": 200000,
    "rum rations greater ability": 200000,
    "signal pigeons specialty item": 1000000,
    "silk hammocks crew supplies": 200000,
    "smoke bombs crew supplies": 1500000,
    "smoothbore cannonshot specialty item": 900000,
    "stacked powderkegs specialty item": 600000,
    "stockade crew supplies ship": 200000,
    "storage lockers specialty item": 400000,
}

deed_prices = {
    "strongbox customization unlock deed [blessed] (used to unlock 'Strongbox' customization)": 2000000,
    "a clothing bless deed": 200000,
}

self_parse_extra_prices = { 
    "Aspect Triumph": 1000000,
    "special fishing net": 4000,
    "an emote deed": 200000,
}

self_parse_extra_aliases = {
    "tome": 175000,
    "mount token": 1900000,
    "lore page /15": 30000,
    "lore page /10": 35000,
    "lustrous totem": 300000,
    "harvest antiquity": 200000,
    "crafting antiquity": 200000,
    "portrait painting antiquity": 200000,
    "landscape painting antiquity": 200000,
    "large painting antiquity": 700000,
    "thief antiquity": 1000000,
    "battle antiquity": 1000000,
    "ocean antiquity": 1000000,
    "chest antiquity": 1000000,
    "invulnerability studded": 5000,
    "invulnerability platemail": 50000,
    "fortification platemail": 50000,
    
}

self_parse_antiquities_prices = {
    "hourglass table": 700000,
}

my_locations = {
    # Alpha
    "N Cambria Gate": (1706,3129, ('a lost girl',2093,200,10)),
    "SE Cambria Gate": (1753,3176, ('a lost girl',2093,201,20)),
    "S Cambria Gate": (1709,3182, ('a lost girl',2093,202,10)),
    "SW Cambria Gate": (1669,3177, ('a lost girl',2093,203,20)),
    "NW Cambria Gate": (1670,3138, ('a lost girl',2093,204,10)),
    "N Outpost Gate": (2980,579, ('a lost girl',2093,205,20)),
    "N Outpost Gate 2": (2976,555, ('a lost girl',2093,206,10)),
    "N Outpost Gate 3": (3001,496, ('a lost girl',2093,207,20)),
    "N Outpost Gate 4": (3061,475, ('a lost girl',2093,208,10)),
    "NW Outpost Gate": (2940,563, ('a lost girl',2093,209,20)),
    "NE Outpost Close": (3390,380, ('a lost girl',2093,210,10)),
    "NE Outpost Close 2":(3364,408, ('a lost girl',2093,211,20)), 
    "NE Outpost Far": (3406,165, ('a lost girl',2093,212,10)),

    "N of GH":(3886,744, ('a lost girl',2093,213,20)),
    "Frozen Ruins SW":(1546,753, ('a lost girl',2093,214,10)),
    "Winterlands VM":(3968,51, ('a lost girl',2093,215,20)),
    "N of Andaria":(2002,547, ('a lost girl',2093,216,10)),
    "N Andaria Gate": (2334,591, ('a lost girl',2093,217,20)),
    "W Andaria Gate": (2315,639, ('a lost girl',2093,218,10)), 
    "Minotaur Island": (3967,1736, ('a lost girl',2093,219,20)),
    "Minotaur Island E": (4067,1766, ('a lost girl',2093,220,10)),
    "N Terran Clearing": (879,1382, ('a lost girl',2093,221,20)),
    "S Terran Clearing": (930,1473, ('a lost girl',2093,222,10)),
    "SW Terran Clearing": (896,1525, ('a lost girl',2093,223,20)),
    "TRT N":(1732,2321, ('a lost girl',2093,224,10)),
    "TRT":(1759,2351, ('a lost girl',2093,225,20)),
    
    # Bravo
    "AR1": (3946,565, ('Aproctoflecticus',1156,200,10)),
    "AR2": (3947,496, ('Aproctoflecticus',1156,201,20)),
    "AR3": (3961,553, ('Aproctoflecticus',1156,202,10)),
    "AR4": (3962,456, ('Aproctoflecticus',1156,203,20)), 
    "AR5": (3976,585, ('Aproctoflecticus',1156,204,10)),
    "AR6": (3978,493, ('Aproctoflecticus',1156,205,20)), 
    "AR7": (4001,555, ('Aproctoflecticus',1156,206,10)),
    "AR8": (3993,460, ('Aproctoflecticus',1156,207,20)),
    "AR9": (4009,589, ('Aproctoflecticus',1156,208,10)),
    "AR10": (4010,497, ('Aproctoflecticus',1156,209,20)),
    "AR11": (4032,525, ('Aproctoflecticus',1156,210,10)),
    "AR12": (4026,462, ('Aproctoflecticus',1156,211,20)),
    "AR14": (4041,495, ('Aproctoflecticus',1156,212,10)),

    "AR15": (4055,448, ('Aproctoflecticus',1156,213,20)),
    "AR16": (4069,538, ('Aproctoflecticus',1156,214,10)),
    "AR17": (4071,510, ('Aproctoflecticus',1156,215,20)),
    "AR18": (4071,472, ('Aproctoflecticus',1156,216,10)),
    "S of Pulma": (1780,1048, ('Aproctoflecticus',1156,217,20)),
    "S of Pulma 2":(1739,1059, ('Aproctoflecticus',1156,218,10)),
    "Shelter Haven": (1588,2550, ('Aproctoflecticus',1156,219,20)),
    "Frozen Ruins NW":(1453,631, ('Aproctoflecticus',1156,220,10)),
    "NE Frozen Waypost":(1759,633, ('Aproctoflecticus',1156,221,20)),
    "Western Camp Island": (3489,1451, ('Aproctoflecticus',1156,222,10)),
    "Far S Prev W":(1765,1740, ('Aproctoflecticus',1156,223,20)),
    "Tofy's Casino":(3446,178, ('Aproctoflecticus',1156,224,10)),
    "AR19": (4071,600,('Aproctoflecticus',1156,225,20)),

    # Charlie
    "N Prev Sandbar": (1667,1318, ('Vendor Police',2089,200,10)),
    "N Prev Clearing N": (1592,1388, ('Vendor Police',2089,201,20)),
    "N Prev Clearing E": (1629,1421, ('Vendor Police',2089,202,10)), 
    "N Prev Clearing Mid": (1596,1419, ('Vendor Police',2089,203,20)),
    "N Prev Clearing S": (1571,1439, ('Vendor Police',2089,204,10)),
    "N Prev Clearing SW": (1554,1439, ('Vendor Police',2089,205,20)),
    "N Prev Clearing W": (1556,1419, ('Vendor Police',2089,206,10)),
    "E of Prev": (2036,1463, ('Vendor Police',2089,207,20)),
    "Khal SE Prev N": (2002,1786, ('Vendor Police',2089,209,10)),
    "Khal SE Prev S": (1980,1825, ('Vendor Police',2089,209,20)),
    "S Prev Xroad N": (1552,1735, ('Vendor Police',2089,210,10)),
    "S Prev Xroad E": (1653,1743, ('Vendor Police',2089,211,20)),
    "S Prev Xroad S": (1545,1772, ('Vendor Police',2089,212,10)),

    "S Prev Xroad NW": (1526,1748, ('Vendor Police',2089,213,20)), #1533 1752
    "S Prev Xroad W": (1499,1757, ('Vendor Police',2089,214,10)),
    "SW Prev Clearing NE 1": (1532,1639, ('Vendor Police',2089,215,20)),
    "SW Prev Clearing SE": (1547,1653, ('Vendor Police',2089,216,10)),
    "SW Prev Clearing SW": (1510,1657, ('Vendor Police',2089,217,20)),
    "SW Prev Clearing NW": (1473,1580, ('Vendor Police',2089,218,10)),
    "Prev Gate": (1475,1488, ('Vendor Police',2089,219,20)),
    "W of SSC": (3267,689,('Vendor Police',2089,220,10)), #!
    "Far N of Anchor's Rest": (3693,285, ('Vendor Police',2089,221,20)), 
    "N of Anchor's Rest": (3751,351, ('Vendor Police',2089,222,10)),
    "S of Anchor's Rest 2": (3752,671, ('Vendor Police',2089,223,20)),
    "Far S Anchor's Rest": (3715,872, ('Vendor Police',2089,224,10)),
    "E of GH": (3976,853, ('Vendor Police',2089,225,20)),

    # Delta
    "N Terran Clearing 2":(905,1387,('Misc1',1989,200,10)),
    "SW Terran Clearing 2":(887,1499,('Misc1',1989,201,20)),
    "Pwnstar":(4218,1090,('Misc1',1989,202,10)),
    "AR13": (4037,591,('Misc1',1989,203,20)),
    "Far N Andaria Gate": (2362,564,('Misc1',1989,204,10)),#2368 546
    "Terran Clearing West": (893,1486, ('Misc1',1989,205,20)),
    "Winterspire":(3571,198,('Misc1',1989,206,10)),
    "Frozen Waypost":(1650,682,('Misc1',1989,207,20)),
    "W of Cambria Entrance":(1662,2988,('Misc1',1989,208,10)),
    "Wildside":(1263,1321,('Misc1',1989,209,20)),
    "S of TRT": (1778,2389,('Misc1',1989,210,10)),
    "S Prev Xroad N 2": (1606,1739, ('Misc1',1989,211,20)),
    "Far SE Cambria Gate": (1794,3172, ('Misc1',1989,212,10)),

    "HSB W": (1916,2261, ('Misc1',1989,213,20)),
    "HSB N": (1961,2090, ('Misc1',1989,214,10)),
    "HSB Gate": (2014,2047, ('Misc1',1989,215,20)),
    "E of HSB": (2229,2337,('Misc1',1989,216,10)),
    "NE Outpost Mid": (3406,289,('Misc1',1989,217,20)),
    "Syn Keep": (4056,325,('Misc1',1989,218,10)), #4057 338
    "NE Outpost Far NW": (3252,294,('Misc1',1989,219,20)),
    "Illuminated Spring": (3843,795,('Misc1',1989,220,10)), 
    "SW of Harpies":(1847,2106,('Misc1',1989,221,20)),
    "Farming Finds":(1436,1029,('Misc1',1989,222,10)),
    "W of Urukton":(1899,1163,('Misc1',1989,223,20)),
    "Ugly Bridge": (1329,1097,('Misc1',1989,224,10)),
    "SE Terran Clearing": (966,1448,('Misc1',1989,225,20)),
    
    # Echo
    "W of Prev Gate":(1425,1483,('Misc2',2828,200,10)),
    "Cedar Island Center":(4027,305,('Misc2',2828,201,20)),
    "Cedar Island Mall":(3985,349,('Misc2',2828,202,10)),
    "E Andaria Gate":(2398,648,('Misc2',2828,203,20)),
    "Frost Forest":(3622,447,('Misc2',2828,204,10)),
    "Terran Gate":(885,1573,('Misc2',2828,205,20)),
    "S Prev Xroad Far S":(1531,1833,('Misc2',2828,206,10)),
    "N Prev Sandbar W":(1551,1315,('Misc2',2828,207,20)),
    "NE Cambria Gate":(1746,3139,('Misc2',2828,208,10)),
    "81 Xroad":(1262,1904,('Misc2',2828,209,20)),
    "S Prev Xroad 2":(1470,1758,('Misc2',2828,210,10)),
    "China Town":(3402,349,('Misc2',2828,211,20)),
    "Illuminated Spring 2":(3912,798,('Misc2',2828,212,10)),
    
    "N Terran Clearing 3":(854,1337,('Misc2',2828,213,20)),
    "Riverrun Lodge":(2785,529,('Misc2',2828,214,10)),
    "N of Ice Prison":(3966,53,('Misc2',2828,215,20)),
    "Mid Terran Clearing":(912,1414,('Misc2',2828,216,10)),
    "NW of Pwnstar":(4153,1044,('Misc2',2828,217,20)),
    "NW of GH":(3782,753,('Misc2',2828,218,10)),
    "PEC on the Water":(1298,1998,('Misc2',2828,219,20)),
    "S Anchor's Rest W":(3678,701,('Misc2',2828,220,10)),
    "N Prev Sandbar Far W":(1425,1343,('Misc2',2828,221,20)),
    "Far S of Pulma":(1791,1138,('Misc2',2828,222,10)),
    "SW of Cavernam":(2668,487,('Misc2',2828,223,20)),
    "NW of Cambria":(1570,2852,('Misc2',2828,224,10)), #TODO exchange out
    "S Prevalia Beach":(2028,1738,('Misc2',2828,225,20)),





    # Foxtrot
    "Totem Gate E1":(3931,2799,('TomeFoxtrot',2091,200,10)),
    "Totem Gate NE1":(3942,2758,('TomeFoxtrot',2091,201,20)),
    "Totem Gate S1":(3912,2821,('TomeFoxtrot',2091,202,10)),
    "Totem Gate S2":(3910,2840,('TomeFoxtrot',2091,203,20)),
    "Totem Gate W1":(3848,2769,('TomeFoxtrot',2091,204,10)),
    "Totem Gate NW1":(3867,2728,('TomeFoxtrot',2091,205,20)),
    "S of Totem":(3852,2943,('TomeFoxtrot',2091,206,10)),
    "Totem Gate Gate Far S":(3917,2939,('TomeFoxtrot',2091,207,20)),
    "Totem Gate E2":(3952,2824,('TomeFoxtrot',2091,208,10)),
    "Totem Camp":(3936,2915,('TomeFoxtrot',2091,209,20)),
    "Burnt Sage SE":(3932,3036,('TomeFoxtrot',2091,210,10)),
    "Totem Tower":(3883,2855,('TomeFoxtrot',2091,211,20)),
    "Totem Gate SW1":(3859,2818,('TomeFoxtrot',2091,212,10)),
    
    "Jungle Junction":(4228,2642,('TomeFoxtrot',2091,213,20)),
    "N Bivouac":(3405,3097,('TomeFoxtrot',2091,214,10)),
    "Abandoned Island":(4344,2850,('TomeFoxtrot',2091,215,20)),
    "W of Totem":(3797,2916,('TomeFoxtrot',2091,216,10)),
    "Dragonfire Ring":(3815,2492,('TomeFoxtrot',2091,217,20)),
    "N of Fishkill":(4129,2180,('TomeFoxtrot',2091,218,10)),
    "Totem Gate N1":(3892,2777,('TomeFoxtrot',2091,219,20)),
    "NE of Ossuary Demon":(1343,2746,('TomeFoxtrot',2091,220,10)),
    "N of Rope Swing":(3940,3411,('TomeFoxtrot',2091,221,20)),
    "SW Terran Clearing 2":(877,1500,('TomeFoxtrot',2091,222,10)),
    "W of Jungle Junction":(4141,2743,('TomeFoxtrot',2091,223,20)),
    "S Prev Xroad E2":(1704,1743,('TomeFoxtrot',2091,224,10)),
    "NE Outpost Close 3":(3391,359,('TomeFoxtrot',2091,225,20)),

    # Gulf
    "Mana Isles 2":(3528,3182,('TomeGulf',1779,200,10)),
    "SW Prev Clearing NE 2":(1560,1628,('TomeGulf',1779,201,20)),
    "placeholder":(0,0,('TomeGulf',1779,202,10)),
    "placeholder":(0,0,('TomeGulf',1779,203,20)),
    "placeholder":(0,0,('TomeGulf',1779,204,10)),
    "placeholder":(0,0,('TomeGulf',1779,205,20)),
    "placeholder":(0,0,('TomeGulf',1779,206,10)),
    "placeholder":(0,0,('TomeGulf',1779,207,20)),
    "placeholder":(0,0,('TomeGulf',1779,208,10)),
    "placeholder":(0,0,('TomeGulf',1779,209,20)),
    "placeholder":(0,0,('TomeGulf',1779,210,10)),
    "placeholder":(0,0,('TomeGulf',1779,211,20)),
    "placeholder":(0,0,('TomeGulf',1779,212,10)),
    
    "placeholder":(0,0,('TomeGulf',1779,213,20)),
    "placeholder":(0,0,('TomeGulf',1779,214,10)),
    "placeholder":(0,0,('TomeGulf',1779,215,20)),
    "placeholder":(0,0,('TomeGulf',1779,216,10)),
    "placeholder":(0,0,('TomeGulf',1779,217,20)),
    "placeholder":(0,0,('TomeGulf',1779,218,10)),
    "placeholder":(0,0,('TomeGulf',1779,219,20)),
    "placeholder":(0,0,('TomeGulf',1779,220,10)),
    "placeholder":(0,0,('TomeGulf',1779,221,20)),
    "placeholder":(0,0,('TomeGulf',1779,222,10)),
    "placeholder":(0,0,('TomeGulf',1779,223,20)),
    "placeholder":(0,0,('TomeGulf',1779,224,10)),
    "placeholder":(0,0,('TomeGulf',1779,225,20)),

    # Wide Reach 1183
    "Mana Isles":(3546,3274,('Wide Reach',1183,200,10)),
    "Ashenmire":(3626,3515,('Wide Reach',1183,201,20)),
    "Bivouac":(3469,3195,('Wide Reach',1183,202,10)),
    "S of Papua":(3729,3195,('Wide Reach',1183,203,20)),
    "Wildflower Highlands":(4026,3149,('Wide Reach',1183,204,10)),
    "Whisperwood":(4012,3015,('Wide Reach',1183,205,20)),
    "Flower Shop":(4325,1178,('Wide Reach',1183,206,10)),
    "Whisperwood Cottage":(4115,2952,('Wide Reach',1183,207,20)),
    "placeholder":(0,0,('Wide Reach',1183,208,10)),
    "placeholder":(0,0,('Wide Reach',1183,209,20)),
    "placeholder":(0,0,('Wide Reach',1183,210,10)),
    "placeholder":(0,0,('Wide Reach',1183,211,20)),
    "placeholder":(0,0,('Wide Reach',1183,212,10)),
    
    "placeholder":(0,0,('Wide Reach',1183,213,20)),
    "placeholder":(0,0,('Wide Reach',1183,214,10)),
    "placeholder":(0,0,('Wide Reach',1183,215,20)),
    "placeholder":(0,0,('Wide Reach',1183,216,10)),
    "placeholder":(0,0,('Wide Reach',1183,217,20)),
    "placeholder":(0,0,('Wide Reach',1183,218,10)),
    "placeholder":(0,0,('Wide Reach',1183,219,20)),
    "placeholder":(0,0,('Wide Reach',1183,220,10)),
    "placeholder":(0,0,('Wide Reach',1183,221,20)),
    "placeholder":(0,0,('Wide Reach',1183,222,10)),
    "placeholder":(0,0,('Wide Reach',1183,223,20)),
    "placeholder":(0,0,('Wide Reach',1183,224,10)),
    "placeholder":(0,0,('Wide Reach',1183,225,20)),


    # Unassigned 
    "Asura's Shop":(1197,2851,('Unlisted',0,0,0)),
    "MyKruelz":(1634,1136,('Unlisted',0,0,0)),
    "N of Pwnstar":(4207,1026,('Unlisted',0,0,0)),
    "S Terran Clearing Tip": (944,1531,('Unlisted',0,0,0)),

    "Dirty Dom": (3787,941, ('Unlisted',0,0,0)),
    "ICE River": (3827,242, ('Unlisted',0,0,0)), #
    "East of Hidden Valley": (1502,2944, ('Unlisted',0,0,0)),

    "Far S Prev SW":(1730,1782, ('Unlisted',0,0,0)),
    "SOF Island Mall": (3571,198,('Unlisted',0,0,0)),
    "JSHINE": (4224,1055, ('Unlisted',0,0,0)),
    "Frozen Ruins SE":(1612,780, ('Unlisted',0,0,0)),

}

aspect_hues = {
        "Air": 2263,
        "Arcane": 1560,
        "Artisan": 2096,
        "Blood": 2087,
        "Command": [1428,1782],
        "Death": 2155,
        "Discipline": 2490,
        "Earth": 2767,
        "Eldritch": [2618,2615],
        "Fire": 2635,
        "Fortune": 2843,
        "Frost": 2234,
        "Gadget": 2669,
        "Harvest": [2208,2086],
        "Holy": 2153,
        "Lightning": 2650,
        "Lyric": 2241,
        "Madness": 1060,
        "Poison": 2897,
        "Shadow": [1757,1790],
        "Void": [2582, 2599],
        "War": 2503,
        "Water": [2592, 1788],
}

scroll_hues = {
    "alchemy": 2291,
    "animal lore": 2479,
    "animal taming": 2479,
    "arms lore": 2722,
    "begging": 2642,
    "blacksmithy": 2291,
    "camping": 2722,
    "carpentry": 2291,
    "cartography": 2768,
    "chivalry": 2810,
    "cooking": 2291,
    "detect hidden": 2768,
    "discordance": 2735,
    "fishing": 2564,
    "forensic eval": 2722,
    "herding": 2479,
    "inscription": 2291,
    "item id": 2642,
    "lockpicking": 2768,
    "lumberjacking": 2564,
    "mining": 2564,
    "musicianship": 2735,
    "necromancy": 2810,
    "peacemaking": 2735,
    "poisoning": 2291,
    "provocation": 2735,
    "spirit speak": 2722,
    "stealth": 2642,
    "tailoring": 2291,
    "taste id": 2642,
    "tinkering": 2291,
    "tracking": 2722,
    "veterinary": 2479,
}


def get_misc_price_list():
    stock_misc = [
        "a skill mastery orb (used to increase a player's total skill cap by 1)",
        "plant chemicals",
        "dyeable gilded gold carpet tile",
        "pristine lumber",
        "immaculate stone",
        "an arcane scroll",
        "mastercrafting diagram",
        "prevalia coins [blessed]",
        "arcane essence",
    ]
    misc_all_prices = dict(ChainMap(misc_lp_prices, misc_hp_prices, misc_crafting_prices))
    misc_prices = {}

    for item in stock_misc:
        misc_prices[item] = misc_all_prices[item]

    return misc_prices


def calculate_grid_coordinates(start_xy, end_xy, row_col):
    start_x, start_y = start_xy
    end_x, end_y = end_xy
    row, col = row_col
    x_space = end_x - start_x
    y_space = end_y - start_y

    x_spacing = max(x_space // col, 1)
    y_spacing = max(y_space // row, 1)

    coordinates = []

    for y in range(start_y, end_y + 1, y_spacing):
        for x in range(start_x, end_x + 1, x_spacing):
            coordinates.append((x, y))
    return coordinates


# start_xy = (44, 105)
# end_xy = (164, 120)
# row_col = (1,24)
# grid_coordinates = calculate_grid_coordinates(start_xy, end_xy, row_col)

# print(grid_coordinates)

def get_inventory_data_dict(sorted_category_dict):
    transformer = {
        "aspect cores": "Cores",
        "distillation": "Distils",
        "skill mastery scroll": "Skill Mastery Scrolls",
        "llorcs yretsam lliks": "Skill Mastery Scrolls",
    }
    extracted_inventory_data_dict = {}
    for category, item_dict in sorted_category_dict.items():
        for item_name,item_data in item_dict.items():
            extracted_inventory_data_dict[item_name] = tuple([tup[2] if len(tup) > 1 else 0 for tup in item_data])
    
    return extracted_inventory_data_dict


def pretty_print(data, indent=0):
    if isinstance(data, dict):
        for key, value in data.items():
            print(' ' * indent + str(key) + ':')
            pretty_print(value, indent + 4)
    elif isinstance(data, list) and all(isinstance(i, list) for i in data):
        print(' ' * indent + '[\n' + ',\n'.join(' ' * (indent + 4) + str(sublist) for sublist in data) + '\n' + ' ' * indent + ']')
    else:
        print(' ' * indent + str(data))

#sorted_category_dict["Cores"]["Air Aspect Core"] = [(20, 15000, 1), (5, 15000, 2), (1, 15000, 2)]
# def render_stock_script(sorted_category_dict={}):
#     restock_data_dict = {
#         "a skill mastery orb (used to increase a player's total skill cap by 1)": {'stack_size': (20,5),'stack_quantity': (4, 9),'pos_xy': ((105, 144), (105, 129)),'item_graphic': 22336,'container_serial': 0x483BE859},
#         'plant chemicals': {'stack_size': (100,),'stack_quantity': (4,),'pos_xy': ((88, 138),),'item_graphic': 29030,'container_serial': 0x483BE859},
#         'dyeable gilded gold carpet tile': {'stack_size': (1,),'stack_quantity': (10,),'pos_xy': ((164, 139),),'item_graphic': 43166,'container_serial': 0x483BE859},
#         'pristine lumber': {'stack_size': (5,),'stack_quantity': (2,),'pos_xy': ((154, 105),),'item_graphic': 23996,'container_serial': 0x483BE859},
#         'immaculate stone': {'stack_size': (5,),'stack_quantity': (2,),'pos_xy': ((164, 105),),'item_graphic': 23997,'container_serial': 0x483BE859},
#         'an arcane scroll': {'stack_size': (100,),'stack_quantity': (10,),'pos_xy': ((44, 143),),'item_graphic': 3827,'container_serial': 0x483BE859},
#         'mastercrafting diagram': {'stack_size': (10,),'stack_quantity': (3,),'pos_xy': ((63, 139),),'item_graphic': 17087,'container_serial': 0x483BE859},
#         'prevalia coins [blessed]': {'stack_size': (1,),'stack_quantity': (20,),'pos_xy': ((44, 90),),'item_graphic': 16898,'container_serial': 0x483BE859},
#         'arcane essence': {'stack_size': (1000,),'stack_quantity': (1,),'pos_xy': ((94, 141),),'item_graphic': 12686,'container_serial': 0x483BE859},
#         'aspect core': {'stack_size': (20, 5, 1),'stack_quantity': (1, 2, 2),'start_xy': ((44, 74), (44, 65), (44, 83)),'end_xy': ((164, 74), (164, 65), (164, 83)),'row_col': (1, 24),'item_graphic': 3985,'container_serial': 0x511A5A6C},
#         'distillation': {'stack_size': (5,),'stack_quantity': (2,),'start_xy': ((44, 105),),'end_xy': ((164, 105), ),'row_col': (1, 24),'item_graphic': 17686,'container_serial': 0x511A5A6C},
#         'skill mastery scroll': {'stack_size': (10, 1),'stack_quantity': (2, 2),'start_xy': ((47, 100), (47, 90)),'end_xy': ((167, 100), (167, 90)),'item_graphic': 8826,'row_col': (1, 17),'container_serial': 0x589848EC},
#         'llorcs yretsam lliks': {'stack_size': (10, 1),'stack_quantity': (2, 2),'start_xy': ((50, 143), (50, 133)),'end_xy': ((170, 143), (170, 133)),'item_graphic': 8826,'row_col': (1, 17),'container_serial': 0x589848EC}
#         }
#     current_inventory_data_dict = get_inventory_data_dict(sorted_category_dict)
#     #logger.debug(json.dumps(current_inventory_data_dict,indent=4))
#     out_str = '''overhead "Starting Restock"
# removelist "tempItemList"
# createlist "tempItemList"
# @clearignore'''
#     #print(f"current_inv: {current_inventory_data_dict}")
#     price_list = get_misc_price_list()
#     for item_name, item_price in price_list.items():
#         restock_data = restock_data_dict[item_name]
#         out_str += render_stock_script_simple(item_name, item_price, restock_data,current_inventory_data_dict)


#     out_str += render_stock_script_complex("aspect core",restock_data_dict["aspect core"],current_inventory_data_dict)
#     out_str += render_stock_script_complex("distillation",restock_data_dict["distillation"],current_inventory_data_dict)
#     out_str += render_stock_script_complex("skill mastery scroll",restock_data_dict["skill mastery scroll"],current_inventory_data_dict)
#     out_str += render_stock_script_complex("llorcs yretsam lliks",restock_data_dict["llorcs yretsam lliks"],current_inventory_data_dict)

#     out_str += 'overhead "Finished Restock"'
#     pyperclip.copy(out_str)
#     return out_str
        
                                                                                                    
                                                                                                                        # 1 0x4F1C1360 SKILL SCROLL 1
                                                                                                                        # 2 0x4F1C0D1B SKILL SCROLL 2
                                                                                                                        # 3 0x4F1C0882 CORE
                                                                                                                        # 4 0x4F1C01AE Distil
                                                                                                                        # 5 0x4F1C1BDE Misc
                                                                                                                        # 6 0x4F1C1F98
                                                                                                                        # 7 0x4F1C24D8
                                                                                                                        # 8 0x4F1C2988

#sorted_category_dict["Cores"]["Air Aspect Core"] = [(20, 15000, 1), (5, 15000, 2), (1, 15000, 2)]
def render_stock_script(sorted_category_dict={},discount_float=1.0,alt_vendors=False):
    restock_data_dict = {
        "a skill mastery orb (used to increase a player's total skill cap by 1)": {'stack_size': (20,5),'stack_quantity': (4, 9),'pos_xy': ((105, 129), (105, 144)),'item_graphic': 22336,'container_serial': 0x483BE859,'container_serial_alt': 0x4F1C1BDE},
        'plant chemicals': {'stack_size': (100,),'stack_quantity': (4,),'pos_xy': ((88, 138),),'item_graphic': 29030,'container_serial': 0x483BE859,'container_serial_alt': 0x4F1C1BDE},
        'dyeable gilded gold carpet tile': {'stack_size': (1,),'stack_quantity': (10,),'pos_xy': ((164, 139),),'item_graphic': 43166,'container_serial': 0x483BE859,'container_serial_alt': 0x4F1C1BDE},
        'pristine lumber': {'stack_size': (5,),'stack_quantity': (2,),'pos_xy': ((154, 105),),'item_graphic': 23996,'container_serial': 0x483BE859,'container_serial_alt': 0x4F1C1BDE},
        'immaculate stone': {'stack_size': (5,),'stack_quantity': (2,),'pos_xy': ((164, 105),),'item_graphic': 23997,'container_serial': 0x483BE859,'container_serial_alt': 0x4F1C1BDE},
        'an arcane scroll': {'stack_size': (100,),'stack_quantity': (10,),'pos_xy': ((44, 143),),'item_graphic': 3827,'container_serial': 0x483BE859,'container_serial_alt': 0x4F1C1BDE},
        'mastercrafting diagram': {'stack_size': (10,),'stack_quantity': (3,),'pos_xy': ((63, 139),),'item_graphic': 17087,'container_serial': 0x483BE859,'container_serial_alt': 0x4F1C1BDE},
        'prevalia coins [blessed]': {'stack_size': (1,),'stack_quantity': (20,),'pos_xy': ((44, 90),),'item_graphic': 16898,'container_serial': 0x483BE859,'container_serial_alt': 0x4F1C1BDE},
        'arcane essence': {'stack_size': (1000,),'stack_quantity': (1,),'pos_xy': ((94, 141),),'item_graphic': 12686,'container_serial': 0x483BE859,'container_serial_alt': 0x4F1C1BDE},
        'aspect core': {'stack_size': (20, 5, 1),'stack_quantity': (1, 2, 2),'start_xy': ((44, 74), (44, 65), (44, 83)),'end_xy': ((164, 74), (164, 65), (164, 83)),'row_col': (1, 24),'item_graphic': 3985,'container_serial': 0x511A5A6C,'container_serial_alt': 0x4F1C0882},
        'distillation': {'stack_size': (5,1),'stack_quantity': (2,2),'start_xy': ((44, 105),(44, 88),),'end_xy': ((164, 105),(164, 88),),'row_col': (1, 24),'item_graphic': 17686,'container_serial': 0x511A5A6C,'container_serial_alt': 0x4F1C01AE },
        'skill mastery scroll': {'stack_size': (10, 1),'stack_quantity': (2, 2),'start_xy': ((47, 100), (47, 90)),'end_xy': ((167, 100), (167, 90)),'item_graphic': 8826,'row_col': (1, 17),'container_serial': 0x589848EC,'container_serial_alt': 0x4F1C1360},
        'llorcs yretsam lliks': {'stack_size': (10, 1),'stack_quantity': (2, 2),'start_xy': ((50, 143), (50, 133)),'end_xy': ((170, 143), (170, 133)),'item_graphic': 8826,'row_col': (1, 17),'container_serial': 0x589848EC,'container_serial_alt': 0x4F1C0D1B}
        } 
    current_inventory_data_dict = get_inventory_data_dict(sorted_category_dict)
    #logger.debug(json.dumps(current_inventory_data_dict,indent=4))
    out_str = '''overhead "Starting Restock"
removelist "tempItemList"
createlist "tempItemList"
@clearignore'''
    #print(f"current_inv: {current_inventory_data_dict}")
    price_list = discount_price_list(get_misc_price_list(),discount_float)
    for item_name, item_price in price_list.items():
        restock_data = restock_data_dict[item_name]
        out_str += render_stock_script_simple(item_name, item_price, restock_data,current_inventory_data_dict,discount_float,alt_vendors)


    out_str += render_stock_script_complex("aspect core",restock_data_dict["aspect core"],current_inventory_data_dict,discount_float,alt_vendors)
    out_str += render_stock_script_complex("distillation",restock_data_dict["distillation"],current_inventory_data_dict,discount_float,alt_vendors)
    out_str += render_stock_script_complex("skill mastery scroll",restock_data_dict["skill mastery scroll"],current_inventory_data_dict,discount_float,alt_vendors)
    out_str += render_stock_script_complex("llorcs yretsam lliks",restock_data_dict["llorcs yretsam lliks"],current_inventory_data_dict,discount_float,alt_vendors)

    out_str += 'overhead "Finished Restock"'
    pyperclip.copy(out_str)
    return out_str


def discount_price_list(price_list:dict,discount_float:float):
    return dict([(item_name, int(float(item_price) * discount_float)) for (item_name, item_price) in price_list.items()])


def split_dict_in_half(d):
    items = list(d.items())
    midpoint = math.ceil(len(items) / 2)
    dict1 = dict(items[:midpoint])
    dict2 = dict(items[midpoint:])
    return dict1, dict2


def render_stock_script_simple(item_name, price_per, restock_data,current_inventory_data_dict,discount_float=1.0,alt_vendors=False):
    import random
    stack_sizes = restock_data['stack_size']
    stack_quantities = restock_data['stack_quantity']
    adjust_quantity = current_inventory_data_dict.get(item_name,tuple())
    if isinstance(adjust_quantity,(list,tuple)) and any(adjust_quantity):
        stack_quantities = tuple(max(a - b,0) for a, b in zip(stack_quantities, adjust_quantity))
    pos_coords = restock_data['pos_xy']
    container_serial = restock_data['container_serial_alt'] if alt_vendors else restock_data['container_serial']
    item_graphic = restock_data['item_graphic']
    outStr = ""
    for ind, stack_size in enumerate(stack_sizes):
        stack_quantity = stack_quantities[ind]
        if stack_quantity <= 0:
            continue
        x, y = pos_coords[ind]
        x += random.randrange(-4,4)
        y += random.randrange(-4,4)
        stack_price = stack_size * price_per
        price_str = format_with_commas(stack_price)

        outStr += f'''
@clearignore
if findtype {item_graphic} self
    dclick {container_serial}
    wait 650
    for {stack_quantity}
        removelist "tempItemList"
        createlist "tempItemList"
        if findtypelist "tempItemList" {item_graphic} self
            foreach "tempItem" in "tempItemList"
                getlabel "tempItem" "itemDesc"
                if "{normalize_name(item_name)}" in "itemDesc"
                    lift "tempItem" {stack_size}
                    drop {container_serial} {x} {y} 0
                    wait 325
                    promptresponse {stack_price}
                    wait 325
                    getlabel "tempItem" "itemDesc"
                    if ": {price_str}" in "itemDesc"
                        if {stack_size} == 1 or " : {stack_size}" in "itemDesc"
                        else
                            lift "tempItem" {stack_size}
                            drop backpack 0 0 0
                            wait 650
                        endif
                    else
                        lift "tempItem" 60000
                        drop backpack 0 0 0
                        wait 650
                        lift "tempItem" 1
                        drop {container_serial} {x} {y} 0
                        wait 325
                        promptresponse {stack_price}
                        wait 325
                        getlabel "tempItem" "itemDesc"
                        if ": {price_str}" in "itemDesc"
                            if {stack_size} == 1 or " : {stack_size}" in "itemDesc"
                            else
                                lift "tempItem" {stack_size}
                                drop backpack 0 0 0
                                wait 650
                            endif
                        else
                            lift "tempItem" 60000
                            drop backpack 0 0 0
                            wait 650
                        endif
                    endif
                    @ignore "tempItem"
                endif
            endfor
        else
            break
        endif
    endfor
endif
'''
            
    return outStr


def render_stock_script_complex(item_category,restock_data,current_inventory_data_dict,discount_float=1.0,alt_vendors=False):
    half1_scroll_prices,half2_scroll_prices = split_dict_in_half(scroll_prices)

    price_list = {
        "aspect core": core_prices,
        "distillation": distil_prices,
        "skill mastery scroll": half1_scroll_prices,
        "llorcs yretsam lliks": half2_scroll_prices
        }.get(item_category,{})
    
    price_list = discount_price_list(price_list,discount_float)
    
    stack_sizes = restock_data['stack_size']
    stack_quantities = restock_data['stack_quantity']
    start_coords = restock_data['start_xy']
    end_coords = restock_data['end_xy']
    row_col = restock_data.get('row_col',(1,1))
    container_serial = restock_data['container_serial_alt'] if alt_vendors else restock_data['container_serial']
    item_graphic = restock_data['item_graphic']

    coord_list_1 = calculate_grid_coordinates(start_coords[0],end_coords[0],row_col) if len(start_coords[0]) > 0 else []
    coord_list_2 = calculate_grid_coordinates(start_coords[1],end_coords[1],row_col) if len(start_coords) > 1 and len(start_coords[1]) > 0 else []
    coord_list_3 = calculate_grid_coordinates(start_coords[2],end_coords[2],row_col) if len(start_coords) > 2 and len(start_coords[2]) > 0 else []

    coord_lists = [coord_list_1,coord_list_2,coord_list_3]

    outStr = ""
    hue = ""
    transformer = {"ani": True, "car": True, "for": True,"pea": True,"ste": True,"min":True}

    for jnd, (item_name,item_price) in enumerate(price_list.items()):
        for ind, stack_size in enumerate(stack_sizes):
            temp_name = item_name
            adjust_quantities = current_inventory_data_dict.get(temp_name,tuple()) #empty inventory tuple fallback
          
            adjust_quantity = adjust_quantities[ind] if ind < len(adjust_quantities) else 0
            stack_quantity = stack_quantities[ind] - adjust_quantity
            if stack_quantity <= 0:
                continue
            # if "item id" in temp_name:
            #     logger.debug(f"{temp_name} ({stack_size}pcs) in stock: {adjust_quantity}\tTo restock: {stack_quantity}\tstack_quantities[ind]:{stack_quantities[ind]}\tadjust_quantities:{adjust_quantities}")
            #print(f"{item_name} ({stack_size} stack): {stack_quantity}")
            pos_coords = coord_lists[ind][jnd]
            x, y = pos_coords
            if "aspect core" in item_category:
                temp_name = item_name[:3]
                type_name = item_name[:-12]
                hue = aspect_hues[type_name]
                if isinstance(hue,list):
                    hue = hue[0]
                if ind == 2:
                    x += 2
            elif "skill mastery scroll" in item_category or "llorcs yretsam lliks" in item_category:
                temp_name = temp_name.replace(" skill mastery scroll (used to increase a player's skill cap for a skill by 1)","")
                type_name = item_name[:-78]
                hue = scroll_hues[type_name]
                if isinstance(hue,list):
                    hue = hue[0]
                temp_name = item_name[:3]
                if transformer.get(temp_name,False):
                    if "ani" in temp_name:
                        temp_name = item_name[:8]
                    else:
                        temp_name = item_name[:4]
            elif "distillation" in item_category:
                temp_name = item_name[:3] if "Discipline" not in item_name else item_name[:4]
                type_name = item_name[:-20]
                hue = aspect_hues[type_name]
                if isinstance(hue,list):
                    hue = hue[1]
            # x += random.randrange(-1,1)
            # y += random.randrange(-1,1)
                
            stack_price = stack_size * item_price
            price_str = format_with_commas(stack_price)

            outStr += f'''
@clearignore
if findtype {item_graphic} self {hue}
    dclick {container_serial}
    for {stack_quantity}
        removelist "tempItemList"
        createlist "tempItemList"
        if findtypelist "tempItemList" {item_graphic} self {hue}
            foreach "tempItem" in "tempItemList"
                getlabel "tempItem" "itemDesc"
                if "{normalize_name(temp_name)}" in "itemDesc"
                    lift "tempItem" {stack_size}
                    drop {container_serial} {x} {y} 0
                    wait 325
                    promptresponse {stack_price}
                    wait 325
                    getlabel "tempItem" "itemDesc"
                    if ": {price_str}" in "itemDesc"
                        if {stack_size} == 1 or " : {stack_size}" in "itemDesc"
                        else
                            lift "tempItem" {stack_size}
                            drop backpack 0 0 0
                            wait 650
                        endif
                    else
                        lift "tempItem" 60000
                        drop backpack 0 0 0
                        wait 650
                        lift "tempItem" 1
                        drop {container_serial} {x} {y} 0
                        wait 325
                        promptresponse {stack_price}
                        wait 325
                        getlabel "tempItem" "itemDesc"
                        if ": {price_str}" in "itemDesc"
                            if {stack_size} == 1 or " : {stack_size}" in "itemDesc"
                            else
                                lift "tempItem" {stack_size}
                                drop backpack 0 0 0
                                wait 650
                            endif
                        else
                            lift "tempItem" 60000
                            drop backpack 0 0 0
                            wait 650
                        endif
                    endif
                    @ignore "tempItem"
                endif
            endfor
        else
            break
        endif
    endfor
endif
'''

            
    return outStr


def normalize_name(s):
    transformer = {
        'a skill mastery orb': ("a skill mastery orb \(used to increase a player's total skill cap by 1\)",'a skill mastery orb'), #a skill mastery orb (used to increase a player's total skill cap by 1)
        }
    for key_string, re_tuple in transformer.items():
        if key_string in s:
            search_pattern, replace_pattern = re_tuple
            s = re.sub(search_pattern, replace_pattern, s)
    return s


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


if __name__ == "__main__":  
    discount_float = 1.
    alt_vendors = True
    render_stock_script({},discount_float,alt_vendors)
    print(f"Price Multiplier: {discount_float}\nAlternate Vendors: {alt_vendors}")

