import glotlib2.glfw


glotlib2.glfw.init_backend()

w = glotlib2.glfw.Window(900, 650, name='GLFW Test 4')

p = w.ctx.add_plot(limits=(-100, -100, 100, 100))
p.add_hline(0, color=(0.5, 0.75, 0.5))
p.add_vline(0, color=(0.5, 0.75, 0.5))

glotlib2.glfw.interact()
