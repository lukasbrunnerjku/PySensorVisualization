#version 330 core
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec4 aColor;

uniform int flag;
uniform vec3 lineColor;

uniform int bflag;
uniform mat4 prev_model;

out vec4 color;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
  if (flag == 1)
  {
    color = vec4(lineColor, 1.0);
  }
  else
  {
    color = aColor;
  }

  if (bflag == 1)
  {
    if (gl_VertexID < 33)
    {
      gl_Position = projection * view * model * vec4(aPos, 1.0);
    }
    else
    {
      gl_Position = projection * view * prev_model * vec4(aPos, 1.0);
    }
  }
  else
  {
    gl_Position = projection * view * model * vec4(aPos, 1.0);
  }
}
