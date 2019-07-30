import numpy as np
import glm
from OpenGL.GL import *

from mesh import Mesh

# utility function:
def structure_model_data(positions, colors, indices):
    data = np.zeros(len(positions), [("position", np.float32, 3),
                                     ("color",    np.float32, 4)])
    data["position"] = positions
    data["color"] = colors

    indices = np.array(indices, dtype=np.uint32)
    return data, indices

class Circle():

    def __init__(self, r, h, color, n=32):
        positions = [[0.0, h, 0.0]]
        colors = [color]
        indices = [0]
        phi = 0.0
        deltaPhi = 360/n
        index = 1
        while phi < 360:
            x = glm.cos(glm.radians(phi))
            z = glm.sin(glm.radians(phi))
            positions.append([x, h, z])
            colors.append(color)
            # indices for GL_TRIANGLE_FAN
            indices.append(index)
            phi += deltaPhi
            index += 1
        indices.append(1)

        # contains entire circle information:
        self.positions = positions
        self.colors = colors
        self.indices = indices

    def getMesh(self):
        data, indices = structure_model_data(self.positions,
                                             self.colors,
                                             self.indices)

        # no need for further drawing information (see mesh.py):
        return Mesh(data, indices)

    def getStructuredData(self):
        data, indices = structure_model_data(self.positions,
                                             self.colors,
                                             self.indices)

        return data, indices

    def getRawData(self):
        # to integrate the circle in a more complex model:
        return self.positions, self.colors, self.indices


class Cylinder():

    def __init__(self, r, heights, layer_colors, n=32):
        positions, colors, indices, offsets = [], [], [], []
        drawing_info = {"modes":[], "offsets":[], "sizes":[]}

        for layer_nr, h in enumerate(heights):
            _positions, _colors, _indices = Circle(r,
                                                   h,
                                                   layer_colors[layer_nr],
                                                   n=n).getRawData()
            size_circle = len(_indices)
            drawing_info["modes"].append(GL_TRIANGLE_FAN)
            drawing_info["offsets"].append(layer_nr * size_circle)
            drawing_info["sizes"].append(size_circle)
            positions.extend(_positions)
            colors.extend(_colors)
            _indices = list(map(lambda x: x + layer_nr * (n + 1), _indices))
            indices.extend(_indices)

        offset_mantle = drawing_info["offsets"][-1] + size_circle
        # make a copy to loop through so the drawing info can be change:
        offsets = drawing_info["offsets"][:]
        # don't loop over last offset -> [:-1]
        for layer_nr, offset in enumerate(offsets[:-1]):
            _indices = []
            for i in range(offset + 1, offset + size_circle):
                _indices.append(indices[i])
                _indices.append(indices[i + size_circle])
            size_mantle = len(_indices)
            drawing_info["modes"].append(GL_TRIANGLE_STRIP)
            drawing_info["offsets"].append(offset_mantle + layer_nr * size_mantle)
            drawing_info["sizes"].append(size_mantle)
            indices.extend(_indices)

        # contains entire cylinder information:
        self.positions = positions
        self.colors = colors
        self.indices = indices
        self.drawing_info = drawing_info

    def getMesh(self):
        data, indices = structure_model_data(self.positions,
                                             self.colors,
                                             self.indices)

        # drawing information needed since multiple drawing modes
        # are required (see mesh.py):
        return Mesh(data, indices, self.drawing_info)

    def getStructuredData(self):
        data, indices = structure_model_data(self.positions,
                                             self.colors,
                                             self.indices)

        return data, indices, self.drawing_info

    def getRawData(self):
        # to integrate the circle in a more complex model:
        return self.positions, self.colors, self.indices, self.drawing_info
