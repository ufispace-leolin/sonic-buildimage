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
import subprocess

from bsp.common.logger import Logger
from bsp.i2c_mux.i2c_mux import I2CMux
from bsp.const.const import BID

class PCA953x:

    def __init__(self, dev_info, bus_num):
        self.name = dev_info["name"]
        self.address = dev_info["address"]
        self.bus_num = bus_num
        self.pins = dev_info["pins"]
        self.init_cfg = dev_info["init_cfg"]

class PCA9555(PCA953x):

    NAME = "pca9555"

class PCA9535(PCA953x):

    NAME = "pca9535"

class PCA9539(PCA953x):

    NAME = "pca9539"

class IOExpander:

    GPIO_BASE = 511
    APOLLO_PROTO_IOExpanders_Order_List = ['9539_HOST_GPIO_I2C', '9539_SYS_LED', '9555_BOARD_ID', '9539_VOL_MARGIN', '9539_CPU_I2C']
    APOLLO_ALPHA_IOExpanders_Order_List = ['9539_HOST_GPIO_I2C', '9539_SYS_LED', '9555_BOARD_ID', '9539_VOL_MARGIN', '9539_CPU_I2C', '9555_BEACON_LED']
    APOLLO_BETA_IOExpanders_Order_List = ['9539_HOST_GPIO_I2C', '9555_BEACON_LED', '9555_BOARD_ID', '9539_VOL_MARGIN', '9539_CPU_I2C']
    APOLLO_IOExpanders = {
        "9539_HOST_GPIO_I2C": {
            "name": "pca9539_HOST_GPIO_I2C", "address": 0x74, "parent": None, "channel": None, "pins": 16,
            "init_cfg": [
                {"gpio": GPIO_BASE, "direction": "out", "value": 1},    # gpio511 IO_1.7 I210_RST_L
                {"gpio": GPIO_BASE-1, "direction": "out", "value": 1},  # gpio510 IO_1.6 I210_PE_RST_L
                {"gpio": GPIO_BASE-2, "direction": "in"},                # gpio509 IO_1.5 OP2_INT_L
                {"gpio": GPIO_BASE-3, "direction": "in"},                # gpio508 IO_1.4 CPLD01_TO_CPU_INT_L
                {"gpio": GPIO_BASE-4, "direction": "in"},                # gpio507 IO_1.3 CPLD2_TO_CPU_INT_L
                {"gpio": GPIO_BASE-5, "direction": "in"},                # gpio506 IO_1.2 CPLD3_TO_CPU_INT_L
                {"gpio": GPIO_BASE-6, "direction": "in"},                # gpio505 IO_1.1 CPLD4_TO_CPU_INT_L
                {"gpio": GPIO_BASE-7, "direction": "in"},                # gpio504 IO_1.0 TH_INT_L
                {"gpio": GPIO_BASE-8, "direction": "in"},                # gpio503 IO_0.7 8V19N474_INT
                {"gpio": GPIO_BASE-9, "direction": "in"},                # gpio502 IO_0.6 TP112012
                {"gpio": GPIO_BASE-10, "direction": "out", "value": 0}, # gpio501 IO_0.5 UART_MUX_SEL
                {"gpio": GPIO_BASE-11, "direction": "out", "value": 0}, # gpio500 IO_0.4 USB_MUX_SEL
                {"gpio": GPIO_BASE-12, "direction": "out", "value": 0}, # gpio499 IO_0.3 HOST_TO_BMC_I2C_GPIO
                {"gpio": GPIO_BASE-13, "direction": "out", "value": 1}, # gpio498 IO_0.2 LED_CLR
                {"gpio": GPIO_BASE-14, "direction": "in"},              # gpio497 IO_0.1 J2_PCIE_RST_L
                {"gpio": GPIO_BASE-15, "direction": "out", "value": 1}  # gpio496 IO_0.0 9539_TH_RST_L
            ],
            "config_0": 0xc0, "config_1": 0x3f, "polarity_inv_0": 0x0, "polarity_inv_1": 0x0, "output_port_0": 0x03, "output_port_1": 0xc0
        },
        "9539_SYS_LED": {
            "name": "pca9539_SYS_LED", "address": 0x76, "parent": "9548_ROOT_GB", "channel": 1, "pins": 16,
            "init_cfg": [
                {"gpio": GPIO_BASE-16, "direction": "in"},   # gpio495 IO_1.7 NONE
                {"gpio": GPIO_BASE-17, "direction": "in"},   # gpio494 IO_1.6 NONE
                {"gpio": GPIO_BASE-18, "direction": "in"},   # gpio493 IO_1.5 NONE
                {"gpio": GPIO_BASE-19, "direction": "in"},   # gpio492 IO_1.4 NONE
                {"gpio": GPIO_BASE-20, "direction": "in"},   # gpio491 IO_1.3 NONE
                {"gpio": GPIO_BASE-21, "direction": "in"},   # gpio490 IO_1.2 NONE
                {"gpio": GPIO_BASE-22, "direction": "in"},   # gpio489 IO_1.1 PSU0_LED_PWR
                {"gpio": GPIO_BASE-23, "direction": "in"},   # gpio488 IO_1.0 PSU1_LED_PWR
                {"gpio": GPIO_BASE-24, "direction": "in"},   # gpio487 IO_0.7 SFP+_P16_TX_DIS
                {"gpio": GPIO_BASE-25, "direction": "in"},   # gpio486 IO_0.6 SFP+_P17_TX_DIS
                {"gpio": GPIO_BASE-26, "direction": "in"},   # gpio485 IO_0.5 NONE
                {"gpio": GPIO_BASE-27, "direction": "in"},   # gpio484 IO_0.4 PSU0_LED_Y
                {"gpio": GPIO_BASE-28, "direction": "in"},   # gpio483 IO_0.3 PSU1_LED_Y
                {"gpio": GPIO_BASE-29, "direction": "in"},   # gpio482 IO_0.2 FAN_LED_Y
                {"gpio": GPIO_BASE-30, "direction": "in"},   # gpio481 IO_0.1 FAN_LED_EN
                {"gpio": GPIO_BASE-31, "direction": "in"}    # gpio480 IO_0.0 SYS_LED_G
            ],
            "config_0": 0xe0, "config_1": 0xfc, "polarity_inv_0": 0x0, "polarity_inv_1": 0x0, "output_port_0": 0x0, "output_port_1": 0x0
        },
        "9555_BOARD_ID": {
            "name": "pca9555_BOARD_ID", "address": 0x20, "parent": "9548_ROOT_GB", "channel": 2, "pins": 16,
            "init_cfg": [
                {"gpio": GPIO_BASE-32, "direction": "in"},   # gpio479 IO_1.7 Board_ID_3
                {"gpio": GPIO_BASE-33, "direction": "in"},   # gpio478 IO_1.6 Board_ID_2
                {"gpio": GPIO_BASE-34, "direction": "in"},   # gpio477 IO_1.5 Board_ID_1
                {"gpio": GPIO_BASE-35, "direction": "in"},   # gpio476 IO_1.4 Board_ID_0
                {"gpio": GPIO_BASE-36, "direction": "in"},   # gpio475 IO_1.3 HW_REV_1
                {"gpio": GPIO_BASE-37, "direction": "in"},   # gpio474 IO_1.2 HW_REV_0
                {"gpio": GPIO_BASE-38, "direction": "in"},   # gpio473 IO_1.1 Build_REV_1
                {"gpio": GPIO_BASE-39, "direction": "in"},   # gpio472 IO_1.0 Build_REV_0
                {"gpio": GPIO_BASE-40, "direction": "in"},   # gpio471 IO_0.7 NONE
                {"gpio": GPIO_BASE-41, "direction": "in"},   # gpio470 IO_0.6 NONE
                {"gpio": GPIO_BASE-42, "direction": "in"},   # gpio469 IO_0.5 NONE
                {"gpio": GPIO_BASE-43, "direction": "in"},   # gpio468 IO_0.4 NONE
                {"gpio": GPIO_BASE-44, "direction": "in"},   # gpio467 IO_0.3 NONE
                {"gpio": GPIO_BASE-45, "direction": "in"},   # gpio466 IO_0.2 NONE
                {"gpio": GPIO_BASE-46, "direction": "in"},   # gpio465 IO_0.1 NONE
                {"gpio": GPIO_BASE-47, "direction": "in"}    # gpio464 IO_0.0 NONE
            ],
            "config_0": 0xff, "config_1": 0xff, "polarity_inv_0": 0x0, "polarity_inv_1": 0x0, "output_port_0": 0x0, "output_port_1": 0x0
        },
        "9539_VOL_MARGIN": {
            "name": "pca9539_VOL_MARGIN", "address": 0x76, "parent": "9548_ROOT_GB", "channel": 5, "pins": 16,
            "init_cfg": [
                {"gpio": GPIO_BASE-48, "direction": "in"},   # gpio463 IO_1.7 P1V2_3_Low_Margin
                {"gpio": GPIO_BASE-49, "direction": "in"},   # gpio462 IO_1.6 P1V2_3_High_Margin
                {"gpio": GPIO_BASE-50, "direction": "in"},   # gpio461 IO_1.5 P0V9_Low_Margin
                {"gpio": GPIO_BASE-51, "direction": "in"},   # gpio460 IO_1.4 P0V9_High_Margin
                {"gpio": GPIO_BASE-52, "direction": "in"},   # gpio459 IO_1.3 P0V88_Low_Margin
                {"gpio": GPIO_BASE-53, "direction": "in"},   # gpio458 IO_1.2 P0V88_High_Margin
                {"gpio": GPIO_BASE-54, "direction": "in"},   # gpio457 IO_1.1 NI
                {"gpio": GPIO_BASE-55, "direction": "in"},   # gpio456 IO_1.0 NI
                {"gpio": GPIO_BASE-56, "direction": "in"},   # gpio455 IO_0.7 P2V5_Low_Margin
                {"gpio": GPIO_BASE-57, "direction": "in"},   # gpio454 IO_0.6 P2V5_High_Margin
                {"gpio": GPIO_BASE-58, "direction": "in"},   # gpio453 IO_0.5 P1V8_Low_Margin
                {"gpio": GPIO_BASE-59, "direction": "in"},   # gpio452 IO_0.4 P1V8_High_Margin
                {"gpio": GPIO_BASE-60, "direction": "in"},   # gpio451 IO_0.3 P1V2_1_Low_Margin
                {"gpio": GPIO_BASE-61, "direction": "in"},   # gpio450 IO_0.2 P1V2_1_High_Margin
                {"gpio": GPIO_BASE-62, "direction": "in"},   # gpio449 IO_0.1 P1V2_2_Low_Margin
                {"gpio": GPIO_BASE-63, "direction": "in"}    # gpio448 IO_0.0 P1V2_2_High_Margin
            ],
            "config_0": 0x0, "config_1": 0x03, "polarity_inv_0": 0x0, "polarity_inv_1": 0x0, "output_port_0": 0x0, "output_port_1": 0x0
        },
        "9539_CPU_I2C": {
            "name": "pca9539_CPU_I2C", "address": 0x77, "parent": None, "channel": None, "pins": 16,
            "init_cfg": [
                {"gpio": GPIO_BASE-64, "direction": "in"},   # gpio447 IO_1.7
                {"gpio": GPIO_BASE-65, "direction": "in"},   # gpio446 IO_1.6
                {"gpio": GPIO_BASE-66, "direction": "in"},   # gpio445 IO_1.5
                {"gpio": GPIO_BASE-67, "direction": "in"},   # gpio444 IO_1.4
                {"gpio": GPIO_BASE-68, "direction": "in"},   # gpio443 IO_1.3
                {"gpio": GPIO_BASE-69, "direction": "in"},   # gpio442 IO_1.2
                {"gpio": GPIO_BASE-70, "direction": "in"},   # gpio441 IO_1.1
                {"gpio": GPIO_BASE-71, "direction": "in"},   # gpio440 IO_1.0
                {"gpio": GPIO_BASE-72, "direction": "in"},   # gpio439 IO_0.7
                {"gpio": GPIO_BASE-73, "direction": "in"},   # gpio438 IO_0.6
                {"gpio": GPIO_BASE-74, "direction": "in"},   # gpio437 IO_0.5
                {"gpio": GPIO_BASE-75, "direction": "in"},   # gpio436 IO_0.4
                {"gpio": GPIO_BASE-76, "direction": "in"},   # gpio435 IO_0.3
                {"gpio": GPIO_BASE-77, "direction": "in"},   # gpio434 IO_0.2
                {"gpio": GPIO_BASE-78, "direction": "in"},   # gpio433 IO_0.1
                {"gpio": GPIO_BASE-79, "direction": "in"}    # gpio432 IO_0.0
            ],
            "config_0": 0xff, "config_1": 0xff, "polarity_inv_0": 0x0, "polarity_inv_1": 0x0, "output_port_0": 0x0, "output_port_1": 0x0
        },
        "9555_BEACON_LED": {
            "name": "pca9555_BEACON_LED", "address": 0x20, "parent": "9548_ROOT_GB", "channel": 6, "pins": 16,
            "init_cfg": [
                {"gpio": GPIO_BASE-80, "direction": "in"},                # gpio431 IO_1.7 NONE
                {"gpio": GPIO_BASE-81, "direction": "out", "value": 1},   # gpio430 IO_1.6 7SEG_RG
                {"gpio": GPIO_BASE-82, "direction": "out", "value": 0},   # gpio429 IO_1.5 7SEG_RB
                {"gpio": GPIO_BASE-83, "direction": "out", "value": 0},   # gpio428 IO_1.4 7SEG_RD
                {"gpio": GPIO_BASE-84, "direction": "out", "value": 0},   # gpio427 IO_1.3 7SEG_RF
                {"gpio": GPIO_BASE-85, "direction": "out", "value": 0},   # gpio426 IO_1.2 7SEG_RC
                {"gpio": GPIO_BASE-86, "direction": "out", "value": 0},   # gpio425 IO_1.1 7SEG_RE
                {"gpio": GPIO_BASE-87, "direction": "out", "value": 0},   # gpio424 IO_1.0 7SEG_RA
                {"gpio": GPIO_BASE-88, "direction": "in"},                # gpio423 IO_0.7 NONE
                {"gpio": GPIO_BASE-89, "direction": "out", "value": 0},   # gpio422 IO_0.6 7SEG_LA
                {"gpio": GPIO_BASE-90, "direction": "out", "value": 0},   # gpio421 IO_0.5 7SEG_LF
                {"gpio": GPIO_BASE-91, "direction": "out", "value": 1},   # gpio420 IO_0.4 7SEG_LG
                {"gpio": GPIO_BASE-92, "direction": "out", "value": 0},   # gpio419 IO_0.3 7SEG_LD
                {"gpio": GPIO_BASE-93, "direction": "out", "value": 0},   # gpio418 IO_0.2 7SEG_LE
                {"gpio": GPIO_BASE-94, "direction": "out", "value": 0},   # gpio417 IO_0.1 7SEG_LB
                {"gpio": GPIO_BASE-95, "direction": "out", "value": 0}    # gpio416 IO_0.0 7SEG_LC
            ],
            "config_0": 0xff, "config_1": 0xff, "polarity_inv_0": 0x0, "polarity_inv_1": 0x0, "output_port_0": 0x0, "output_port_1": 0x0
        },
    }
    
    APOLLO_BETA_IOExpanders = {
        "9539_HOST_GPIO_I2C": {
            "name": "pca9539_HOST_GPIO_I2C", "address": 0x74, "parent": None, "channel": None, "pins": 16,
            "init_cfg": [
                {"gpio": GPIO_BASE, "direction": "out", "value": 1},    # gpio511 IO_1.7 I210_RST_L
                {"gpio": GPIO_BASE-1, "direction": "out", "value": 1},  # gpio510 IO_1.6 I210_PE_RST_L
                {"gpio": GPIO_BASE-2, "direction": "in"},                # gpio509 IO_1.5 OP2_INT_L
                {"gpio": GPIO_BASE-3, "direction": "in"},                # gpio508 IO_1.4 CPLD01_TO_CPU_INT_L
                {"gpio": GPIO_BASE-4, "direction": "in"},                # gpio507 IO_1.3 CPLD2_TO_CPU_INT_L
                {"gpio": GPIO_BASE-5, "direction": "in"},                # gpio506 IO_1.2 CPLD3_TO_CPU_INT_L
                {"gpio": GPIO_BASE-6, "direction": "in"},                # gpio505 IO_1.1 CPLD4_TO_CPU_INT_L
                {"gpio": GPIO_BASE-7, "direction": "in"},                # gpio504 IO_1.0 TH_INT_L
                {"gpio": GPIO_BASE-8, "direction": "in"},                # gpio503 IO_0.7 8V19N474_INT
                {"gpio": GPIO_BASE-9, "direction": "in"},                # gpio502 IO_0.6 TP112012
                {"gpio": GPIO_BASE-10, "direction": "in"},               # gpio501 IO_0.5 UART_MUX_SEL
                {"gpio": GPIO_BASE-11, "direction": "out", "value": 0}, # gpio500 IO_0.4 USB_MUX_SEL
                {"gpio": GPIO_BASE-12, "direction": "out", "value": 0}, # gpio499 IO_0.3 HOST_TO_BMC_I2C_GPIO
                {"gpio": GPIO_BASE-13, "direction": "out", "value": 1}, # gpio498 IO_0.2 LED_CLR
                {"gpio": GPIO_BASE-14, "direction": "in"},              # gpio497 IO_0.1 J2_PCIE_RST_L
                {"gpio": GPIO_BASE-15, "direction": "out", "value": 1}  # gpio496 IO_0.0 9539_TH_RST_L
            ],
            "config_0": 0xc0, "config_1": 0x3f, "polarity_inv_0": 0x0, "polarity_inv_1": 0x0, "output_port_0": 0x03, "output_port_1": 0xc0
        },
        "9555_BEACON_LED": {
            "name": "pca9555_BEACON_LED", "address": 0x20, "parent": "9548_ROOT_GB", "channel": 6, "pins": 16,
            "init_cfg": [
                {"gpio": GPIO_BASE-16, "direction": "in"},                # gpio495 IO_1.7 NONE
                {"gpio": GPIO_BASE-17, "direction": "out", "value": 1},   # gpio494 IO_1.6 7SEG_RG
                {"gpio": GPIO_BASE-18, "direction": "out", "value": 0},   # gpio493 IO_1.5 7SEG_RB
                {"gpio": GPIO_BASE-19, "direction": "out", "value": 0},   # gpio492 IO_1.4 7SEG_RD
                {"gpio": GPIO_BASE-20, "direction": "out", "value": 0},   # gpio491 IO_1.3 7SEG_RF
                {"gpio": GPIO_BASE-21, "direction": "out", "value": 0},   # gpio490 IO_1.2 7SEG_RC
                {"gpio": GPIO_BASE-22, "direction": "out", "value": 0},   # gpio489 IO_1.1 7SEG_RE
                {"gpio": GPIO_BASE-23, "direction": "out", "value": 0},   # gpio488 IO_1.0 7SEG_RA
                {"gpio": GPIO_BASE-24, "direction": "in"},                # gpio487 IO_0.7 NONE
                {"gpio": GPIO_BASE-25, "direction": "out", "value": 0},   # gpio486 IO_0.6 7SEG_LA
                {"gpio": GPIO_BASE-26, "direction": "out", "value": 0},   # gpio485 IO_0.5 7SEG_LF
                {"gpio": GPIO_BASE-27, "direction": "out", "value": 1},   # gpio484 IO_0.4 7SEG_LG
                {"gpio": GPIO_BASE-28, "direction": "out", "value": 0},   # gpio483 IO_0.3 7SEG_LD
                {"gpio": GPIO_BASE-29, "direction": "out", "value": 0},   # gpio482 IO_0.2 7SEG_LE
                {"gpio": GPIO_BASE-30, "direction": "out", "value": 0},   # gpio481 IO_0.1 7SEG_LB
                {"gpio": GPIO_BASE-31, "direction": "out", "value": 0}    # gpio480 IO_0.0 7SEG_LC
            ],
            "config_0": 0xff, "config_1": 0xff, "polarity_inv_0": 0x0, "polarity_inv_1": 0x0, "output_port_0": 0x0, "output_port_1": 0x0
        },
        "9555_BOARD_ID": {
            "name": "pca9555_BOARD_ID", "address": 0x20, "parent": "9548_ROOT_GB", "channel": 2, "pins": 16,
            "init_cfg": [
                {"gpio": GPIO_BASE-32, "direction": "in"},   # gpio479 IO_1.7 Board_ID_3
                {"gpio": GPIO_BASE-33, "direction": "in"},   # gpio478 IO_1.6 Board_ID_2
                {"gpio": GPIO_BASE-34, "direction": "in"},   # gpio477 IO_1.5 Board_ID_1
                {"gpio": GPIO_BASE-35, "direction": "in"},   # gpio476 IO_1.4 Board_ID_0
                {"gpio": GPIO_BASE-36, "direction": "in"},   # gpio475 IO_1.3 HW_REV_1
                {"gpio": GPIO_BASE-37, "direction": "in"},   # gpio474 IO_1.2 HW_REV_0
                {"gpio": GPIO_BASE-38, "direction": "in"},   # gpio473 IO_1.1 Build_REV_1
                {"gpio": GPIO_BASE-39, "direction": "in"},   # gpio472 IO_1.0 Build_REV_0
                {"gpio": GPIO_BASE-40, "direction": "in"},   # gpio471 IO_0.7 NONE
                {"gpio": GPIO_BASE-41, "direction": "in"},   # gpio470 IO_0.6 NONE
                {"gpio": GPIO_BASE-42, "direction": "in"},   # gpio469 IO_0.5 NONE
                {"gpio": GPIO_BASE-43, "direction": "in"},   # gpio468 IO_0.4 NONE
                {"gpio": GPIO_BASE-44, "direction": "in"},   # gpio467 IO_0.3 NONE
                {"gpio": GPIO_BASE-45, "direction": "in"},   # gpio466 IO_0.2 NONE
                {"gpio": GPIO_BASE-46, "direction": "in"},   # gpio465 IO_0.1 NONE
                {"gpio": GPIO_BASE-47, "direction": "in"}    # gpio464 IO_0.0 NONE
            ],
            "config_0": 0xff, "config_1": 0xff, "polarity_inv_0": 0x0, "polarity_inv_1": 0x0, "output_port_0": 0x0, "output_port_1": 0x0
        },
        "9539_VOL_MARGIN": {
            "name": "pca9539_VOL_MARGIN", "address": 0x76, "parent": "9548_ROOT_GB", "channel": 5, "pins": 16,
            "init_cfg": [
                {"gpio": GPIO_BASE-48, "direction": "in"},   # gpio463 IO_1.7 P1V2_3_Low_Margin
                {"gpio": GPIO_BASE-49, "direction": "in"},   # gpio462 IO_1.6 P1V2_3_High_Margin
                {"gpio": GPIO_BASE-50, "direction": "in"},   # gpio461 IO_1.5 P0V9_Low_Margin
                {"gpio": GPIO_BASE-51, "direction": "in"},   # gpio460 IO_1.4 P0V9_High_Margin
                {"gpio": GPIO_BASE-52, "direction": "in"},   # gpio459 IO_1.3 P0V88_Low_Margin
                {"gpio": GPIO_BASE-53, "direction": "in"},   # gpio458 IO_1.2 P0V88_High_Margin
                {"gpio": GPIO_BASE-54, "direction": "in"},   # gpio457 IO_1.1 NI
                {"gpio": GPIO_BASE-55, "direction": "in"},   # gpio456 IO_1.0 NI
                {"gpio": GPIO_BASE-56, "direction": "in"},   # gpio455 IO_0.7 P2V5_Low_Margin
                {"gpio": GPIO_BASE-57, "direction": "in"},   # gpio454 IO_0.6 P2V5_High_Margin
                {"gpio": GPIO_BASE-58, "direction": "in"},   # gpio453 IO_0.5 P1V8_Low_Margin
                {"gpio": GPIO_BASE-59, "direction": "in"},   # gpio452 IO_0.4 P1V8_High_Margin
                {"gpio": GPIO_BASE-60, "direction": "in"},   # gpio451 IO_0.3 P1V2_1_Low_Margin
                {"gpio": GPIO_BASE-61, "direction": "in"},   # gpio450 IO_0.2 P1V2_1_High_Margin
                {"gpio": GPIO_BASE-62, "direction": "in"},   # gpio449 IO_0.1 P1V2_2_Low_Margin
                {"gpio": GPIO_BASE-63, "direction": "in"}    # gpio448 IO_0.0 P1V2_2_High_Margin
            ],
            "config_0": 0x0, "config_1": 0x03, "polarity_inv_0": 0x0, "polarity_inv_1": 0x0, "output_port_0": 0x0, "output_port_1": 0x0
        },
        "9539_CPU_I2C": {
            "name": "pca9539_CPU_I2C", "address": 0x77, "parent": None, "channel": None, "pins": 16,
            "init_cfg": [
                {"gpio": GPIO_BASE-64, "direction": "in"},   # gpio447 IO_1.7
                {"gpio": GPIO_BASE-65, "direction": "in"},   # gpio446 IO_1.6
                {"gpio": GPIO_BASE-66, "direction": "in"},   # gpio445 IO_1.5
                {"gpio": GPIO_BASE-67, "direction": "in"},   # gpio444 IO_1.4
                {"gpio": GPIO_BASE-68, "direction": "in"},   # gpio443 IO_1.3
                {"gpio": GPIO_BASE-69, "direction": "in"},   # gpio442 IO_1.2
                {"gpio": GPIO_BASE-70, "direction": "in"},   # gpio441 IO_1.1
                {"gpio": GPIO_BASE-71, "direction": "in"},   # gpio440 IO_1.0
                {"gpio": GPIO_BASE-72, "direction": "in"},   # gpio439 IO_0.7
                {"gpio": GPIO_BASE-73, "direction": "in"},   # gpio438 IO_0.6
                {"gpio": GPIO_BASE-74, "direction": "in"},   # gpio437 IO_0.5
                {"gpio": GPIO_BASE-75, "direction": "in"},   # gpio436 IO_0.4
                {"gpio": GPIO_BASE-76, "direction": "in"},   # gpio435 IO_0.3
                {"gpio": GPIO_BASE-77, "direction": "in"},   # gpio434 IO_0.2
                {"gpio": GPIO_BASE-78, "direction": "in"},   # gpio433 IO_0.1
                {"gpio": GPIO_BASE-79, "direction": "in"}    # gpio432 IO_0.0
            ],
            "config_0": 0xff, "config_1": 0xff, "polarity_inv_0": 0x0, "polarity_inv_1": 0x0, "output_port_0": 0x0, "output_port_1": 0x0
        },
        
    }

    PATH_SYS_I2C_DEVICES = "/sys/bus/i2c/devices"
    PATH_SYS_GPIO = "/sys/class/gpio"
    PATH_SYS_GPIO_N = "/sys/class/gpio/gpio{0}"
    PATH_SYS_GPIO_VALUE = "/sys/class/gpio/gpio{0}/value"

    def __init__(self):
        log = Logger(__name__)
        self.logger = log.getLogger()
        self.IOExpanders = self.APOLLO_IOExpanders
        self.board_id = self.preinit_get_board_id()
        
        if self.board_id == BID.NCP1_1_PROTO:
            self.IOExpanders = self.APOLLO_IOExpanders
            self.ordered_ioexps = self.APOLLO_PROTO_IOExpanders_Order_List
        elif (self.board_id & BID.BUILD_REV_MASK) == BID.NCP1_1_ALPHA:
            self.IOExpanders = self.APOLLO_IOExpanders
            self.ordered_ioexps = self.APOLLO_ALPHA_IOExpanders_Order_List
        elif (self.board_id & BID.BUILD_REV_MASK) >= BID.NCP1_1_BETA:
            self.IOExpanders = self.APOLLO_BETA_IOExpanders
            self.ordered_ioexps = self.APOLLO_BETA_IOExpanders_Order_List
        else:
            sys.exit("Invalid Board ID:" + str(self.board_id))
        
    def _create_sysfs(self, path_parent, ioexp):
        try:
            sysfs_path = self.PATH_SYS_I2C_DEVICES + "/" + str(ioexp.bus_num) +\
                         "-" + hex(ioexp.address)[2:].zfill(4)
            if os.path.exists(sysfs_path):
                self.logger.info(ioexp.name + " is already exist")
                return

            with open(path_parent + "/new_device", 'w') as f:
                f.write(ioexp.NAME + " " + hex(ioexp.address))
            self.logger.info("Register " + ioexp.name + " in sysfs")
        except Exception as e:
            self.logger.error("Register IOExpander " + ioexp.name + " error: " + str(e))
            raise

    def _export_gpio(self, ioexp, pin, gpio_num):
        try:
            if (os.path.exists(self.PATH_SYS_GPIO + "/gpio" + str(gpio_num))):
                self.logger.info(ioexp.name + "(pin:" + str(pin) + ") is already exist")
            else:
                with open(self.PATH_SYS_GPIO + "/export", "w") as f:
                    f.write(str(gpio_num))
                self.logger.info("Export " + ioexp.name + "(pin:" + str(pin) + ") at GPIO " + str(gpio_num))
        except Exception as e:
            self.logger.error("Export GPIO for " + ioexp.name + "(pin:" + str(pin) + ") error: " + str(e))
            raise

    def _init_gpio(self, ioexp, pin, gpio_num):
        try:
            gpio_path = self.PATH_SYS_GPIO_N.format(gpio_num)
            gpio_dir_path = gpio_path + "/direction"            
            direction = ioexp.init_cfg[pin]["direction"]
            
            if (os.path.exists(gpio_path)):
                # Set direction
                with open(gpio_dir_path, "w") as f:
                    if direction == "out":
                        # If no "value" in dict, means this pin is for input, config next one
                        key = "value"
                        if key not in ioexp.init_cfg[pin]:
                            return

                        # This pin is for output, set initial value
                        value = ioexp.init_cfg[pin]["value"]
                        
                        # set output direction and init value with high/low 
                        if value == 0:
                            direction = "low"
                        else:
                            direction = "high"
                    
                    f.write(direction)                    
                        
                self.logger.info("Set " + ioexp.name + "(pin:" + str(pin) + ") direction: " + direction)                
            else:
                self.logger.warning(ioexp.name + "(pin:" + str(pin) + ") is not exported yet")
        except Exception as e:
            self.logger.error("Initialize " + ioexp.name + "(pin:" + str(pin) + ") fail, error: " + str(e))
            raise

    def _remove_sysfs(self, path_parent, dev_info):
        try:
            with open(path_parent + "/delete_device", 'w') as f:
                f.write(hex(dev_info["address"]))
            self.logger.info("Un-register " + dev_info["name"])
        except Exception:
            raise

    def _write_gpio(self, sysfs_path, value):
        try:
            if isinstance(value, int):
                value = str(value)
                                    
            if os.path.exists(sysfs_path):
                with open(sysfs_path, "w") as f:
                    f.write(value)
            else:
                raise IOError("sysfs_path does not exist: {0}".format(sysfs_path))
                return 0            
        except Exception as e:            
            self.logger.error(e)
            raise

    def _read_gpio(self, sysfs_path):
        try:
            if os.path.exists(sysfs_path):
                with open(sysfs_path, "r") as f:
                    content = f.read()
                if content != None:
                    return content
            else:
                raise IOError("sysfs_path does not exist: {0}".format(sysfs_path))
                return 0            
        except Exception as e:            
            self.logger.error(e)
            raise
        
    def preinit_get_board_id(self):
        mux_addr = I2CMux.I2C_ADDR_9548_ROOT_GB
        board_id_addr = self.IOExpanders["9555_BOARD_ID"]["address"]
        gpio_num = self.IOExpanders["9555_BOARD_ID"]["init_cfg"][7]["gpio"]
        gpio_path = self.PATH_SYS_GPIO_N.format(gpio_num)
        bid_bus_num = str(3)
        bid_i2c_channel_path = self.PATH_SYS_I2C_DEVICES + "/i2c-" + bid_bus_num
        board_info = 0
        
        try:
            # Check i2c_i801 and i2c_dev exist
            mod = subprocess.getoutput("lsmod | grep i2c_i801")
            if mod == "":
                subprocess.run(['modprobe', 'i2c_i801'])
            mod = subprocess.getoutput("lsmod | grep i2c_dev")
            if mod == "":
                subprocess.run(['modprobe', 'i2c_dev'])
            # Check gpio export or unexport
            if (os.path.exists(gpio_path)):
                self.logger.info(gpio_path + "(board ID) is already exist, get board id from sysfs")
                for i in range(8):
                    sysfs_path = self.PATH_SYS_GPIO_VALUE.format(gpio_num+i)
                    gpio_content = self._read_gpio(sysfs_path)
                    gpio_value = int(gpio_content)
                    board_info |= gpio_value << i
                return board_info
            elif (os.path.exists(bid_i2c_channel_path)):
                bus_num = bid_bus_num
                # read board_id/hw_rev/build_rev
                board_info = subprocess.getoutput("i2cget -y {} {} 0x1".format(bus_num, board_id_addr))
            else:
                bus_num = 0
                # Open mux channel for board id
                mod = subprocess.getoutput("i2cset -y {} {} 0x4".format(bus_num, mux_addr))
                if mod != "":                
                    self.logger.error("Open I2C Mux channel for board id failed: {}, mux_addr={}".format(mod, mux_addr))
                    return -1
                # read board_id/hw_rev/build_rev
                board_info = subprocess.getoutput("i2cget -y {} {} 0x1".format(bus_num, board_id_addr))
                # Close mux channel for board id
                mod = subprocess.getoutput("i2cset -y {} {} 0x0".format(bus_num, mux_addr))   
            
            return int(board_info, 16)
        except Exception:
            raise

    def init(self, i2c_mux):
        # Create sysfs, export gpio and initial gpio
        for ioexp_name in self.ordered_ioexps:
            try:
                if self.IOExpanders[ioexp_name]["parent"] is None:
                    bus_num = 0
                else:
                    bus_num = i2c_mux[self.IOExpanders[ioexp_name]["parent"]].ch_bus[self.IOExpanders[ioexp_name]["channel"]]
                if ioexp_name == "9539_HOST_GPIO_I2C":
                    ioexp = PCA9539(self.IOExpanders[ioexp_name], bus_num)
                else:
                    ioexp = PCA9535(self.IOExpanders[ioexp_name], bus_num)
                
                self.logger.debug("Create sysfs for " + ioexp.name)
                path_parent = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(ioexp.bus_num)
                self._create_sysfs(path_parent, ioexp)
                
                for i in range(ioexp.pins):
                    self.logger.info("Export gpio " + str(ioexp.init_cfg[i]["gpio"]) + " for " + ioexp.name + " pin: " + str(i))
                    self._export_gpio(ioexp, i, ioexp.init_cfg[i]["gpio"])
                    self._init_gpio(ioexp, i, ioexp.init_cfg[i]["gpio"])

            except Exception:
                raise

    def deinit(self, i2c_mux):
        for ioexp_name in self.ordered_ioexps:
            try:
                if self.IOExpanders[ioexp_name]["parent"] is None:
                    bus_num = 0
                else:
                    bus_num = i2c_mux[self.IOExpanders[ioexp_name]["parent"]].ch_bus[self.IOExpanders[ioexp_name]["channel"]]
                path_parent = self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(bus_num)
                self._remove_sysfs(path_parent, self.IOExpanders[ioexp_name])
            except Exception:
                raise
        
    def set_uart_mux(self, value):
        try:
            gpio_num = self.IOExpanders["9539_HOST_GPIO_I2C"]["init_cfg"][10]["gpio"]
            sysfs_path = self.PATH_SYS_GPIO_VALUE.format(gpio_num)
        
            self._write_gpio(sysfs_path, value)            
        except Exception as e:
            self.logger.error("set_uart_mux {0} failed, error: {1}".format(value, e))
            raise              
            
    def set_usb_mux(self, value):
        try:
            gpio_num = self.IOExpanders["9539_HOST_GPIO_I2C"]["init_cfg"][11]["gpio"]
            sysfs_path = self.PATH_SYS_GPIO_VALUE.format(gpio_num)
        
            self._write_gpio(sysfs_path, value)            
        except Exception as e:
            self.logger.error("set_usb_mux {0} failed, error: {1}".format(value, e))
            raise 
    
    def set_sys_led_g(self, value):
        try:
            gpio_num = self.IOExpanders["9539_SYS_LED"]["init_cfg"][15]["gpio"]
            sysfs_path = self.PATH_SYS_GPIO_VALUE.format(gpio_num)
        
            self.logger.debug("set_sys_led_g(), _write_gpio({0}, {1})".format(sysfs_path, value))
            self._write_gpio(sysfs_path, value)            
        except Exception as e:
            self.logger.error("set_sys_led_g {0} failed, error: {1}".format(value, e))
            raise 
            
    def set_fan_led_en(self, value):
        try:
            gpio_num = self.IOExpanders["9539_SYS_LED"]["init_cfg"][14]["gpio"]
            sysfs_path = self.PATH_SYS_GPIO_VALUE.format(gpio_num)
        
            self.logger.debug("set_fan_led_en(), _write_gpio({0}, {1})".format(sysfs_path, value))
            self._write_gpio(sysfs_path, value)            
        except Exception as e:
            self.logger.error("set_fan_led_en {0} failed, error: {1}".format(value, e))
            raise
     
    def set_fan_led_y(self, value):
        try:
            gpio_num = self.IOExpanders["9539_SYS_LED"]["init_cfg"][13]["gpio"]
            sysfs_path = self.PATH_SYS_GPIO_VALUE.format(gpio_num)
        
            self._write_gpio(sysfs_path, value)            
        except Exception as e:
            self.logger.error("set_fan_led_y {0} failed, error: {1}".format(value, e))
            raise 
    
    def set_psu0_led_y(self, value):
        try:
            gpio_num = self.IOExpanders["9539_SYS_LED"]["init_cfg"][12]["gpio"]
            sysfs_path = self.PATH_SYS_GPIO_VALUE.format(gpio_num)
        
            self.logger.debug("set_psu0_led_y(), _write_gpio({0}, {1})".format(sysfs_path, value))
            self._write_gpio(sysfs_path, value)            
        except Exception as e:
            self.logger.error("set_psu0_led_y {0} failed, error: {1}".format(value, e))
            raise 
     
    def set_psu1_led_y(self, value):
        try:
            gpio_num = self.IOExpanders["9539_SYS_LED"]["init_cfg"][11]["gpio"]
            sysfs_path = self.PATH_SYS_GPIO_VALUE.format(gpio_num)
        
            self.logger.debug("set_psu1_led_y(), _write_gpio({0}, {1})".format(sysfs_path, value))
            self._write_gpio(sysfs_path, value)            
        except Exception as e:
            self.logger.error("set_psu1_led_y {0} failed, error: {1}".format(value, e))
            raise
        
    def set_psu0_pwrok(self, value):
        try:
            gpio_num = self.IOExpanders["9539_SYS_LED"]["init_cfg"][7]["gpio"]
            sysfs_path = self.PATH_SYS_GPIO_VALUE.format(gpio_num)
        
            self.logger.debug("set_psu0_pwrok(), _write_gpio({0}, {1})".format(sysfs_path, value))
            self._write_gpio(sysfs_path, value)            
        except Exception as e:
            self.logger.error("set_psu0_pwrok {0} failed, error: {1}".format(value, e))
            raise 
     
    def set_psu1_pwrok(self, value):
        try:
            gpio_num = self.IOExpanders["9539_SYS_LED"]["init_cfg"][6]["gpio"]
            sysfs_path = self.PATH_SYS_GPIO_VALUE.format(gpio_num)
        
            self.logger.debug("set_psu1_pwrok(), _write_gpio({0}, {1})".format(sysfs_path, value))
            self._write_gpio(sysfs_path, value)            
        except Exception as e:
            self.logger.error("set_psu1_pwrok {0} failed, error: {1}".format(value, e))
            raise  
        
    def set_beacon_led(self, seg7_left, seg7_right):
        try:
            #left beacon LED, IO_0.0~IO_0.6
            j=0
            for i in range(15, 8, -1):            
                gpio_num = self.IOExpanders["9555_BEACON_LED"]["init_cfg"][i]["gpio"]            
                sysfs_path = self.PATH_SYS_GPIO_VALUE.format(gpio_num)
        
                value = seg7_left[j] ^ 1
                self.logger.debug("set_beacon_led(), _write_gpio({}, {})".format(sysfs_path, value))
                self._write_gpio(sysfs_path, value)
                j+=1
            
            #right beacon LED, IO_1.0~IO_1.6
            j=0
            for i in range(7, 0, -1):            
                gpio_num = self.IOExpanders["9555_BEACON_LED"]["init_cfg"][i]["gpio"]            
                sysfs_path = self.PATH_SYS_GPIO_VALUE.format(gpio_num)
        
                value = seg7_right[j] ^ 1
                self.logger.debug("set_beacon_led(), _write_gpio({}, {})".format(sysfs_path, value))
                self._write_gpio(sysfs_path, value)   
                j+=1                      
        except Exception as e:
            self.logger.error("set_beacon_led {0} failed, error: {1}".format(value, e))
            raise                              
