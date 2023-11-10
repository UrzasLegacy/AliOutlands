import re

# A simplified regex pattern which assumes:
# - 'item ID:' is followed by any digit (captured as the ID)
# - 'Price:' is followed by any digit or comma or period (captured as the price)
# - 'Description:' is optional and can contain any character (captured as the description)
# - Item name might be followed by extra details, which are captured until the end of the string
pattern = re.compile(r'item ID:(\d+)\s+Price: ([\d,]+)(?:\s+Description: - (.*?))?(.*?)(?::|\()')

def parse_item_string(item_string):
    match = pattern.search(item_string)
    if match:
        item_id, price, description, item_name_details = match.groups()
        # Further processing to clean up item_name_details
        # Remove leading and trailing spaces, and split based on ':' or '(' if needed
        item_name_details = item_name_details.strip()
        # Assume extra details are separated by ':' or '('
        details_split = re.split(r'[:\(]', item_name_details, 1)  # Split only once
        item_name = details_split[0].strip()
        extra_details = details_split[1].strip() if len(details_split) > 1 else ''
        return {
            'item_id': item_id,
            'price': price.replace(',', ''),  # Remove commas from price for consistency
            'description': description.strip() if description else '',  # Clean up description
            'item_name': item_name,
            'extra_details': extra_details  # Additional details like "(used to increase...)" or ": 10"
        }
    else:
        return None

# Test strings
test_strings = [
    "item ID:1496383994 Price: 21000 mastercrafting diagram",
    "item ID:1645918429 Price: 38000 animal taming skill mastery scroll : 2 (used to increase a player's skill cap for a skill by 1)",
    "item ID:1597891453 Price: 68000 bronze mastery chain link Poison Damage/Resist Ignore (+2.50%)",
    "item ID:1169137716 Price: 750000 Description: REDUCED PRICE invulnerability wooden shield"

]

# Parse test strings
parsed_items = [parse_item_string(s) for s in test_strings if parse_item_string(s) is not None]
parsed_items
