import numpy as np
import glm
from OpenGL.GL import *

from mesh import Mesh

class Circle():

    def create(r, h, color, n=32, mesh=True):
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

        if mesh:
            data = np.zeros(len(positions), [("position", np.float32, 3),
                                             ("color",    np.float32, 4)])
            data["position"] = positions
            data["color"] = colors

            indices = np.array(indices, dtype=np.uint32)
            # no need for further drawing information (see mesh.py):
            return Mesh(data, indices)
        else:
            # to integrate the circle in a more complex model:
            return positions, colors, indices


class Cylinder():

    def create(r, heights, n=32, mesh=True):
        positions, colors, indices, offsets = [], [], [], []
        drawing_info = {"modes":[], "offsets":[], "sizes":[]}
        test_color = [[1.0, 0.0, 0.0, 1.0],
                      [0.0, 1.0, 0.0, 1.0],
                      [0.0, 0.0, 1.0, 1.0],
                      [1.0, 0.0, 0.0, 1.0],
                      [0.0, 1.0, 0.0, 1.0],
                      [0.0, 0.0, 1.0, 1.0]]
        for layer_nr, h in enumerate(heights):
            _positions, _colors, _indices = Circle.create(r, h, test_color[layer_nr], n=n, mesh=False)
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

        if mesh:
            data = np.zeros(len(positions), [("position", np.float32, 3),
                                             ("color",    np.float32, 4)])
            data["position"] = positions
            data["color"] = colors
            # flatten the indices:
            #indices = list(itertools.chain(*indices))

            indices = np.array(indices, dtype=np.uint32)
            return Mesh(data, indices, drawing_info)
        else:
            return positions, indices, drawing_info
