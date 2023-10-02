import re
inputString = """Creatures of Aegis Keep: 15
Creatures of Cavernam.: 15
Creatures of Darkmire Temple.: 15
Creatures of Inf.: 15
Creatures of Maus.: 15
Creatures of Mt.P.: 15
Creatures of Nusero: 15
Creatures of Oss.: 15
Creatures of Pulma: 15
History of Andaria: 10
History of Corpse Creek.: 10
History of Cambria: 10
History of Horseshoe Bay.: 10
History of Outpost: 10
History of Prevalia: 10
History of Terran: 10
Outlands Mythology Vol 1: 10
Outlands Mythology Vol 2: 10
Outlands Mythology Vol 3: 10
Outlands Mythology Vol 4: 10
Outlands Mythology Vol 5: 10
Outlands Mythology Vol 6: 10
Outlands Mythology Vol 7: 10
Tales of Aegis Keep: 10
Tales of Cavernam: 10
Tales of Darkmire Temple: 10
Tales of Inferno: 10
Tales of of The Mausoleum: 10
Tales of Mount Petram: 10
Tales of Nusero: 10
Tales of Ossuary: 10
Tales of Pulma: 10"""
split = inputString.split("\n")
sum = 0
for line in split:
    match = re.search(r"(\d\d?)($|\")", line)
    sum += int(match.group(1))
print(f'Lore Books: {len(split)}\nLore Pages: {sum}')
