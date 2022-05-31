import numpy as np 


Filter = np.array( [
    [-1,  1, -1],
    [ 1,  1,  1],
    [-1,  1, -1]
] )

image = np.array([
    [-1, -1, -1, -1, -1, -1, -1],
    [-1,  1, -1, -1,  1, -1, -1],
    [-1,  1, -1,  1,  1,  1, -1],
    [-1,  1, -1, -1,  1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1],
    [-1,  1,  1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1]
])

output = []
for x in range(1, 6):
    for y in range(1, 6):
        convolution = np.dot(Filter.T, image[y-1:y+2, x-1:x+2])
        output.append((x-1, y-1, np.sum(convolution)))
print(output)
print(len(output))
print(max(output, key = lambda pixel: pixel[2]))