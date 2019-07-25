import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

import sys
import math

import numpy as np
from ctypes import c_void_p

# my modules:
from shader import *

# create a window, OpenGL are callable after window initialization!
pygame.init()
pygame.display.set_mode((800, 600), flags=DOUBLEBUF|OPENGL)

# OpenGL initialization:
glViewport(0, 0, 800, 600)
glEnable(GL_DEPTH_TEST)
glClearColor(0.5, 0.5, 0.5, 1.0)

# create the shader program to run on the gpu:
shader = Shader("shader.vs", "shader.fs")
shader.use()

# create vertices:
data = np.zeros(8, [("position", np.float32, 3),
                    ("color",    np.float32, 4)])
data["position"] = [[ 1, 1, 1], [-1, 1, 1], [-1,-1, 1], [ 1,-1, 1],
                    [ 1,-1,-1], [ 1, 1,-1], [-1, 1,-1], [-1,-1,-1]]
data["color"]    = [[0, 1, 1, 1], [0, 0, 1, 1], [0, 0, 0, 1], [0, 1, 0, 1],
                    [1, 1, 0, 1], [1, 1, 1, 1], [1, 0, 1, 1], [1, 0, 0, 1]]

stride = data.strides[0]

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


# vertex buffer object:
VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

# element buffer object:
EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

# positions:
offset = c_void_p(0)
glEnableVertexAttribArray(0) # layout(location = 0)
glVertexAttribPointer(0, 3, GL_FLOAT, False, stride, offset)
# colors:
offset = c_void_p(data.dtype["position"].itemsize)
glEnableVertexAttribArray(1) # layout(location = 1)
glVertexAttribPointer(1, 4, GL_FLOAT, False, stride, offset)

# game loop
while True:
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    # draw
    offset = c_void_p(0)
    glDrawElements(GL_TRIANGLES, indices.size, GL_UNSIGNED_INT, offset)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == K_w:
                print("w")
            if event.key == K_a:
                print("a")
            if event.key == K_s:
                print("s")
            if event.key == K_d:
                print("d")

    # delay in ms
    pygame.time.wait(10)

    # when using the OPENGL pygame display mode this is equivalent to
    # the swap buffer function, we need that to actually see something!
    pygame.display.flip()
