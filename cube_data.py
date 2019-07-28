import numpy as np

# create a colored cube, use GL_TRIANGLES as drawing mode:
data = np.zeros(8, [("position", np.float32, 3),
                    ("color",    np.float32, 4)])
data["position"] = [[ 1, 1, 1], [-1, 1, 1], [-1,-1, 1], [ 1,-1, 1],
                    [ 1,-1,-1], [ 1, 1,-1], [-1, 1,-1], [-1,-1,-1]]
data["color"]    = [[0, 1, 1, 1], [0, 0, 1, 1], [0, 0, 0, 1], [0, 1, 0, 1],
                    [1, 1, 0, 1], [1, 1, 1, 1], [1, 0, 1, 1], [1, 0, 0, 1]]

# front faces are defined counter clockwise (face culling)
indices = np.array([
# front
7, 5, 6,
7, 4, 5,
# back
1, 0, 2,
0, 3, 2,
# right side
4, 0, 5,
4, 3, 0,
# left side
7, 6, 1,
1, 2, 7,
# top
1, 6, 5,
5, 0, 1,
# bottom
7, 2, 3,
3, 4, 7
], dtype=np.uint32)
