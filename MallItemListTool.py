from OutlandsUtils import *
import pyperclip

current_item_list_file = r"current_item_list.txt"

def get_item_list():
    with open(current_item_list_file,"r") as file:
        current_items = file.read()
    return current_items

def write_clipboard_to_item_list():
    current_item_list = pyperclip.paste()
    with open(current_item_list_file,"w") as file:
        file.write(current_item_list)

before = get_item_list()
after = "4025|4026"

def main():
    temp = PipedListConcatenator(before, after)
    #temp = PipedListDiffer(before, after)
    #temp = PipedListSubtract(before, after)

    splits = PipedListSplitter(before,250)
    pyperclip.copy(splits)

    #write_clipboard_to_item_list()

if __name__ == "__main__":
    main()

