import glotlib2.glfw


glotlib2.glfw.init_backend()

w = glotlib2.glfw.Window(900, 650, name='GLFW Test 2')
w.ctx.add_label((0.5, 0.5),
                '.Woven silk pyjamas\nexchanged\nfor blue quartz.',
                face=w.ctx.faces.vera, font_size=20, font_oversample_log2=1,
                anchor='C')

glotlib2.glfw.interact()
