from OpenGL.GL import *
from ctypes import c_void_p
import numpy as np

class Mesh():

    def __init__(self, positions, colors, indices):
        self.positions = positions
        self.colors = colors
        self.indices = indices

        # use numpy to structure the data (memory layout is sequential):
        data = np.zeros(len(positions), [("position", np.float32, 3),
                                         ("color",    np.float32, 4)])
        data["position"] = positions
        data["color"] = colors

        indices = np.array(indices, dtype=np.uint32)

        self.data = data
        self.indices = indices
        # vartex array object:
        self.VAO = glGenVertexArrays(1)
        glBindVertexArray(self.VAO)

        # vertex buffer object:
        self.VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, self.data.nbytes, self.data, GL_STATIC_DRAW)

        # element buffer object:
        self.EBO = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        # number of bytes to go from one vertex to the next:
        self.stride = self.data.strides[0]
        # using np.float32 for both position and color:
        # self.stride = 3 * 4 + 4 * 4 because 3 values for position each 4 bytes
        # and 4 values for color each 4 bytes!

        # positions:
        offset = c_void_p(0)
        glEnableVertexAttribArray(0) # layout(location = 0)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, self.stride, offset)
        # colors:
        offset = c_void_p(self.data.dtype["position"].itemsize) # OFFSET IS ALWAYS IN BYTES
        glEnableVertexAttribArray(1) # layout(location = 1)
        glVertexAttribPointer(1, 4, GL_FLOAT, False, self.stride, offset)

        # unbind buffers:
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def draw(self, mode, size, offset):
        # bind the VAO, it contains all info about the buffers and attributes:
        glBindVertexArray(self.VAO)
        # to calculate the offset in bytes as required:
        offset = c_void_p(offset * self.indices.itemsize) # OFFSET IS ALWAYS IN BYTES
        # draw the data with the help of the indices:
        glDrawElements(mode, size, GL_UNSIGNED_INT, offset)

    def __repr__(self):
        return "data:\n{}\nindices:\n{}\n".format(self.data, self.indices)
