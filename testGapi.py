import gspread

# Authenticate with the service account JSON key file
gc = gspread.service_account(filename='outlands-pricesheet-594e57a3357a.json')

# Open a sheet from a spreadsheet by title
sh = gc.open("Outlands Pricesheet")

# Select worksheet by index. Worksheet indices are zero-based.
worksheet = sh.get_worksheet(0)

# Or by title
# worksheet = sh.worksheet("Sheet1")

# Update a range of cells using the top left corner address
worksheet.update(values=[
    [1,3,5,7],
    [3,4],
    [5,6,7,8],
    [1,3,5,7,5,7,5,7,5,7,5,7,5,7,5,7],
    [3,4],
    [5,6,7,8],
    [1,3,5,7],
    [3,4],
    [5,6,7,8],
    [1,3,5,7],
    [3,4,5,7,5,7,5,7,5,7,5,7,5,7],
    [5,6,7,8],
    [7,8,9,0]
    ], range_name='A2')

# If you want to append rows to your sheet
#worksheet.append_rows(values=[[5, 6], [7, 8]])
