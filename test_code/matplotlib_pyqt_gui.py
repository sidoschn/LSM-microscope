import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QLabel, QGridLayout
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import pco
import numpy as np

class MplCanvas(FigureCanvas):
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.img_plot = self.ax.imshow(np.zeros((2048, 2048)), cmap='gray', norm=Normalize(vmin=0, vmax=255))
        self.ax.set_ylim(0, 2048)
        self.ax.set_xlim(0, 2048)
        super().__init__(self.fig)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Camera Viewer')

        self.canvas = MplCanvas()

        # Create layout
        main_layout = QHBoxLayout()
        
        # Create settings layout with fixed width
        settings_layout = QVBoxLayout()
        settings_widget = QWidget()
        settings_widget.setLayout(settings_layout)
        settings_widget.setFixedWidth(500)  # Fixed width for settings
        
        # Create and add exposure time input
        exposure_layout = QHBoxLayout()
        exposure_label = QLabel("Exposure Time (ms):")
        self.exposure_input = QLineEdit()
        self.exposure_input.setText("10")
        self.exposure_input.returnPressed.connect(self.update_exposure_time)
        exposure_layout.addWidget(exposure_label)
        exposure_layout.addWidget(self.exposure_input)
        
        # Create and add vmin input
        vmin_layout = QHBoxLayout()
        vmin_label = QLabel("vmin:")
        self.vmin_input = QLineEdit()
        self.vmin_input.setText("0")
        self.vmin_input.returnPressed.connect(self.update_vmin_vmax)
        vmin_layout.addWidget(vmin_label)
        vmin_layout.addWidget(self.vmin_input)
        
        # Create and add vmax input
        vmax_layout = QHBoxLayout()
        vmax_label = QLabel("vmax:")
        self.vmax_input = QLineEdit()
        self.vmax_input.setText("255")
        self.vmax_input.returnPressed.connect(self.update_vmin_vmax)
        vmax_layout.addWidget(vmax_label)
        vmax_layout.addWidget(self.vmax_input)
        
        # Add all layouts to the settings layout
        settings_layout.addLayout(exposure_layout)
        settings_layout.addLayout(vmin_layout)
        settings_layout.addLayout(vmax_layout)
        
        # Add settings widget and canvas to main layout
        main_layout.addWidget(settings_widget)
        main_layout.addWidget(self.canvas)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_canvas)
        self.timer.start(100)  # 10 frames per second

        self.cam = pco.Camera(interface='USB 3.0')
        self.cam.sdk.set_delay_exposure_time(0, 'ms', 10, 'ms')
        self.cam.record(5, mode="ring buffer")
        self.cam.wait_for_first_image()

    def update_exposure_time(self):
        try:
            exposure_time = int(self.exposure_input.text())
            self.cam.sdk.set_delay_exposure_time(0, 'ms', exposure_time, 'ms')
        except ValueError:
            print("Invalid exposure time")

    def update_vmin_vmax(self):
        try:
            vmin = int(self.vmin_input.text())
            vmax = int(self.vmax_input.text())
            self.canvas.img_plot.set_norm(Normalize(vmin=vmin, vmax=vmax))
            self.canvas.draw()
        except ValueError:
            print("Invalid vmin or vmax")

    def update_canvas(self):
        img, meta = self.cam.image()
        self.canvas.img_plot.set_array(img)
        self.canvas.draw()

    def closeEvent(self, event):
        self.cam.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
