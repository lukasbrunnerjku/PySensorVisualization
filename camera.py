import glm

class Camera():

    def __init__(self,
                 position=glm.vec3(0.0, 0.0, 3.0),
                 up=glm.vec3(0.0, 1.0, 0.0),
                 front=glm.vec3(0.0, 0.0, -1.0),
                 yaw=-90.0,
                 pitch=0.0,
                 movementSpeed=3.0,
                 mouseSensitivity=0.2):
        # position of the camera:
        self.position = position
        # up vector of the camera:
        self.up = up
        # front vector of the camera:
        self.front = front
        # used to calculate the right vector of the camera:
        self.worldUp = up
        # calculate it in updateCameraVectors and use it in processKeyboard:
        self.right = None
        # angle for left/right movement:
        self.yaw = yaw
        # angle for up/down movement:
        self.pitch = pitch
        # set sensitivities of the camera:
        self.movementSpeed = movementSpeed
        self.mouseSensitivity = mouseSensitivity

        self.updateCameraVectors()

    def processKeyboard(self, direction, deltaTime):
        # to get equal movement speed independent of hardware speed:
        velocity = self.movementSpeed * deltaTime
        if direction == "forward":
            self.position += self.front * velocity
        if direction == "backward":
            self.position -= self.front * velocity
        if direction == "left":
            self.position -= self.right * velocity
        if direction == "right":
            self.position += self.right * velocity

    def processMouseMovement(self, xOffset, yOffset, constrainPitch=True):
        xOffset *= self.mouseSensitivity;
        yOffset *= self.mouseSensitivity;

        self.yaw += xOffset
        self.pitch += yOffset

        if constrainPitch:
            if self.pitch > 89.0:
                self.pitch = 89.0
            if self.pitch < -89.0:
                self.pitch = -89.0

        self.updateCameraVectors()

    def updateCameraVectors(self):
        self.front.x = glm.cos(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        self.front.y = glm.sin(glm.radians(self.pitch))
        self.front.z = glm.sin(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        self.front = glm.normalize(self.front)

        self.right = glm.normalize(glm.cross(self.front, self.worldUp))
        self.up = glm.normalize(glm.cross(self.right, self.front))

    def getViewMatrix(self):
        """Returns a view matrix which simulates the cameras point of view"""
        return glm.lookAt(self.position,
                          self.position + self.front,
                          self.up)

    def __repr__(self):
        return "position: {}\nup: {}\nfront: {}\nworldUp: {}\nright: {}".format(
                self.position, self.up, self.front, self.worldUp, self.right)

if __name__ == '__main__':
    camera = Camera()
    print(camera)
    view = camera.getViewMatrix()
    print(view)
