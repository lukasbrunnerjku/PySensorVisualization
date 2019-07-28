import pygame
from pygame.locals import *

from OpenGL.GL import *
#from OpenGL.GLU import *

import sys
import math
import glm
import time

import numpy as np

# my modules:
from shader import Shader
from mesh import Mesh
from camera import Camera

# create a window, OpenGL are callable after window initialization!
pygame.init()
width = 800
height = 600
pygame.display.set_mode((width, height), flags=DOUBLEBUF|OPENGL)

# OpenGL initialization:
glViewport(0, 0, width, height)
glEnable(GL_DEPTH_TEST)
glClearColor(0.5, 0.5, 0.5, 1.0)

# create the shader program to run on the gpu:
shader = Shader("shader.vs", "shader.fs")
shader.use()

# set the model, view and projection matrices:
model = glm.mat4()
model = glm.scale(model, glm.vec3(0.5, 0.5, 0.5))
shader.setMatrix("model", model)

camera = Camera()
view = camera.getViewMatrix()
shader.setMatrix("view", view)

projection = glm.perspective(glm.radians(45.0), width/height, 0.1, 100.0)
shader.setMatrix("projection", projection)


def create_circle(r, h, color, n=32, mesh=True):
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
        return Mesh(data, indices)
    else:
        return positions, colors, indices


def create_cylinder(r, heights, n=32, mesh=True):
    positions, colors, indices, offsets = [], [], [], []
    drawing_info = {"modes":[], "offsets":[], "sizes":[]}
    test_color = [[1.0, 0.0, 0.0, 1.0], [0.0, 1.0, 0.0, 1.0]]
    for layer_nr, h in enumerate(heights):
        _positions, _colors, _indices = create_circle(r, h, test_color[layer_nr], n=n, mesh=False)
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

# create an object ready for drawing:
positions, indices, drawing_info = create_cylinder(1.0, [0.5, 1.5], mesh=False)
print(positions)
print("pos:", positions[indices[0]], positions[indices[34]], positions[indices[68]])
print(indices)
print(drawing_info)

mesh = create_cylinder(1.0, [0.5, 1.5])

# initialize the last_frame_time:
last_frame_time = time.time()

# initialize last mouse position to be centered in screen
last_x = width/2
last_y = height/2
# set the mouse position to the center of the screen:
pygame.mouse.set_pos([last_x, last_y])
pygame.mouse.set_visible(False)
# mouse can no longer leave the window:
pygame.event.set_grab(True)

# initialize keyboard status:
w_pressed = False
a_pressed = False
s_pressed = False
d_pressed = False

# game loop
while True:
    current_frame_time = time.time()
    deltaTime = current_frame_time - last_frame_time
    last_frame_time = current_frame_time

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    # draw the object:
    mesh.draw()
    # draw the components individually:
    #mesh._draw(GL_TRIANGLE_FAN, 34, 0)
    #mesh._draw(GL_TRIANGLE_FAN, 34, 34)
    #mesh._draw(GL_TRIANGLE_STRIP, 66, 68)

    # input handler:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == K_w:
                w_pressed = True
            if event.key == K_a:
                a_pressed = True
            if event.key == K_s:
                s_pressed = True
            if event.key == K_d:
                d_pressed = True
        elif event.type == KEYUP:
            if event.key == K_w:
                w_pressed = False
            if event.key == K_a:
                a_pressed = False
            if event.key == K_s:
                s_pressed = False
            if event.key == K_d:
                d_pressed = False
        elif event.type == MOUSEMOTION:
            x, y = event.pos
            camera.processMouseMovement(x - last_x, last_y - y)
            last_x, last_y = x, y

    if w_pressed:
        camera.processKeyboard("forward", deltaTime)
    if a_pressed:
        camera.processKeyboard("left", deltaTime)
    if s_pressed:
        camera.processKeyboard("backward", deltaTime)
    if d_pressed:
        camera.processKeyboard("right", deltaTime)

    # update the view matrix in the shader to simulate the camera's view:
    view = camera.getViewMatrix()
    shader.setMatrix("view", view)

    # delay in ms:
    pygame.time.wait(10)

    # when using the OPENGL pygame display mode this is equivalent to
    # the swap buffer function, we need that to actually see something!
    pygame.display.flip()
