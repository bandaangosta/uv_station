import machine
import config_general as cfg
from machine import ADC
from time import sleep

ITER_FOR_AVG = 5

def create_config():
    ''' Calculate conversion parameters for A/D

        This is done by obtaining 2 measurement points (x5, y5) and (x0, y0) and calculating
        line equation parameters for A/D to real (scaled) voltage conversion.
        Conversion is assumed linear.

        This calibration is necessary given we are using an extra resistor in the voltage divider to be able
        to use Wemos A/D (maximum input 1V) with around 5V input.
    '''

    # Instantiate A/D converter
    adc = machine.ADC(machine.Pin(cfg.PIN_ADC_BATTERY))
    adc.atten(machine.ADC.ATTN_6DB)

    # Open configuration file for writing (will overwrite if existing)
    f = open('config_adc.py', 'w')

    # Input 5V pin voltage read with handheld voltmeter
    lines = []
    user_input = input('Enter voltmeter voltage on 5V pin: ')
    line = 'REAL_5V = {}'.format(user_input)
    f.write(line + '\n')
    lines.append(line)

    y5 = float(user_input)

    # Get ADC readout for GND pin
    input('Connect ADC to GND pin and press Enter...')

    readout = 0
    for i in range(ITER_FOR_AVG):
        readout += adc.read()
        sleep(0.5)

    line = 'ADC_0V = {:.0f}'.format(readout / ITER_FOR_AVG)
    f.write(line + '\n')
    lines.append(line)

    x0 = int(readout / ITER_FOR_AVG)
    y0 = 0

    # Get ADC readout for 5V pin
    input('Connect ADC to 5V pin and press Enter...')

    readout = 0
    for i in range(ITER_FOR_AVG):
        readout += adc.read()
        sleep(0.5)

    line = 'ADC_5V = {:.0f}'.format(readout / ITER_FOR_AVG)
    f.write(line + '\n')
    lines.append(line)

    x5 = int(readout / ITER_FOR_AVG)

    # Parameter calculation for equation y = m * x + b
    m = (y5 - y0) / (x5 - x0)
    b = -1 * m * x0

    line = 'ADC_SLOPE = {:.4f}'.format(m)
    lines.append(line)
    f.write(line + '\n')

    line = 'ADC_INTERCEPT = {:.4f}'.format(b)
    lines.append(line)
    f.write(line + '\n')
    f.close()

    print('config.py was written with content:')
    print('\n'.join(lines))

def test_config():
    import config_adc as cfg_adc

    # Instantiate A/D converter
    adc = machine.ADC(machine.Pin(cfg.PIN_ADC_BATTERY))
    adc.atten(machine.ADC.ATTN_6DB)

    while True:
        input('Connect ADC to a test voltage and press Enter...')
        x = adc.read()

        # Convert to real voltage after voltage divider, truncating to "our" zero voltage and
        # with abs() to remove the negative sign in -0.00
        y = abs(cfg_adc.ADC_SLOPE * max(cfg_adc.ADC_0V, x) + cfg_adc.ADC_INTERCEPT)
        battery = '{:.2f}'.format(y)
        print('adc: {} converted: {}'.format(x, battery))
