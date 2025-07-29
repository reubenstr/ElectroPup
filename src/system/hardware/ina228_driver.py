#############################################################
#
#   INA228 by @megalloid
#   Git: https://github.com/megalloid/INA228
#
#   Need to fix:
#   1) Value of VSHUHT is needed to multiply to 10 that get correct value
#
#   @reubenstr
#   Modifed from original source to pass bus into class, return values
#
##############################################################


import time
from smbus2 import SMBus

# INA228 Address
INA228_PORT = 1
INA228_ADDRESS = 0x45
INA228_SHUNT_OHMS = 0.025
INA228_SHUNT_TEMPCO_VALUE = 0

#############################################################
# INA228 Reset bytes for CONFIG [15] / [14]
# Decription:
# RST - Generates a system reset that is the same as power-on reset.
# RSTACC - Resets the contents of accumulation registers ENERGY and CHARGE to 0
#############################################################
INA228_RST_NBIT = 15
INA228_RSTACC_NBIT = 14

#############################################################
# INA228 Initial conversion delay CONFIG [13:6]
# Description: Delay for initial ADC conversion in steps of 2 ms
# Values:
# 0x0 - 0 seconds (default)
# 0x1 - 2 ms
# 0xFF - 510ms
#############################################################
INA228_CONVERSION_DELAY = 0
INA228_CONVDLY_NBIT = 6

#############################################################
# INA228 Temperature compensation CONFIG [5]
# Description: Enables temperature compensation of an external shunt
# Values:
# 0x0 - disabled (default)
# 0x1 - enabled
#############################################################
INA228_TEMP_COMP = 0
INA228_TEMPCOMP_NBIT = 5

#############################################################
# INA228 ADC Shunt full scale range selection CONFIG [4]
# Description: Shunt full scale range selection across IN+ and IN–.
# Values:
# 0x0 - ±163.84 mV (default)
# 0x1 - ±40.96 mV
#############################################################
INA228_ADCRANGE = 0
INA228_ADCRANGE_NBIT = 4

#############################################################
# INA228 ADC Mode
# Description: The user can set the MODE bits for continuous or
# triggered mode on bus voltage, shunt voltage or temperature measurement.
#
# Values:
# 0x0h = Shutdown
# 0x1h = Triggered bus voltage, single shot
# 0x2h = Triggered shunt voltage, single shot
# 0x3h = Triggered shunt voltage and bus voltage, single shot
# 0x4h = Triggered temperature, single shot
# 0x5h = Triggered temperature and bus voltage, single shot
# 0x6h = Triggered temperature and shunt voltage, single shot
# 0x7h = Triggered bus voltage, shunt voltage and temperature, single shot
# 0x8h = Shutdown
# 0x9h = Continuous bus voltage only
# 0xAh = Continuous shunt voltage only
# 0xBh = Continuous shunt and bus voltage
# 0xCh = Continuous temperature only
# 0xDh = Continuous bus voltage and temperature
# 0xEh = Continuous temperature and shunt voltage
# 0xFh = Continuous bus voltage, shunt voltage and temperature (default)
#############################################################
INA228_ADC_MODE = 0xB
INA228_ADC_MODE_NBIT = 12

#############################################################
# INA228 ADC conversion time of bus voltage meas.
# Description: Sets the conversion time of the bus voltage measurement
#
# Values:
# 0x00h = 50 μs
# 0x01h = 84 μs
# 0x02h = 150 μs
# 0x03h = 280 μs
# 0x04h = 540 μs
# 0x05h = 1052 μs
# 0x06h = 2074 μs
# 0x07h = 4120 μs
#############################################################
INA228_VBUS_CONV_TIME = 0x05
INA228_VBUS_CONV_TIME_NBIT = 0x09

#############################################################
# INA228 ADC conversion time of shunt voltage meas.
# Description: Sets the conversion time of the shunt voltage measurement
#
# Values:
# 0x00h = 50 μs
# 0x01h = 84 μs
# 0x02h = 150 μs
# 0x03h = 280 μs
# 0x04h = 540 μs
# 0x05h = 1052 μs
# 0x06h = 2074 μs
# 0x07h = 4120 μs
#############################################################
INA228_VSHCT_CONV_TIME = 0x05
INA228_VSHCT_CONV_TIME_NBIT = 0x06

#############################################################
# INA228 ADC conversion time of temperatrure meas.
# Description: Sets the conversion time of the temperatrure measurement
#
# Values:
# 0x00h = 50 μs
# 0x01h = 84 μs
# 0x02h = 150 μs
# 0x03h = 280 μs
# 0x04h = 540 μs
# 0x05h = 1052 μs
# 0x06h = 2074 μs
# 0x07h = 4120 μs
#############################################################
INA228_VTCT_CONV_TIME = 0x05
INA228_VTCT_CONV_TIME_NBIT = 0x03


#############################################################
# INA228 ADC sample averaging count.
#
# Values:
# 0x0h = 1
# 0x1h = 4
# 0x2h = 16
# 0x3h = 64
# 0x4h = 128
# 0x5h = 256
# 0x6h = 512
# 0x7h = 1024
#############################################################
INA228_ADC_AVG = 3
INA228_AVG_NBIT = 0


#############################################################
# INA228 ADC alerts signal
#############################################################
INA228_ALERT_MEMSTAT = 0
INA228_ALERT_CNVRF = 1
INA228_ALERT_POL = 2
INA228_ALERT_BUSUL = 3
INA228_ALERT_BUSOL = 4
INA228_ALERT_SHNTUL = 5
INA228_ALERT_SHNTOL = 6
INA228_ALERT_TMPOL = 7
INA228_ALERT_MATHOF = 9
INA228_ALERT_CHARGEOF = 10
INA228_ALERT_ENERGYOF = 11
INA228_ALERT_APOL = 12
INA228_ALERT_SLOWALERT = 13
INA228_ALERT_CNVR = 14
INA228_ALERT_ALATCH = 15


class INA228:

    __INA228_CONFIG = 0x00
    __INA228_ADC_CONFIG = 0x01
    __INA228_SHUNT_CAL = 0x02
    __INA228_SHUNT_TEMPCO = 0x03
    __INA228_VSHUNT = 0x04
    __INA228_VBUS = 0x05
    __INA228_DIETEMP = 0x06
    __INA228_CURRENT = 0x07
    __INA228_POWER = 0x08
    __INA228_ENERGY = 0x09
    __INA228_CHARGE = 0x0A
    __INA228_DIAG_ALRT = 0x0B
    __INA228_SOVL = 0x0C
    __INA228_SUVL = 0x0D
    __INA228_BOVL = 0x0E
    __INA228_BUVL = 0x0F
    __INA228_TEMP_LIMIT = 0x10
    __INA228_PWR_LIMIT = 0x11
    __INA228_MANUFACTURER_ID = 0x3E
    __INA228_DEVICE_ID = 0x3F

    def __init__(
        self, bus : SMBus, address, shunt_ohms : float
    ):
        self._i2c = bus
        self._address = address        
        self._shunt_ohms = shunt_ohms

    def __convert2comp2float(self, twocompdata, nrofbit, factor):

        isnegative = 1
        isnegative = isnegative << (nrofbit - 1)

        dietemp = twocompdata

        if dietemp > isnegative:
            dietemp = (dietemp - (2 * isnegative)) * factor
        else:
            dietemp = dietemp * factor

        return dietemp

    def __binary_as_string(self, register_value):
        return bin(register_value)[2:].zfill(16)

    def __to_bytes(self, register_value):
        return [(register_value >> 8) & 0xFF, register_value & 0xFF]

    def read_register40(self, register):
        result = self._i2c.read_i2c_block_data(self._address, register, 5)
        register_value = (
            ((result[0] << 32) & 0xFF00000000)
            | ((result[1] << 24) & 0xFF000000)
            | ((result[2] << 16) & 0xFF0000)
            | ((result[3] << 8) & 0xFF00)
            | (result[4] & 0xFF)
        )
        # print("Read register 16 bits - 0x%02X: 0x%05X = 0b%s" %(register, register_value, self.__binary_as_string(register_value)))
        return register_value

    def read_register24(self, register):
        result = self._i2c.read_i2c_block_data(self._address, register, 3)
        register_value = (
            ((result[0] << 16) & 0xFF0000)
            | ((result[1] << 8) & 0xFF00)
            | (result[2] & 0xFF)
        )
        # print("Read register 24 bits - 0x%02X: 0x%05X = 0b%s" %(register, register_value, self.__binary_as_string(register_value)))
        return register_value

    def read_register16(self, register):
        result = self._i2c.read_i2c_block_data(self._address, register, 2)
        register_value = ((result[0] << 8) & 0xFF00) | (result[1] & 0xFF)
        # print("Read register 16 bits - 0x%02X: 0x%04X = 0b%s" %(register, register_value, self.__binary_as_string(register_value)))
        return register_value

    def write_register16(self, register, register_value):
        register_bytes = self.__to_bytes(register_value)
        # print("Write register 16 bits 0x%02X: 0x%02X 0b%s" % (register, register_value, self.__binary_as_string(register_value)))
        self._i2c.write_i2c_block_data(self._address, register, register_bytes)
        # self._i2c.write_word_data(self._address, register, register_value)

    def get_current_lsb(self):
        if INA228_ADCRANGE == 0:
            temp = 163.84e-3
        else:
            temp = 40.96e-3
        current_lsb = (temp / INA228_SHUNT_OHMS) / 524288
        return current_lsb

    def get_shunt_conv_factor(self):
        if INA228_ADCRANGE == 0:
            shunt_conv_factor = 1.25e-6
        else:
            shunt_conv_factor = 5.0e-6
        return shunt_conv_factor

    def reset_all(self):
        config = self.read_register16(self.__INA228_CONFIG)
        data = 1 << INA228_RST_NBIT
        config = config | data
        self.write_register16(self.__INA228_CONFIG, config)

    def reset_energy(self):
        config = self.read_register16(self.__INA228_CONFIG)
        data = 1 << INA228_RSTACC_NBIT
        config = config | data
        self.write_register16(self.__INA228_CONFIG, config)

    def set_config(self):
        # Write settings to CONFIG register
        config = self.read_register16(self.__INA228_CONFIG)
        config = (
            config
            | (INA228_CONVERSION_DELAY << INA228_CONVDLY_NBIT)
            | (INA228_TEMP_COMP << INA228_TEMPCOMP_NBIT)
            | (INA228_ADCRANGE << INA228_ADCRANGE_NBIT)
        )
        self.write_register16(self.__INA228_CONFIG, config)

    def set_adc_config(self):
        # Write settings to ADC CONFIG register
        config = self.read_register16(self.__INA228_ADC_CONFIG)
        config = (
            config
            | (INA228_ADC_MODE << INA228_ADC_MODE_NBIT)
            | (INA228_VBUS_CONV_TIME << INA228_VBUS_CONV_TIME_NBIT)
            | (INA228_VSHCT_CONV_TIME << INA228_VSHCT_CONV_TIME_NBIT)
            | (INA228_VTCT_CONV_TIME << INA228_VTCT_CONV_TIME_NBIT)
            | (INA228_ADC_AVG << INA228_AVG_NBIT)
        )
        self.write_register16(self.__INA228_ADC_CONFIG, config)

    def shunt_calib(self):
        calib_value = int(13107.2e6 * self.get_current_lsb() * INA228_SHUNT_OHMS)
        self.write_register16(self.__INA228_SHUNT_CAL, calib_value)

    def shunt_tempco(self):
        self.write_register16(self.__INA228_SHUNT_TEMPCO, INA228_SHUNT_TEMPCO_VALUE)

    def configure(self):
        self.reset_all()
        self.set_config()
        self.set_adc_config()
        self.shunt_calib()
        self.shunt_tempco()
        time.sleep(0.1)

    def get_shunt_voltage(self):
        if INA228_ADCRANGE == 1:
            conversion_factor = 312.5e-9  # nV/LSB
        else:
            conversion_factor = 78.125e-9  # nV/LSB
        raw = self.read_register24(self.__INA228_VSHUNT)
        vshunt = (
            self.__convert2comp2float(raw >> 4, 20, conversion_factor)
        ) * 10  # Find and fix *10
        return vshunt

    def get_vbus_voltage(self):
        conversion_factor = 195.3125e-6  # uV/LSB
        raw = self.read_register24(self.__INA228_VBUS)
        vbus = self.__convert2comp2float(raw >> 4, 20, conversion_factor)
        return vbus

    def get_temp_voltage(self):
        conversion_factor = 7.8125e-3
        raw = self.read_register16(self.__INA228_DIETEMP)
        temp = self.__convert2comp2float(raw, 16, conversion_factor)
        return temp

    def get_current(self):
        raw = self.read_register24(self.__INA228_CURRENT)
        current = self.__convert2comp2float(raw >> 4, 20, self.get_current_lsb())
        return current

    def get_power(self):
        current_lsb = self.get_current_lsb()
        raw = self.read_register24(self.__INA228_POWER)
        power = 3.2 * raw * current_lsb
        return power

    def get_energy(self):
        raw = self.read_register40(self.__INA228_ENERGY)
        energy = raw * 3.2 * 16 * self.get_current_lsb()
        return energy

    def get_charge(self):
        raw = self.read_register40(self.__INA228_CHARGE)
        return raw

    def get_diag_alerts(self, alert):
        raw = self.read_register16(self.__INA228_DIAG_ALRT)

        if alert == INA228_ALERT_ALATCH:
            if (raw & 0x1) == 0x0:
                print(
                    "MEMSTAT: Checksum error is detected in the device trim memory space"
                )
                return 1

        elif alert == INA228_ALERT_CNVRF:
            if (raw & 0x2) == 0x1:
                print("CNVRF: Conversion is completed")

        elif alert == INA228_ALERT_BUSUL:
            if (raw & 0x4) == 0x1:
                print(
                    "BUSUL: Bus voltage measurement falls below the threshold limit in the bus under-limit register"
                )

        elif alert == INA228_ALERT_BUSOL:
            if (raw & 0x8) == 0x1:
                print(
                    "BUSOL: Bus voltage measurement exceeds the threshold limit in the bus over-limit register"
                )

        elif alert == INA228_ALERT_SHNTUL:
            if (raw & 0x10) == 0x1:
                print(
                    "SHNTUL: Shunt voltage measurement falls below the threshold limit in the shunt under-limit register"
                )

        elif alert == INA228_ALERT_SHNTOL:
            if (raw & 0x40) == 0x1:
                print(
                    "SHNTOL: Shunt voltage measurement exceeds the threshold limit in the shunt over-limit register"
                )

        elif alert == INA228_ALERT_TMPOL:
            if (raw & 0x80) == 0x1:
                print(
                    "TMPOL: Temperature measurement exceeds the threshold limit in the temperature over-limit register"
                )

        elif alert == INA228_ALERT_MATHOF:
            if (raw & 0x100) == 0x1:
                print("MATHOF: Arithmetic operation resulted in an overflow error")

        elif alert == INA228_ALERT_CHARGEOF:
            if (raw & 0x200) == 0x1:
                print("CHARGEOF: 40 bit CHARGE register has overflowed")

        elif alert == INA228_ALERT_ENERGYOF:
            if (raw & 0x400) == 0x1:
                print("ENERGYOF: 40 bit ENERGY register has overflowed")

        elif alert == INA228_ALERT_APOL:
            if (raw & 0x800) == 0x1:
                print("APOL: Alert pin polarity inverted (active-high, open-drain)")
            else:
                print("APOL: Alert pin polarity normale (active-low, open-drain)")

        elif alert == INA228_ALERT_SLOWALERT:
            if (raw & 0x2000) == 0x1:
                print(
                    "SLOWALERT: ALERT function is asserted on the completed averaged value. ALERT comparison on averaged value"
                )
            else:
                print("SLOWALERT: ALERT comparison on non-averaged (ADC) value")

        elif alert == INA228_ALERT_CNVR:
            if (raw & 0x4000) == 0x1:
                print(
                    "CNVR: Alert pin to be asserted when the Conversion Ready Flag (bit 1) is asserted, indicating that a conversion cycle has completed. Enables conversion ready flag on ALERT pin"
                )
            else:
                print("CNVR: Disable conversion ready flag on ALERT pin")

        elif alert == INA228_ALERT_ALATCH:
            if (raw & 0x8000) == 0x1:
                print("ALATCH: Latched")
            else:
                print("ALATCH: Transparent")

    def set_shunt_overvoltage(self, value):
        if value >= 0:

            data = (value * INA228_SHUNT_OHMS) / self.get_shunt_conv_factor()

        else:

            value_temp = value * (-1)

            data = (value_temp * INA228_SHUNT_OHMS) / self.get_shunt_conv_factor()
            data = ~data
            data = data + 1

        self.read_register16(self.__INA228_SOVL)
        self.write_register16(self.__INA228_SOVL, data)

    def set_shunt_undervoltage(self, value):

        if value >= 0:

            data = (value * INA228_SHUNT_OHMS) / self.get_shunt_conv_factor()

        else:

            value_temp = value * (-1)

            data = (value_temp * INA228_SHUNT_OHMS) / self.get_shunt_conv_factor()
            data = ~data
            data = data + 1

        self.read_register16(self.__INA228_SUVL)
        self.write_register16(self.__INA228_SUVL, data)

    def set_bus_overvoltage(self, value):
        data = value / (16 * 195.3125e-6)
        self.read_register16(self.__INA228_BOVL)
        self.write_register16(self.__INA228_BOVL, data)

    def set_bus_undervoltage(self, value):
        data = value / (16 * 195.3125e-6)
        self.read_register16(self.__INA228_BUVL)
        self.write_register16(self.__INA228_BUVL, data)

    def set_temp_limit(self, value, consta):
        data = value / (16 * consta)
        self.read_register16(self.__INA228_TEMP_LIMIT)
        self.write_register16(self.__INA228_TEMP_LIMIT, data)

    def set_power_overlimit(self, value, consta):
        data = value / (16 * consta)
        self.read_register16(self.__INA228_PWR_LIMIT)
        self.write_register16(self.__INA228_PWR_LIMIT, data)

    def get_manufacturer_id(self):
        raw_id = self.read_register16(self.__INA228_MANUFACTURER_ID)
        return raw_id

    def get_deviceid(self):
        raw_id = self.read_register16(self.__INA228_DEVICE_ID)
        id = raw_id >> 4
        revision = raw_id & 0xF
        return id, revision