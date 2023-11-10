import matplotlib.pyplot as plt

def get_grid_coords(start_x=1,start_y=1,end_x=20,end_y=20,x_offset=1,y_offset=1,x_on_y_offset=0):
    start_x, start_y = [24,65]
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
print(grid)
pass
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


# 0, 1, 2, 3, 4, 5, 6
# 7, 8, 9,10,11,12,13
# 14,15,16,17,18,19,20
# 21,22,23,24,25,26,27
# 28,29,30,31,32,33,34
# 35,36,37,38,39,40,41

grid = [[None for _ in range(7)] for _ in range(14)]

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
    [{'x': 102,  'y': 143},  {'x': 109, 'y': 143},  {'x': 116, 'y': 143},   {'x': 123, 'y': 143},  {'x': 130, 'y': 143},  {'x': 137, 'y': 143},  {'x': 144, 'y': 143}
    ]
]


