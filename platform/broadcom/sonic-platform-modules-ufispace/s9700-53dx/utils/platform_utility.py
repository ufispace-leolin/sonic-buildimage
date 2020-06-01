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
from bsp.gpio.ioexp import IOExpander
from bsp.cpld.cpld import CPLD
from bsp.eeprom.eeprom import EEPRom
from bsp.thermal.thermal import Thermal
from bsp.const.const import BID

class PlatformUtility:

    builtin_pca954x_path = "/lib/modules/{}/kernel/drivers/i2c/muxes/i2c-mux-pca954x.ko"
    #kernel release version
    kr_version_cmd = "uname -r" 
    depmod_cmd = "depmod -a"
    
    def __init__(self):
        try:
            log = Logger(__name__)
            self.logger = log.getLogger()
            self.ioexp = IOExpander()
            
            #Check Board ID
            board_id = self.ioexp.preinit_get_board_id()
            #board_id = BID.NCP1_1_ALPHA

            self.board_id = board_id
            self.i2c_mux = I2CMux(self.board_id)
            self.eeprom = EEPRom(self.board_id)
            self.cpld = CPLD()
            self.thermal = Thermal()
        except Exception as e:
            raise

    def device_init(self):
        try:
            # Unmount kernel modules
            mod = subprocess.getoutput("lsmod | grep gpio_ich")
            if mod != "":
                subprocess.run(['rmmod', 'gpio_ich'])

            # Mount kernel modules
            # I2C I801
            subprocess.run(['modprobe', 'i2c_i801'])

            # I2C Dev
            subprocess.run(['modprobe', 'i2c_dev'])
            
            #CPLD 0x30 missing workaround :BEGIN
            #open mux 0x75
            mod = subprocess.getoutput("i2cset -y 0 0x75 0x1")
            if mod != "":                
                self.logger.error("Open I2C Mux channel for CPLD WA failed.")
            #Access CPLD2 version
            retcode, mod = subprocess.getstatusoutput("i2cget -y 0 0x39 0x2")
            if retcode != 0:                
                self.logger.error("Open I2C Mux channel for CPLD WA failed.")
            #close mux 0x75
            mod = subprocess.getoutput("i2cset -y 0 0x75 0x0")
            if mod != "":                
                self.logger.error("Close I2C Mux channel for CPLD WA failed.")
            #CPLD 0x30 missing workaround :END

            # I2C Mux
            subprocess.run(['modprobe', 'i2c_mux_pca954x', 'force_deselect_on_exit=1'])
            self.i2c_mux.init()

            # EEPROM
            subprocess.run(['modprobe', 'eeprom_mb'])
            mod = subprocess.getoutput("lsmod | grep sff_8436_eeprom")
            if mod != "":
                subprocess.run(['rmmod', 'sff_8436_eeprom'])
            subprocess.run(['modprobe', 'optoe'])
            self.eeprom = EEPRom(self.board_id)
            self.eeprom.init()

            # Thermal
            subprocess.run(['modprobe', 'lm75'])
            self.thermal.init()

            # GPIO
            subprocess.run(['modprobe', 'gpio-pca953x'])
            self.ioexp.init(self.i2c_mux.MUXs)
            
            # IPMI
            subprocess.run(['modprobe', 'ipmi_devintf'])            
            subprocess.run(['modprobe', 'ipmi_si'])

            # CPLD
            subprocess.run(['modprobe', 'apollo_cpld'])
            self.cpld.init()
            
        except Exception as e:
            raise

    def device_deinit(self):
        try:
            self.i2c_mux = I2CMux(self.board_id)
            # Remove kernel modules
            # CPLD
            self.cpld.deinit()
            mod = subprocess.getoutput("lsmod | grep apollo_cpld")
            if mod != "":                
                subprocess.run(['rmmod', 'apollo_cpld'])
                        
            # GPIO
            mod = subprocess.getoutput("lsmod | grep pca953x")
            if mod != "":
                self.ioexp.deinit(self.i2c_mux.MUXs)
                subprocess.run(['rmmod', 'gpio-pca953x'])

            # Thermal
            mod = subprocess.getoutput("lsmod | grep lm75")
            if mod != "":
                subprocess.run(['rmmod', 'lm75'])

            # MB EEPROM
            mod = subprocess.getoutput("lsmod | grep eeprom_mb")
            if mod != "":
                subprocess.run(['rmmod', 'eeprom_mb'])

            # OPTOE EEPROM
            mod = subprocess.getoutput("lsmod | grep optoe")
            if mod != "":
                subprocess.run(['rmmod', 'optoe'])

            # I2C Mux
            mod = subprocess.getoutput("lsmod | grep pca954x")
            if mod != "":
                self.i2c_mux.deinit()
                subprocess.run(['rmmod', 'i2c_mux_pca954x'])
        except Exception:
            raise

    def get_kernel_release(self):
        try:
            return subprocess.getoutput(self.kr_version_cmd)            
        except Exception:
            raise
        
    def check_ko(self):
        try:            
            #get kernel release
            kr = self.get_kernel_release()
            
            #remove built-in i2c-mux-pca954x.ko if exist
            pca954x_path = self.builtin_pca954x_path.format(kr)
            if os.path.exists(pca954x_path):                
                os.remove(pca954x_path)
                #generate modules.dep
                subprocess.run(self.depmod_cmd, shell=True)
            
        except Exception:
            raise        

def main():
    util = PlatformUtility()

    if len(sys.argv) != 2:
        print("\nUsage: sudo " + sys.argv[0] + " init|deinit")
        return

    if sys.argv[1] == 'init':
	#util.check_ko()
        util.device_init()
    elif sys.argv[1] == 'deinit':
        util.device_deinit()
    else:
        print("Invalid arguments:")

        # print command line arguments
        for arg in sys.argv[1:]:
            print(arg)
        print("\nUsage: sudo " + sys.argv[0] + " init|deinit")

if __name__ == "__main__":
    main()
