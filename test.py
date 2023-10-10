def exclude_leather(s: str) -> bool:
    exclusions = {'leather'}  # Add other words to this list as needed
    print(s.strip())
    return s in exclusions

# Test
string1 = 'leathers'
string2 = 'leather armor '
string3 = '  blue leather '

print(exclude_leather(string1))  # True
print(exclude_leather(string2))  # False
print(exclude_leather(string3))  # False