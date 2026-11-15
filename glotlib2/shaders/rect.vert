#version 330

uniform mat4  u_mvp;
uniform float u_z;
uniform vec4 u_rect;

void main()
{
    float x1 = u_rect.x;
    float y1 = u_rect.y;
    float x2 = u_rect.z;
    float y2 = u_rect.w;

    vec2 position;
    position.x = (gl_VertexID > 1) ? x2 : x1;
    position.y = (gl_VertexID % 2 == 1) ? y2 : y1;

    gl_Position = u_mvp * vec4(position, u_z, 1);
}
