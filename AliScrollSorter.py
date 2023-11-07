import matplotlib.pyplot as plt

def get_grid_coords(start_x=1,start_y=1,end_x=20,end_y=20,x_offset=1,y_offset=1,x_on_y_offset=0):
    start_x, start_y = [24,65]
    end_x, end_y = [164,143]

    x_offset = 7
    x_on_y_offset = 6 # x adjustment on each new row for a slanted grid
    y_offset = 6

    x_range = end_x - start_x #120
    y_range = end_y - start_y #78

    rows = int(y_range / y_offset) + 1 #14
    cols = int((x_range - ((rows - 1) * x_on_y_offset)) / x_offset) + 1 # 7

    grid = [[None for _ in range(cols)] for _ in range(rows)]

    for row in range(rows):
        hopY = start_y + (y_offset * row)
        for col in range(cols):
            hopX = start_x + (x_offset * col) + (x_on_y_offset * row)
            cell_coord = {"x":hopX,"y":hopY}
            grid[row][col] = cell_coord
    return grid

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