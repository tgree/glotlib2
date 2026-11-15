# glotlib2

Copyright (c) 2026 Terry Greeniaus

This library is a rewrite of the original glotlib library. It now supports embedding a glotlib context inside a PySide6 window, as well as continuing to support running in a glfw window.

In order to support the multiple backends, the event-handling has been abstracted so the client will never need to import glfw to get identifiers for things like key names to handle a keypress event.

## Installation

Since multiple backends are now supported, you can install `glotlib2` along with the backend package that you want to use:

```bash
python3 -m pip install glotlib2[glfw]
python3 -m pip install glotlib2[pyside6]
```

Installing both backends is also supported if you want to experiment with both:

```bash
python3 -m pip install glotlib2[all]
```

## Usage

While `glotlib2` is pretty similar to `glotlib`, you now need to explicitly initialize the backend you want to use in your app. For glfw:

```python
import glotlib2.glfw

glotlib2.glfw.init_backend()
```

And for PySide6:

```python
import glotlib2.pyside6

glotlib2.pyside6.init_backend()
```

Check out the `tests/` subdirectories for examples supporting both backends.

## License

Licensed under the [Mozilla Public License 2.0](LICENSE). Bundled Bitstream Vera fonts are licensed under the [Bitstream Vera Fonts Copyright](glotlib2/font_files/ttf_bitstream_vera_1_10/COPYRIGHT.TXT).

