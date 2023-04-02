import urequests
import machine
import network
import time
import ubinascii
import config_general as cfg
import config_adc
import stats

PRINT_ENABLE = cfg.PRINT_ENABLE
LOCATION = int.from_bytes(machine.unique_id(), 'big')

# Network influxdb database URL
URL = cfg.URL

# LED pin for blinking
led = machine.Pin(cfg.PIN_LED_BLINKER, machine.Pin.OUT)

def printer(msg, enable=PRINT_ENABLE):
    if enable:
        print(msg)

def blink(num=1, hold_secs=0.1):
    for _ in range(num):
        led.on()
        time.sleep(hold_secs)
        led.off()
        time.sleep(hold_secs)

def wifi_connect(wdt):
    # Disable access point mode
    ap = network.WLAN(network.AP_IF)
    ap.active(False)

    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        sta_if.active(True)

        ssid = cfg.WIFI_SSID
        password = cfg.WIFI_PASSWORD

        printer('')
        printer('Connecting to network {}...'.format(ssid))

        # Change MAC address
        if cfg.CHANGE_MAC:
            new_mac = cfg.NEW_MAC
            new_mac = ubinascii.unhexlify(new_mac.replace(':', ''))
            sta_if.config(mac=new_mac)

        sta_if.connect(ssid, password)

        start = time.ticks_ms()
        while not sta_if.isconnected():
            # If not connected in WIFI_WAIT seconds, go to deep sleep and try again in INTERVAL_WAKE_SENSOR seconds
            if time.ticks_diff(time.ticks_ms(), start) > cfg.WIFI_WAIT:
                printer("Gave up connecting to wifi. Will sleep a while and try again later...")
                machine.deepsleep(cfg.INTERVAL_WAKE_SENSOR)
            machine.idle()

    printer('Connected. Network config: {}'.format(sta_if.ifconfig()))

    # If jumper is placed between pins PIN_TRIGGER_WEBREPL and PIN_CHECK_FOR_WEBREPL, start WebREPL feature instead of regular application
    # Useful for testing and OTA firmware upgrade
    trigger_webrepl = machine.Pin(cfg.PIN_TRIGGER_WEBREPL, machine.Pin.OUT)
    trigger_webrepl.on()
    check_trigger_webrepl = machine.Pin(cfg.PIN_CHECK_FOR_WEBREPL, machine.Pin.IN, machine.Pin.PULL_DOWN)
    if check_trigger_webrepl.value():
        import webrepl
        printer("WebREPL started")
        blink(4, 0.3)
        webrepl.start()
        trigger_webrepl.off()
        while True:
            wdt.feed()
            machine.idle()

def main():
    blink()

    power = machine.Pin(cfg.PIN_POWER_SENSOR, machine.Pin.OUT)

    # ADC for UV sensor (0-1 V), no attenuation: 12 bits in 0-1V range
    adc_uv = machine.ADC(machine.Pin(cfg.PIN_ADC_UV))

    # ADC for battery charge sensor, 6 dB attenuation: 12 bits in 0-2V range
    adc_battery = machine.ADC(machine.Pin(cfg.PIN_ADC_BATTERY))
    adc_battery.atten(machine.ADC.ATTN_6DB)

    power.on()
    time.sleep(1)

    # Enable a watchdog timer, mainly to prevent hanging when connecting to wifi
    wdt = machine.WDT(timeout=cfg.WDT_WAIT)

    # Connect to network
    wifi_connect(wdt)
    wdt.feed()

    while True:
        _uv_reading = []
        while len(_uv_reading) < cfg.NUM_READINGS_FILTER:
            _uv_reading.append(adc_uv.read() / 4095)
            time.sleep(cfg.SLEEP_SAMPLING)

        # UV sensor reading in V
        uv_reading = stats.get_median(_uv_reading)
        power.off()

        # UV index calculation
        uv_index = 0
        for row in reversed(cfg.uv_index_table):
            if uv_reading >= row[1]:
                uv_index = row[0]
                break

        # Convert to real voltage after voltage divider, truncating to "our" zero voltage and
        # with abs() to remove the negative sign in -0.00
        x = adc_battery.read()
        y = abs(config_adc.ADC_SLOPE * max(config_adc.ADC_0V, x) + config_adc.ADC_INTERCEPT)
        battery = '{:.2f}'.format(y)

        printer('')
        printer('UV: {:.3f} V'.format(uv_reading))
        printer('UV index: {}'.format(uv_index))
        printer('Bat: {} V'.format(battery))

        data = 'uv_vout,location={0} value={1:.3f} \n uv_index,location={0} value={2} \n battery,location={0} value={3}'.format(
            LOCATION, uv_reading, uv_index, battery
        )
        printer(data)

        wdt.feed()
        try:
            if cfg.SEND_TO_DB:
                if cfg.JWT_TOKEN is not None:
                    header_data = {"content-type": 'application/json; charset=utf-8', "Authorization": "Bearer " + cfg.JWT_TOKEN}
                    resp = urequests.post(URL, data=data, headers=header_data)
                else:
                    resp = urequests.post(URL, data=data)

                if resp.status_code == 204:
                    printer('Measurement post OK')
                    blink()
                else:
                    printer('Measurement post error')
                    blink(2, 0.3)
                resp.close()
        except:
            printer('Measurement post exception')
            blink(3, 0.3)

        # check if the device woke from a deep sleep
        if machine.reset_cause() == machine.DEEPSLEEP_RESET:
            printer('Woke from a deep sleep')

        printer('Going to deep sleep now...')

        # put the device to sleep
        machine.deepsleep(cfg.INTERVAL_WAKE_SENSOR)

        # Never gets here
        printer('Sleep 5')
        time.sleep(5)

# Main loop
main()
