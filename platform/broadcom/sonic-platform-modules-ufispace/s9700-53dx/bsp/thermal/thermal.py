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
import subprocess

from bsp.common.logger import Logger

class Thermal:

    PATH_SYS_I2C_DEVICES = "/sys/bus/i2c/devices"
    PATH_CORETEMP_DEVICES = "/sys/devices/platform/coretemp.0/hwmon/hwmon0"

    I2C_BUS_CPU_TMP75 = 0
    I2C_BUS_CPU_CORETEMP = 0

    I2C_ADDR_TMP75_CPU_BOARD  = 0x4F

    def __init__(self):
        log = Logger(__name__)
        self.logger = log.getLogger()

    def _create_tmp75_cpu_sysfs(self):
        try:
            tmp75_cpu_sysfs_path = self.PATH_SYS_I2C_DEVICES + "/" + \
                                    str(self.I2C_BUS_CPU_TMP75) + "-" + \
                                    hex(self.I2C_ADDR_TMP75_CPU_BOARD)[2:].zfill(4)

            if os.path.exists(tmp75_cpu_sysfs_path):
                pass
            else:
                with open(self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.I2C_BUS_CPU_TMP75) + "/new_device", "w") as f:
                    f.write("tmp75 " + hex(self.I2C_ADDR_TMP75_CPU_BOARD))

            self.logger.debug("TMP75 CPU:" + tmp75_cpu_sysfs_path)
        except Exception as e:
            self.logger.error("Register TMP75 on CPU board to sysfs fail, error: " + str(e))
            raise

    def _create_coretemp_cpu_sysfs(self):
        try:
            coretemp_cpu_sysfs_path = self.PATH_CORETEMP_DEVICES

            if os.path.exists(coretemp_cpu_sysfs_path):
                pass
            else:
                subprocess.run(['modprobe', 'coretemp'])

            self.logger.debug("Coretemp CPU:" + coretemp_cpu_sysfs_path)
        except Exception as e:
            self.logger.error("Register Coretemp on CPU board to sysfs fail, error: " + str(e))
            raise

    def init(self):
        try:
            self._create_coretemp_cpu_sysfs()
        except Exception as e:
            self.logger.error("Init CPU Coretemp fail, error: " + str(e))
            raise

        try:
            self._create_tmp75_cpu_sysfs()
        except Exception as e:
            self.logger.error("Init TMP75 on CPU board fail, error: " + str(e))
            raise

    def get_tmp75_cpu_board(self):
        try:
            tmp75_cpu_sysfs_path = self.PATH_SYS_I2C_DEVICES + "/" + \
                                    str(self.I2C_BUS_CPU_TMP75) + "-" + \
                                    hex(self.I2C_ADDR_TMP75_CPU_BOARD)[2:].zfill(4)

            if os.path.exists(tmp75_cpu_sysfs_path):
                with open(tmp75_cpu_sysfs_path + "/hwmon/hwmon1/temp1_input", "rb") as f:
                    content = f.read()

                return int(content.strip())
            else:
                self.logger.error("CPU TMP75 is not registered in sysfs")
        except Exception as e:
            self.logger.error("Dump CPU TMP75 fail, error: " + str(e))
            raise

    def get_coretemp_cpu(self, core_num):
        try:
            coretemp_cpu_sysfs_path = self.PATH_CORETEMP_DEVICES

            if os.path.exists(coretemp_cpu_sysfs_path):
                with open(coretemp_cpu_sysfs_path + "/temp" + str(core_num) + "_input", "rb") as f:
                    content = f.read()

                return int(content.strip())
            else:
                self.logger.error("CPU Coretemp is not registered in sysfs")
        except Exception as e:
            self.logger.error("Dump CPU Coretemp fail, error: " + str(e))
            raise
