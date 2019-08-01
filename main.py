import pygame
from pygame.locals import *

from OpenGL.GL import *

import sys
import glm
import time
import math

# my modules:
from shader import Shader
from mesh import Mesh
from camera import Camera

# create a window, OpenGL functions are callable after window initialization,
# the error will say that
pygame.init()
width = 1200
height = 600
pygame.display.set_mode((width, height), flags=DOUBLEBUF|OPENGL)

# OpenGL initialization:
glViewport(0, 0, width, height)
glEnable(GL_DEPTH_TEST)
glClearColor(1.0, 1.0, 1.0, 1.0)
glEnable(GL_LINE_SMOOTH)
glLineWidth(4)
glPointSize(8)


# create the shader program to run on the gpu:
shader = Shader("shader.vs", "shader.fs")
shader.use()

# set the uniform color to black (the corresponding shader must be in use):
shader.setVector("outlineColor", 0.0, 0.0, 0.0)

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

"""
Number of points (use linear interpolation for drawing):
n = 10

The initial state of the bending animation:
b = r * 2*pi/4 (4th of a circle)
----------------------------------------
x, z = 0.0, 0.0
for i in range(0, n): # (i = 0, 1,... n-1)
    y = i * b/(n-1)
----------------------------------------

The final state of the bending animation:
x = r * sin(t) + r
y = r * cos(t)
z = 0.0 (-> positive z-axis points out of screen)
t = [3*pi/2, 2*pi] (4th of a circle)
----------------------------------------
r = 1
t0 = 3*pi/2
t1 = 2*pi
for i in range(0, n):
    t = t0 + i * (t1-t0)/(n-1)
    x = r * sin(t) + r
    y = r * cos(t)
    z = 0.0
----------------------------------------
"""
n = 10
r = 1
b = r * 2*math.pi/4
positions, colors, indices = [], [], []
color = [1.0, 0.0, 0.0, 1.0]
for i in range(0, n):
    y = i * b/(n-1)
    positions.append([0.0, y, 0.0])
    colors.append(color)
    # e.g. n = 10 -> indices for GL_LINE_STRIP: 0, 1, 1, 2, 2, 3,... 7, 8, 8, 9
    if i == 0 or i == n-1:
        indices.append(i)
    else:
        indices.extend([i, i])
# e.g. n = 10 -> indices for GL_POINTS: 0, 1, 2,... 8, 9
indices.extend([i for i in range(0, n)])
start_points = Mesh(positions, colors, indices)

positions, colors, indices = [], [], []
color = [0.0, 1.0, 0.0, 1.0]
t0, t1 = 3*math.pi/2, 2*math.pi
for i in range(0, n):
    t = t0 + i * (t1-t0)/(n-1)
    x = r * math.sin(t) + r
    y = r * math.cos(t)
    positions.append([x, y, 0.0])
    colors.append(color)
    # e.g. n = 10 -> indices for GL_LINE_STRIP: 0, 1, 1, 2, 2, 3... 7, 8, 8, 9
    if i == 0 or i == n-1:
        indices.append(i)
    else:
        indices.extend([i, i])
# e.g. n = 10 -> indices for GL_POINTS: 0, 1, 2,... 8, 9
indices.extend([i for i in range(0, n)])
end_points = Mesh(positions, colors, indices)


"""
For the animation we want that each vertex travels in an elliptic curve
from the start to the end point!

Calculate the elliptic curve(centered in the origin) which connects the start
and end vertex:
x_e^2/a + y_e^2 = y_s^2 (_e ... end, _s ... start)
The above elliptic equation has an unknown parameter a:
a = x_e / sqrt(y_s^2 - y_e^2)
Then to interpolate to get the new positions we parameterize the elliptic curve:
x_new = a * y_s * cos(t)
y_new = y_s * sin(t)
Now we need start and stop value of t:
t_s = pi/2 (this is always the case)
t_e = arcsin(y_e/y_s) (this must be in radians which is the case using math lib)
Now if we want to be like 50% (p=0.5) in the animation we get the t value with:
t = t_s + p * (t_e - t_s)
The new point will then be, using the above t value:
x_new = a * y_s * cos(t)
y_new = y_s * sin(t)
"""
positions = []
p = 0.95 # change this from 0 to 1.0 for the animation!
t_s = math.pi/2
is_first = True
for pos_s, pos_e in zip(start_points.positions, end_points.positions):
    if is_first:
        is_first = False
        positions.append([0.0, 0.0, 0.0])
        continue
    y_s = pos_s[1]
    x_e = pos_e[0]
    y_e = pos_e[1]
    a = x_e / math.sqrt(y_s**2 - y_e**2)
    t_e = math.asin(y_e / y_s)
    t = t_s + p * (t_e - t_s)
    x_new = a * y_s * math.cos(t)
    y_new = y_s * math.sin(t)
    positions.append([x_new, y_new, 0.0])

colors = [[0.0, 0.0, 1.0, 1.0] for _ in colors]
points = Mesh(positions, colors, indices)
print(points)

# game loop
while True:
    current_frame_time = time.time()
    deltaTime = current_frame_time - last_frame_time
    last_frame_time = current_frame_time

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    # update the view matrix in the shader to simulate the camera's view:
    view = camera.getViewMatrix()
    shader.setMatrix("view", view)

    shader.setInt("lflag", 0)
    shader.setInt("tsflag", 1)

    # for object1
    model1 = glm.mat4()
    model1 = glm.scale(model1, glm.vec3(1.0, 1.0, 1.0))
    model1 = glm.translate(model1, glm.vec3(0.0, 0.0, 0.0))
    model1 = glm.rotate(model1, glm.radians(0.0), glm.vec3(0.0, 0.0, -1.0))
    shader.setMatrix("model1", model1)

    # for object2
    model2 = glm.mat4()
    model2 = glm.scale(model2, glm.vec3(1.0, 1.0, 1.0))
    model2 = glm.translate(model2, glm.vec3(0.0, 0.0, 0.0))
    model2 = glm.rotate(model2, glm.radians(0.0), glm.vec3(0.0, 0.0, -1.0))
    shader.setMatrix("model2", model2)

    # draw the lines:
    start_points.draw(GL_LINE_STRIP, 2*(n-2)+2, 0)
    points.draw(GL_LINE_STRIP, 2*(n-2)+2, 0)
    end_points.draw(GL_LINE_STRIP, 2*(n-2)+2, 0)
    # draw the points:
    shader.setInt("lflag", 1)
    start_points.draw(GL_POINTS, n, 2*(n-2)+2)
    points.draw(GL_POINTS, n, 2*(n-2)+2)
    end_points.draw(GL_POINTS, n, 2*(n-2)+2)

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
