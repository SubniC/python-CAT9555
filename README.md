# Python CAT9555/TCA9555 16bits I2C GPIO expander library.

***

# Description and credits

This is a very simple wrapper to work with CAT9555 I2C port expander, it is simple, fast and thread-safe (based on https://github.com/leloup314/TCA9555)

The library is designed to work with any SBC with I2C capabilities, the underlying communication is done by the smbus2 package (https://pypi.org/project/smbus2/)

CAT9555 datasheet -> https://www.onsemi.com/pdf/datasheet/cat9555-d.pdf

## Example

```python

# Create the object to access the CAT9555 on addres 0x24 on the I2C bus with ID 3
driver = CAT9555(i2c_port=3, address=0x24)

# Write the configuration register, PORT0 is the MSB, PORT1 the LSB.
driver.write_config(0x1eff)

# Set the polarity inverted on all pins
driver.write_polarity(0xffff)

# set all the outputs to low level
driver.write_output(0x0000)

# retrieve the configuration registers
config = driver.read_config()

# retrieve the io state
iostate = driver.read_state()

# retrieve the polarity register
pol = driver.read_polarity()
```

