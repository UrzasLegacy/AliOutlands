import re
import pyperclip

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
    total_stacks = 21

    start_pos = "X=59, Y=132, Z=0"
    end_pos = "X=94, Y=143, Z=0"
    x_offset = 3
    y_offset = 11

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
        wait 650
        if {price} > 0
            promptresponse {price}
            wait 325
            getlabel "itemToMove" "itemDesc"
            if ": {price}" in "itemDesc"
            else
                wait 325
                lift "itemToMove" {quant}
                drop backpack 0 0 0
                pushlist "coordList" y "front"
                pushlist "coordList" x "front"
                continue
            endif
        endif
        @ignore "itemToMove"
    endif
endwhile'''

    pyperclip.copy(out_str)


def SkillScrollStocker():
    pass

def main():
    SimpleStocker()





