import pygame
from pygame.locals import *

from OpenGL.GL import *

import sys
import glm
import time
import math
import numpy as np

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
r = 2
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
class Animation():

    def __init__(self, start_points, end_points, p_step):
        self.meshes = None
        self.pose_nr = 0
        self.start_points = start_points
        self.end_points = end_points
        self.pose_positions = []
        self.pose_positions.append(start_points.positions)
        start = time.time()
        for p in np.arange(0.0 + p_step, 1.0 - p_step, p_step):
            self.pose_positions.append(self.interpolate(p))
        print("Interpolation step size:", p_step, "-- Caculation time[s]:", time.time() - start)
        self.pose_positions.append(end_points.positions)
        self.max_pose_nr = len(self.pose_positions) - 1

    def interpolate(self, p):
        positions = []
        t_s = math.pi/2
        is_first = True
        for pos_s, pos_e in zip(self.start_points.positions, self.end_points.positions):
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
        return positions

    def createMeshes(self, colors, indices):
        self.meshes = []
        start = time.time()
        for positions in self.pose_positions:
            self.meshes.append(Mesh(positions, colors, indices))
        print("Mesh creation time[s]:", time.time() - start)

    def nextFrame(self):
        if self.pose_nr == 0:
            self.flag = True
            self.pose_nr += 1
        elif self.pose_nr == self.max_pose_nr:
            self.flag = False
            self.pose_nr -= 1
        elif self.pose_nr < self.max_pose_nr and self.pose_nr > 0:
            if self.flag:
                self.pose_nr += 1
            elif not self.flag:
                self.pose_nr -= 1


animation = Animation(start_points, end_points, 0.01)
colors = [[0.0, 0.0, 1.0, 1.0] for _ in colors]
animation.createMeshes(colors, indices)


"""
By now we have the bones of the actuator, it's time to create the mantle, therefore
create 2 circles with origins centered in local space!
(the circles are in the x, z plane due to our coordinate system where the y-axis is up)

Indices in the positions list:
|<------circle1------>| |<------circle2----->|
[p_0, p_1, p_2,... p_n, p_0, p_1, p_2,... p_n] (p_0 is the cirlce center)
  0,   1,   2,...   n,  n+1, n+2, n+3,... 2n+1 <--- these are the indices
in the positions list!

GL_TRIANGLE_FAN is used for the area...
Cirlce1 -> for the area: 0,... n, 1
Cirlce2 -> for the area: n+1,... 2n+1, n+2

GL_LINE_LOOP is used for the line...
Cirlce1 -> for the line: 1,... n
Cirlce2 -> for the line: n+2,... 2n+1

GL_TRIANGLE_STRIP is used for the mantle...
Cylinder mantle: 1, n+2, 2, n+3,... n, 2*n+1, 1, n+2 (p_0's aren't used)

In the actual code n is reserved, use m instead!!!!!!!

This is how to draw from the indices buffer then:
Cirlce1 -> for the area:
mode: GL_TRIANGLE_FAN, size: m + 2, offset: 0
Cirlce2 -> for the area:
mode: GL_TRIANGLE_FAN, size: m + 2, offset: m + 2
(note: next offset is always previous offset + previous size)
Cirlce1 -> for the line:
mode: GL_LINE_LOOP, size: m, offset: 2 * m + 4
Cirlce2 -> for the line:
mode: GL_LINE_LOOP, size: m, offset: 3 * m + 4

Cylinder mantle (therefore we need both circles in one VAO):
note: circle1 needs to be the top and circle2 the bottom of the mantle!
mode: GL_TRIANGLE_STRIP, size: 2 * m + 2, offset: 4 * m + 4
"""
m = 32 # blender default value for number of vertices of a circle
r = 0.5
positions = [[0.0, 0.0, 0.0]]
colors = [color]
indices = [0] # this is the circle center
# --- first circle -----
phi = 0.0
deltaPhi = 360/m
index = 1
while phi < 360:
    x = r * math.cos(math.radians(phi))
    z = r * math.sin(math.radians(phi))
    positions.append([x, 0.0, z])
    colors.append(color)
    # indices for GL_TRIANGLE_FAN
    indices.append(index)
    phi += deltaPhi
    index += 1
# to get a closed circle:
indices.append(1) # Cirlce1 -> for the area --- finished!

# --- second circle ---
indices.append(m + 1) # this is the index for the circle center
positions.append([0.0, 0.0, 0.0]) # this is the circle center position
colors.append(color) # this is the circle center color
phi = 0.0
deltaPhi = 360/m
index = m + 2
while phi < 360:
    x = r * math.cos(math.radians(phi))
    z = r * math.sin(math.radians(phi))
    positions.append([x, 0.0, z])
    colors.append(color)
    # indices for GL_TRIANGLE_FAN
    indices.append(index)
    phi += deltaPhi
    index += 1
# to get a closed circle:
indices.append(m + 2) # Cirlce2 -> for the area --- finished!

# Cirlce1 -> for the line:
for i in range(1, m + 1): # 1,... m
    indices.append(i)

# Cirlce2 -> for the line:
for i in range(m + 2, 2 * m + 2): # m + 2,... 2 * m + 1
    indices.append(i)

# Cylinder mantle:
for i in range(1, m + 1): # 1,... m
    indices.append(i)
    indices.append(i + m + 1)
# to get a closed mantle:
indices.append(1)
indices.append(m + 2)

skin_mesh = Mesh(positions, colors, indices)
print(skin_mesh)

objectSize = m + 1 # the number of positions of a cirlce
shader.setInt("objectSize", objectSize)

"""
Input:
The mesh of a pose which held n positions for the circle centers

Returns:
Rotation matrices rms
and
Transformation matrices tms
"""
def getTranslationRotationMatricesForCircles(mesh):
    rms, tms = [], []
    v_n0 = glm.vec3(0.0, 1.0, 0.0) # normal vector of first circle area!
    for i in range(0, n): # 0,... n - 1 (= last position of the pose)
        p_i = mesh.positions[i] # each mesh contains the positions p_i of the pose
        rm, tm = glm.mat4(), glm.mat4() # initialize unit matrices
        tm = glm.translate(tm, glm.vec3(p_i[0], p_i[1], p_i[2])) # each p_i: [x, y, z]
        tms.append(tm)

        # if first pose position:
        if i == 0:
            rms.append(rm) # append a unit matrix = no rotation
            continue

        # if last pose position:
        if i == n - 1:
            # position vector at: i-1
            p_i_prev = glm.vec3(mesh.positions[i-1][0],
                                mesh.positions[i-1][1],
                                mesh.positions[i-1][2])
            # normalized gradient vector at p_i:
            v_ni = glm.normalize(p_i - p_i_prev)

            if v_ni == v_n0:
                rms.append(rm) # append a unit matrix = no rotation
                continue

            angle = glm.acos(glm.length(v_n0 * v_ni)) # get the rotation angle
            rot_axis = glm.cross(v_n0, v_ni) # get the rotation axis
            rm = glm.rotate(rm, angle, rot_axis)
            rms.append(rm) # append the rotation matrix
            continue

        # position vector at: i+1
        p_i_next = glm.vec3(mesh.positions[i+1][0],
                            mesh.positions[i+1][1],
                            mesh.positions[i+1][2])
        # position vector at: i-1
        p_i_prev = glm.vec3(mesh.positions[i-1][0],
                            mesh.positions[i-1][1],
                            mesh.positions[i-1][2])
        # normalized gradient vector at p_i:
        v_ni = glm.normalize(p_i_next - p_i_prev)

        if v_ni == v_n0:
            rms.append(rm) # append a unit matrix = no rotation
            continue

        angle = glm.acos(glm.length(v_n0 * v_ni)) # get the rotation angle
        rot_axis = glm.cross(v_n0, v_ni) # get the rotation axis
        rm = glm.rotate(rm, angle, rot_axis)
        rms.append(rm) # append the rotation matrix

    return rms, tms

"""
Input:
The mesh of a pose which held n positions for the circle centers
"""
def drawSkinFromBoneMesh(mesh):
    rms, tms = getTranslationRotationMatricesForCircles(mesh)
    prev_transform = None
    for rm, tm in zip(rms, tms):
        if prev_transform is None:
            # draw the bottom area of the actuator:
            prev_transform = tm * rm
            shader.setMatrix("model1", prev_transform)
            shader.setInt("lflag", 0)
            skin_mesh.draw(GL_TRIANGLE_FAN, m + 2, m + 2)

        # here we use the objectSize uniform variable and the tsflag to
        # get different model matrices for the circles:
        shader.setInt("lflag", 0)
        shader.setInt("tsflag", 1)
        # model1 applied on circle1 and model2 on circle2
        shader.setMatrix("model2", prev_transform)
        cur_transform = tm * rm
        shader.setMatrix("model1", cur_transform)
        prev_transform = cur_transform
        # use both circles to draw the mantle:
        skin_mesh.draw(GL_TRIANGLE_STRIP, 2 * m + 2, 4 * m + 4)
        # use circle2 to draw the black rings:
        shader.setInt("lflag", 1)
        skin_mesh.draw(GL_LINE_LOOP, m, 3 * m + 4)

    # use circle1 to draw the area of the actuator:
    shader.setInt("lflag", 0)
    skin_mesh.draw(GL_TRIANGLE_FAN, m + 2, 0)
    # use circle2 to draw the last black ring:
    shader.setMatrix("model2", cur_transform)
    shader.setInt("lflag", 1)
    skin_mesh.draw(GL_LINE_LOOP, m, 3 * m + 4)

    # reset flags:
    shader.setInt("lflag", 0)
    shader.setInt("tsflag", 0)


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
    shader.setInt("tsflag", 0)

    """---uncomment this section to see the skin in detail and still for pose i---"""
    # i = -1
    # mesh = animation.meshes[i]
    # drawSkinFromBoneMesh(mesh)
    #
    # model1 = glm.mat4()
    # shader.setMatrix("model1", model1)
    # model2 = glm.mat4()
    # shader.setMatrix("model2", model2)
    #
    # shader.setInt("lflag", 0)
    # animation.meshes[i].draw(GL_LINE_STRIP, 2*(n-2)+2, 0)
    # shader.setInt("lflag", 1)
    # animation.meshes[i].draw(GL_POINTS, n, 2*(n-2)+2)
    """----------------------------------------------------------------"""

    """---uncomment this section to see the animation bounds---"""
    # # draw the lines:
    # start_points.draw(GL_LINE_STRIP, 2*(n-2)+2, 0)
    # end_points.draw(GL_LINE_STRIP, 2*(n-2)+2, 0)
    # # draw the points:
    # shader.setInt("lflag", 1)
    # start_points.draw(GL_POINTS, n, 2*(n-2)+2)
    # end_points.draw(GL_POINTS, n, 2*(n-2)+2)
    """--------------------------------------------------------"""

    """---uncomment this section to see the animation in motion between start and end pose---"""
    # draw the animation:
    model1 = glm.mat4()
    shader.setMatrix("model1", model1)
    model2 = glm.mat4()
    shader.setMatrix("model2", model2)

    shader.setInt("lflag", 0)
    animation.meshes[animation.pose_nr].draw(GL_LINE_STRIP, 2*(n-2)+2, 0)
    shader.setInt("lflag", 1)
    animation.meshes[animation.pose_nr].draw(GL_POINTS, n, 2*(n-2)+2)

    # uncomment the next line and it will apply the skin to the animation
    drawSkinFromBoneMesh(animation.meshes[animation.pose_nr])

    # to increase or decrease the pose_nr:
    animation.nextFrame()
    """-------------------------------------------------------------------------------------"""

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

    # when using the OPENGL pygame display mode this is equivalent to
    # the swap buffer function, we need that to actually see something!
    pygame.display.flip()
