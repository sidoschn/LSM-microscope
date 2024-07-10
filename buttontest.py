from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
 
 
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
 
        # setting title
        self.setWindowTitle("Python ")
 
        # setting geometry
        self.setGeometry(100, 100, 600, 400)
        
        self.statusBar = QStatusBar()

        self.setStatusBar(self.statusBar)
        # calling method
        self.UiComponents()
        self.statusBar.addPermanentWidget(self.button)
        self.statusBar.addPermanentWidget(self.slider)
        # showing all the widgets
        self.show()
 
    # method for widgets
    def UiComponents(self):
 
        # creating a push button
        self.button = QPushButton(self)
        self.button2 = QPushButton(self)
        # setting geometry of button
        self.button2.setGeometry(50, 50, 20, 20)
 
        # setting radius and border
        self.button.setStyleSheet("border : 2px solid black; background-color : green")
 
        # adding action to a button
        self.button2.clicked.connect(self.clickme)
     
        self.button.setDisabled(True)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(-5)
        self.slider.setMaximum(5)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.sliderAction)
 
    # action method
    def clickme(self):
 
        self.button.setStyleSheet("border : 2px solid black; background-color : red")
        self.slider.setValue(2)
        # printing pressed
        print("pressed")
    
    def sliderAction(self):
        print("value changed event")
        
# create pyqt5 app
App = QApplication(sys.argv)
 
# create the instance of our Window
window = Window()




# start the app
sys.exit(App.exec())