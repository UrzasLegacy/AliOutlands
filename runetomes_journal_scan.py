
import re
import json
import pyperclip

def clipboard_runetome_dictionary(filename="runetomes.json", REG_EXP=r"ID:(\d+).*Name:(.+?) a rune tome"):
    with open(filename) as file:
        line_list = file.read().strip().split('\n') or []

    tome_dictionary = {match.group(2): match.group(1) for line in line_list if (match := re.search(REG_EXP, line))}

    sorted_tome_dictionary = {
        k: v for (k, v) in sorted(
            tome_dictionary.items(), key=lambda x: (x[0].split()[0], int(re.search(r'\d+', x[0]).group()) if re.search(r'\d+', x[0]) else 0)
            )
        }
    
    pyperclip.copy(json.dumps(sorted_tome_dictionary, indent=2))

if __name__ == "__main__":
    clipboard_runetome_dictionary()
