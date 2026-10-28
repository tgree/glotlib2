import glotlib2.glfw


glotlib2.glfw.init_backend()

w = glotlib2.glfw.Window(900, 650, name='Test 2')

p = w.ctx.add_plot(limits=(-100, -100, 100, 100))
p.set_x_label('X axis')
p.set_y_label('Y axis')

glotlib2.glfw.interact()
