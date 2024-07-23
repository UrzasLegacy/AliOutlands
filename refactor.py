def parse_log_to_object():
    #my_vendors = [0x2A2814, 0x2A280D, 0x2A27FA, 0x2A27F3, 0x2A281C, 0x2A2830, 0x2A2835, 0x2A283D]
    my_vendors = user_config['vendor_info']
    vendors = {}
    current_vendor = None
    latest_log = get_most_recent_log()
    if not latest_log:
        return False
    character_name = None
    pass_flag = False
    my_vendor_objs = []
    with open(latest_log, 'r', encoding='utf-8') as lines:
        for line in lines:
            if "System: Welcome" in line:
                match = re.search(r'System: Welcome (.+)!', line)
                character_name = match.group(1) if match else 'Invalid Name'
            elif "…item" in line and current_vendor is not None:
                if "Not for sale" in line:
                    continue
                match = re.search(r'ID:(\d+) Price: ([\d,]+) (.+?)(?:( : (\d+))(.*))?$', line)
                if match:
                    item_id = int(match.group(1))
                    item_price = int(match.group(2).replace(',',""))
                    item_description = match.group(3)
                    if " dye " in item_description and ") (hue" in item_description:
                        item_description = item_description.split(") (hue")[0] + ")"
                    item_match = f"{item_description}{match.group(4)}{match.group(6)}" if match.group(6) else item_description
                    item_quantity = int(match.group(5)) if match.group(5) else 1
                    item_suffix = match.group(6) if match.group(5) else ''
                    if(item_suffix):
                        item_description += item_suffix
                    item_unitprice = round(item_price / item_quantity,4)
                    item = {
                        'id': item_id,
                        "price": item_unitprice,
                        "description": item_description,
                        "full_description": item_match,
                        "quantity": item_quantity,
                        'location': location,
                        'location_name': location_name
                    }
                    pass_flag = True
                    current_vendor["items"].append(item)
                else:
                    print('parse_log_to_object: missing: ' + line)
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
                        x2 = int(tuple_loc[0])
                        y2 = int(tuple_loc[1])
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
    if character_name:
        return (latest_log, character_name)