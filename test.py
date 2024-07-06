def save_user_data():
    import json
    my_vendors = [0x2A2814, 0x2A280D, 0x2A27FA, 0x2A27F3, 0x2A281C, 0x2A2830, 0x2A2835, 0x2A283D]
    filename = f"vendor_info.json"
    with open(filename, "w") as file:
        json.dump(my_vendors, file, indent=4)
save_user_data()