import sys
import math

import numpy as np
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QHBoxLayout,
                               QLabel, QPushButton, QVBoxLayout, QWidget,
                               QLineEdit)

import glotlib2.pyside6


NVERTICES = 501


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PySide6 Test 13')
        self.resize(1100, 750)

        main_layout = QHBoxLayout(self)
        sidebar = QVBoxLayout()

        # Add sample text inputs to demonstrate moving focus cleanly via TAB
        sidebar.addWidget(QLabel('Sample Parameter Input 1:'))
        self.input1 = QLineEdit()
        self.input1.setPlaceholderText('Press Tab to navigate out...')
        sidebar.addWidget(self.input1)

        sidebar.addWidget(QLabel('Sample Parameter Input 2:'))
        self.input2 = QLineEdit()
        sidebar.addWidget(self.input2)

        sidebar.addWidget(QLabel('Camera Depth Info Control:'))
        self.depth_box = QDoubleSpinBox()
        self.depth_box.setRange(-20.0, -1.0)
        self.depth_box.setValue(-3.5)
        sidebar.addWidget(self.depth_box)

        self.reset_btn = QPushButton('Reset Scene View')
        sidebar.addWidget(self.reset_btn)

        sidebar.addStretch()
        main_layout.addLayout(sidebar, stretch=1)

        self.gl_widget = glotlib2.pyside6.GLWidgetFocusable(None)
        main_layout.addWidget(self.gl_widget, stretch=4)

        ctx = self.gl_widget.ctx
        self.plot = ctx.add_plot(limits=(0, -1, math.pi * 2, 1))
        X = np.linspace(0, math.pi * 2, NVERTICES)
        Y = np.sin(X)
        self.plot.add_steps(X=X, Y=Y)
        self.plot.set_x_label('X label goes here')
        self.plot.set_y_label('Y label goes here')


if __name__ == '__main__':
    glotlib2.pyside6.init_backend()

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
