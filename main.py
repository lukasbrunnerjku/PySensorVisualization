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

# create vertices:
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

# create an object ready for drawing:
mesh = Mesh(data, indices)

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
