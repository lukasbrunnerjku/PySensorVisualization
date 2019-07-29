from OpenGL.GL import *
from ctypes import c_void_p
import numpy as np

class Mesh():

    def __init__(self, data, indices, drawing_info=None):
        # use (structured) numpy arrays, their memory layout is sequential:
        self.data = data
        self.indices = indices
        # mode, offset and size for glDrawElements!
        # drawing_info = {"modes":[], "offsets":[], "sizes":[]}
        self.drawing_info = drawing_info

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
        stride = self.data.strides[0]

        # positions:
        offset = c_void_p(0)
        glEnableVertexAttribArray(0) # layout(location = 0)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, stride, offset)
        # colors:
        offset = c_void_p(self.data.dtype["position"].itemsize) # OFFSET IS ALWAYS IN BYTES
        glEnableVertexAttribArray(1) # layout(location = 1)
        glVertexAttribPointer(1, 4, GL_FLOAT, False, stride, offset)

        # unbind buffers:
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def _draw(self, mode, size, offset):
        # bind the VAO, it contains all info about the buffers and attributes:
        glBindVertexArray(self.VAO)
        # to calculate the offset in bytes as required:
        offset = c_void_p(offset * self.indices.itemsize) # OFFSET IS ALWAYS IN BYTES
        # draw the data with the help of the indices:
        glDrawElements(mode, size, GL_UNSIGNED_INT, offset)

    def draw(self):
        if self.drawing_info == None:
            self._draw(GL_TRIANGLES, self.indices.size, 0)
        else:
            # drawing_info = {"modes":[], "offsets":[], "sizes":[]}
            for mode, offset, size in zip(self.drawing_info["modes"],
                                          self.drawing_info["offsets"],
                                          self.drawing_info["sizes"]):
                self._draw(mode, size, offset)

    def __repr__(self):
        return "data: {}\nindices: {}\ndrawing_info: {}".format(self.data, self.indices, self.drawing_info)
