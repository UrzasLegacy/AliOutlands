from collections import defaultdict
import json

hue_list = {
    'Shimmer Oxide':         {'rare cloth': 175000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 750000, 'facial hair dye': 750000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1483},
    'Shimmer Cardinal':      {'rare cloth': 125000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 750000, 'facial hair dye': 750000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1476},
    'Shimmer Evergreen':     {'rare cloth': 125000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 750000, 'facial hair dye': 750000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1479},
    'Shimmer Valentine':     {'rare cloth': 125000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 750000, 'facial hair dye': 750000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2916},
    'Shimmer Periwinkle':    {'rare cloth': 175000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 750000, 'facial hair dye': 750000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2251},
    'Shimmer Shamrock':      {'rare cloth': 175000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 750000, 'facial hair dye': 750000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2664},
    'Shimmer Lunar':         {'rare cloth': 75000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 750000, 'facial hair dye': 750000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2342},
    'Shimmer Solstice':      {'rare cloth': 75000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 500000, 'facial hair dye': 500000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1967},
    'Shimmer Dahlia':        {'rare cloth': 125000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1956},
    'Shimmer Paradox':       {'rare cloth': 600000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 1000000, 'facial hair dye': 1000000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2346},
    'Shimmer Redux':         {'rare cloth': 300000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1957},
    'Shimmer Spice':         {'rare cloth': 100000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1557},
    'Shimmer Garnet':        {'rare cloth': 500000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 1000000, 'facial hair dye': 1000000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1571},
    'Shimmer Equinox':       {'rare cloth': 100000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1574},
    'Shimmer Moonlight':     {'rare cloth': 100000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2284},
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
    'Shimmer Mirage':        {'rare cloth': 40000, 'runebook dye': 300000, 'accessory dye': 50000, 'headwear dye': 100000, 'carpet dye': 50000, 'furniture dye': 200000, 'hair dye': 250000, 'facial hair dye': 250000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1575},
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
    'Monster Hunter':        {'rare cloth': 50000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2817},
    'Adventurer Lodge':      {'rare cloth': 50000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1918},
    'Tradesman Union':       {'rare cloth': 50000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2765},
    'Order of Armorers':     {'rare cloth': 50000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2915},
    'Seafarer League':       {'rare cloth': 50000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2906},
    'Artificer\'s Enclave':  {'rare cloth': 50000, 'runebook dye': 1000, 'accessory dye': 1000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 1000, 'hair dye': 1000, 'facial hair dye': 1000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2875},
    'Aegis Keep':            {'rare cloth': 6000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 1000, 'carpet dye': 4000, 'furniture dye': 20000, 'hair dye': 60000, 'facial hair dye': 60000, 'backpack dye': 40000, 'mount gear dye': 10000,  'hue': 1779},
    'Inferno':               {'rare cloth': 6000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 20000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 60000, 'facial hair dye': 60000, 'backpack dye': 75000, 'mount gear dye': 15000,  'hue': 1909},
    'Ossuary':               {'rare cloth': 6000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 1000, 'carpet dye': 500, 'furniture dye': 20000, 'hair dye': 40000, 'facial hair dye': 40000, 'backpack dye': 50000, 'mount gear dye': 10000,  'hue': 2091},
    'Darkmire Temple':       {'rare cloth': 6000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 40000, 'facial hair dye': 40000, 'backpack dye': 50000, 'mount gear dye': 10000,  'hue': 2099},
    'Pulma':                 {'rare cloth': 6000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 90000, 'facial hair dye': 90000, 'backpack dye': 50000, 'mount gear dye': 10000,  'hue': 2085},
    'The Mausoleum':         {'rare cloth': 6000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 60000, 'facial hair dye': 60000, 'backpack dye': 50000, 'mount gear dye': 10000,  'hue': 2092},
    'Mount Petram':          {'rare cloth': 6000, 'runebook dye': 15000, 'accessory dye': 2000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 40000, 'facial hair dye': 40000, 'backpack dye': 50000, 'mount gear dye': 10000,  'hue': 2089},
    'Nusero':                {'rare cloth': 6000, 'runebook dye': 15000, 'accessory dye': 2000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 20000, 'facial hair dye': 20000, 'backpack dye': 50000, 'mount gear dye': 10000,  'hue': 2796},
    'Cavernam':              {'rare cloth': 4000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 1000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 300000, 'facial hair dye': 300000, 'backpack dye': 50000, 'mount gear dye': 10000,  'hue': 2338},
    'Shadowspire Cathedral': {'rare cloth': 12000, 'runebook dye': 15000, 'accessory dye': 2000, 'headwear dye': 30000, 'carpet dye': 14000, 'furniture dye': 80000, 'hair dye': 40000, 'facial hair dye': 40000, 'backpack dye': 50000, 'mount gear dye': 10000,  'hue': 2093},
    'Wilderness':            {'rare cloth': 6000, 'runebook dye': 15000, 'accessory dye': 1000, 'headwear dye': 20000, 'carpet dye': 100, 'furniture dye': 15000, 'hair dye': 15000, 'facial hair dye': 15000, 'backpack dye': 50000, 'mount gear dye': 10000,  'hue': 1182},
    'Ocean':                 {'rare cloth': 18000, 'runebook dye': 150000, 'accessory dye': 2000, 'headwear dye': 50000, 'carpet dye': 5000, 'furniture dye': 120000, 'hair dye': 100000, 'facial hair dye': 100000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1183},
    'Metallic Cherry':       {'rare cloth': 65000, 'runebook dye': 40000, 'accessory dye': 20000, 'headwear dye': 30000, 'carpet dye': 4000, 'furniture dye': 50000, 'hair dye': 100000, 'facial hair dye': 100000, 'backpack dye': 150000, 'mount gear dye': 600000,  'hue': 2380},
    'Metallic Orange':       {'rare cloth': 12000, 'runebook dye': 30000, 'accessory dye': 6000, 'headwear dye': 30000, 'carpet dye': 3000, 'furniture dye': 40000, 'hair dye': 100000, 'facial hair dye': 100000, 'backpack dye': 150000, 'mount gear dye': 600000,  'hue': 1989},
    'Metallic Amber':        {'rare cloth': 8000, 'runebook dye': 25000, 'accessory dye': 1000, 'headwear dye': 30000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 50000, 'facial hair dye': 50000, 'backpack dye': 50000, 'mount gear dye': 600000,  'hue': 1990},
    'Metallic Lemon-Lime':   {'rare cloth': 5000, 'runebook dye': 25000, 'accessory dye': 1000, 'headwear dye': 30000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 50000, 'facial hair dye': 50000, 'backpack dye': 50000, 'mount gear dye': 600000,  'hue': 2653},
    'Metallic Olive':        {'rare cloth': 4000, 'runebook dye': 25000, 'accessory dye': 1000, 'headwear dye': 30000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 50000, 'facial hair dye': 50000, 'backpack dye': 50000, 'mount gear dye': 600000,  'hue': 2398},
    'Metallic Pickle':       {'rare cloth': 10000, 'runebook dye': 30000, 'accessory dye': 5000, 'headwear dye': 30000, 'carpet dye': 3000, 'furniture dye': 20000, 'hair dye': 50000, 'facial hair dye': 50000, 'backpack dye': 50000, 'mount gear dye': 600000,  'hue': 2828},
    'Metallic Juniper':      {'rare cloth': 4000, 'runebook dye': 25000, 'accessory dye': 1000, 'headwear dye': 30000, 'carpet dye': 500, 'furniture dye': 2000, 'hair dye': 30000, 'facial hair dye': 30000, 'backpack dye': 50000, 'mount gear dye': 600000,  'hue': 2845},
    'Metallic Mint':         {'rare cloth': 4000, 'runebook dye': 25000, 'accessory dye': 1000, 'headwear dye': 30000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 30000, 'facial hair dye': 30000, 'backpack dye': 50000, 'mount gear dye': 600000,  'hue': 2827},
    'Metallic Sky':          {'rare cloth': 5000, 'runebook dye': 25000, 'accessory dye': 3000, 'headwear dye': 30000, 'carpet dye': 2000, 'furniture dye': 20000, 'hair dye': 50000, 'facial hair dye': 50000, 'backpack dye': 50000, 'mount gear dye': 600000,  'hue': 2826},
    'Metallic Sapphire':     {'rare cloth': 10000, 'runebook dye': 30000, 'accessory dye': 3000, 'headwear dye': 30000, 'carpet dye': 1000, 'furniture dye': 30000, 'hair dye': 50000, 'facial hair dye': 50000, 'backpack dye': 50000, 'mount gear dye': 600000,  'hue': 2379},
    'Metallic Cerulean':     {'rare cloth': 10000, 'runebook dye': 40000, 'accessory dye': 1000, 'headwear dye': 30000, 'carpet dye': 1000, 'furniture dye': 30000, 'hair dye': 50000, 'facial hair dye': 50000, 'backpack dye': 50000, 'mount gear dye': 600000,  'hue': 1484},
    'Metallic Eggplant':     {'rare cloth': 15000, 'runebook dye': 40000, 'accessory dye': 5000, 'headwear dye': 30000, 'carpet dye': 5000, 'furniture dye': 20000, 'hair dye': 100000, 'facial hair dye': 100000, 'backpack dye': 150000, 'mount gear dye': 600000,  'hue': 2898},
    'Metallic Raspberry':    {'rare cloth': 6000, 'runebook dye': 25000, 'accessory dye': 3000, 'headwear dye': 30000, 'carpet dye': 2000, 'furniture dye': 20000, 'hair dye': 50000, 'facial hair dye': 50000, 'backpack dye': 50000, 'mount gear dye': 600000,  'hue': 1489},
    'Metallic Wine':         {'rare cloth': 10000, 'runebook dye': 25000, 'accessory dye': 3000, 'headwear dye': 30000, 'carpet dye': 1000, 'furniture dye': 30000, 'hair dye': 50000, 'facial hair dye': 50000, 'backpack dye': 50000, 'mount gear dye': 600000,  'hue': 1995},
    'Metallic Pewter':       {'rare cloth': 6000, 'runebook dye': 25000, 'accessory dye': 1000, 'headwear dye': 30000, 'carpet dye': 1000, 'furniture dye': 20000, 'hair dye': 10000, 'facial hair dye': 10000, 'backpack dye': 25000, 'mount gear dye': 600000,  'hue': 2167},
    'Metallic Chalk':        {'rare cloth': 5000, 'runebook dye': 25000, 'accessory dye': 1000, 'headwear dye': 30000, 'carpet dye': 500, 'furniture dye': 20000, 'hair dye': 50000, 'facial hair dye': 50000, 'backpack dye': 50000, 'mount gear dye': 600000,  'hue': 2928},
    'Metallic Umber':        {'rare cloth': 5000, 'runebook dye': 25000, 'accessory dye': 5000, 'headwear dye': 30000, 'carpet dye': 500, 'furniture dye': 20000, 'hair dye': 20000, 'facial hair dye': 20000, 'backpack dye': 25000, 'mount gear dye': 600000,  'hue': 1470},
    'Dark Coffee':           {'rare cloth': 65000, 'runebook dye': 50000, 'accessory dye': 2000, 'headwear dye': 100000, 'carpet dye': 5000, 'furniture dye': 75000, 'hair dye': 70000, 'facial hair dye': 70000, 'backpack dye': 200000, 'mount gear dye': 600000,  'hue': 1467},
    'Dark Rust':             {'rare cloth': 3000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 20000, 'carpet dye': 1000, 'furniture dye': 30000, 'hair dye': 25000, 'facial hair dye': 25000, 'backpack dye': 40000, 'mount gear dye': 600000,  'hue': 2807},
    'Dark Crimson':          {'rare cloth': 5000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 20000, 'carpet dye': 1000, 'furniture dye': 30000, 'hair dye': 30000, 'facial hair dye': 30000, 'backpack dye': 40000, 'mount gear dye': 600000,  'hue': 1939},
    'Dark Blood':            {'rare cloth': 10000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 20000, 'carpet dye': 5000, 'furniture dye': 30000, 'hair dye': 50000, 'facial hair dye': 50000, 'backpack dye': 40000, 'mount gear dye': 600000,  'hue': 1465},
    'Dark Salmon':           {'rare cloth': 4000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 20000, 'carpet dye': 1000, 'furniture dye': 30000, 'hair dye': 25000, 'facial hair dye': 25000, 'backpack dye': 40000, 'mount gear dye': 600000,  'hue': 2174},
    'Dark Forest':           {'rare cloth': 5000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 20000, 'carpet dye': 1000, 'furniture dye': 30000, 'hair dye': 20000, 'facial hair dye': 20000, 'backpack dye': 40000, 'mount gear dye': 600000,  'hue': 2804},
    'Dark Peacock':          {'rare cloth': 8000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 20000, 'carpet dye': 3000, 'furniture dye': 30000, 'hair dye': 25000, 'facial hair dye': 25000, 'backpack dye': 40000, 'mount gear dye': 600000,  'hue': 2226},
    'Dark Denim':            {'rare cloth': 5000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 100000, 'carpet dye': 1000, 'furniture dye': 30000, 'hair dye': 25000, 'facial hair dye': 25000, 'backpack dye': 40000, 'mount gear dye': 600000,  'hue': 2801},
    'Dark Blueberry':        {'rare cloth': 5000, 'runebook dye': 20000, 'accessory dye': 2000, 'headwear dye': 20000, 'carpet dye': 1000, 'furniture dye': 30000, 'hair dye': 25000, 'facial hair dye': 25000, 'backpack dye': 40000, 'mount gear dye': 600000,  'hue': 1156},
    'Dark Jam':              {'rare cloth': 60000, 'runebook dye': 50000, 'accessory dye': 12000, 'headwear dye': 100000, 'carpet dye': 20000, 'furniture dye': 100000, 'hair dye': 150000, 'facial hair dye': 150000, 'backpack dye': 200000, 'mount gear dye': 600000,  'hue': 2230},
    'Powder Ruby':           {'rare cloth': 175000, 'runebook dye': 80000, 'accessory dye': 30000, 'headwear dye': 600000, 'carpet dye': 20000, 'furniture dye': 250000, 'hair dye': 400000, 'facial hair dye': 400000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2227},
    'Powder Coral':          {'rare cloth': 30000, 'runebook dye': 30000, 'accessory dye': 10000, 'headwear dye': 150000, 'carpet dye': 9000, 'furniture dye': 100000, 'hair dye': 100000, 'facial hair dye': 100000, 'backpack dye': 150000, 'mount gear dye': 600000,  'hue': 1495},
    'Powder Peach':          {'rare cloth': 20000, 'runebook dye': 30000, 'accessory dye': 10000, 'headwear dye': 150000, 'carpet dye': 2000, 'furniture dye': 100000, 'hair dye': 150000, 'facial hair dye': 150000, 'backpack dye': 150000, 'mount gear dye': 600000,  'hue': 1496},
    'Powder Lemon':          {'rare cloth': 75000, 'runebook dye': 50000, 'accessory dye': 15000, 'headwear dye': 500000, 'carpet dye': 8000, 'furniture dye': 100000, 'hair dye': 300000, 'facial hair dye': 300000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1382},
    'Powder Pistachio':      {'rare cloth': 20000, 'runebook dye': 30000, 'accessory dye': 10000, 'headwear dye': 150000, 'carpet dye': 4000, 'furniture dye': 100000, 'hair dye': 75000, 'facial hair dye': 75000, 'backpack dye': 150000, 'mount gear dye': 600000,  'hue': 1494},
    'Powder Seafoam':        {'rare cloth': 35000, 'runebook dye': 30000, 'accessory dye': 15000, 'headwear dye': 150000, 'carpet dye': 4000, 'furniture dye': 100000, 'hair dye': 300000, 'facial hair dye': 300000, 'backpack dye': 150000, 'mount gear dye': 600000,  'hue': 2246},
    'Powder Spring':         {'rare cloth': 35000, 'runebook dye': 30000, 'accessory dye': 15000, 'headwear dye': 150000, 'carpet dye': 9000, 'furniture dye': 100000, 'hair dye': 300000, 'facial hair dye': 300000, 'backpack dye': 150000, 'mount gear dye': 600000,  'hue': 1381},
    'Powder Lapis':          {'rare cloth': 55000, 'runebook dye': 80000, 'accessory dye': 15000, 'headwear dye': 500000, 'carpet dye': 5000, 'furniture dye': 100000, 'hair dye': 400000, 'facial hair dye': 400000, 'backpack dye': 150000, 'mount gear dye': 600000,  'hue': 2255},
    'Powder Cyan':           {'rare cloth': 50000, 'runebook dye': 30000, 'accessory dye': 15000, 'headwear dye': 150000, 'carpet dye': 5000, 'furniture dye': 100000, 'hair dye': 100000, 'facial hair dye': 100000, 'backpack dye': 150000, 'mount gear dye': 600000,  'hue': 2877},
    'Powder Azure':          {'rare cloth': 200000, 'runebook dye': 80000, 'accessory dye': 30000, 'headwear dye': 1200000, 'carpet dye': 8000, 'furniture dye': 100000, 'hair dye': 800000, 'facial hair dye': 800000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1384},
    'Powder Orchid':         {'rare cloth': 55000, 'runebook dye': 30000, 'accessory dye': 15000, 'headwear dye': 500000, 'carpet dye': 5000, 'furniture dye': 100000, 'hair dye': 200000, 'facial hair dye': 200000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 1462},
    'Powder Iris':           {'rare cloth': 400000, 'runebook dye': 100000, 'accessory dye': 60000, 'headwear dye': 1300000, 'carpet dye': 20000, 'furniture dye': 250000, 'hair dye': 800000, 'facial hair dye': 800000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2173},
    'Powder Cloud':          {'rare cloth': 200000, 'runebook dye': 80000, 'accessory dye': 40000, 'headwear dye': 600000, 'carpet dye': 9000, 'furniture dye': 100000, 'hair dye': 800000, 'facial hair dye': 800000, 'backpack dye': 800000, 'mount gear dye': 600000,  'hue': 2903},
    'Powder Blush':          {'rare cloth': 35000, 'runebook dye': 30000, 'accessory dye': 15000, 'headwear dye': 150000, 'carpet dye': 5000, 'furniture dye': 100000, 'hair dye': 100000, 'facial hair dye': 100000, 'backpack dye': 500000, 'mount gear dye': 600000,  'hue': 2808},
    'Powder Bubblegum':      {'rare cloth': 125000, 'runebook dye': 50000, 'accessory dye': 40000, 'headwear dye': 400000, 'carpet dye': 18000, 'furniture dye': 250000, 'hair dye': 600000, 'facial hair dye': 600000, 'backpack dye': 800000, 'mount gear dye': 600000,  'hue': 1952},
}

#dark forest cloth
#rare cloth (hue 2804: dark forest)

#dark forest runebook dye
#dark forest accessory dye
#dark forest headwear dye

#dark forest carpet dye
#carpet dye (hue 2804: dark forest)

#dark forest furniture dye
#dark forest hair dye dye
#hair dye (hue 2804: dark forest)
#dark forest rare hair dye
#rare hair dye (hue 2804: dark forest)

#dark forest facial hair dye
#facial hair dye (hue 2804: dark forest)

#dark forest rare facial hair dye
#rare facial hair dye (hue 2804: dark forest)
#dark forest backpack dye
#backpack dye (hue 2804: dark forest)

#dark forest mount gear dye
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

print(json.dumps(alter_hue_dict(self_parse=True, item_type="accessory dye"), indent=4))
