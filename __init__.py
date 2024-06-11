import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QLineEdit, QCheckBox, QFrame, QGridLayout
from PyQt5.QtGui import QPixmap, QImage, QIntValidator
from PyQt5.QtCore import Qt, QTimer
import MCM300 as mc
import threading
import serial
import time
from optotune_lens import Lens
from pycromanager import Acquisition, multi_d_acquisition_events, Core


default_um_btn_move = 10

class MicroscopeControlGUI(QWidget):
    def __init__(self):
        super().__init__()
        #Init the stage
        self.controller_mcm = mc.Controller(which_port='COM4',
                                        stages=('ZFM2020', 'ZFM2020', 'ZFM2020'),
                                        reverse=(False, False, False),
                                        verbose=True,
                                        very_verbose=False)
        #set all the counters for the stage in 0
        for channel in range(3):
            self.controller_mcm._set_encoder_counts_to_zero(channel)
        
        # Init the optotune lens
        self.lens = Lens('COM5', debug=False)
        print(self.lens.firmware_type)
        print(self.lens.firmware_version)
        print(self.lens.get_firmware_branch())
        print('Lens serial number:', self.lens.lens_serial)
        print('Lens temperature:', self.lens.get_temperature())
        self.lens.to_current_mode()
        
        # Check if umanager is open
        try:
            self.core = Core()
            print(self.core)
            print("micromanager connection established succesfully!")
        except:
            print("Did you open uManager with the proper configuration?")
            return -1


        # Init arduino serial communication
        self.arduino = serial.Serial(port="COM6", baudrate=115200, timeout=1)

        self.initUI()

    def initUI(self):
        self.setWindowTitle('LSM Control')

        self.label_joystick = QLabel('10 um steps for sample stage')

        # Create buttons for X, Y, Z control
        self.create_control_buttons()

        # Sliders for velocity and position
        x_layout, self.x_slider, self.x_text = self.create_slider_with_text('X Position (um)', -10000, 10000, 0, self.move_stage, channel=0)
        y_layout, self.y_slider, self.y_text = self.create_slider_with_text('Y Position (um)', -10000, 10000, 0, self.move_stage, channel=1)
        z_layout, self.z_slider, self.z_text = self.create_slider_with_text('Z Position (um)', -10000, 10000, 0, self.move_stage, channel=2)

        # Slider for current value
        current_layout, self.current_slider, self.current_text = self.create_slider_with_text('Current', -300, 300, 0, self.change_optotune_current)

        # Sliders for motor frequency and amplitude
        acceleration_layout, self.acceleration_slider, self.acceleration_text = self.create_slider_with_text('Acceleration', 1000, 15000, 5000, self.send_acc_serial_command)
        amplitude_layout, self.amplitude_slider, self.amplitude_text = self.create_slider_with_text('Amplitude', 20, 100, 100, self.send_width_serial_command)

        # Button for stop and start stepper motor operation
        self.stop_stepper_motor_btn = QPushButton("Stop stepper motor")
        self.stop_stepper_motor_btn.clicked.connect(lambda: self.send_command_arduino("h?"))

        self.start_stepper_motor_btn = QPushButton("Start stepper motor")
        self.start_stepper_motor_btn.clicked.connect(lambda: self.send_command_arduino("s?"))

        # Create a layout for the previous buttons
        light_house_layout = QGridLayout()
        light_house_layout.addWidget(self.stop_stepper_motor_btn, 0, 0)
        light_house_layout.addWidget(self.start_stepper_motor_btn, 0, 1)

        # Z max and min position and z step
        self.z_max_label = QLabel('Z-Max')
        self.z_max_btn = QPushButton('Set Z-Max')
        self.z_max_btn.clicked.connect(lambda: self.set_z_position('max'))

        self.z_min_label = QLabel('Z-Min')
        self.z_min_btn = QPushButton('Set Z-Min')
        self.z_min_btn.clicked.connect(lambda: self.set_z_position('min'))

        self.z_step_label = QLabel('Z-Step')
        self.z_step_text = QLineEdit('10')
        self.z_step_text.setValidator(QIntValidator(1, 500))
        self.z_step_text.setFixedWidth(50)
        self.z_step_text.setAlignment(Qt.AlignCenter)

        # Button for start acquisition
        self.set_encoders_to_cero_btn = QPushButton("Set to cero encoders sample stage")
        self.set_encoders_to_cero_btn.clicked.connect(self.set_encoders_to_cero)

        # Button for start acquisition
        self.start_acquisition_btn = QPushButton("Start Acquisition")
        self.start_acquisition_btn.clicked.connect(self.start_acquisition)

        # Stop acquisition        
        self.stop_acquisition_btn = QPushButton("Stop Acquisition")
        self.stop_acquisition_btn.clicked.connect(self.stop_acquisition)

        # Main layout setup
        main_layout = QVBoxLayout()

        # Joystick and Z control layout
        joystick_z_layout = QHBoxLayout()
        joystick_z_layout.addLayout(self.joystick_layout)

        main_layout.addWidget(self.label_joystick)
        main_layout.addLayout(joystick_z_layout)

        # Add other components below the joystick and Z controls
        main_layout.addLayout(x_layout)
        main_layout.addLayout(y_layout)
        main_layout.addLayout(z_layout)
        main_layout.addLayout(current_layout)
        main_layout.addLayout(acceleration_layout)
        main_layout.addLayout(amplitude_layout)
        main_layout.addLayout(light_house_layout)

        # Z position buttons and step layout
        z_pos_layout = QHBoxLayout()

        z_pos_layout.addWidget(self.z_max_label)
        z_pos_layout.addWidget(self.z_max_btn)
        z_pos_layout.addWidget(self.z_min_label)
        z_pos_layout.addWidget(self.z_min_btn)
        z_pos_layout.addWidget(self.z_step_label)
        z_pos_layout.addWidget(self.z_step_text)

        main_layout.addLayout(z_pos_layout)
        main_layout.addWidget(self.set_encoders_to_cero_btn)
        main_layout.addWidget(self.start_acquisition_btn)
        main_layout.addWidget(self.stop_acquisition_btn)

        self.setLayout(main_layout)
        self.show()

    def closeEvent(self, event):
        # This method is called when the window is closed
        self.send_command_arduino("h?")    # to stop the stepper motor
        self.arduino.close()
        self.controller_mcm.close()
        event.accept()

    def create_slider_with_text(self, label, min_val, max_val, default_val, callback, channel=None):
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.setTickPosition(QSlider.TicksBelow)

        text_box = QLineEdit(str(default_val))
        text_box.setFixedWidth(40)
        text_box.setAlignment(Qt.AlignCenter)

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel(label))
        hbox.addWidget(slider)
        hbox.addWidget(text_box)

        # Update textbox and slider values if one of them changed
        slider.valueChanged.connect(lambda value, text_box=text_box: self.update_text_box_from_slider(value, text_box))
        text_box.textChanged.connect(lambda text, slider=slider, min_val=min_val, max_val=max_val: self.update_slider_from_text_box(text, slider, min_val, max_val))

        # Move the stage only when the slider is released or after pressing enter in the textbox (more safe)
        if channel is not None:
            slider.sliderReleased.connect(lambda: callback(channel, slider.value()))
            text_box.editingFinished.connect(lambda: callback(channel, slider.value()))
        else:
            # General callback function
            slider.sliderReleased.connect(lambda: callback(slider.value()))
            text_box.editingFinished.connect(lambda: callback(slider.value()))

        return hbox, slider, text_box

    def change_optotune_current(self,value):
        thread = threading.Thread(target=self.lens.set_current, args=([value]))
        thread.start()

    
    def send_acc_serial_command(self,value):
        command = "a?"+str(value)
        self.arduino.write(bytes(command, 'utf-8'))
        time.sleep(0.5)  

    def send_width_serial_command(self,value):
        command = "w?"+str(value)
        self.arduino.write(bytes(command, 'utf-8'))
        time.sleep(0.5)  

    def update_text_box_from_slider(self, value, text_box):
        text_box.setText(str(value))

    def update_slider_from_text_box(self, text, slider, min_val, max_val):
        try:
            value = int(text)
            if value < min_val:
                value = min_val
            elif value > max_val:
                value = max_val
            slider.setValue(value)
        except ValueError:
            pass

    # Update slider and text values from the joystick btns
    def update_ui_elements(self, channel, value):
        if channel == 0:
            new_value = value + int(self.x_text.text())
            self.x_text.setText(str(new_value))
            self.x_slider.setValue(new_value)
        elif channel == 1:
            new_value = value + int(self.y_text.text())
            self.y_text.setText(str(new_value))
            self.y_slider.setValue(new_value)
        elif channel == 2:
            new_value = value + int(self.z_text.text())
            self.z_text.setText(str(new_value))
            self.z_slider.setValue(new_value)

    def create_control_buttons(self):
        self.joystick_layout = QGridLayout()

        # X and Y control buttons
        up_button = QPushButton('X↑')
        up_button.clicked.connect(lambda: self.move_stage_2(0, 1))
        
        down_button = QPushButton('X↓')
        down_button.clicked.connect(lambda: self.move_stage_2(0, -1))
        
        left_button = QPushButton('←Y')
        left_button.clicked.connect(lambda: self.move_stage_2(1, -1))
        
        right_button = QPushButton('Y→')
        right_button.clicked.connect(lambda: self.move_stage_2(1, 1))
        

        # Arrange the joystick buttons
        self.joystick_layout.addWidget(up_button, 0, 1)
        self.joystick_layout.addWidget(left_button, 1, 0)
        self.joystick_layout.addWidget(right_button, 1, 2)
        self.joystick_layout.addWidget(down_button, 2, 1)

        # Z control buttons
        z_up_button = QPushButton('Z↑')
        z_up_button.clicked.connect(lambda: self.move_stage_2(2, 1))
        
        z_down_button = QPushButton('Z↓')
        z_down_button.clicked.connect(lambda: self.move_stage_2(2, -1))

        # Arrange the Z buttons
        self.joystick_layout.addWidget(z_up_button,0,3)
        self.joystick_layout.addWidget(z_down_button,2,3)
        
 
    def move_stage(self, channel, value):
        thread = threading.Thread(target=self.controller_mcm.move_um, args=(channel, value, False))
        thread.start()

    def move_stage_2(self, channel, direction):
        move_value = default_um_btn_move * direction
        thread = threading.Thread(target=self.controller_mcm.move_um, args=(channel, default_um_btn_move*direction, True))
        thread.start()
        self.update_ui_elements(channel, move_value)

    def send_command_arduino(self,command):
        self.arduino.write(bytes(command, 'utf-8'))
        time.sleep(0.5)  


    def set_z_position(self, position_type):
        current_z_position = self.z_slider.value()
        if position_type == 'max':
            self.z_max_label.setText(f'Z-Max: {current_z_position}')
        elif position_type == 'min':
            self.z_min_label.setText(f'Z-Min: {current_z_position}')

    def start_acquisition(self):
        try:
            z_min = int(self.z_min_label.text().split(": ")[1])
            z_max = int(self.z_max_label.text().split(": ")[1])
            z_step = int(self.z_step_text.text())
        except ValueError:
            print("Invalid Z values or Z step")
            return

        self.acquisition_running = True  # Set the running flag to True
        self.send_command_arduino("s?")  # Start stepper motor

        def move_z():
            for z in range(z_min, z_max+z_step, z_step):
                if not self.acquisition_running:
                    break
                self.move_stage(2, z)
                if not z == z_min:
                    self.update_ui_elements(2, z_step) # do not add a delta the first time
                time.sleep(1)  # Wait for 1 second

            self.send_command_arduino("h?")  # Stop stepper motor

        self.acquisition_thread = threading.Thread(target=move_z)
        self.acquisition_thread.start()

    def stop_acquisition(self):
        self.acquisition_running = False
        self.send_command_arduino("h?")  # Stop stepper motor

    def set_encoders_to_cero(self):
        #set all the counters for the stage in 0
        for channel in range(3):
            self.controller_mcm._set_encoder_counts_to_zero(channel)
        self.x_text.setText(str(0))
        self.x_slider.setValue(0)

        self.y_text.setText(str(0))
        self.y_slider.setValue(0)

        self.z_text.setText(str(0))
        self.z_slider.setValue(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MicroscopeControlGUI()      
    sys.exit(app.exec_())
