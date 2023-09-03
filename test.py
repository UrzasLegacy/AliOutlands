dict1 = {'a': 1, 'b': 2}
dict2 = {'b': 3, 'c': 4}
dict3 = {'d': 5, 'e': 6}
combined = {**dict1, **dict2, **dict3}
print(combined)  # {'a': 1, 'b': 3, 'c': 4}