import glfw


WINDOWS = set()


def init_backend(msaa=None):
    '''
    Initializes the global OpenGL format requirements for glotlib.
    '''
    glfw.init()
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    if msaa is not None:
        glfw.window_hint(glfw.SAMPLES, msaa)


def _register_window(w):
    WINDOWS.add(w)


def _draw_windows():
    for w in WINDOWS:
        w.ctx._paint_gl()
        w._swap_buffers()


def interact():
    while WINDOWS:
        del_ws = [w for w in WINDOWS if w._should_close()]
        for w in del_ws:
            w._destroy()
            WINDOWS.remove(w)
        if not WINDOWS:
            break

        _draw_windows()
        glfw.wait_events()
