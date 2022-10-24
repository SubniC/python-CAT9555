#!/bin/python3 -u
# -*- coding: utf-8 -*-

__author__ = "mdps"
__copyright__ = "Copyright 2021"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "mdps"
__status__ = "prealpha"

import logging
from enum import unique, IntEnum
from typing import Union, Optional, List, Tuple
from smbus2 import SMBus
from functools import wraps
from threading import Event


def _event_lock(io_func):
    """
    Decorator which allows the complete execution of *io_func* without a different
    thread calling another io functions which are decorated with this decorator.
    Uses threading.Event to make simply block other calls until done.
    """
    @wraps(io_func)
    def wrapper(*args, **kwargs):
        # Wait for flag to indicate that its available
        args[0].device_event.wait()

        # Clear the available state and indicate we're now locking access
        args[0].device_event.clear()

        res = io_func(*args, **kwargs)

        # Make access available again
        args[0].device_event.set()

        return res

    return wrapper


@unique
class RegisterEnum(IntEnum):
    INPUT = 0x00
    OUTPUT = 0x02
    POLARITY = 0x04
    CONFIG = 0x06


def word_to_bytes(word: int) -> Tuple[int, int]:
    msb = (word >> 8) & 0xff
    lsb = word & 0xff
    return msb, lsb


def bytes_to_word(byte_list: Union[Tuple[int, int], List]) -> int:
    return (byte_list[0] << 8) | byte_list[1]


class CAT9555:
    def __init__(self, i2c_port=1, address=0x24, logger: Optional[logging.Logger] = None):
        self.address = address
        self._i2c_port = i2c_port

        # Flag which indicates writing or reading condition
        self._device_available = Event()
        self._device_available.set()

        self._logger = logger or logging.getLogger('CAT9555')

        self._logger.info(f"CAT9555 created")

    @property
    def device_event(self):
        return self._device_available

    @property
    def device_busy(self) -> bool:
        return not self._device_available.is_set()

    def read_config(self) -> int:
        return self._read_word(RegisterEnum.CONFIG)

    def write_config(self, value: int) -> bool:
        return self._write_word(RegisterEnum.CONFIG, word_to_bytes(value))

    def read_polarity(self) -> int:
        return self._read_word(RegisterEnum.POLARITY)

    def write_polarity(self, value: int) -> bool:
        return self._write_word(RegisterEnum.POLARITY, word_to_bytes(value))

    def write_output(self, value: int) -> bool:
        return self._write_word(RegisterEnum.OUTPUT, word_to_bytes(value))

    def read_state(self) -> int:
        return self._read_word(RegisterEnum.INPUT)

    @_event_lock
    def _read_word(self, register: Union[RegisterEnum, int]) -> int:
        with SMBus(self._i2c_port) as bus:
            block = bus.read_i2c_block_data(self.address, int(register), 2)
            return bytes_to_word(block)

    @_event_lock
    def _write_word(self, register: Union[RegisterEnum, int], value: Union[Tuple[int, int], List]):
        try:
            with SMBus(self._i2c_port) as bus:
                bus.write_i2c_block_data(self.address, int(register), value)
                return True
        except:
            print("ERROR!!!!")
            return False
