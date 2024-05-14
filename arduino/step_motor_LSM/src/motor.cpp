#include "motor.h"

TMC2130Stepper driver = TMC2130Stepper(EN_PIN, DIR_PIN, STEP_PIN, CS_PIN);
AccelStepper stepper = AccelStepper(stepper.DRIVER, STEP_PIN, DIR_PIN);

bool dir = false;
int sheetWidth = 200;
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
    stepper.enableOutputs();
}

void task_move_motor(void *pvParameters) {
    while(1){
        if (stepper.distanceToGo() == 0) {
            if (dir){
            stepper.move(sheetWidth);
            }else{
            stepper.move(-1*sheetWidth);
            }
            dir = !dir;
        }
        stepper.run();

        vTaskDelay(2/ portTICK_PERIOD_MS);
    }
  
}