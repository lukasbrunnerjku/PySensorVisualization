#version 330 core
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec4 aColor;

uniform int flag;
uniform vec3 lineColor;

out vec4 color;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
  gl_Position = projection * view * model * vec4(aPos, 1.0);

  if (flag == 1)
  {
    color = vec4(lineColor, 1.0);
  }
  else
  {
    color = aColor;
  }
}
