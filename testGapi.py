import gspread


def send_to_outlands_pricesheet():
    gclient = gspread.service_account(filename='outlands-pricesheet-594e57a3357a.json')

    # Open a sheet from a spreadsheet by title
    spreadsheet = gclient.open("Outlands Pricesheet")

    # Select worksheet by index. Worksheet indices are zero-based.
    worksheet = spreadsheet.get_worksheet(0)

    # Or by title
    # worksheet = spreadsheet.worksheet("Sheet1")

    # Update a range of cells using the top left corner address
    worksheet.update(values=[
            []
        ], range_name='B3')

    # If you want to append rows to your sheet
    #worksheet.append_rows(values=[[5, 6], [7, 8]])
