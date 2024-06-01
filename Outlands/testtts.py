import pyperclip
def generate_comma_conditions_over_1mil():
    conditions = []
    for i in range(1000):
        part = f"{i:03}"
        conditions.append(f'",{part}," in "numberString"')
    return "if " + " or ".join(conditions) + """
    return false
    endif"""


def generate_comma_conditions_over_100k():
    conditions = []
    for i in range(1000):
        new_i = 1000 - i
        part = f"{new_i:03}"
        conditions.append(f'"Price: {part}," in "numberString"')
    return "if " + " or ".join(conditions) + """
    stop
endif"""

# Example usage
comma_conditions = generate_comma_conditions_over_100k()
pyperclip.copy(comma_conditions)
