# General
INTERVAL_WAKE_SENSOR = int(5 * 60 * 1000)
NUM_READINGS_FILTER = 5
SLEEP_SAMPLING = 1.1
PRINT_ENABLE = False
SEND_TO_DB = False
CHANGE_MAC = False
WDT_WAIT = 1000 * 30
WIFI_WAIT = 1000 * 20

# URL for DB API write operation
URL = "URL_to_influxdb_write_endpoint_here"
JWT_TOKEN = "authorization_token_for_operation_above"

# Wi-fi
NEW_MAC = None
WIFI_SSID = "wifi_ssid_here"
WIFI_PASSWORD = "wifi_password_here"

# Pinout (GPIO numbering)
PIN_LED_BLINKER = 2 # ESP32 D1 mini
PIN_ADC_UV = 34 # ADC0 ESP32 D1 mini
PIN_ADC_BATTERY = 35 # ADC1 ESP32 D1 mini
PIN_POWER_SENSOR = 27 # pin used to temporarily provide power to UV sensor
PIN_CHECK_FOR_WEBREPL = 21
PIN_TRIGGER_WEBREPL = 17

# Sensor V to UV index lookup table
uv_index_table = [
    [1, 0.227],
    [2, 0.318],
    [3, 0.408],
    [4, 0.503],
    [5, 0.606],
    [6, 0.696],
    [7, 0.795],
    [8, 0.881],
    [9, 0.976],
    [10, 1.079],
    [11, 1.170]
]

