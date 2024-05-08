import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer
import pco
import numpy as np

class LiveViewGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.camera = pco.Camera(interface='USB 3.0')  # Initialize the camera
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Live View')
        self.setGeometry(100, 100, 400, 400)

        # QLabel to display the live video feed
        self.image_label = QLabel(self)
        #self.image_label.setFixedSize(2048, 2048)
        self.image_label.setAlignment(Qt.AlignCenter)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        self.setLayout(layout)

        # Create a QTimer for updating the image label
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_image)
        self.timer.start(100)  # Update every 100 ms

        # Start the camera
        self.camera.sdk.set_delay_exposure_time(0, 'ms', 10, 'ms')
        self.camera.record(5, mode="ring buffer")
        self.camera.wait_for_first_image()

    def update_image(self):
        # Get the latest frame from the camera
        img, _ = self.camera.image()
        if img is not None:
            # Convert the frame to a QImage
            height, width = img.shape
            q_img = QImage(img.data, width, height, QImage.Format_Grayscale8)

            # Convert the QImage to a QPixmap and display it
            pixmap = QPixmap.fromImage(q_img)
            self.image_label.setPixmap(pixmap)

    def closeEvent(self, event):
        # This method is called when the window is closed
        # Close the camera
        self.camera.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LiveViewGUI()
    window.show()
    sys.exit(app.exec_())