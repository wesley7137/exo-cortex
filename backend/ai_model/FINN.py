class AI_Assistant_FINN:
    def __init__(self):
        self.is_listening = False
        self.image_capture_interval = 5  # seconds
        
    def wake_word_detection(self):
        # Mockup code for detecting wake word 'FINN'
        print('Listening for wake word...')
        # In real application, use ESP-SR for wake word detection
        examples = ['Hey FINN', 'Hello', 'Hey FINN analyze image', 'Stop listening']
        for sentence in examples:
            if 'hey FINN' in sentence.lower():
                print(f'Wake word detected in: "{sentence}"')
                self.command_recognition(sentence)

    def command_recognition(self, sentence):
        print('Processing command...')
        # In real implementation, use ESP-SR's MultiNet for command recognition
        if 'analyze image' in sentence.lower():
            self.capture_and_send_image()
        elif 'chat mode' in sentence.lower():
            self.start_audio_streaming()
        elif 'send image with context' in sentence.lower():
            self.capture_image_and_wait_for_text()
        elif 'stop listening' in sentence.lower():
            self.stop_listening()

    def capture_and_send_image(self):
        print('Capturing and sending image...')
        # Implementation: Use ESP32-CAM to capture and send image to backend

    def start_audio_streaming(self):
        print('Starting audio stream for conversation with FINN...')
        self.is_listening = True
        # Start continuous audio streaming and periodic image capture
        count = 0
        while self.is_listening and count < 3:  # Demo limit
            self.capture_and_send_image()
            time.sleep(self.image_capture_interval)
            count += 1

    def capture_image_and_wait_for_text(self):
        print('Taking image and waiting for text input...')
        self.capture_and_send_image()

    def stop_listening(self):
        print('Stopping listening...')
        self.is_listening = False
