def parse_log_to_object():
    my_vendors = user_config['vendor_info']
    vendors = {}
    current_vendor = None
    latest_log = get_most_recent_log()
    if not latest_log:
        return False
    character_name = None
    pass_flag = False
    my_vendor_objs = []
    
    with open(latest_log, 'r', encoding='utf-8') as file:
        for line in file:
            if "System: Welcome" in line:
                match = re.search(r'System: Welcome (.+)!', line)
                character_name = match.group(1) if match else 'Invalid Name'
            elif "…item" in line and current_vendor:
                if "Not for sale" not in line:
                    match = re.search(r'ID:(\d+) Price: ([\d,]+) (.+?)(?:( : (\d+))(.*))?$', line)
                    if match:
                        item_id = int(match.group(1))
                        item_price = int(match.group(2).replace(',', ""))
                        item_description = match.group(3)
                        if " dye " in item_description and ") (hue" in item_description:
                            item_description = item_description.split(") (hue")[0] + ")"
                        item_match = f"{item_description}{match.group(4)}{match.group(6)}" if match.group(6) else item_description
                        item_quantity = int(match.group(5)) if match.group(5) else 1
                        item_suffix = match.group(6) if match.group(5) else ''
                        item_description += item_suffix if item_suffix else ''
                        item_unitprice = round(item_price / item_quantity, 4)
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
            elif "…vendorEnd" in line and current_vendor:
                if current_vendor['id'] in my_vendors:
                    my_vendor_objs.append(current_vendor)
                current_vendor = None
            elif "System: Current location is" in line:
                match = re.search(r'Current location is \((\d+), (\d+)', line)
                if match:
                    x1, y1 = int(match.group(1)), int(match.group(2))
                    location = f"{x1}, {y1}"
                    closest = min(my_locations.items(), key=lambda loc: get_distance(x1, y1, int(loc[1][0]), int(loc[1][1])), default=('N/A',))[0]
                    location_name = closest
                else:
                    location = "0,0"
                    location_name = "N/A"
    
    if pass_flag and my_vendor_objs:
        handle_my_vendors(my_vendor_objs)
        return vendors, latest_log, character_name
    
    return latest_log, character_name if character_name else False