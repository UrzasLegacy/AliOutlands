rows = 4  # Number of rows
cols = 3  # Number of columns

# Create an empty grid
grid = [['-' for _ in range(cols)] for _ in range(rows)]

# Populate the grid using zero-based index, modulo, and floor division
for i in range(rows * cols):
    row_index = i // cols
    col_index = i % cols
    grid[row_index][col_index] = i

# Print the grid
for row in grid:
    print(row)



