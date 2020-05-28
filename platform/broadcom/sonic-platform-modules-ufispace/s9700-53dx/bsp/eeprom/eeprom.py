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
from bsp.const.const import QSFP
from bsp.const.const import QSFPDD
from bsp.const.const import BID
     
class EEPRom:

    PATH_SYS_I2C_DEVICES = "/sys/bus/i2c/devices"

    I2C_BUS_CPU_EEPROM = 0

    I2C_ADDR_EEPROM_CPU  = 0x57
    I2C_ADDR_EEPROM_SFP  = 0x50
    I2C_ADDR_EEPROM_QSFP = 0x50
    I2C_ADDR_EEPROM_QSFPDD = 0x50


    QSFPReg = {
        "SFF8436": {
               "TEMP":    [0, 22], #[PAGE, ADDR]
               "VOLT":    [0, 26],
               "VENDOR":  [1, 20],
               "SN":      [1, 68],               
               "TX_BIAS": [0, 42],
               "RX_PWR":  [0, 34],
               },        
        "CHL_MAX": 4,
        "PAGE_SIZE": 5
    }
    
    QSFPDDReg = {
        #REV 2.0
        "20": {"REV":     [0, 1], #[PAGE, ADDR]
               "TEMP":    [0, 26],
               "VOLT":    [0, 30],
               "VENDOR":  [1, 20],
               "SN":      [1, 68],
               "TX_PWR":  [0, 64],
               "TX_BIAS": [0, 48],
               "RX_PWR":  [0, 32],
               },
        #REV 3.0
        "30": {"REV":     [0, 1], #[PAGE, ADDR]
               "TEMP":    [0, 14],
               "VOLT":    [0, 16],
               "VENDOR":  [1, 1],
               "SN":      [1, 38],
               "TX_PWR":  [18, 26],
               "TX_BIAS": [18, 42],
               "RX_PWR":  [18, 58],
               },
        "CHL_MAX": 8,
        "PAGE_SIZE": 257
    }

    HD_HEX="02x"
    HD_ASCII="c"

    EEPROM_CMD = {"READ_BLK": "dd if={} bs=128 count=1 skip={} status=none | base64",
                  "READ_BYTE": "echo '{}' | base64 -d -i | hexdump -s {} -n {} -e '{}/1 \"%{}\"'"}

    def __init__(self, board_id):
        log = Logger(__name__)
        self.logger = log.getLogger()
        self.i2c_mux = I2CMux(board_id)
        self.ioexp = IOExpander()
        self.board_id = board_id

    def _qsfp_port_fp2phy(self, fp_port):
        if 0 <= fp_port <= 19:
            phy_port = fp_port
        else:
            if fp_port % 2 == 0:
                phy_port = fp_port + 1
            else:
                phy_port = fp_port - 1

        return phy_port

    def _get_qsfp_bus_num(self, port_num):
        port_num = self._qsfp_port_fp2phy(port_num)
        port_grp = int(port_num / 8)
        ch = port_num % 8

        if port_grp == 0:      # P0~P7
            mux = "9548_CHILD_QSFP0"
        elif port_grp == 1:    # P8~P15
            mux = "9548_CHILD_QSFP1"
        elif port_grp == 2:    # P16~P23
            mux = "9548_CHILD_QSFP2"
        elif port_grp == 3:    # P24~P31
            mux = "9548_CHILD_QSFP3"
        else:                  # P32~P39
            mux = "9548_CHILD_QSFP4"

        return self.i2c_mux.MUXs[mux].ch_bus[ch]

    def _get_qsfpdd_bus_num(self, port_num):
        if self.board_id == BID.NCP1_1_PROTO:
            port_grp = int(port_num / 4)
            ch = port_num % 8

            if port_grp == 0:      # P0~P3
                mux = "9548_CHILD_QSFPDDBOARD"
            elif port_grp == 1:      # P4~P7
                mux = "9548_CHILD_QSFPDD0"
            else:                  # P8~P12
                mux = "9548_CHILD_QSFPDD1"

            return self.i2c_mux.MUXs[mux].ch_bus[ch]

        elif (self.board_id & BID.BUILD_REV_MASK) >= BID.NCP1_1_ALPHA:
            port_grp = int(port_num / 8)
            ch = port_num % 8

            if port_grp == 0:    # P0~P7
                mux = "9548_CHILD_QSFPDD0"
            else:                  # P8~P12
                mux = "9548_CHILD_QSFPDD1"

            return self.i2c_mux.MUXs[mux].ch_bus[ch]
        else:
            sys.exit("Invalid Board ID:" + str(self.board_id))
            
    def _create_cpu_eeprom_sysfs(self):
        try:
            cpu_eeprom_sysfs_path = self.PATH_SYS_I2C_DEVICES + "/" + \
                                    str(self.I2C_BUS_CPU_EEPROM) + "-" + \
                                    hex(self.I2C_ADDR_EEPROM_CPU)[2:].zfill(4)

            if os.path.exists(cpu_eeprom_sysfs_path):
                pass
            else:
                with open(self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(self.I2C_BUS_CPU_EEPROM) + "/new_device", "w") as f:
                    f.write("mb_eeprom " + hex(self.I2C_ADDR_EEPROM_CPU))

            self.logger.debug("CPU EEPROM:" + cpu_eeprom_sysfs_path)
        except Exception as e:
            self.logger.error("Register CPU EEPROM to sysfs fail, error: " + str(e))
            raise

    def _create_qsfp_eeprom_sysfs(self):
        try:
            for port in range(QSFP.MAX_PORT):
                bus_num = self._get_qsfp_bus_num(port)

                qsfp_eeprom_sysfs_path = self.PATH_SYS_I2C_DEVICES + "/" + \
                                        str(bus_num) + "-" + \
                                        hex(self.I2C_ADDR_EEPROM_QSFP)[2:].zfill(4)

                if os.path.exists(qsfp_eeprom_sysfs_path):
                    pass
                else:
                    with open(self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(bus_num) + "/new_device", "w") as f:
                        f.write("sff8436 " + hex(self.I2C_ADDR_EEPROM_QSFP))

                self.logger.debug("QSFP(" + str(port) + ") EEPROM:" + qsfp_eeprom_sysfs_path)
        except Exception as e:
            self.logger.error("Register QSFP EEPROM to sysfs fail, error: " + str(e))
            raise

    def _create_qsfpdd_eeprom_sysfs(self):
        try:
            for port in range(QSFPDD.MAX_PORT):
                bus_num = self._get_qsfpdd_bus_num(port)

                qsfpdd_eeprom_sysfs_path = self.PATH_SYS_I2C_DEVICES + "/" + \
                                        str(bus_num) + "-" + \
                                        hex(self.I2C_ADDR_EEPROM_QSFPDD)[2:].zfill(4)

                if os.path.exists(qsfpdd_eeprom_sysfs_path):
                    pass
                else:
                    with open(self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(bus_num) + "/new_device", "w") as f:
                        f.write("sff8436 " + hex(self.I2C_ADDR_EEPROM_QSFPDD))

                self.logger.debug("QSFPDD(" + str(port) + ") EEPROM:" + qsfpdd_eeprom_sysfs_path)
        except Exception as e:
            self.logger.error("Register QSFPDD EEPROM to sysfs fail, error: " + str(e))
            raise

    def _read_page(self, eeprom_sysfs, skip_page):
        page_data = subprocess.getoutput(self.EEPROM_CMD["READ_BLK"].format(eeprom_sysfs, skip_page))

        return page_data

    def _read_page_byte(self, page_data, offset):
        byte_data = subprocess.getoutput(self.EEPROM_CMD["READ_BYTE"].format(page_data, offset, 1, 1, self.HD_HEX))

        return byte_data

    def _read_page_word(self, page_data, offset, repeat=1):
        word_list = [0] * repeat

        for i in range(repeat):
            word_list[i] = subprocess.getoutput(self.EEPROM_CMD["READ_BYTE"].format(page_data, offset+i*2, 2, 2, self.HD_HEX))

        return word_list

    def _read_page_ascii(self, page_data, offset, length):
        try:
            ascii_data = subprocess.getoutput(self.EEPROM_CMD["READ_BYTE"].format(page_data, offset, length, length, self.HD_ASCII))
        except:
            ascii_data = "n/a"
        
        return ascii_data

    def _twos_comp(self, val, bits):
        """compute the 2's complement of int value val"""
        if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)        # compute negative value
        return val                         # return positive value as is

    # def _create_sfp_eeprom_sysfs(self):
        # try:
            # for port in range(2):
                # if port == 0:
                    # bus_num = self.i2c_mux.MUXs["9548_ROOT_SFP_CPLD"].ch_bus[0]
                # else:
                    # bus_num = self.i2c_mux.MUXs["9548_ROOT_SFP_CPLD"].ch_bus[1]

                # sfp_eeprom_sysfs_path = self.PATH_SYS_I2C_DEVICES + "/" + \
                                         # str(bus_num) + "-" + \
                                         # hex(self.I2C_ADDR_EEPROM_SFP)[2:].zfill(4)

                # if os.path.exists(sfp_eeprom_sysfs_path):
                    # pass
                # else:
                    # with open(self.PATH_SYS_I2C_DEVICES + "/i2c-" + str(bus_num) + "/new_device", "w") as f:
                        # f.write("optoe2 " + hex(self.I2C_ADDR_EEPROM_SFP))

                # self.logger.debug("SFP+(" + str(port) + ") EEPROM:" + sfp_eeprom_sysfs_path)
        # except Exception as e:
            # self.logger.error("Register SFP+ EEPROM to sysfs fail, error: " + str(e))
            # raise

    def init(self):
        try:
            self._create_cpu_eeprom_sysfs()
        except Exception as e:
            self.logger.error("Init CPU EEPROM fail, error: " + str(e))
            raise

        try:
            self._create_qsfp_eeprom_sysfs()
        except Exception as e:
            self.logger.error("Init QSFP port EEPROM fail, error: " + str(e))
            raise

        try:
            self._create_qsfpdd_eeprom_sysfs()
        except Exception as e:
            self.logger.error("Init QSFPDD port EEPROM fail, error: " + str(e))
            raise

        # try:
            # self._create_sfp_eeprom_sysfs()
        # except Exception as e:
            # self.logger.error("Init SFP+ port EEPROM fail, error: " + str(e))
            # raise

    def dump_cpu_eeprom(self):
        try:
            cpu_eeprom_sysfs_path = self.PATH_SYS_I2C_DEVICES + "/" + \
                                    str(self.I2C_BUS_CPU_EEPROM) + "-" + \
                                    hex(self.I2C_ADDR_EEPROM_CPU)[2:].zfill(4)

            if os.path.exists(cpu_eeprom_sysfs_path):
                with open(cpu_eeprom_sysfs_path + "/eeprom", "rb") as f:
                    content = f.read()

                return content
            else:
                self.logger.error("CPU EEPROM is not registered in sysfs")
        except Exception as e:
            self.logger.error("Dump CPU EEPROM fail, error: " + str(e))
            raise

    def dump_qsfp_eeprom(self, port_num):
        try:
            bus_num = self._get_qsfp_bus_num(port_num)
            qsfp_eeprom_sysfs_path = self.PATH_SYS_I2C_DEVICES + "/" + \
                                    str(bus_num) + "-" + \
                                    hex(self.I2C_ADDR_EEPROM_QSFP)[2:].zfill(4)

            if os.path.exists(qsfp_eeprom_sysfs_path):
                with open(qsfp_eeprom_sysfs_path + "/eeprom", "rb") as f:
                    content = f.read()

                return content
            else:
                self.logger.error("QSFP port(" + str(port_num) + ") EEPROM is not registered in sysfs")
        except Exception as e:
            self.logger.error("Dump QSFP port(" + str(port_num) + ") EEPROM fail, error: " + str(e))
            raise

    def dump_qsfpdd_eeprom(self, port_num):
        try:
            bus_num = self._get_qsfpdd_bus_num(port_num)
            qsfpdd_eeprom_sysfs_path = self.PATH_SYS_I2C_DEVICES + "/" + \
                                    str(bus_num) + "-" + \
                                    hex(self.I2C_ADDR_EEPROM_QSFPDD)[2:].zfill(4)

            if os.path.exists(qsfpdd_eeprom_sysfs_path):
                with open(qsfpdd_eeprom_sysfs_path + "/eeprom", "rb") as f:
                    content = f.read()

                return content
            else:
                self.logger.error("QSFPDD port(" + str(port_num) + ") EEPROM is not registered in sysfs")
        except Exception as e:
            self.logger.error("Dump QSFPDD port(" + str(port_num) + ") EEPROM fail, sysfs path=" + qsfpdd_eeprom_sysfs_path + " error: " + str(e))
            raise

    def get_qsfp_info(self, port_num):        
        try:
            list_rx_pwr = [0] * self.QSFPReg["CHL_MAX"]
            list_tx_bias = [0] * self.QSFPReg["CHL_MAX"]            
            eeprom_pages = [0] * self.QSFPReg["PAGE_SIZE"]

            bus_num = self._get_qsfp_bus_num(port_num)
            qsfp_eeprom_sysfs_path = self.PATH_SYS_I2C_DEVICES + "/" + \
                                    str(bus_num) + "-" + \
                                    hex(self.I2C_ADDR_EEPROM_QSFP)[2:].zfill(4) + \
                                    "/eeprom"

            if os.path.exists(qsfp_eeprom_sysfs_path):

                #get revision
                eeprom_pages[0] = self._read_page(qsfp_eeprom_sysfs_path, 0)
                
                qsfpreg = self.QSFPReg["SFF8436"]

                #read pages from qsfpreg
                for _, value in qsfpreg.items():
                    page = value[0]
                    if eeprom_pages[page] == 0:
                        eeprom_pages[page] = self._read_page(qsfp_eeprom_sysfs_path, page)
                
                raw_list_temp = self._read_page_word(eeprom_pages[qsfpreg["TEMP"][0]], qsfpreg["TEMP"][1])
                raw_list_volt = self._read_page_word(eeprom_pages[qsfpreg["VOLT"][0]], qsfpreg["VOLT"][1])
                raw_vendor = self._read_page_ascii(eeprom_pages[qsfpreg["VENDOR"][0]], qsfpreg["VENDOR"][1], 16)
                raw_sn = self._read_page_ascii(eeprom_pages[qsfpreg["SN"][0]], qsfpreg["SN"][1], 16)
                raw_list_rx_pwr = self._read_page_word(eeprom_pages[qsfpreg["RX_PWR"][0]],
                                                       qsfpreg["RX_PWR"][1],
                                                       self.QSFPReg["CHL_MAX"])
                raw_list_tx_bias = self._read_page_word(eeprom_pages[qsfpreg["TX_BIAS"][0]],
                                                       qsfpreg["TX_BIAS"][1],
                                                       self.QSFPReg["CHL_MAX"])
                
                #Temperature in Celsius Degree
                try:
                    temp = self._twos_comp(int(raw_list_temp[0],16), 16)/256
                except:
                    temp = "n/a"
                    
                #Volt
                try:
                    volt = int(raw_list_volt[0],16)/10000
                except:
                    volt = "n/a"
                
                #Vendor name     
                vendor = raw_vendor.strip()
                
                #SN
                sn = raw_sn.strip()

                for i in range(self.QSFPReg["CHL_MAX"]):
                    #RX Power, 0 to 6.5535 mW                    
                    try:                         
                        list_rx_pwr[i] = int(raw_list_rx_pwr[i], 16)/10000
                    except:
                        list_rx_pwr[i] = "n/a"
                        
                    #TX Bias, 0 to 131 mA                    
                    try:                         
                        list_tx_bias[i] = int(raw_list_tx_bias[i], 16)*0.002
                    except:
                        list_tx_bias[i] = "n/a"
                                        
                return {"temp": temp,
                        "volt": volt,
                        "vendor": vendor,
                        "sn": sn,
                        "rx_pwr": list_rx_pwr,
                        "tx_bias": list_tx_bias}
            else:
                self.logger.error("QSFP port(" + str(port_num) + ") EEPROM is not registered in sysfs")


        except Exception as e:
            self.logger.error("Dump QSFP port(" + str(port_num) + ") EEPROM fail, sysfs path=" + qsfp_eeprom_sysfs_path + " error: " + str(e))
            raise
        
    def get_qsfpdd_info(self, port_num):
        try:
            list_rx_pwr = [0] * self.QSFPDDReg["CHL_MAX"]
            list_tx_bias = [0] * self.QSFPDDReg["CHL_MAX"]
            list_tx_pwr = [0] * self.QSFPDDReg["CHL_MAX"]
            eeprom_pages = [0] * self.QSFPDDReg["PAGE_SIZE"]

            bus_num = self._get_qsfpdd_bus_num(port_num)
            qsfpdd_eeprom_sysfs_path = self.PATH_SYS_I2C_DEVICES + "/" + \
                                    str(bus_num) + "-" + \
                                    hex(self.I2C_ADDR_EEPROM_QSFPDD)[2:].zfill(4) + \
                                    "/eeprom"

            if os.path.exists(qsfpdd_eeprom_sysfs_path):

                #get revision
                eeprom_pages[0] = self._read_page(qsfpdd_eeprom_sysfs_path, 0)
                raw_rev = self._read_page_byte(eeprom_pages[0], self.QSFPDDReg["30"]["REV"][1])

                #set qsfdreg by revision
                if raw_rev > "20":
                    qsfpddreg = self.QSFPDDReg["30"]
                else:
                    qsfpddreg = self.QSFPDDReg["20"]

                #read pages from qsfpddreg
                for _, value in qsfpddreg.items():
                    page = value[0]
                    if eeprom_pages[page] == 0:
                        eeprom_pages[page] = self._read_page(qsfpdd_eeprom_sysfs_path, page)
                
                raw_list_temp = self._read_page_word(eeprom_pages[qsfpddreg["TEMP"][0]], qsfpddreg["TEMP"][1])
                raw_list_volt = self._read_page_word(eeprom_pages[qsfpddreg["VOLT"][0]], qsfpddreg["VOLT"][1])
                raw_vendor = self._read_page_ascii(eeprom_pages[qsfpddreg["VENDOR"][0]], qsfpddreg["VENDOR"][1], 16)
                raw_sn = self._read_page_ascii(eeprom_pages[qsfpddreg["SN"][0]], qsfpddreg["SN"][1], 16)
                raw_list_rx_pwr = self._read_page_word(eeprom_pages[qsfpddreg["RX_PWR"][0]],
                                                       qsfpddreg["RX_PWR"][1],
                                                       self.QSFPDDReg["CHL_MAX"])
                raw_list_tx_bias = self._read_page_word(eeprom_pages[qsfpddreg["TX_BIAS"][0]],
                                                       qsfpddreg["TX_BIAS"][1],
                                                       self.QSFPDDReg["CHL_MAX"])
                raw_list_tx_pwr = self._read_page_word(eeprom_pages[qsfpddreg["TX_PWR"][0]],
                                                       qsfpddreg["TX_PWR"][1],
                                                       self.QSFPDDReg["CHL_MAX"])

                #Rev 2.X/3.X 
                rev = raw_rev[:1] + "." + raw_rev[1:]
                
                #Temperature in Celsius Degree
                try:
                    temp = self._twos_comp(int(raw_list_temp[0],16), 16)/256
                except:
                    temp = "n/a"
                    
                #Volt
                try:
                    volt = int(raw_list_volt[0],16)/10000
                except:
                    volt = "n/a"
                
                #Vendor name     
                vendor = raw_vendor.strip()
                
                #SN
                sn = raw_sn.strip()

                for i in range(self.QSFPDDReg["CHL_MAX"]):
                    #RX Power, 0 to 6.5535 mW                    
                    try:                         
                        list_rx_pwr[i] = int(raw_list_rx_pwr[i], 16)/10000
                    except:
                        list_rx_pwr[i] = "n/a"
                    
                    #TX Bias, 0 to 131 mA                    
                    try:                         
                        list_tx_bias[i] = int(raw_list_tx_bias[i], 16)*0.002
                    except:
                        list_tx_bias[i] = "n/a"
                        
                    #TX Power, 0 to 6.5535 mW                    
                    try:                         
                        list_tx_pwr[i] = int(raw_list_tx_pwr[i], 16)/10000
                    except:
                        list_tx_pwr[i] = "n/a"
                            
                return {"rev": rev,
                        "temp": temp,
                        "volt": volt,
                        "vendor": vendor,
                        "sn": sn,
                        "rx_pwr": list_rx_pwr,
                        "tx_bias": list_tx_bias,
                        "tx_pwr": list_tx_pwr}
            else:
                self.logger.error("QSFPDD port(" + str(port_num) + ") EEPROM is not registered in sysfs")

        except Exception as e:
            self.logger.error("Dump QSFPDD port(" + str(port_num) + ") EEPROM fail, sysfs path=" + qsfpdd_eeprom_sysfs_path + " error: " + str(e))
            raise
        
    # def dump_sfp_eeprom(self, port_num):
        # try:
            # if port_num == 0:
                # sfp_eeprom_sysfs_path = self.PATH_SYS_I2C_DEVICES + "/" + \
                                         # str(self.i2c_mux.MUXs["9548_ROOT_SFP_CPLD"].ch_bus[0]) + "-" + \
                                         # hex(self.I2C_ADDR_EEPROM_SFP)[2:].zfill(4)
            # else:
                # sfp_eeprom_sysfs_path = self.PATH_SYS_I2C_DEVICES + "/" + \
                                         # str(self.i2c_mux.MUXs["9548_ROOT_SFP_CPLD"].ch_bus[1]) + "-" + \
                                         # hex(self.I2C_ADDR_EEPROM_SFP)[2:].zfill(4)

            # if os.path.exists(sfp_eeprom_sysfs_path):
                # with open(sfp_eeprom_sysfs_path + "/eeprom", "rb") as f:
                    # content = f.read()

                # return content
            # else:
                # self.logger.error("SFP+ port(" + str(port_num) + ") EEPROM is not registered in sysfs")
        # except Exception as e:
            # self.logger.error("Dump SFP+ port(" + str(port_num) + ") EEPROM fail, error: " + str(e))
            # raise
