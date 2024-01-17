import numpy as np
import matplotlib.pyplot as plt

# Set dimensions
nx = 250
ny = 250

# Create map
grid = np.ones((nx,ny))
wx = nx//10 + 1
wy = ny//10 + 1
grid[int(.2*nx):int(.2*nx)+wx,int(.1*ny):int(.1*ny)+wy] = 0
grid[int(.1*nx):int(.1*nx)+wx,int(.5*ny):int(.5*ny)+wy] = 0
grid[int(.6*nx):int(.6*nx)+wx,int(.6*ny):int(.6*ny)+wy] = 0
grid[int(.2*nx):int(.8*nx)+wx,int(.6*ny):int(.6*ny)+wy] = 0

# Display map
plt.figure("Map")
plt.imshow(np.transpose(grid))

# Set viewpoint
x0 = nx//2
y0 = ny//2



# Define visibility function
def visibility_from_corner(grid):
    for x in range(grid.shape[0]):
        for y in range(int(x==0), grid.shape[1]):
            grid[x,y] *= (x*grid[x-1,y] + y*grid[x,y-1]) / (x + y)
    grid[:] = (grid >= 0.5)

# Compute visibility
visibility_from_corner(grid[x0:,y0:])
visibility_from_corner(grid[x0::-1,y0:])
visibility_from_corner(grid[x0::-1,y0::-1])
visibility_from_corner(grid[x0:,y0::-1])

# Display visibility
plt.figure("Visibility")
plt.imshow(np.transpose(grid))
plt.show()