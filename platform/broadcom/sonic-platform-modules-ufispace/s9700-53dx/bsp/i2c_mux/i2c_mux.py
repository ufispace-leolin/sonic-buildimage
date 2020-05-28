#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2019 UfiSpace Co.,Ltd. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys

from bsp.common.logger import Logger
from bsp.const.const import BID

class PCA954x:

    def __init__(self, name, address, bus_num, bus_of_channel):
        self.name = self.NAME + " " + name
        self.address = address
        self.bus_num = bus_num
        self.ch_bus = bus_of_channel

class PCA9548(PCA954x):

    NAME = "pca9548"
    CHANNEL_MAX = 8

class PCA9546(PCA954x):

    NAME = "pca9546"
    CHANNEL_MAX = 4

class I2CMux:

    # MUX Addr
    I2C_ADDR_9548_ROOT_GB = 0x75
    I2C_ADDR_9548_ROOT_QSFP = 0x72
    I2C_ADDR_9548_ROOT_SFP_CPLD = 0x73
    I2C_ADDR_9548_CHILD_GB = 0x76
    I2C_ADDR_9548_CHILD_QSFP = 0x76
    I2C_ADDR_9548_CHILD_QSFPDD = 0x76
    I2C_ADDR_9548_CHILD_QSFPDDBOARD = 0x71

    NUM_I801_DEVICE = 0
    PATH_SYS_I2C_DEVICES = "/sys/bus/i2c/devices"

    def __init__(self, board_id):
        log = Logger(__name__)
        self.logger = log.getLogger()
        
        #Global Mux Alias
        self.I2C_BUS_MUX_ROOT = self.NUM_I801_DEVICE
        self.board_id = board_id

        if board_id == BID.NCP1_1_PROTO:
            # MUX PCA9548 ROOT Gearbox
            self.NUM_MUX_9548_ROOT_GB = (
                                        self.NUM_I801_DEVICE + 1,
                                        self.NUM_I801_DEVICE + 2,
                                        self.NUM_I801_DEVICE + 3,
                                        self.NUM_I801_DEVICE + 4,
                                        self.NUM_I801_DEVICE + 5,
                                        self.NUM_I801_DEVICE + 6,
                                        self.NUM_I801_DEVICE + 7,
                                        self.NUM_I801_DEVICE + 8)
            # MUX PCA9548 ROOT QSFP, QSFPDD
            self.NUM_MUX_9548_ROOT_QSFP = (
                                        self.NUM_I801_DEVICE + 9,
                                        self.NUM_I801_DEVICE + 10,
                                        self.NUM_I801_DEVICE + 11,
                                        self.NUM_I801_DEVICE + 12,
                                        self.NUM_I801_DEVICE + 13,
                                        self.NUM_I801_DEVICE + 14,
                                        self.NUM_I801_DEVICE + 15,
                                        self.NUM_I801_DEVICE + 16)
            # MUX PCA9548#2 SFP, CPLD, etc.
            self.NUM_MUX_9548_ROOT_SFP_CPLD = (
                                        self.NUM_I801_DEVICE + 17,
                                        self.NUM_I801_DEVICE + 18,
                                        self.NUM_I801_DEVICE + 19,
                                        self.NUM_I801_DEVICE + 20,
                                        self.NUM_I801_DEVICE + 21,
                                        self.NUM_I801_DEVICE + 22,
                                        self.NUM_I801_DEVICE + 23,
                                        self.NUM_I801_DEVICE + 24)
            # MUX PCA9548#3 Gearbox #1-#8
            self.NUM_MUX_9548_CHILD_GB0 = (
                                        self.NUM_I801_DEVICE + 25,
                                        self.NUM_I801_DEVICE + 26,
                                        self.NUM_I801_DEVICE + 27,
                                        self.NUM_I801_DEVICE + 28,
                                        self.NUM_I801_DEVICE + 29,
                                        self.NUM_I801_DEVICE + 30,
                                        self.NUM_I801_DEVICE + 31,
                                        self.NUM_I801_DEVICE + 32)
            # MUX PCA9548 Gearbox #9-#10
            self.NUM_MUX_9548_CHILD_GB1 = (
                                        self.NUM_I801_DEVICE + 33,
                                        self.NUM_I801_DEVICE + 34,
                                        self.NUM_I801_DEVICE + 35,
                                        self.NUM_I801_DEVICE + 36,
                                        self.NUM_I801_DEVICE + 37,
                                        self.NUM_I801_DEVICE + 38,
                                        self.NUM_I801_DEVICE + 39,
                                        self.NUM_I801_DEVICE + 40)
            # MUX PCA9548 QSFP 0-7
            self.NUM_MUX_9548_CHILD_QSFP0 = (
                                        self.NUM_I801_DEVICE + 41,
                                        self.NUM_I801_DEVICE + 42,
                                        self.NUM_I801_DEVICE + 43,
                                        self.NUM_I801_DEVICE + 44,
                                        self.NUM_I801_DEVICE + 45,
                                        self.NUM_I801_DEVICE + 46,
                                        self.NUM_I801_DEVICE + 47,
                                        self.NUM_I801_DEVICE + 48
                                        )
            # MUX PCA9548 QSFP 8-15
            self.NUM_MUX_9548_CHILD_QSFP1 = (
                                        self.NUM_I801_DEVICE + 49,
                                        self.NUM_I801_DEVICE + 50,
                                        self.NUM_I801_DEVICE + 51,
                                        self.NUM_I801_DEVICE + 52,
                                        self.NUM_I801_DEVICE + 53,
                                        self.NUM_I801_DEVICE + 54,
                                        self.NUM_I801_DEVICE + 55,
                                        self.NUM_I801_DEVICE + 56
                                        )
            # MUX PCA9548 QSFP 16-23
            self.NUM_MUX_9548_CHILD_QSFP2 = (
                                        self.NUM_I801_DEVICE + 57,
                                        self.NUM_I801_DEVICE + 58,
                                        self.NUM_I801_DEVICE + 59,
                                        self.NUM_I801_DEVICE + 60,
                                        self.NUM_I801_DEVICE + 61,
                                        self.NUM_I801_DEVICE + 62,
                                        self.NUM_I801_DEVICE + 63,
                                        self.NUM_I801_DEVICE + 64
                                        )
            # MUX PCA9548 QSFP 24-31
            self.NUM_MUX_9548_CHILD_QSFP3 = (
                                        self.NUM_I801_DEVICE + 65,
                                        self.NUM_I801_DEVICE + 66,
                                        self.NUM_I801_DEVICE + 67,
                                        self.NUM_I801_DEVICE + 68,
                                        self.NUM_I801_DEVICE + 69,
                                        self.NUM_I801_DEVICE + 70,
                                        self.NUM_I801_DEVICE + 71,
                                        self.NUM_I801_DEVICE + 72
                                        )
            # MUX PCA9548 QSFP 32-39
            self.NUM_MUX_9548_CHILD_QSFP4 = (
                                        self.NUM_I801_DEVICE + 73,
                                        self.NUM_I801_DEVICE + 74,
                                        self.NUM_I801_DEVICE + 75,
                                        self.NUM_I801_DEVICE + 76,
                                        self.NUM_I801_DEVICE + 77,
                                        self.NUM_I801_DEVICE + 78,
                                        self.NUM_I801_DEVICE + 79,
                                        self.NUM_I801_DEVICE + 80
                                        )
            # MUX PCA9548 QSFPDD 4-7 & DD Board
            self.NUM_MUX_9548_CHILD_QSFPDD0 = (
                                        self.NUM_I801_DEVICE + 81, # DD Board
                                        self.NUM_I801_DEVICE + 82, # NONE
                                        self.NUM_I801_DEVICE + 83, # NONE
                                        self.NUM_I801_DEVICE + 84, # NONE
                                        self.NUM_I801_DEVICE + 85, # Port 4
                                        self.NUM_I801_DEVICE + 86, # Port 5
                                        self.NUM_I801_DEVICE + 87, # Port 6
                                        self.NUM_I801_DEVICE + 88  # Port 7
                                        )
            # MUX PCA9548 QSFPDD 0-3
            self.NUM_MUX_9548_CHILD_QSFPDDBOARD = (
                                        self.NUM_I801_DEVICE + 89, # Port 0
                                        self.NUM_I801_DEVICE + 90, # Port 1
                                        self.NUM_I801_DEVICE + 91, # Port 2
                                        self.NUM_I801_DEVICE + 92, # Port 3
                                        self.NUM_I801_DEVICE + 93, # NONE
                                        self.NUM_I801_DEVICE + 94, # NONE
                                        self.NUM_I801_DEVICE + 95, # NONE
                                        self.NUM_I801_DEVICE + 96  # NONE
                                        )
            # MUX PCA9548 QSFPDD 8-12
            self.NUM_MUX_9548_CHILD_QSFPDD1 = (
                                        self.NUM_I801_DEVICE + 97,
                                        self.NUM_I801_DEVICE + 98,
                                        self.NUM_I801_DEVICE + 99,
                                        self.NUM_I801_DEVICE + 100,
                                        self.NUM_I801_DEVICE + 101,
                                        self.NUM_I801_DEVICE + 102,
                                        self.NUM_I801_DEVICE + 103,
                                        self.NUM_I801_DEVICE + 104
                                        )

            # Sysfs path
            self.PATH_I2C_BUS_ROOT = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.I2C_BUS_MUX_ROOT)
            self.PATH_MUX_9548_ROOT_GB_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_ROOT_GB[0])
            self.PATH_MUX_9548_ROOT_GB_CHAN6 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_ROOT_GB[6])
            self.PATH_MUX_9548_ROOT_GB_CHAN7 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_ROOT_GB[7])
            self.PATH_MUX_9548_ROOT_QSFP_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_ROOT_QSFP[0])
            self.PATH_MUX_9548_ROOT_QSFP_CHAN1 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_ROOT_QSFP[1])
            self.PATH_MUX_9548_ROOT_QSFP_CHAN2 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_ROOT_QSFP[2])
            self.PATH_MUX_9548_ROOT_QSFP_CHAN3 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_ROOT_QSFP[3])
            self.PATH_MUX_9548_ROOT_QSFP_CHAN4 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_ROOT_QSFP[4])
            self.PATH_MUX_9548_ROOT_QSFP_CHAN6 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_ROOT_QSFP[6])
            self.PATH_MUX_9548_ROOT_QSFP_CHAN7 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_ROOT_QSFP[7])
            self.PATH_MUX_9548_ROOT_SFP_CPLD_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_ROOT_SFP_CPLD[0])
            self.PATH_MUX_9548_CHILD_GB0_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_CHILD_GB0[0])
            self.PATH_MUX_9548_CHILD_GB1_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_CHILD_GB1[0])
            self.PATH_MUX_9548_CHILD_QSFP0_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_CHILD_QSFP0[0])
            self.PATH_MUX_9548_CHILD_QSFP1_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_CHILD_QSFP1[1])
            self.PATH_MUX_9548_CHILD_QSFP2_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_CHILD_QSFP2[2])
            self.PATH_MUX_9548_CHILD_QSFP3_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_CHILD_QSFP3[3])
            self.PATH_MUX_9548_CHILD_QSFP4_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_CHILD_QSFP4[4])
            self.PATH_MUX_9548_CHILD_QSFPDD0_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_CHILD_QSFPDD0[0])
            self.PATH_MUX_9548_CHILD_QSFPDDBOARD_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_CHILD_QSFPDDBOARD[0])
            self.PATH_MUX_9548_CHILD_QSFPDD1_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_CHILD_QSFPDD1[0])

            self.MUXs = {
                "9548_ROOT_GB": PCA9548("ROOT_GB", self.I2C_ADDR_9548_ROOT_GB, self.I2C_BUS_MUX_ROOT, self.NUM_MUX_9548_ROOT_GB),
                "9548_ROOT_QSFP": PCA9548("ROOT_QSFP", self.I2C_ADDR_9548_ROOT_QSFP, self.I2C_BUS_MUX_ROOT, self.NUM_MUX_9548_ROOT_QSFP),
                "9548_ROOT_SFP_CPLD": PCA9548("ROOT_SFP_CPLD", self.I2C_ADDR_9548_ROOT_SFP_CPLD, self.I2C_BUS_MUX_ROOT, self.NUM_MUX_9548_ROOT_SFP_CPLD),
                "9548_CHILD_GB0": PCA9548("CHILD_GB0", self.I2C_ADDR_9548_CHILD_GB, self.NUM_MUX_9548_ROOT_GB[6], self.NUM_MUX_9548_CHILD_GB0),
                "9548_CHILD_GB1": PCA9548("CHILD_GB1", self.I2C_ADDR_9548_CHILD_GB, self.NUM_MUX_9548_ROOT_GB[7], self.NUM_MUX_9548_CHILD_GB1),
                "9548_CHILD_QSFP0": PCA9548("CHILD_QSFP0", self.I2C_ADDR_9548_CHILD_QSFP, self.NUM_MUX_9548_ROOT_QSFP[0], self.NUM_MUX_9548_CHILD_QSFP0),
                "9548_CHILD_QSFP1": PCA9548("CHILD_QSFP1", self.I2C_ADDR_9548_CHILD_QSFP, self.NUM_MUX_9548_ROOT_QSFP[1], self.NUM_MUX_9548_CHILD_QSFP1),
                "9548_CHILD_QSFP2": PCA9548("CHILD_QSFP2", self.I2C_ADDR_9548_CHILD_QSFP, self.NUM_MUX_9548_ROOT_QSFP[2], self.NUM_MUX_9548_CHILD_QSFP2),
                "9548_CHILD_QSFP3": PCA9548("CHILD_QSFP3", self.I2C_ADDR_9548_CHILD_QSFP, self.NUM_MUX_9548_ROOT_QSFP[3], self.NUM_MUX_9548_CHILD_QSFP3),
                "9548_CHILD_QSFP4": PCA9548("CHILD_QSFP4", self.I2C_ADDR_9548_CHILD_QSFP, self.NUM_MUX_9548_ROOT_QSFP[4], self.NUM_MUX_9548_CHILD_QSFP4),
                "9548_CHILD_QSFPDD0": PCA9548("CHILD_QSFPDD0", self.I2C_ADDR_9548_CHILD_QSFPDD, self.NUM_MUX_9548_ROOT_QSFP[6], self.NUM_MUX_9548_CHILD_QSFPDD0),
                "9548_CHILD_QSFPDDBOARD": PCA9548("CHILD_QSFPDDBOARD", self.I2C_ADDR_9548_CHILD_QSFPDDBOARD, self.NUM_MUX_9548_CHILD_QSFPDD0[0], self.NUM_MUX_9548_CHILD_QSFPDDBOARD),
                "9548_CHILD_QSFPDD1": PCA9548("CHILD_QSFPDD1", self.I2C_ADDR_9548_CHILD_QSFPDD, self.NUM_MUX_9548_ROOT_QSFP[7], self.NUM_MUX_9548_CHILD_QSFPDD1)
            }
        elif (board_id & BID.BUILD_REV_MASK) >= BID.NCP1_1_ALPHA:
            # MUX PCA9548 ROOT Gearbox
            self.NUM_MUX_9548_ROOT_GB = (
                                        self.NUM_I801_DEVICE + 1,
                                        self.NUM_I801_DEVICE + 2,
                                        self.NUM_I801_DEVICE + 3,
                                        self.NUM_I801_DEVICE + 4,
                                        self.NUM_I801_DEVICE + 5,
                                        self.NUM_I801_DEVICE + 6,
                                        self.NUM_I801_DEVICE + 7,
                                        self.NUM_I801_DEVICE + 8)
            # MUX PCA9548 ROOT QSFP, QSFPDD
            self.NUM_MUX_9548_ROOT_QSFP = (
                                        self.NUM_I801_DEVICE + 9,
                                        self.NUM_I801_DEVICE + 10,
                                        self.NUM_I801_DEVICE + 11,
                                        self.NUM_I801_DEVICE + 12,
                                        self.NUM_I801_DEVICE + 13,
                                        self.NUM_I801_DEVICE + 14,
                                        self.NUM_I801_DEVICE + 15,
                                        self.NUM_I801_DEVICE + 16)
            # MUX PCA9548#2 SFP, CPLD, etc.
            self.NUM_MUX_9548_ROOT_SFP_CPLD = (
                                        self.NUM_I801_DEVICE + 17,
                                        self.NUM_I801_DEVICE + 18,
                                        self.NUM_I801_DEVICE + 19,
                                        self.NUM_I801_DEVICE + 20,
                                        self.NUM_I801_DEVICE + 21,
                                        self.NUM_I801_DEVICE + 22,
                                        self.NUM_I801_DEVICE + 23,
                                        self.NUM_I801_DEVICE + 24)
            # MUX PCA9548 QSFP 0-7
            self.NUM_MUX_9548_CHILD_QSFP0 = (
                                        self.NUM_I801_DEVICE + 25,
                                        self.NUM_I801_DEVICE + 26,
                                        self.NUM_I801_DEVICE + 27,
                                        self.NUM_I801_DEVICE + 28,
                                        self.NUM_I801_DEVICE + 29,
                                        self.NUM_I801_DEVICE + 30,
                                        self.NUM_I801_DEVICE + 31,
                                        self.NUM_I801_DEVICE + 32
                                        )
            # MUX PCA9548 QSFP 8-15
            self.NUM_MUX_9548_CHILD_QSFP1 = (
                                        self.NUM_I801_DEVICE + 33,
                                        self.NUM_I801_DEVICE + 34,
                                        self.NUM_I801_DEVICE + 35,
                                        self.NUM_I801_DEVICE + 36,
                                        self.NUM_I801_DEVICE + 37,
                                        self.NUM_I801_DEVICE + 38,
                                        self.NUM_I801_DEVICE + 39,
                                        self.NUM_I801_DEVICE + 40
                                        )
            # MUX PCA9548 QSFP 16-23
            self.NUM_MUX_9548_CHILD_QSFP2 = (
                                        self.NUM_I801_DEVICE + 41,
                                        self.NUM_I801_DEVICE + 42,
                                        self.NUM_I801_DEVICE + 43,
                                        self.NUM_I801_DEVICE + 44,
                                        self.NUM_I801_DEVICE + 45,
                                        self.NUM_I801_DEVICE + 46,
                                        self.NUM_I801_DEVICE + 47,
                                        self.NUM_I801_DEVICE + 48
                                        )
            # MUX PCA9548 QSFP 24-31
            self.NUM_MUX_9548_CHILD_QSFP3 = (
                                        self.NUM_I801_DEVICE + 49,
                                        self.NUM_I801_DEVICE + 50,
                                        self.NUM_I801_DEVICE + 51,
                                        self.NUM_I801_DEVICE + 52,
                                        self.NUM_I801_DEVICE + 53,
                                        self.NUM_I801_DEVICE + 54,
                                        self.NUM_I801_DEVICE + 55,
                                        self.NUM_I801_DEVICE + 56
                                        )
            # MUX PCA9548 QSFP 32-39
            self.NUM_MUX_9548_CHILD_QSFP4 = (
                                        self.NUM_I801_DEVICE + 57,
                                        self.NUM_I801_DEVICE + 58,
                                        self.NUM_I801_DEVICE + 59,
                                        self.NUM_I801_DEVICE + 60,
                                        self.NUM_I801_DEVICE + 61,
                                        self.NUM_I801_DEVICE + 62,
                                        self.NUM_I801_DEVICE + 63,
                                        self.NUM_I801_DEVICE + 64
                                        )
            # MUX PCA9548 QSFPDD 0-7
            self.NUM_MUX_9548_CHILD_QSFPDD0 = (
                                        self.NUM_I801_DEVICE + 65, # Port 0
                                        self.NUM_I801_DEVICE + 66, # Port 1
                                        self.NUM_I801_DEVICE + 67, # Port 2
                                        self.NUM_I801_DEVICE + 68, # Port 3
                                        self.NUM_I801_DEVICE + 69, # Port 4
                                        self.NUM_I801_DEVICE + 70, # Port 5
                                        self.NUM_I801_DEVICE + 71, # Port 6
                                        self.NUM_I801_DEVICE + 72  # Port 7
                                        )
            # MUX PCA9548 QSFPDD 8-12
            self.NUM_MUX_9548_CHILD_QSFPDD1 = (
                                        self.NUM_I801_DEVICE + 73,
                                        self.NUM_I801_DEVICE + 74,
                                        self.NUM_I801_DEVICE + 75,
                                        self.NUM_I801_DEVICE + 76,
                                        self.NUM_I801_DEVICE + 77,
                                        self.NUM_I801_DEVICE + 78,
                                        self.NUM_I801_DEVICE + 79,
                                        self.NUM_I801_DEVICE + 80
                                        )

            # Sysfs path
            self.PATH_I2C_BUS_ROOT = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.I2C_BUS_MUX_ROOT)
            self.PATH_MUX_9548_ROOT_GB_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_ROOT_GB[0])
            self.PATH_MUX_9548_ROOT_GB_CHAN6 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_ROOT_GB[6])
            self.PATH_MUX_9548_ROOT_GB_CHAN7 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_ROOT_GB[7])
            self.PATH_MUX_9548_ROOT_QSFP_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_ROOT_QSFP[0])
            self.PATH_MUX_9548_ROOT_QSFP_CHAN1 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_ROOT_QSFP[1])
            self.PATH_MUX_9548_ROOT_QSFP_CHAN2 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_ROOT_QSFP[2])
            self.PATH_MUX_9548_ROOT_QSFP_CHAN3 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_ROOT_QSFP[3])
            self.PATH_MUX_9548_ROOT_QSFP_CHAN4 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_ROOT_QSFP[4])
            self.PATH_MUX_9548_ROOT_QSFP_CHAN6 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_ROOT_QSFP[6])
            self.PATH_MUX_9548_ROOT_QSFP_CHAN7 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_ROOT_QSFP[7])
            self.PATH_MUX_9548_ROOT_SFP_CPLD_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_ROOT_SFP_CPLD[0])
            self.PATH_MUX_9548_CHILD_QSFP0_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_CHILD_QSFP0[0])
            self.PATH_MUX_9548_CHILD_QSFP1_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_CHILD_QSFP1[1])
            self.PATH_MUX_9548_CHILD_QSFP2_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_CHILD_QSFP2[2])
            self.PATH_MUX_9548_CHILD_QSFP3_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_CHILD_QSFP3[3])
            self.PATH_MUX_9548_CHILD_QSFP4_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_CHILD_QSFP4[4])
            self.PATH_MUX_9548_CHILD_QSFPDD0_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_CHILD_QSFPDD0[0])
            self.PATH_MUX_9548_CHILD_QSFPDD1_CHAN0 = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.NUM_MUX_9548_CHILD_QSFPDD1[0])

            self.MUXs = {
                "9548_ROOT_GB": PCA9548("ROOT_GB", self.I2C_ADDR_9548_ROOT_GB, self.I2C_BUS_MUX_ROOT, self.NUM_MUX_9548_ROOT_GB),
                "9548_ROOT_QSFP": PCA9548("ROOT_QSFP", self.I2C_ADDR_9548_ROOT_QSFP, self.I2C_BUS_MUX_ROOT, self.NUM_MUX_9548_ROOT_QSFP),
                "9548_ROOT_SFP_CPLD": PCA9548("ROOT_SFP_CPLD", self.I2C_ADDR_9548_ROOT_SFP_CPLD, self.I2C_BUS_MUX_ROOT, self.NUM_MUX_9548_ROOT_SFP_CPLD),
                "9548_CHILD_QSFP0": PCA9548("CHILD_QSFP0", self.I2C_ADDR_9548_CHILD_QSFP, self.NUM_MUX_9548_ROOT_QSFP[0], self.NUM_MUX_9548_CHILD_QSFP0),
                "9548_CHILD_QSFP1": PCA9548("CHILD_QSFP1", self.I2C_ADDR_9548_CHILD_QSFP, self.NUM_MUX_9548_ROOT_QSFP[1], self.NUM_MUX_9548_CHILD_QSFP1),
                "9548_CHILD_QSFP2": PCA9548("CHILD_QSFP2", self.I2C_ADDR_9548_CHILD_QSFP, self.NUM_MUX_9548_ROOT_QSFP[2], self.NUM_MUX_9548_CHILD_QSFP2),
                "9548_CHILD_QSFP3": PCA9548("CHILD_QSFP3", self.I2C_ADDR_9548_CHILD_QSFP, self.NUM_MUX_9548_ROOT_QSFP[3], self.NUM_MUX_9548_CHILD_QSFP3),
                "9548_CHILD_QSFP4": PCA9548("CHILD_QSFP4", self.I2C_ADDR_9548_CHILD_QSFP, self.NUM_MUX_9548_ROOT_QSFP[4], self.NUM_MUX_9548_CHILD_QSFP4),
                "9548_CHILD_QSFPDD0": PCA9548("CHILD_QSFPDD0", self.I2C_ADDR_9548_CHILD_QSFPDD, self.NUM_MUX_9548_ROOT_QSFP[6], self.NUM_MUX_9548_CHILD_QSFPDD0),
                "9548_CHILD_QSFPDD1": PCA9548("CHILD_QSFPDD1", self.I2C_ADDR_9548_CHILD_QSFPDD, self.NUM_MUX_9548_ROOT_QSFP[7], self.NUM_MUX_9548_CHILD_QSFPDD1)
            }
        else:
            self.logger.error("Invalid Board ID:" + str(board_id))
            sys.exit("Invalid Board ID:" + str(board_id))

    def _create_sysfs(self, path_ch0, path_parent, i2c_mux):
        try:
            if os.path.exists(path_ch0):
                self.logger.info(i2c_mux.NAME + " is already exist")
            else:
                with open(path_parent + "/new_device", 'w') as f:
                    self.logger.info(i2c_mux.NAME + " " + hex(i2c_mux.address))
                    f.write(i2c_mux.NAME + " " + hex(i2c_mux.address))
                self.logger.info("Register " + i2c_mux.name + " in sysfs")
        except Exception as e:
            self.logger.error("Register MUX " + i2c_mux.name + " to sysfs fail, error: ", str(e))
            raise

    def init(self):
        # MUX 9548 ROOT_GB
        try:
            self._create_sysfs(self.PATH_MUX_9548_ROOT_GB_CHAN0,
                               self.PATH_I2C_BUS_ROOT,
                               self.MUXs["9548_ROOT_GB"])
            #sleep(0.5)
        except Exception as e:
            self.logger.error("Create MUX PCA9548 ROOT_GB fail, error: ", str(e))
            raise

        # MUX 9548 ROOT_QSFP
        try:
            self._create_sysfs(self.PATH_MUX_9548_ROOT_QSFP_CHAN0,
                               self.PATH_I2C_BUS_ROOT,
                               self.MUXs["9548_ROOT_QSFP"])
            #sleep(0.1)
        except Exception as e:
            self.logger.error("Create MUX PCA9548 ROOT_QSFP fail, error: ", str(e))
            raise

        # MUX 9548 ROOT_SFP_CPLD
        try:
            self._create_sysfs(self.PATH_MUX_9548_ROOT_SFP_CPLD_CHAN0,
                               self.PATH_I2C_BUS_ROOT,
                               self.MUXs["9548_ROOT_SFP_CPLD"])
            #sleep(0.1)
        except Exception as e:
            self.logger.error("Create MUX PCA9548 ROOT_SFP_CPLD fail, error: ", str(e))
            raise

        if self.board_id == BID.NCP1_1_PROTO:
            # MUX 9548 GB0
            try:
                self._create_sysfs(self.PATH_MUX_9548_CHILD_GB0_CHAN0,
                                   self.PATH_MUX_9548_ROOT_GB_CHAN6,
                                   self.MUXs["9548_CHILD_GB0"])
                #sleep(0.1)
            except Exception as e:
                self.logger.error("Create MUX 9548 CHILD_GB0 fail, error: ", str(e))
                raise

            # MUX 9548 GB1
            try:
                self._create_sysfs(self.PATH_MUX_9548_CHILD_GB1_CHAN0,
                                   self.PATH_MUX_9548_ROOT_GB_CHAN7,
                                   self.MUXs["9548_CHILD_GB1"])
                #sleep(0.1)
            except Exception as e:
                self.logger.error("Create MUX 9548 CHILD_GB1 fail, error: ", str(e))
                raise

        # MUX 9548 QSFP0
        try:
            self._create_sysfs(self.PATH_MUX_9548_CHILD_QSFP0_CHAN0,
                               self.PATH_MUX_9548_ROOT_QSFP_CHAN0,
                               self.MUXs["9548_CHILD_QSFP0"])
            #sleep(0.1)
        except Exception as e:
            self.logger.error("Create MUX 9548 CHILD_QSFP0 fail, error: ", str(e))
            raise

        # MUX 9548 QSFP1
        try:
            self._create_sysfs(self.PATH_MUX_9548_CHILD_QSFP1_CHAN0,
                               self.PATH_MUX_9548_ROOT_QSFP_CHAN1,
                               self.MUXs["9548_CHILD_QSFP1"])
        except Exception as e:
            self.logger.error("Create MUX 9548 CHILD_QSFP1 fail, error: ", str(e))
            raise

        # MUX 9548 QSFP2
        try:
            self._create_sysfs(self.PATH_MUX_9548_CHILD_QSFP2_CHAN0,
                               self.PATH_MUX_9548_ROOT_QSFP_CHAN2,
                               self.MUXs["9548_CHILD_QSFP2"])
        except Exception as e:
            self.logger.error("Create MUX 9548 CHILD_QSFP2 fail, error: ", str(e))
            raise

        # MUX 9548 QSFP3
        try:
            self._create_sysfs(self.PATH_MUX_9548_CHILD_QSFP3_CHAN0,
                               self.PATH_MUX_9548_ROOT_QSFP_CHAN3,
                               self.MUXs["9548_CHILD_QSFP3"])
        except Exception as e:
            self.logger.error("Create MUX 9548 CHILD_QSFP3 fail, error: ", str(e))
            raise

        # MUX 9548 QSFP4
        try:
            self._create_sysfs(self.PATH_MUX_9548_CHILD_QSFP4_CHAN0,
                               self.PATH_MUX_9548_ROOT_QSFP_CHAN4,
                               self.MUXs["9548_CHILD_QSFP4"])
        except Exception as e:
            self.logger.error("Create MUX 9548 CHILD_QSFP4 fail, error: ", str(e))
            raise

        # MUX 9548 QSFPDD0
        try:
            self._create_sysfs(self.PATH_MUX_9548_CHILD_QSFPDD0_CHAN0,
                               self.PATH_MUX_9548_ROOT_QSFP_CHAN6,
                               self.MUXs["9548_CHILD_QSFPDD0"])
        except Exception as e:
            self.logger.error("Create MUX 9548 CHILD_QSFPDD0 fail, error: ", str(e))
            raise

        if self.board_id == BID.NCP1_1_PROTO:
            # MUX 9548 QSFPDDBOARD
            try:
                self._create_sysfs(self.PATH_MUX_9548_CHILD_QSFPDDBOARD_CHAN0,
                                   self.PATH_MUX_9548_CHILD_QSFPDD0_CHAN0,
                                   self.MUXs["9548_CHILD_QSFPDDBOARD"])
            except Exception as e:
                self.logger.error("Create MUX 9548 CHILD_QSFPDDBOARD fail, error: ", str(e))
                raise

        # MUX 9548 QSFPDD1
        try:
            self._create_sysfs(self.PATH_MUX_9548_CHILD_QSFPDD1_CHAN0,
                               self.PATH_MUX_9548_ROOT_QSFP_CHAN7,
                               self.MUXs["9548_CHILD_QSFPDD1"])
        except Exception as e:
            self.logger.error("Create MUX 9548 CHILD_QSFPDD1 fail, error: ", str(e))
            raise


    def deinit(self):
        pass
