import pygame
from pygame.locals import *

from OpenGL.GL import *

import sys
import glm
import time

# my modules:
from shader import Shader
from mesh import Mesh
from camera import Camera
from models import Bridge, Rectangle, Circle, Cylinder

# create a window, OpenGL functions are callable after window initialization,
# the error will say that
pygame.init()
width = 1200
height = 600
pygame.display.set_mode((width, height), flags=DOUBLEBUF|OPENGL)

# OpenGL initialization:
glViewport(0, 0, width, height)
glEnable(GL_DEPTH_TEST)
glClearColor(0.5, 0.5, 0.5, 1.0)
glEnable(GL_LINE_SMOOTH)
glLineWidth(4)


# create an cylinder ready for drawing:
colors = [[0.0, 1.0, 0.0, 1.0],
          [1.0, 0.0, 0.0, 1.0],
          [0.0, 1.0, 0.0, 1.0]]
cylinder = Cylinder(1.0, [-1.0, 1.0], layer_colors=colors)
cylinder_mesh = cylinder.getMesh()

rectangle = Rectangle(5.0, 5.0, 0.0, [0.0, 0.0, 0.0, 1.0])
rectangle_mesh = rectangle.getMesh()

circle = Circle(2.5, -1.0, [1.0, 1.0, 1.0, 1.0])
circle_mesh = circle.getMesh()

# ----- add bridge feature -----
print("----- add bridge feature -----")
positions, colors, indices, drawing_info = cylinder.getRawData()
# get bottom circle:
bc_pos = positions[0:drawing_info["sizes"][0] - 1]
bc_col = colors[0:drawing_info["sizes"][0] - 1]
print(bc_pos)
print(bc_col)
bc_ind = [i for i in range(1, drawing_info["sizes"][0] - 1)]
bc_ind.append(bc_ind[0])
print(bc_ind)
print("----- add bridge feature -----")
# get top circle:
# at first we need the last occurance of mode: GL_TRIANGLE_FAN since a cylinder
# could have more then 2 layers!
for index, mode in enumerate(drawing_info["modes"]):
    if mode == GL_TRIANGLE_FAN:
        last = index

# now get pos, col, ind of tc:
start = indices[drawing_info["offsets"][last]]
tc_pos = positions[start:start + drawing_info["sizes"][last] - 1]
tc_col = colors[start:start + drawing_info["sizes"][last] - 1]
print(tc_pos)
print(tc_col)
tc_ind = [i for i in range(len(bc_pos) + 1, len(bc_pos) + len(tc_pos))]
tc_ind.append(tc_ind[0])
print(tc_ind)
# make the indices for GL_TRIANGLE_STRIP:
# after the model matrices are applied the tc will be bottom
# and the bc will be top therefore:
indices = []
for tc, bc in zip(tc_ind, bc_ind):
    indices.append(tc)
    indices.append(bc)
print(indices)

bc_pos.extend(tc_pos)
bc_col.extend(tc_col)
positions = bc_pos
colors = bc_col
print(positions)

bridge = Bridge(positions, colors, indices)
bridge_mesh = bridge.getMesh()
#-------------------------------

# create the shader program to run on the gpu:
shader = Shader("shader.vs", "shader.fs")
shader.use()

# use color provided by vertex not the uniform vec3 lineColor:
shader.setInt("flag", 0)

# set the uniform color to black (the corresponding shader must be in use):
shader.setVector("outlineColor", 0.0, 0.0, 0.0)

# set the model, view and projection matrices (the corresponding shader must be in use):
model = glm.mat4()
model = glm.scale(model, glm.vec3(0.5, 0.5, 0.5))
shader.setMatrix("model", model)

camera = Camera()
view = camera.getViewMatrix()
shader.setMatrix("view", view)

projection = glm.perspective(glm.radians(45.0), width/height, 0.1, 100.0)
shader.setMatrix("projection", projection)


# initialize the last_frame_time:
last_frame_time = time.time()

# set the mouse position to the center of the screen:
pygame.mouse.set_pos([width/2, height/2])
# set_visible and set_grab together with pygame.mouse.get_rel make a full 360°
# rotaion possible, not restricted to screen -> called: virtual input mode!
pygame.mouse.set_visible(False)
# mouse can no longer leave the window:
pygame.event.set_grab(True)

# initialize keyboard status:
w_pressed = False
a_pressed = False
s_pressed = False
d_pressed = False

prev_model = glm.mat4()
shader.setMatrix("prev_model", prev_model)

# game loop
while True:
    current_frame_time = time.time()
    deltaTime = current_frame_time - last_frame_time
    last_frame_time = current_frame_time

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    # update the view matrix in the shader to simulate the camera's view:
    view = camera.getViewMatrix()

    # draw the object:
    shader.use()
    shader.setMatrix("view", view)

    # use color provided by vertex not the uniform vec3 lineColor:
    shader.setInt("flag", 0)
    shader.setInt("bflag", 0)

    model = glm.mat4()
    model = glm.scale(model, glm.vec3(0.5, 0.5, 0.5))
    model = glm.translate(model, glm.vec3(0.0, 0.0, 0.0))
    model = glm.rotate(model, glm.radians(0.0), glm.vec3(0.0, 0.0, -1.0))
    shader.setMatrix("model", model)
    cylinder_mesh.draw()
    shader.setMatrix("prev_model", model)

    # before drawing circles set the color for the fragment shader to lineColor:
    shader.setInt("flag", 1)
    # draw the layer circles
    for mode, size, offset in zip(cylinder_mesh.drawing_info["modes"],
                                  cylinder_mesh.drawing_info["sizes"],
                                  cylinder_mesh.drawing_info["offsets"]):
        if mode == GL_TRIANGLE_FAN:
            cylinder_mesh._draw(GL_LINE_STRIP, size-1, offset+1)
    shader.setInt("flag", 0)


    model = glm.mat4()
    model = glm.scale(model, glm.vec3(0.5, 0.5, 0.5))
    model = glm.translate(model, glm.vec3(0.5, 2.5, 0.0))
    model = glm.rotate(model, glm.radians(20.0), glm.vec3(0.0, 0.0, -1.0))
    shader.setMatrix("model", model)
    cylinder_mesh.draw()

    # before drawing circles set the color for the fragment shader to lineColor:
    shader.setInt("flag", 1)
    # draw the layer circles
    for mode, size, offset in zip(cylinder_mesh.drawing_info["modes"],
                                  cylinder_mesh.drawing_info["sizes"],
                                  cylinder_mesh.drawing_info["offsets"]):
        if mode == GL_TRIANGLE_FAN:
            cylinder_mesh._draw(GL_LINE_STRIP, size-1, offset+1)
    shader.setInt("flag", 0)

    shader.setInt("bflag", 1)
    bridge_mesh.draw()
    shader.setInt("bflag", 0)
    shader.setMatrix("prev_model", model)

    model = glm.mat4()
    model = glm.scale(model, glm.vec3(0.5, 0.5, 0.5))
    model = glm.translate(model, glm.vec3(2.0, 4.7, 0.0))
    model = glm.rotate(model, glm.radians(40.0), glm.vec3(0.0, 0.0, -1.0))
    shader.setMatrix("model", model)
    cylinder_mesh.draw()

    # before drawing circles set the color for the fragment shader to lineColor:
    shader.setInt("flag", 1)
    # draw the layer circles
    for mode, size, offset in zip(cylinder_mesh.drawing_info["modes"],
                                  cylinder_mesh.drawing_info["sizes"],
                                  cylinder_mesh.drawing_info["offsets"]):
        if mode == GL_TRIANGLE_FAN:
            cylinder_mesh._draw(GL_LINE_STRIP, size-1, offset+1)
    shader.setInt("flag", 0)

    shader.setInt("bflag", 1)
    bridge_mesh.draw()
    shader.setInt("bflag", 0)
    shader.setMatrix("prev_model", model)

    model = glm.mat4()
    model = glm.scale(model, glm.vec3(0.5, 0.5, 0.5))
    shader.setMatrix("model", model)
    shader.setInt("flag", 0)
    rectangle_mesh.draw()
    circle_mesh.draw()

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
            # virtual input mode (see pygame):
            x, y = pygame.mouse.get_rel()
            camera.processMouseMovement(x, -y)

    if w_pressed:
        camera.processKeyboard("forward", deltaTime)
    if a_pressed:
        camera.processKeyboard("left", deltaTime)
    if s_pressed:
        camera.processKeyboard("backward", deltaTime)
    if d_pressed:
        camera.processKeyboard("right", deltaTime)

    # delay in ms:
    pygame.time.wait(10)

    # when using the OPENGL pygame display mode this is equivalent to
    # the swap buffer function, we need that to actually see something!
    pygame.display.flip()
