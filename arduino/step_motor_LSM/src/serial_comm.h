#pragma once
#include <Arduino.h>
#include <Arduino_FreeRTOS.h>
#include <semphr.h>
#include <queue.h>

#define QUEUE_LEN 10
#define SEMAPHORE_BLOCK_TIME 15
#define QUEUE_SEND_BLOCK_TIME 15

extern SemaphoreHandle_t x_serial_rx_semaphore;
extern QueueHandle_t x_received_commands_queue;

typedef struct{
    String command;
    int value;
}command_t;

void task_rx_serial(void *pvParameters);