import re
price_cell = "💰\n        \n        1,847"
price_cell_sanitized = re.sub(r"\D",'',price_cell)

print(float(price_cell_sanitized))