import re
import pyperclip
from collections import defaultdict
distil_prices = { #exact string MATTERS
    "Air Aspect Distillation": 7000,
    "Artisan Aspect Distillation": 4000,
    "Blood Aspect Distillation": 10000,
    "Command Aspect Distillation": 8000,
    "Death Aspect Distillation": 3000,
    "Discipline Aspect Distillation": 3000,
    "Earth Aspect Distillation": 3000,
    "Eldritch Aspect Distillation": 8000,
    "Fire Aspect Distillation": 3000,
    "Fortune Aspect Distillation": 8000,
    "Gadget Aspect Distillation": 4000,
    "Harvest Aspect Distillation": 10000,
    "Holy Aspect Distillation": 3000,
    "Lyric Aspect Distillation": 3000,
    "Poison Aspect Distillation": 6000,
    "Shadow Aspect Distillation": 4000,
    "Void Aspect Distillation": 4000,
    "Water Aspect Distillation": 4000,
    "War Aspect Distillation": 2000,
}

def RenderDistilScript():
    out_str = ''
    for distil, price in distil_prices.items():
        pass

def SimpleStocker():
    item_ID = 3827
    item_string = 'arcane scroll'
    from_container = 'backpack'
    to_container = 0x483BE859
    price = 10000
    quant = 10
    total_stacks = 20

    start_pos = "X=62, Y=133, Z=0"
    end_pos = "X=107, Y=143, Z=0"
    x_offset = 3
    y_offset = 10

    start_match = re.search(r"X=(\d+), Y=(\d+), Z=(\d+)",start_pos)
    start_X = int(start_match.group(1)) if start_match else 0
    start_Y = int(start_match.group(2)) if start_match else 0
    #start_Z = start_match.group(3) if start_match else 0
    print(f"startX: {start_X},startY: {start_Y}")
    end_match = re.search(r"X=(\d+), Y=(\d+), Z=(\d+)",end_pos)
    end_X = int(end_match.group(1)) if end_match else 0
    end_Y = int(end_match.group(2)) if end_match else 0
    #end_Z = end_match.group(3) if end_match else 0

    x_range = end_X - start_X
    y_range = end_Y - start_Y

    print(f"x_range: {x_range},y_range: {y_range}")
    column_count = 1
    if x_range > 0:
        column_count = int(x_range / x_offset)
        start_X += int((x_range - (x_offset * column_count)) / 2)
        column_count += 1
    
    row_count = 1
    if y_range > 0:
        row_count = int(y_range / y_offset)
        start_Y += int((y_range - (y_offset * row_count)) / 2)
        row_count += 1

    max_items = row_count * column_count
    print(f"Max Stacks: {max_items}")
    if max_items < total_stacks:
        print(f"r:{row_count},c:{column_count} < {total_stacks}")
        return

    #grid = [[None for _ in range(column_count)] for _ in range(row_count)]

    out_str = '''removelist "coordList"
createlist "coordList"

'''

    for row in range(row_count):
        hopY = start_Y + (y_offset * row)
        for col in range(column_count):
            hopX = start_X + (x_offset * col)
            out_str += f"\npushlist \"coordList\" {hopX}\npushlist \"coordList\" {hopY}"
            #cell_coord = {"x":hopX,"y":hopY}
            #grid[row][col] = cell_coord
    
    out_str += f'''

@clearignore
dclick {from_container}
wait 650
while findtype {item_ID} {from_container} as "itemToMove"
    if "{item_string}" != 0
        getlabel "itemToMove" 'itemDesc'
        if "{item_string}" in 'itemDesc'
        else
            @ignore "itemToMove"
            continue
        endif
    endif
    if poplist "coordList" "front" as x and poplist "coordList" "front" as y
        lift "itemToMove" {quant}
        drop {to_container} x y 0
        wait 325
        if {price} > 0
            promptresponse {price}
            wait 325
            getlabel "itemToMove" "itemDesc"
            if ": {price}" in "itemDesc"
            else
                lift "itemToMove" {quant}
                drop backpack 0 0 0
                pushlist "coordList" y "front"
                pushlist "coordList" x "front"
                wait 650
                continue
            endif
        endif
        wait 325
        @ignore "itemToMove"
    endif
endwhile'''

    pyperclip.copy(out_str)


def SkillScrollStocker():
    scrolls = { #exact string MATTERS
        "alchemy": 30000,
        "animal lore": 21000,
        "animal taming": 21000,
        "arms lore": 9000,
        "blacksmithy": 9000,
        "begging": 9000,
        "camping": 10000,
        "carpentry": 9000,
        "cartography": 10000,
        "chivalry": 22000,
        "cooking": 10000,
        "detect hidden": 13000,
        "discordance": 9000,
        "fishing": 9000,
        "forensic eval": 12000,
        "herding": 21000,
        "inscription": 23000,
        "item id": 10000,
        "lockpicking": 17000,
        "lumberjacking": 9000,
        "mining": 9000,
        "musicianship": 9000,
        "necromancy": 24000,
        "peacemaking": 9000,
        "poisoning": 10000,
        "provocation": 9000,
        "spirit speak": 10000,
        "stealth": 16000,
        "tailoring": 40000,
        "taste id": 13000,
        "tinkering": 9000,
        "tracking": 10000,
        "veterinary": 21000,
    }
 #21,22,23,24,25,26,27
 #42,43,44,45,46,47,48
 #63,64,65,66,67,68,69
 #82,83,84,85,86,87,88
 #102
    coord_list = [
        {'x': 44, 'y': 65}, {'x': 50, 'y': 71}, {'x': 56, 'y': 77}, {'x': 51, 'y': 65}, {'x': 57, 'y': 71}, {'x': 63, 'y': 77}, {'x': 58, 'y': 65}, 
        {'x': 64, 'y': 71}, {'x': 70, 'y': 77}, {'x': 65, 'y': 65}, {'x': 71, 'y': 71}, {'x': 77, 'y': 77}, {'x': 72, 'y': 65}, {'x': 78, 'y': 71}, 
        {'x': 84, 'y': 77}, {'x': 79, 'y': 65}, {'x': 85, 'y': 71}, {'x': 91, 'y': 77}, {'x': 86, 'y': 65}, {'x': 92, 'y': 71}, {'x': 98, 'y': 77}, 
        {'x': 62, 'y': 83}, {'x': 68, 'y': 89}, {'x': 74, 'y': 95}, {'x': 69, 'y': 83}, {'x': 75, 'y': 89}, {'x': 81, 'y': 95}, {'x': 76, 'y': 83}, 
        {'x': 82, 'y': 89}, {'x': 88, 'y': 95}, {'x': 83, 'y': 83}, {'x': 89, 'y': 89}, {'x': 95, 'y': 95}, {'x': 90, 'y': 83}, {'x': 96, 'y': 89}, 
        {'x': 102, 'y': 95}, {'x': 97, 'y': 83}, {'x': 103, 'y': 89}, {'x': 109, 'y': 95}, {'x': 104, 'y': 83}, {'x': 110, 'y': 89}, {'x': 116, 'y': 95}, 
        {'x': 80, 'y': 101}, {'x': 86, 'y': 107}, {'x': 92, 'y': 113}, {'x': 87, 'y': 101}, {'x': 93, 'y': 107}, {'x': 99, 'y': 113}, {'x': 94, 'y': 101}, 
        {'x': 100, 'y': 107}, {'x': 106, 'y': 113}, {'x': 101, 'y': 101}, {'x': 107, 'y': 107}, {'x': 113, 'y': 113}, {'x': 108, 'y': 101}, {'x': 114, 'y': 107}, 
        {'x': 120, 'y': 113}, {'x': 115, 'y': 101}, {'x': 121, 'y': 107}, {'x': 127, 'y': 113}, {'x': 122, 'y': 101}, {'x': 128, 'y': 107}, {'x': 134, 'y': 113}, 
        {'x': 98, 'y': 119}, {'x': 104, 'y': 125}, {'x': 110, 'y': 131}, {'x': 105, 'y': 119}, {'x': 111, 'y': 125}, {'x': 117, 'y': 131}, {'x': 112, 'y': 119}, 
        {'x': 118, 'y': 125}, {'x': 124, 'y': 131}, {'x': 119, 'y': 119}, {'x': 125, 'y': 125}, {'x': 131, 'y': 131}, {'x': 126, 'y': 119}, {'x': 132, 'y': 125}, 
        {'x': 138, 'y': 131}, {'x': 133, 'y': 119}, {'x': 139, 'y': 125}, {'x': 145, 'y': 131}, {'x': 140, 'y': 119}, {'x': 146, 'y': 125}, {'x': 152, 'y': 131}, 
        {'x': 116, 'y': 137}, {'x': 122, 'y': 143}, {'x': 123, 'y': 137}, {'x': 129, 'y': 143}, {'x': 130, 'y': 137}, {'x': 136, 'y': 143}, {'x': 137, 'y': 137}, 
        {'x': 143, 'y': 143}, {'x': 144, 'y': 137}, {'x': 150, 'y': 143}, {'x': 151, 'y': 137}, {'x': 157, 'y': 143}, {'x': 158, 'y': 137}, {'x': 164, 'y': 143}
        ]
    
    toContainer = 0x589848EC
    i = 0
    newDict = defaultdict(list)
    outStr = '''removelist "tempScrollList"
createlist "tempScrollList"
@clearignore

'''
    for name,price in scrolls.items():
       
        for repeat in range(3):
            if name == "tinkering" and repeat == 2:
                continue
            coord = coord_list[i]
            # coord1x, coord1y = coord_list[i]["x"], coord_list[i]["y"]
            # coord2x, coord2y = coord_list[i+1]["x"], coord_list[i+1]["y"]
            # coord3x, coord3y = coord_list[i+2]["x"], coord_list[i+2]["y"]
            x = coord["x"]
            y = coord["y"]
            i += 1
            #x = coord_list[(index % 7) * increment + 21]["x"]
        # newDict[name] = [price, coord1x, coord1y, coord2x, coord2y, coord3x,coord3y]
            outStr += f'''
clearlist "tempScrollList"
if findtypelist "tempScrollList" 8826 self
    foreach "tempScroll" in "tempScrollList"
        getlabel "tempScroll" "tempDesc"
        if "{name}" in "tempDesc"
            lift "tempScroll" 1
            drop {toContainer} {x} {y} 0
            wait 325
            promptresponse {price}
            wait 325
            getlabel "tempScroll" "tempDesc"
            if ": {price}" in "tempDesc"
            else
                lift "tempScroll" 60000
                drop backpack 0 0 0
                wait 650
                lift "tempScroll" 1
                drop {toContainer} {x} {y} 0
                wait 325
                promptresponse {price}
                wait 325
                getlabel "tempScroll" "tempDesc"
                if ": {price}" in "tempDesc"
                else
                    lift "tempScroll" 60000
                    drop backpack 0 0 0
                    wait 650
                endif
            endif
            @ignore "tempScroll"
            break
        endif
    endfor
endif
'''
            
    pyperclip.copy(outStr)
    for k,v in newDict.items():
        print(f"{k}:{v},")      



def NumberCompare(minPrice=20000,maxPrice=32000):
    outStr = f'    if \"Price: 999 " in "desc"\n      setvar "buyThis" 1\n'
    
    for i in range(-maxPrice+1,-minPrice):
        if i % 1000 == 0:
            outStr += f'    elseif "Price: {-i} " in "desc"\n      setvar "buyThis\" 1\n'
        elif i % 500 == 0:
            outStr += f'    elseif "Price: {-i} " in "desc"\n      setvar "buyThis\" 1\n'     
        elif i % 100 == 0:
            outStr += f'    elseif "Price: {-i} " in "desc"\n      setvar "buyThis\" 1\n' 
        elif i % 50 == 0:
            outStr += f'    elseif "Price: {-i} " in "desc"\n      setvar "buyThis\" 1\n'
        elif i % 5 == 0:
            outStr += f'    elseif "Price: {-i} " in "desc"\n      setvar "buyThis\" 1\n'

    for i in range(-maxPrice+1,minPrice):
        if i % 1000 == 0:
            for j in range(i - 3, i + 4):
                if j % 1000 == 0 or j % 500 == 0 or j % 100 == 0 or j % 50 or j % 5:
                    continue
                outStr += f'    elseif "Price: {-j} " in "desc"\n      setvar "buyThis\" 1\n'  
        elif i % 500 == 0:
            for j in range(i - 2, i + 3):
                if j % 1000 == 0 or j % 500 == 0 or j % 100 == 0 or j % 50 or j % 5:
                    continue
                outStr += f'    elseif "Price: {-j} " in "desc"\n      setvar "buyThis\" 1\n'
        elif i % 100 == 0:
            for j in range(i - 1, i + 2):
                if j % 1000 == 0 or j % 500 == 0 or j % 100 == 0 or j % 50 or j % 5:
                    continue
                outStr += f'    elseif "Price: {-j} " in "desc"\n      setvar "buyThis\" 1\n'     

    pyperclip.copy(outStr)



def main():
    SkillScrollStocker()
    # SimpleStocker()

main()


