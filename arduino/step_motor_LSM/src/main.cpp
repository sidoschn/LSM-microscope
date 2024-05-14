#include <Arduino.h>
#include <Arduino_FreeRTOS.h>
#include <semphr.h>
#include <queue.h>
#include "motor.h"

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(10); // This time might be increased if the string is large

  init_motor();
  
  // Create task  
  xTaskCreate(
    task_move_motor
    ,  "Move motor according to amplitude and acceleration parameters"   
    ,  128  // stack size
    ,  NULL
    ,  2  // Priority 
    ,  NULL );

}

void loop(){
  // Hola mundo
  // Hallo welt
  // Hello world
}
