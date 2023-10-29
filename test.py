import re
import time

# def process_item(stringExample):
#     match = re.search(r'ID:(\d+) Price: (\d+) (.+?)(?: : (\d+)(.*))?$', stringExample)
#     item_description = match.group(3)
    
#     if " dye " in item_description:
#         # Using regex to find duplicates of the form "(hue xxxx: color)"
#         duplicates = re.findall(r'\(hue \d+: .+?\)', item_description)
        
#         # Remove duplicates while keeping the first instance
#         if len(duplicates) > 1 and duplicates[0] == duplicates[1]:
#             item_description = item_description.replace(duplicates[0], "", 1)
            
#     return item_description


def process_item(stringExample):
    match = re.search(r'ID:(\d+) Price: (\d+) (.+?)(?: : (\d+)(.*))?$', stringExample)
    item_description = match.group(3)  #todo fix double descriptions on some dyes
    if " dye " in item_description and ") (hue" in item_description:
        item_description = item_description.split(") (hue")[0] + ")"
    return item_description


stringExample = "…item ID:1150998096 Price: 200000 rare facial hair dye (hue 1939: dark crimson)"
# start_time = time.time()
# for i in range (1,1000000):
#     process_item(stringExample)
# delta_time = time.time() - start_time
print(process_item(stringExample)[:-1])
