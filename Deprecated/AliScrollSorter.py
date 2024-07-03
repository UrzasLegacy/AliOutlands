#import matplotlib.pyplot as plt

def get_grid_coords(start_x=1,start_y=1,end_x=20,end_y=20,x_offset=1,y_offset=1,x_on_y_offset=0):
    start_x, start_y = [44,65]
    end_x, end_y = [164,143]

    x_offset = 7
    x_on_y_offset = 6 # x adjustment on each new row for a slanted grid
    y_offset = 6

    x_range = end_x - start_x #120
    y_range = end_y - start_y #78

    rows = 14 #int(y_range / y_offset) + 1 #14
    cols = 7#int((x_range - ((rows - 1) * x_on_y_offset)) / x_offset) # 7

    grid = [[None for _ in range(cols)] for _ in range(rows)]
    print(rows)

    print(cols)
    for row in range(rows):
        hopY = start_y + (y_offset * row)
        for col in range(cols):
            hopX = start_x + (x_offset * col) + (x_on_y_offset * row)
            cell_coord = {"x":hopX,"y":hopY}
            grid[row][col] = cell_coord
    return grid


grid = get_grid_coords()
#print(grid)


def Plot_Points():
    # Use matplotlib to plot the grid points
    plt.figure(figsize=(19, 12))  # Set the figure size to something appropriate
    for row in grid:
        for cell in row:
            plt.scatter(cell["x"], cell["y"])  # Plot each point
            plt.text(cell["x"], cell["y"] + 1.5, f'({cell["x"]},{cell["y"]})')  # Show coordinates

    # Set grid, labels, and title
    plt.grid(True)
    plt.xlabel('X coordinate')
    plt.ylabel('Y coordinate')
    plt.title('Grid Coordinates Visualization')
    plt.gca().invert_yaxis()
    # Show the plot with all points
    plt.show()




arr = [ 
    [{'x': 24,   'y': 65},   {'x': 31,  'y': 65},   {'x': 38,  'y': 65},    {'x': 45,  'y': 65},   {'x': 52,  'y': 65},   {'x': 59,  'y': 65},   {'x': 66,  'y': 65}],
    [{'x': 30,   'y': 71},   {'x': 37,  'y': 71},   {'x': 44,  'y': 71},    {'x': 51,  'y': 71},   {'x': 58,  'y': 71},   {'x': 65,  'y': 71},   {'x': 72,  'y': 71}],
    [{'x': 36,   'y': 77},   {'x': 43,  'y': 77},   {'x': 50,  'y': 77},    {'x': 57,  'y': 77},   {'x': 64,  'y': 77},   {'x': 71,  'y': 77},   {'x': 78,  'y': 77}],
    [{'x': 42,   'y': 83},   {'x': 49,  'y': 83},   {'x': 56,  'y': 83},    {'x': 63,  'y': 83},   {'x': 70,  'y': 83},   {'x': 77,  'y': 83},   {'x': 84,  'y': 83}],
    [{'x': 48,   'y': 89},   {'x': 55,  'y': 89},   {'x': 62,  'y': 89},    {'x': 69,  'y': 89},   {'x': 76,  'y': 89},   {'x': 83,  'y': 89},   {'x': 90,  'y': 89}],
    [{'x': 54,   'y': 95},   {'x': 61,  'y': 95},   {'x': 68,  'y': 95},    {'x': 75,  'y': 95},   {'x': 82,  'y': 95},   {'x': 89,  'y': 95},   {'x': 96,  'y': 95}],
    [{'x': 60,   'y': 101},  {'x': 67,  'y': 101},  {'x': 74,  'y': 101},   {'x': 81,  'y': 101},  {'x': 88,  'y': 101},  {'x': 95,  'y': 101},  {'x': 102, 'y': 101}],
    [{'x': 66,   'y': 107},  {'x': 73,  'y': 107},  {'x': 80,  'y': 107},   {'x': 87,  'y': 107},  {'x': 94,  'y': 107},  {'x': 101, 'y': 107},  {'x': 108, 'y': 107}],
    [{'x': 72,   'y': 113},  {'x': 79,  'y': 113},  {'x': 86,  'y': 113},   {'x': 93,  'y': 113},  {'x': 100, 'y': 113},  {'x': 107, 'y': 113},  {'x': 114, 'y': 113}],
    [{'x': 78,   'y': 119},  {'x': 85,  'y': 119},  {'x': 92,  'y': 119},   {'x': 99,  'y': 119},  {'x': 106, 'y': 119},  {'x': 113, 'y': 119},  {'x': 120, 'y': 119}],
    [{'x': 84,   'y': 125},  {'x': 91,  'y': 125},  {'x': 98,  'y': 125},   {'x': 105, 'y': 125},  {'x': 112, 'y': 125},  {'x': 119, 'y': 125},  {'x': 126, 'y': 125}],
    [{'x': 90,   'y': 131},  {'x': 97,  'y': 131},  {'x': 104, 'y': 131},   {'x': 111, 'y': 131},  {'x': 118, 'y': 131},  {'x': 125, 'y': 131},  {'x': 132, 'y': 131}],
    [{'x': 96,   'y': 137},  {'x': 103, 'y': 137},  {'x': 110, 'y': 137},   {'x': 117, 'y': 137},  {'x': 124, 'y': 137},  {'x': 131, 'y': 137},  {'x': 138, 'y': 137}],
    [{'x': 102,  'y': 143},  {'x': 109, 'y': 143},  {'x': 116, 'y': 143},   {'x': 123, 'y': 143},  {'x': 130, 'y': 143},  {'x': 137, 'y': 143},  {'x': 144, 'y': 143}]
]

# Given the new requirement, we need to iterate over the array in 'slices' of three rows at a time, then within those slices,
# take elements column by column.

# This function will take a slice of the array (3 rows) and collect elements column by column.
def collect_by_columns(slice_of_three):
    collected_elements = []
    # We assume each row in the slice has the same number of columns, so we use the first row to determine the loop range.
    for col_index in range(len(slice_of_three[0])):  
        for row in slice_of_three:
            collected_elements.append(row[col_index])
    return collected_elements

# We will use a loop to go through the array in slices of three rows at a time.
sequenced_arr_by_threes = []
for i in range(0, len(grid), 3):  # Step by three rows at a time
    # Get a slice of three rows, or remaining rows if fewer than three at the end.
    three_row_slice = grid[i:i+3]  
    # Collect elements from the current slice, column by column.
    sequenced_arr_by_threes.extend(collect_by_columns(three_row_slice))

# Output the new sequenced list
print(sequenced_arr_by_threes)  # Show the first 21 elements to check the pattern

scrolls = { #exact string MATTERS
    "alchemy": 30000,
    "animal lore": 19000,
    "animal taming": 19000,
    "carpentry": 9000,
    "arms lore": 9000,
    "begging": 9000,
    "blacksmithy": 9000,
    "camping": 10000,
    "cartography": 9000,
    "chivalry": 22000,
    "cooking": 10000,
    "detect hidden": 13000,
    "lockpicking": 17000,
    "discordance": 9000,
    "fishing": 9000,
    "forensic eval": 11000,
    "herding": 19000,
    "inscription": 23000,
    "item id": 9000,
    "lumberjacking": 9000,
    "mining": 9000,
    "musicianship": 9000,
    "necromancy": 24000,
    "peacemaking": 9000,
    "poisoning": 10000,
    "provocation": 9000,
    "spirit speak": 9000,
    "stealth": 16000,
    "tailoring": 40000,
    "taste id": 12000,
    "tinkering": 9000,
    "tracking": 10000,
    "veterinary": 19000,
}

coord_list = [
    {'x': 24, 'y': 65}, {'x': 30, 'y': 71}, {'x': 36, 'y': 77}, {'x': 31, 'y': 65}, {'x': 37, 'y': 71}, {'x': 43, 'y': 77}, {'x': 38, 'y': 65}, 
    {'x': 44, 'y': 71}, {'x': 50, 'y': 77}, {'x': 45, 'y': 65}, {'x': 51, 'y': 71}, {'x': 57, 'y': 77}, {'x': 52, 'y': 65}, {'x': 58, 'y': 71}, 
    {'x': 64, 'y': 77}, {'x': 59, 'y': 65}, {'x': 65, 'y': 71}, {'x': 71, 'y': 77}, {'x': 66, 'y': 65}, {'x': 72, 'y': 71}, {'x': 78, 'y': 77}, 
    {'x': 42, 'y': 83}, {'x': 48, 'y': 89}, {'x': 54, 'y': 95}, {'x': 49, 'y': 83}, {'x': 55, 'y': 89}, {'x': 61, 'y': 95}, {'x': 56, 'y': 83}, 
    {'x': 62, 'y': 89}, {'x': 68, 'y': 95}, {'x': 63, 'y': 83}, {'x': 69, 'y': 89}, {'x': 75, 'y': 95}, {'x': 70, 'y': 83}, {'x': 76, 'y': 89}, 
    {'x': 82, 'y': 95}, {'x': 77, 'y': 83}, {'x': 83, 'y': 89}, {'x': 89, 'y': 95}, {'x': 84, 'y': 83}, {'x': 90, 'y': 89}, {'x': 96, 'y': 95}, 
    {'x': 60,'y': 101}, {'x': 66,'y': 107}, {'x': 72,'y': 113}, {'x': 67,'y': 101}, {'x': 73,'y': 107}, {'x': 79,'y': 113}, {'x': 74,'y': 101},
    {'x': 80,'y': 107}, {'x': 86,'y': 113}, {'x': 81,'y': 101}, {'x': 87,'y': 107}, {'x': 93,'y': 113}, {'x': 88,'y': 101}, {'x': 94,'y': 107},
    {'x': 100,'y':113}, {'x': 95,'y': 101}, {'x': 101,'y':107}, {'x': 107,'y':113}, {'x': 102,'y':101}, {'x': 108,'y':107}, {'x': 114,'y':113},
    {'x': 78,'y': 119}, {'x': 84,'y': 125}, {'x': 90,'y': 131}, {'x': 85,'y': 119}, {'x': 91,'y': 125}, {'x': 97,'y': 131}, {'x': 92,'y': 119}, 
    {'x': 98,'y': 125}, {'x': 104,'y':131}, {'x': 99,'y': 119}, {'x': 105,'y':125}, {'x': 111,'y':131}, {'x': 106,'y':119}, {'x': 112,'y':125},
    {'x': 118,'y':131}, {'x': 113,'y':119}, {'x': 119,'y':125}, {'x': 125,'y':131}, {'x': 120,'y':119}, {'x': 126,'y':125}, {'x': 132,'y':131},
    {'x': 96,'y': 137}, {'x': 102,'y':143}, {'x': 103,'y':137}, {'x': 109,'y':143}, {'x': 110,'y':137}, {'x': 116,'y':143}, {'x': 117,'y':137},
    {'x': 123,'y':143}, {'x': 124,'y':137}, {'x': 130,'y':143}, {'x': 131,'y':137}, {'x': 137,'y':143}, {'x': 138,'y':137}, {'x': 144,'y':143}
]