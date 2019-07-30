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
from models import Cylinder

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
glLineWidth(5)

# create an cylinder ready for drawing:
positions, indices, drawing_info = Cylinder.create(1.0, [0.5, 1.5], mesh=False)
print(positions)
print("pos:", positions[indices[0]], positions[indices[34]], positions[indices[68]])
print(indices)
print(drawing_info)
mesh = Cylinder.create(1.0, [0.0, 1.0, 2.0])
#mesh = Cylinder.create(1.0, [0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
print(mesh)

# create the shader program to run on the gpu:
shader = Shader("shader.vs", "shader.fs")
shader.use()

index = 0
shader.setInt("index", index)

# set the transformation matrix:
transformation = glm.mat4()
transformation = glm.rotate(transformation, glm.radians(20.0), glm.vec3(0.0, 0.0, -1.0))
shader.setMatrix("transformation", transformation)

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

#line_shader = Shader("line_shader.vs", "line_shader.fs")
#line_shader.use()

# set the model, view and projection matrices (the corresponding shader must be in use):
#line_shader.setMatrix("model", model)
#line_shader.setMatrix("view", view)
#line_shader.setMatrix("projection", projection)
#line_shader.setMatrix("transformation", transformation)

# set the uniform color to black (the corresponding shader must be in use):
#line_shader.setVector("color", 0.0, 0.0, 0.0)


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
    #mesh.draw()

    # draw the layer circles
    # line_shader.use()
    # line_shader.setMatrix("view", view)
    # for mode, size, offset in zip(mesh.drawing_info["modes"],
    #                               mesh.drawing_info["sizes"],
    #                               mesh.drawing_info["offsets"]):
    #     if mode == GL_TRIANGLE_FAN:
    #         mesh._draw(GL_LINE_STRIP, size-1, offset+1)

    # draw the components of a cylinder individually:
    index = 1000
    shader.setInt("index", index)
    mesh._draw(GL_TRIANGLE_FAN, 34, 0)

    index = 0
    shader.setInt("index", index)
    transformation = glm.mat4()
    transformation = glm.rotate(transformation, glm.radians(20.0), glm.vec3(0.0, 0.0, -1.0))
    shader.setMatrix("transformation", transformation)
    mesh._draw(GL_TRIANGLE_FAN, 34, 34)
    mesh._draw(GL_TRIANGLE_STRIP, 66, 68+34)

    transformation = glm.mat4()
    transformation = glm.rotate(transformation, glm.radians(40.0), glm.vec3(0.0, 0.0, -1.0))
    shader.setMatrix("transformation", transformation)
    mesh._draw(GL_TRIANGLE_FAN, 34, 68)
    mesh._draw(GL_TRIANGLE_STRIP, 66, 68+34+66)


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
