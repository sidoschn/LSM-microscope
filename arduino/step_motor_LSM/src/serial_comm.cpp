#include "serial_comm.h"

// Declare a mutex Semaphore Handle which we will use to manage the Serial Port.
SemaphoreHandle_t x_serial_rx_semaphore;

// Queue to handle messages between serial task and analog ports task
QueueHandle_t x_received_commands_queue;
// Function to store the received command into the final structure

void command_to_structure(String command, command_t *received_message){

  // Get the positions of the separator "?"
  uint8_t question_mark_index = command.indexOf('?');

  // Store the values in the structure
  received_message->command = command.substring(0, question_mark_index);
  received_message->value = command.substring(question_mark_index + 1).toInt();

}


void task_rx_serial(void *pvParameters){
  command_t received_message;
  
  while(true){

    // take the semaphore if there is an incomming message
    while (Serial.available()){
      if ( xSemaphoreTake( x_serial_rx_semaphore, SEMAPHORE_BLOCK_TIME ) == pdTRUE )
      {  
        String command_received = Serial.readString();
        command_received.trim(); // remove \n character

        command_to_structure(command_received, &received_message);        
        if(xQueueSend(x_received_commands_queue,(void *)&received_message, QUEUE_SEND_BLOCK_TIME) == pdTRUE){
            // do nothing... maybe later print a feedback message
        }
        xSemaphoreGive( x_serial_rx_semaphore );  // give the semaphore
      }
    }
    vTaskDelay( 15 / portTICK_PERIOD_MS);
  }
}