#include <Arduino.h>
#include <Arduino_FreeRTOS.h>
#include <semphr.h>
#include <queue.h>
#include "motor.h"
#include "serial_comm.h"

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(10); // This time might be increased if the string is large

   // Create semaphore for serial printing
  if ( x_serial_rx_semaphore == NULL )  // Check to confirm that the Serial Semaphore has not already been created.
  {
    x_serial_rx_semaphore = xSemaphoreCreateMutex();  // Create a mutex semaphore
    if ( ( x_serial_rx_semaphore ) != NULL )
      xSemaphoreGive( ( x_serial_rx_semaphore ) );  // Make the Serial Port available for use
  }

  // Create queues of 10 elements for possible commands and messages
  x_received_commands_queue = xQueueCreate(QUEUE_LEN, sizeof(command_t)); 

  init_motor();
  
  // Create task  
  xTaskCreate(
    task_move_motor
    ,  "Move motor according to amplitude and acceleration parameters"   
    ,  128  // stack size
    ,  NULL
    ,  2  // Priority 
    ,  NULL );

  xTaskCreate(
    task_rx_serial
    ,  "Rx for serial communication"   // name
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
