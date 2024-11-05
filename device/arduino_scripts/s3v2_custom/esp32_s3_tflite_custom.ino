#include <TensorFlowLite_ESP32.h>
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_log.h"
#include "tensorflow/lite/schema/schema_generated.h"


// Allocate tensor arena for model operations
constexpr int kTensorArenaSize = 100 * 1024;  // 100KB for ESP32-S3
uint8_t tensor_arena[kTensorArenaSize] __attribute__((aligned(16)));

// Global variables
tflite::MicroInterpreter* interpreter = nullptr;
TfLiteTensor* input = nullptr;
TfLiteTensor* output = nullptr;


void setupTensorFlow() {
    // Set up model
    static tflite::AllOpsResolver resolver;
    static tflite::MicroInterpreter static_interpreter(
        model, resolver, tensor_arena, kTensorArenaSize);
    interpreter = &static_interpreter;

    // Allocate tensors
    TfLiteStatus allocate_status = interpreter->AllocateTensors();
    if (allocate_status != kTfLiteOk) {
        Serial.println("AllocateTensors() failed");
        return;
    }

    // Get pointers for input/output tensors
    input = interpreter->input(0);
    output = interpreter->output(0);
}


void processAudio(int16_t* audioData, size_t length) {
    // Convert audio to model input format
    for (size_t i = 0; i < length && i < input->bytes / sizeof(float); i++) {
        input->data.f[i] = audioData[i] / 32768.0f;
    }

    // Run inference
    TfLiteStatus invoke_status = interpreter->Invoke();
    if (invoke_status != kTfLiteOk) {
        Serial.println("Invoke failed");
        return;
    }

    // Get prediction
    float prediction = output->data.f[0];
    if (prediction > 0.8) {  // Threshold for wake word detection
        Serial.println("Wake word detected!");
    }
}
