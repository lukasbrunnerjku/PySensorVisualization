#version 330 core
// shader runs for each vertex, aPos and aColor are attributes of single vertex
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec4 aColor;

uniform int lflag;
uniform int tsflag;

uniform vec3 lineColor;
uniform int objectSize;

// if only one model matrix needed use model1 (e.g. tsflag = 0)
uniform mat4 model1;
uniform mat4 model2;
uniform mat4 view;
uniform mat4 projection;

out vec4 color;

void main()
{
  // line flag, the lines should be drawn in black
  if (lflag == 1)
  {
    color = vec4(lineColor, 1.0);
  }
  else
  {
    color = aColor;
  }

  // transformation selection flag, if VBO has 2 objects which need to be
  // transformed individually
  if (tsflag == 1)
  {
    // if the VBO is structure like: vertices of object1, vertices of object2
    // then model1 is applied to object1 and model2 on object2!
    if (gl_VertexID > objectSize)
    {
      gl_Position = projection * view * model2 * vec4(aPos, 1.0);
    }
    else
    {
      gl_Position = projection * view * model1 * vec4(aPos, 1.0);
    }
  }
  else
  {
    gl_Position = projection * view * model1 * vec4(aPos, 1.0);
  }
}
