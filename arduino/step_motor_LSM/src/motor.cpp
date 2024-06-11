#include "motor.h"

TMC2130Stepper driver = TMC2130Stepper(EN_PIN, DIR_PIN, STEP_PIN, CS_PIN);
AccelStepper stepper = AccelStepper(stepper.DRIVER, STEP_PIN, DIR_PIN);

bool dir = true;
int sheet_width = 100;
long headAcceleration = 5000;

void init_motor() {
    
    pinMode(CS_PIN, OUTPUT);
    digitalWrite(CS_PIN, HIGH);
   
    driver.begin();           
    driver.rms_current(600);    // Set stepper current to 600mA
    driver.stealthChop(1);      // Enable extremely quiet stepping
    driver.stealth_autoscale(1);
    driver.microsteps(16);

    stepper.setMaxSpeed(SCAN_SPEED);
    stepper.setAcceleration(headAcceleration); 
    stepper.setEnablePin(EN_PIN);
    stepper.setPinsInverted(false, false, true);
    //stepper.enableOutputs();
    // Grab the initial position and set it as the cero position
    //stepper.setCurrentPosition(0);
}

void task_move_motor(void *pvParameters) {
  command_t received_command;
  bool first_move = true;
  bool allow_movement = false;

  while(1)
  {
    // If there is an element in the queue...
    if(x_received_commands_queue != NULL && xQueueReceive(x_received_commands_queue, (void *)&received_command, 0) == pdTRUE){
      if(received_command.command == "w"){ // change width
        sheet_width = received_command.value;
      }else if (received_command.command == "a"){ // Change amplitude
        stepper.setAcceleration(received_command.value); 
      }else if(received_command.command == "s"){  // Start the stepper motor movement
        stepper.enableOutputs();
        stepper.setCurrentPosition(0);
        allow_movement = true;
        first_move = true;
      }else if(received_command.command == "h"){  // Stop the stepper motor
        stepper.stop();
        stepper.disableOutputs();
        allow_movement = false;
      }
      
    }

    if(allow_movement){
      if (stepper.distanceToGo() == 0) {
        if (first_move){
          stepper.moveTo(sheet_width/2);
          first_move = false;
        }
        else if (dir){
          stepper.moveTo(sheet_width);  
        }else{
          stepper.moveTo(-1*sheet_width);
        }
        dir = !dir;
      }

      stepper.run();
    }
    vTaskDelay(1/ portTICK_PERIOD_MS);
  }
  
}