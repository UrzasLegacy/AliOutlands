import re

def format_ingame_name(name_string, quantity_string, remove_quantity=False):
    match = re.search(r"(.+?)(?:( : (\d+))(.*))?$", name_string)
    if match:
        item_description = match.group(1)
        item_suffix = match.group(4) if match.group(4) else ""
        if remove_quantity:
            item_description += item_suffix
            return item_description
        item_quantity = match.group(2) if match.group(2) else ""
        item_description += item_quantity ; item_description += item_suffix

        item_match = f"{item_description}{match.group(2)}" if match.group(2) else item_description




    match = re.search(r'(.+?)(?:( : (\d+))(.*))?$', name_string)
    if match:
        item_description = match.group(1)
        item_match = f"{item_description}{match.group(2)}" if match.group(2) else item_description
        item_quantity = int(match.group(3)) if match.group(3) else 1
        item_suffix = match.group(4) if match.group(4) else ''
        if(item_suffix):
            item_description += item_suffix