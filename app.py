from flask import Flask, Response
from smbus import SMBus

# I2C simplified: 0x5E
EE895ADDRESS = 0x5E
I2CREGISTER = 0x00

app = Flask(__name__)
i2cbus = SMBus(1)

@app.route('/metrics')
def metrics():
    read_data = i2cbus.read_i2c_block_data(EE895ADDRESS, I2CREGISTER, 8)
    # read_data contains ints, which we need to convert to bytes and merge
    # see datasheet
    co2 = read_data[0].to_bytes(1, 'big') + read_data[1].to_bytes(1, 'big')
    temperature = read_data[2].to_bytes(1, 'big') + read_data[3].to_bytes(1, 'big')
    # reserved value - useful to check that the sensor is reading out correctly
    # this should be 0x8000
    resvd = read_data[4].to_bytes(1, 'big') + read_data[5].to_bytes(1, 'big')
    pressure = read_data[6].to_bytes(1, 'big') + read_data[7].to_bytes(1, 'big')
    resp = '# HELP co2_ppm CO2 ppm\n# TYPE co2_ppm gauge\nco2_ppm ' + str(int.from_bytes(co2, "big")) + '\n' + \
            '# HELP temperature_celsius Temperature in Celsius\n# TYPE temperature_celsius gauge\ntemperature_celsius ' + str(int.from_bytes(temperature, "big") / 100) + '\n' + \
            '# HELP pressure_mbar Pressure in millibar\n# TYPE pressure_mbar gauge\npressure_mbar ' + str(int.from_bytes(pressure, "big") / 10) + '\n' + \
            '# HELP resvd Reserved value\n# TYPE resvd gauge\nresvd ' + str(int.from_bytes(resvd, "big"))

    return Response(resp, mimetype='text/plain')
