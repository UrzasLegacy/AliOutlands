# Define the size of the grid
rows, cols = 7, 7  # 7x7 grid

# Prepare the numbers in advance
sequence = list(range(1, rows*cols+1))
sequence_index = 0  # Start with the first number in the sequence

# Create the grid
grid = [[None for _ in range(cols)] for _ in range(rows)]

# Fill the grid with numbers
for row in range(rows):
    # Start from 'row' index as an offset for diagonal pattern
    for col in range(row, cols):
        if sequence_index < len(sequence):
            grid[row][col-row] = sequence[sequence_index]
            sequence_index += 1

# Print the grid
for row in grid:
    print(' '.join(['{:4}'.format(item if item is not None else '') for item in row]))
