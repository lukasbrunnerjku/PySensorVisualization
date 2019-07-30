from OpenGL.GL import *
import glm

class Shader():

    def __init__(self, vs_filename, fs_filename):
        # get vertex shader source code:
        with open(vs_filename, "r") as file:
            vs_source = file.read()

        print(vs_source)

        # get fragment shader source code:
        with open(fs_filename, "r") as file:
            fs_source = file.read()

        print(fs_source)

        # compile shaders:
        vs = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vs, vs_source)
        glCompileShader(vs)
        if glGetShaderiv(vs, GL_COMPILE_STATUS) != GL_TRUE:
            raise RuntimeError(glGetShaderInfoLog(vs))

        fs = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fs, fs_source)
        glCompileShader(fs)
        if glGetShaderiv(fs, GL_COMPILE_STATUS) != GL_TRUE:
            raise RuntimeError(glGetShaderInfoLog(fs))

        # link shaders, create program:
        self.id = glCreateProgram()
        glAttachShader(self.id, vs)
        glAttachShader(self.id, fs)
        glLinkProgram(self.id)
        if glGetProgramiv(self.id, GL_LINK_STATUS) != GL_TRUE:
            raise RuntimeError(glGetProgramInfoLog(self.id))

        # shaders aren't needed anymore, free the resources:
        glDeleteShader(vs)
        glDeleteShader(fs)

    def use(self):
        """Always have a program in use before calling any glUniform...!"""
        glUseProgram(self.id)

    # e.g in the shader write: uniform int index; -> name = "index"
    def setInt(self, name, x):
        """Always have a program in use before calling this function!"""
        glUniform1i(glGetUniformLocation(self.id, name), x)

    def setFloat(self, name, x):
        """Always have a program in use before calling this function!"""
        glUniform1f(glGetUniformLocation(self.id, name), x)


    def setVector(self, name, x, y, z):
        """Always have a program in use before calling this function!"""
        glUniform3f(glGetUniformLocation(self.id, name), x, y, z)

    def setMatrix(self, name, matrix):
        """Always have a program in use before calling this function!"""
        glUniformMatrix4fv(glGetUniformLocation(self.id, name), 1, GL_FALSE, glm.value_ptr(matrix))
