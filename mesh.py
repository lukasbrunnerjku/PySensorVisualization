from OpenGL.GL import *
from ctypes import c_void_p
import numpy as np

class Mesh():

    def __init__(self, data, indices):
        self.data = data
        self.indices = indices

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
        stride = self.data.strides[0]

        # positions:
        offset = c_void_p(0)
        glEnableVertexAttribArray(0) # layout(location = 0)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, stride, offset)
        # colors:
        offset = c_void_p(self.data.dtype["position"].itemsize)
        glEnableVertexAttribArray(1) # layout(location = 1)
        glVertexAttribPointer(1, 4, GL_FLOAT, False, stride, offset)

        # unbind buffers:
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def draw(self):
        # bind the VAO, it contains all info about the buffers and attributes:
        glBindVertexArray(self.VAO)
        # draw the data with the help of the indices:
        offset = c_void_p(0)
        glDrawElements(GL_TRIANGLES, self.indices.size, GL_UNSIGNED_INT, offset)
