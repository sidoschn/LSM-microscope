#include "motor.h"

TMC2130Stepper driver = TMC2130Stepper(EN_PIN, DIR_PIN, STEP_PIN, CS_PIN);
AccelStepper stepper = AccelStepper(stepper.DRIVER, STEP_PIN, DIR_PIN);

bool dir = true;
int sheet_width = 200;
long headAcceleration = 5000;
long cero_position = 0;

void init_motor() {
    
    pinMode(CS_PIN, OUTPUT);
    digitalWrite(CS_PIN, HIGH);

    // Grab the initial position and set it as the cero position
    cero_position = stepper.currentPosition();
    
    driver.begin();           
    driver.rms_current(600);    // Set stepper current to 600mA
    driver.stealthChop(1);      // Enable extremely quiet stepping
    driver.stealth_autoscale(1);
    driver.microsteps(16);

    stepper.setMaxSpeed(SCAN_SPEED);
    stepper.setAcceleration(headAcceleration); 
    stepper.setEnablePin(EN_PIN);
    stepper.setPinsInverted(false, false, true);
    stepper.enableOutputs();
}

void task_move_motor(void *pvParameters) {
  command_t received_command;
  long current_position;
  int new_sheet_width = sheet_width;
  int first_move = true;

  while(1)
  {
    // If there is an element in the queue...
    if(x_received_commands_queue != NULL && xQueueReceive(x_received_commands_queue, (void *)&received_command, 0) == pdTRUE){
      if(received_command.command == "w"){
        new_sheet_width = received_command.value;
      }else if (received_command.command == "a"){
        stepper.setAcceleration(received_command.value); 
      }
      
    }

    current_position = stepper.currentPosition();
  
    if (stepper.distanceToGo() == 0) {
      if (first_move){
        stepper.move(sheet_width/2);
        first_move = false;
      }
      else if (dir){
        stepper.move(sheet_width);  
      }else{
        stepper.move(-1*sheet_width);
      }
      dir = !dir;
    }

    // Update the sheet width only when it cross the cero position
    if(current_position == cero_position){
      sheet_width = new_sheet_width;
    }
    stepper.run();

    vTaskDelay(2/ portTICK_PERIOD_MS);
  }
  
}