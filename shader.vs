#version 330 core
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec4 aColor;

uniform int index;

out vec4 color;

uniform mat4 transformation;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
  if (gl_VertexID < index)
  {
    gl_Position = projection * view * model * vec4(aPos, 1.0);
  }
  else
  {
    gl_Position = projection * view * model * transformation * vec4(aPos, 1.0);
  }
  color = aColor;
}
