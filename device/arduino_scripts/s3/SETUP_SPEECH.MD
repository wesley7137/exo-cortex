ESP-SR Logo

    Getting Started
    Audio Front-end (AFE)
    Wake Word WakeNet

Speech Command Word MultiNet

    MultiNet Command Word Recognition Model
    Commands Recognition Process

Speech Commands Customization Methods

        Use MultiNet
        Resource Occupancy
    Speech Synthesis (Only Supports Chinese Language)
    Flashing Models
    Benchmark
    Test Methods
    Glossary

    » Command Word
    Edit on GitHub

Command Word

[中文]
MultiNet Command Word Recognition Model

MultiNet is a lightweight model designed to recognize multiple speech command words offline based on ESP32-S3. Currently, up to 200 speech commands, including customized commands, are supported.

    Support Chinese and English speech commands recognition

    Support user-defined commands

    Support adding / deleting / modifying commands during operation

    Up to 200 commands are supported

    It supports single recognition and continuous recognition

    Lightweight and low resource consumption

    Low delay, within 500ms

    Support online Chinese and English model switching (esp32s3 only)

    The model is partitioned separately to support users to apply OTA

The MultiNet input is the audio processed by the audio-front-end algorithm (AFE), with the format of 16 KHz, 16 bit and mono. By recognizing the audio signals, speech commands can be recognized.

Please refer to Models Benchmark to check models supported by Espressif SoCs.

For details on flash models, see Section Flashing Models .

Note

Models ending with Q8 represents the 8 bit version of the model, which is more lightweight.
Commands Recognition Process

Please see the flow diagram for commands recognition below:
speech_command-recognition-system

speech_command-recognition-system
Speech Commands Customization Methods

Note

Mixed Chinese and English is not supported in command words.

The command word cannot contain Arabic numerals and special characters.

Please refer to Chinese version documentation for Chinese speech commands customization methods.
MultiNet7 customize speech commands

MultiNet7 use phonemes for English speech commands. Please modify a text file model/multinet_model/fst/commands_en.txt by the following format:

    # command_id,command_grapheme,command_phoneme
    1,tell me a joke,TfL Mm c qbK
    2,sing a song,Sgl c Sel

    Column 1: command ID, it should start from 1 and cannot be set to 0.

    Column 2: command_grapheme, the command sentence. It is recommended to use lowercase letters unless it is an acronym that is meant to be pronounced differently.

    Column 3: command_phoneme, the phoneme sequence of the command which is optional. To fill this column, please use tool/multinet_g2p.py to do the Grapheme-to-Phoneme conversion and paste the results at the third column correspondingly (this is the recommended way).

If Column 3 is left empty, then an internal Grapheme-to-Phoneme tool will be called at runtime. But there might be a little accuracy drop in this way due the different Grapheme-to-Phoneme algorithms used.
MultiNet6 customize speech commands

MultiNet6 use grapheme for English speech commands, you can add/modify speech commands by words directly. Please modify a text file model/multinet_model/fst/commands_en.txt by the following format:

    # command_id,command_grapheme
    1,TELL ME A JOKE
    2,MAKE A COFFEE

    Column 1: command ID, it should start from 1 and cannot be set to 0.

    Column 2: command_grapheme, the command sentence. It is recommended to use all capital letters.

The extra column in the default commands_en.txt is to keep it compatible with MultiNet7, there is no need to fill the third column when using MultiNet6.
MultiNet5 customize speech commands

MultiNet5 use phonemes for English speech commands. For simplicity, we use characters to denote different phonemes. Please use tool/multinet_g2p.py to do the convention.

    Via menuconfig

            Navigate to idf.py menuconfig > ESP Speech Recognition > Add Chinese speech commands/Add English speech commands to add speech commands. For details, please refer to the example in ESP-Skainet.
        menuconfig_add_speech_commands

        menuconfig_add_speech_commands

        Please note that a single Command ID can correspond to more than one commands. For example, “da kai kong tiao” and “kai kong tiao” have the same meaning. Therefore, users can assign the same command id to these two commands and separate them with “,” (no space required before and after).

            Call the following API:

        /**
            * @brief Update the speech commands of MultiNet by menuconfig
            *
            * @param multinet            The multinet handle
            *
            * @param model_data          The model object to query
            *
            * @param langugae            The language of MultiNet
            *
            * @return
            *     - ESP_OK                  Success
            *     - ESP_ERR_INVALID_STATE   Fail
            */
            esp_err_t esp_mn_commands_update_from_sdkconfig(esp_mn_iface_t *multinet, const model_iface_data_t *model_data);

Customize Speech Commands Via API calls

Alternatively, speech commands can be modified via API calls, this method works for MultiNet5, MultiNet6 and MultiNet7.

MutiNet5 requires the input command string to be phonemes, and MultiNet6 and MultiNet7 only accepts grapheme inputs to API calls.

    Apply new changes, the add/remove/modify/clear actions will not take effect util this function is called.

        /**
        * @brief Update the speech commands of MultiNet
        *
        * @Warning: Must be used after [add/remove/modify/clear] function,
        *           otherwise the language model of multinet can not be updated.
        *
        * @return
        *     - NULL                 Success
        *     - others               The list of error phrase which can not be parsed by multinet.
        */
        esp_mn_error_t *esp_mn_commands_update();

    Note

    The modifications will not be applied, thus not printed out, until you call esp_mn_commands_update().

Add a new speech command, will return ESP_ERR_INVALID_STATE if the input string is not in the correct format.

    /**
    * @brief Add one speech commands with command string and command ID
    *
    * @param command_id      The command ID
    * @param string  The command string of the speech commands
    *
    * @return
    *     - ESP_OK                  Success
    *     - ESP_ERR_INVALID_STATE   Fail
    */
    esp_err_t esp_mn_commands_add(int command_id, char *string);

Remove a speech command, will return ESP_ERR_INVALID_STATE if the command does not exist.

    /**
    * @brief Remove one speech commands by command string
    *
    * @param string  The command string of the speech commands
    *
    * @return
    *     - ESP_OK                  Success
    *     - ESP_ERR_INVALID_STATE   Fail
    */
    esp_err_t esp_mn_commands_remove(char *string);

Modify a speech command, will return ESP_ERR_INVALID_STATE if the command does not exist.

    /**
    * @brief Modify one speech commands with new command string
    *
    * @param old_string  The old command string of the speech commands
    * @param new_string  The new command string of the speech commands
    *
    * @return
    *     - ESP_OK                  Success
    *     - ESP_ERR_INVALID_STATE   Fail
    */
    esp_err_t esp_mn_commands_modify(char *old_string, char *new_string);

Clear all speech commands.

    /**
    * @brief Clear all speech commands in linked list
    *
    * @return
    *     - ESP_OK                  Success
    *     - ESP_ERR_INVALID_STATE   Fail
    */
    esp_err_t esp_mn_commands_clear(void);

Print cached speech commands, this function will print out all cached speech commands. Cached speech commands will be applied after esp_mn_commands_update() is called.

    /**
    * @brief Print all commands in linked list.
    */
    void esp_mn_commands_print(void);

Print active speech commands, this function will print out all active speech commands.

    /**
    * @brief Print all commands in linked list.
    */
    void esp_mn_active_commands_print(void);

Use MultiNet

We suggest to use MultiNet together with audio front-end (AFE) in ESP-SR. For details, see Section AFE Introduction and Use .

After configuring AFE, users can follow the steps below to configure and run MultiNet.
Initialize MultiNet

    Load and initialize MultiNet. For details, see Section flash_model

    Customize speech commands. For details, see Section Speech Commands Customization Methods

Run MultiNet

Users can start MultiNet after enabling AFE and WakeNet, but must pay attention to the following limitations:

    The frame length of MultiNet must be equal to the AFE fetch frame length

    The audio format supported is 16 KHz, 16 bit, mono. The data obtained by AFE fetch is also in this format

    Get the length of frame that needs to pass to MultiNet

        int mu_chunksize = multinet->get_samp_chunksize(model_data);

    mu_chunksize describes the short of each frame passed to MultiNet. This size is exactly the same as the number of data points per frame obtained in AFE.

Start the speech recognition

    We send the data from AFE fetch to the following API:

    esp_mn_state_t mn_state = multinet->detect(model_data, buff);

    The length of buff is mu_chunksize * sizeof(int16_t).

MultiNet Output

Speech command recognition must be used with WakeNet. After wake-up, MultiNet detection can start.

Afer running, MultiNet returns the recognition output of the current frame in real time mn_state, which is currently divided into the following identification states:

    ESP_MN_STATE_DETECTING

        Indicates that the MultiNet is detecting but the target speech command word has not been recognized.

    ESP_MN_STATE_DETECTED

        Indicates that the target speech command has been recognized. At this time, the user can call get_results interface to obtain the recognition results.

        esp_mn_results_t *mn_result = multinet->get_results(model_data);

The recognition result is stored in the return value of the get_result API in the following format:

typedef struct{
esp_mn_state_t state;
int num; // The number of phrase in list, num<=5. When num=0, no phrase is recognized.
int phrase_id[ESP_MN_RESULT_MAX_NUM]; // The list of phrase id.
float prob[ESP_MN_RESULT_MAX_NUM]; // The list of probability.
} esp_mn_results_t;

        where,

            state is the recognition status of the current frame

            num means the number of recognized commands, num <= 5, up to 5 possible results are returned

            phrase_id means the Phrase ID of speech commands

            prob means the recognition probability of the recognized entries, which is arranged from large to small

        Users can use phrase_id[0] and prob[0] get the recognition result with the highest probability.

    ESP_MN_STATE_TIMEOUT

        Indicates the speech commands has not been detected for a long time and will exit automatically and wait to be waked up again.

Single recognition mode and Continuous recognition mode: _ Single recognition mode: exit the speech recognition when the return status is ESP_MN_STATE_DETECTED _ Continuous recognition mode: exit the speech recognition when the return status is ESP_MN_STATE_TIMEOUT
Resource Occupancy

For the resource occupancy for this model, see Resource Occupancy.

Provide feedback about this document

© Copyright 2016 - 2022, Espressif Systems (Shanghai) Co., Ltd.

    Built with Sphinx using a theme based on Read the Docs Sphinx Theme.
    Download PDF


    Getting Started
    Audio Front-end (AFE)
    Wake Word WakeNet
    Speech Command Word MultiNet
    Speech Synthesis (Only Supports Chinese Language)

Flashing Models

Configuration

        How To Use
    Benchmark
    Test Methods
    Glossary

    » Flashing Models
    Edit on GitHub

Flashing Models

[中文]

In the AI industry, a model refers to a mathematical representation of a system or process. It is used to make predictions or decisions based on input data. There are many types of models, such as decision trees, neural networks, and support vector machines, each with their own strengths and weaknesses. Esprssif also provides our trained models such as WakeNet and MultiNet (see the model data used in model)

To use our models in your project, you need to flash these models. Currently, ESP-SR supports the following methods to flash models:

ESP32-S3:

    Load directly from SIP Flash File System (flash)

    Load from external SD card

So that on ESP32-S3 you can:

        Greatly reduce the size of the user application APP BIN

        Supports the selection of up to two wake words

        Support online switching of Chinese and English Speech Command Recognition

        Convenient for users to perform OTA

        Supports reading and changing models from SD card, which is more convenient and can reduce the size of module Flash used in the project

        When the user is developing the code, when the modification does not involve the model, it can avoid flashing the model data every time, greatly reducing the flashing time and improving the development efficiency

Configuration

Run idf.py menuconfig to navigate to ESP Speech Recognition:
overview

overview
Model Data Path

This option indicates the storage location of the model data: Read model data from flash or Read model data from SD card.

    Read model data from flash means that the model data is stored in the flash, and the model data will be loaded from the flash partition

    Read model data from SD card means that the model data is stored in the SD card, and the model data will be loaded from the SD card

Use AFE

This option is enabled by default. Users do not need to modify it. Please keep the default configuration.
Use WakeNet

This option is enabled by default. When the user only uses AEC or BSS, etc., and does not need WakeNet or MultiNet, please disable this option, which reduces the size of the project firmware.

Select wake words by via menuconfig by navigating to ESP Speech Recognition > Select wake words. The model name of wake word in parentheses must be used to initialize WakeNet handle.

    select wake wake

If you want to select multiple wake words, please select Load Multiple Wake Words

    multi wake wake

Then you can select multiple wake words at the same time:

    image1

Note

ESP32-S3 does support multiple wake words. Users can select more than one wake words according to the hardware flash size.

For more details, please refer to WakeNet .
Use Multinet

This option is enabled by default. When users only use WakeNet or other algorithm modules, please disable this option, which reduces the size of the project firmware in some cases.
Chinese Speech Commands Model

ESP32-S3 supports command words in both Chinese and English:

    None

    Chinese single recognition (MultiNet4.5)

    Chinese single recognition (MultiNet4.5 quantized with 8-bit)

    English Speech Commands Model

The user needs to add Chinese Speech Command words to this item when Chinese Speech Commands Model is not None.

For more details, please refer to Section MultiNet .
English Speech Commands Model

ESP32-S3 supports command words in both Chinese and English, and allows users to switch between these two languages.

    None

    English recognition (MultiNet5 quantized with 8-bit, depends on WakeNet8)

    Add Chinese speech commands

The user needs to add English Speech Command words to this item when English Speech Commands Model is not None.
How To Use

After the above-mentioned configuration, users can initialize and start using the models following the examples described in the ESP-Skainet repo.

Here, we only introduce the code implementation, which can also be found in src/model_path.c.

ESP32-S3 can load model data from flash or SD card.
Load Model Data from flash

    Write a partition table:

        model,  data, spiffs,         , SIZE,

        Among them, SIZE can refer to the recommended size when the user uses idf.py build to compile, for example: Recommended model partition size: 500K

    Initialize the flash partition: User can use esp_srmodel_init(partition_label) API to initialize flash and return all loaded models.

            base_path: The model storage base_path is srmodel and cannot be changed

            partition_label: The partition label of the model is model, which needs to be consistent with the Name in the above partition table

After completing the above configuration, the project will automatically generate model.bin after the project is compiled, and flash it to the flash partition.
Load Model Data from SD Card

When configured to load model data from Read model data from SD card, users need to:

    Manually load model data from SD card

        After the above-mentioned configuration, users can compile the code, and copy the files in model/target to the root directory of the SD card.

    Initialize SD card

        Users must initialize SD card so the chip can load SD card. Users of ESP-Skainet can call esp_sdcard_init("/sdcard", num); to initialize any board supported SD cards. Otherwise, users need to write the initialization code themselves. After the above-mentioned steps, users can flash the project.

    Read models

        User use esp_srmodel_init(model_path) to read models in model_path of SD card.

Model initialization and Usage

//
// step1: return models in flash or in sdcard
//
char \*model_path = your_model_path: // partition_label or model_path in sdcard;
models = esp_srmodel_init(model_path);

//
// step2: select the specific model by keywords
//
char *wn_name = esp_srmodel_filter(models, ESP_WN_PREFIX, NULL); // select WakeNet model
char *nm_name = esp_srmodel_filter(models, ESP_MN_PREFIX, NULL); // select MultiNet model
char *alexa_wn_name = esp_srmodel_filter(models, ESP_WN_PREFIX, "alexa"); // select WakeNet with "alexa" wake word.
char *en_mn_name = esp_srmodel_filter(models, ESP_MN_PREFIX, ESP_MN_ENGLISH); // select english MultiNet model
char \*cn_mn_name = esp_srmodel_filter(models, ESP_MN_PREFIX, ESP_MN_CHINESE); // select english MultiNet model

// It also works if you use the model name directly in your code.
char \*my_wn_name = "wn9_hilexin"
// we recommend you to check that it is loaded correctly
if (!esp_srmodel_exists(models, my_wn_name))
printf("%s can not be loaded correctly\n")

//
// step3: initialize model
//
esp_wn_iface_t *wakenet = esp_wn_handle_from_name(wn_name);
model_iface_data_t *wn_model_data = wakenet->create(wn_name, DET_MODE_2CH_90);

esp_mn_iface_t *multinet = esp_mn_handle_from_name(mn_name);
model_iface_data_t *mn_model_data = multinet->create(mn_name, 6000);

Provide feedback about this document
