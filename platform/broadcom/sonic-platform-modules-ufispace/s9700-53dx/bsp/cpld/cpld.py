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
from time import sleep

from bsp.common.logger import Logger
from bsp.const.const import DataType
from bsp.const.const import LPMode
from bsp.const.const import PSU
from bsp.const.const import SFP
from bsp.const.const import Led
from bsp.const.const import QSFPDD
from bsp.const.const import PortStatus
from bsp.const.const import CPLDConst
from bsp.const.const import DevType
from bsp.protocol.i2c import I2C, I2C_Dev
from bsp.protocol.lpc import LPC
from bsp.protocol.lpc import LPCDevType

class CPLDCPUReg(object):
    REG_CPLD_REVISION = 0x00
    REG_RESET_CTRL = 0x03

class CPLD:

    EXT_BOARD_ID = 0b1110
    
    BOARD_ID_MAP = {0b0000: "Apache phase1",
                    0b0001: "Apache phase2",
                    0b0010: "Apollo NCP1-1 40+13P",
                    0b0011: "Apollo NCP1-2",
                    0b0100: "Apollo NCP2-1 10+13P",
                    0b0101: "Apollo NCP2-2",
                    0b0110: "Apollo NCP3",
                    0b0111: "Apollo NCF 48P",
                    0b1000: "EMUX",
                    0b1110: "Extended board ID"}    

    EXT_BOARD_ID_MAP = {}

    HARDWARE_REV_MAP = {0b00: "Proto",
                        0b01: "Alpha",
                        0b10: "Beta",
                        0b11: "PVT"}

    BUILD_REV_MAP = {0b00: "A1",
                     0b01: "A2",
                     0b10: "A3",
                     0b11: "A4"}    
    
    CPLD_I2C_BUS = 1
    CPLD_I2C_ADDR = [0x30, 0x39, 0x3A, 0x3B, 0x3C]
    
    CPLD_MODEL_ID_BIT = 0b11110000
    CPLD_HW_REV_BIT = 0b00001100
    CPLD_BUILD_REV_BIT = 0b00000011
    CPLD_PORT_INT_BIT = 0b00000001
    
    CPLD_QSFP_STATUS_INT_BIT = 0b00000001
    CPLD_QSFP_STATUS_ABS_BIT = 0b00000010    
    CPLD_QSFP_CONFIG_RST_BIT = 0b00000001
    CPLD_QSFP_CONFIG_LP_BIT = 0b00000100    
    
    CPLD_QSFPDD_STATUS_INT_BIT = 0b00000001
    CPLD_QSFPDD_STATUS_ABS_BIT = 0b00000010    
    CPLD_QSFPDD_CONFIG_RST_BIT = 0b00000001
    CPLD_QSFPDD_CONFIG_LP_BIT = 0b00000100
    
    CPLD_SFP0_STATUS_PRSNT_BIT = 0b00000001
    CPLD_SFP0_STATUS_TX_FAULT_BIT = 0b00000010
    CPLD_SFP0_STATUS_RX_LOS_BIT = 0b00000100
    CPLD_SFP0_CONFIG_TX_DIS_BIT = 0b00000001        
    
    CPLD_SFP1_STATUS_PRSNT_BIT = 0b00010000
    CPLD_SFP1_STATUS_TX_FAULT_BIT = 0b00100000
    CPLD_SFP1_STATUS_RX_LOS_BIT = 0b01000000
    CPLD_SFP1_CONFIG_TX_DIS_BIT = 0b00010000    
    
    CPLD_PSU0_STATUS_PRSNT_BIT = 0b01000000
    CPLD_PSU0_STATUS_POWER_BIT = 0b00010000
        
    CPLD_PSU1_STATUS_PRSNT_BIT = 0b10000000
    CPLD_PSU1_STATUS_POWER_BIT = 0b00100000

    CPLD_BMC_PRNST_BIT = 0b00000001
    
    CPLD_CS4227_RESET_BIT = 0b00010000
    CPLD_GBX_RESET_BIT = 0b00100000
    CPLD_J2_RESET_BIT = 0b01000000    
    CPLD_RETIMER_RESET_BIT = 0b00000001
    
    ATTR_CPLD_VERSION = "cpld_version"
    ATTR_CPLD_ID = "cpld_id"
    ATTR_CPLD_BOARD_TYPE = "cpld_board_type"
    ATTR_CPLD_EXT_BOARD_TYPE = "cpld_ext_board_type"
    ATTR_CPLD_INT = "cpld_interrupt"
    ATTR_CPLD_QSFPDD_PORT_STATUS = "cpld_qsfpdd_port_status"
    ATTR_CPLD_QSFPDD_PORT_CONFIG = "cpld_qsfpdd_port_config"
    ATTR_CPLD_QSFP_PORT_STATUS = "cpld_qsfp_port_status"
    ATTR_CPLD_QSFP_PORT_CONFIG = "cpld_qsfp_port_config"
    ATTR_CPLD_SFP_PORT_STATUS = "cpld_sfp_port_status"
    ATTR_CPLD_SFP_PORT_CONFIG = "cpld_sfp_port_config"
    ATTR_CPLD_PSU_STATUS = "cpld_psu_status"
    ATTR_CPLD_SFP_LED = "cpld_sfp_led"
    ATTR_CPLD_QSFPDD_LED = "cpld_qsfpdd_led"
    ATTR_CPLD_SYSTEM_LED = "cpld_system_led"
    ATTR_CPLD_BMC_PRSNT = "cpld_bmc_status"
    ATTR_CPLD_RESET_CTRL = "cpld_reset_control"
    ATTR_CPLD_RESET_MAC = "cpld_reset_mac"
    ATTR_CPLD_RESET_RETIMER = "cpld_reset_retimer"
    
    PATH_SYS_I2C_DEVICES = "/sys/bus/i2c/devices"      

    def __init__(self):
        log = Logger(__name__)
        self.logger = log.getLogger()        
        self.i2c = I2C()
        self.lpc = LPC()
        
        # init i2c devices for CPLD
        self.i2c_dev = []
        for i in range(CPLDConst.CPLD_MAX):
            self.i2c_dev.append(I2C_Dev(self.CPLD_I2C_BUS, self.CPLD_I2C_ADDR[i]))                    

    def init(self):        
        try:
            for cpld_index in range(CPLDConst.CPLD_MAX):
                 
                sysfs_path = "{0}/{1}-{2}".format(
                    self.PATH_SYS_I2C_DEVICES,
                    self.CPLD_I2C_BUS,
                    "{:04x}".format(self.i2c_dev[cpld_index].addr))
                 
                sysfs_new_dev_path = "{0}/i2c-{1}/new_device".format(
                    self.PATH_SYS_I2C_DEVICES,
                    self.i2c_dev[cpld_index].bus)
                 
                if not os.path.exists(sysfs_path):
                    with open(sysfs_new_dev_path, "w") as f:
                        f.write("apollo_cpld{0} {1}".format(cpld_index + 1, self.i2c_dev[cpld_index].addr))
                else:
                    self.logger.error("sysfs_path already exist: {0}".format(sysfs_path))
                    return 0
        except IOError as e:
            self.logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))        
        except:
            self.logger.error("Unexpected error:", sys.exc_info()[0])
            raise

    def deinit(self):
        try:
            for cpld_index in range(CPLDConst.CPLD_MAX):
                 
                sysfs_path = "{0}/{1}-{2}".format(
                    self.PATH_SYS_I2C_DEVICES,
                    self.CPLD_I2C_BUS,
                    "{:04x}".format(self.i2c_dev[cpld_index].addr))
                 
                sysfs_del_dev_path = "{0}/i2c-{1}/delete_device".format(
                    self.PATH_SYS_I2C_DEVICES,
                    self.i2c_dev[cpld_index].bus)
                 
                if os.path.exists(sysfs_path):
                    with open(sysfs_del_dev_path, "w") as f:
                        f.write("{0}".format(self.i2c_dev[cpld_index].addr))
                else:
                    self.logger.error("sysfs_path does not exist: {0}".format(sysfs_path))
                    return 0
        except IOError as e:
            self.logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))        
        except:
            self.logger.error("Unexpected error:", sys.exc_info()[0])
            raise

    def _get_sysfs_path(self, cpld_index, cpld_attr, cpld_port_index=-1):
        sysfs_path = "{0}/{1}-{2}/{3}".format(
            self.PATH_SYS_I2C_DEVICES,
            self.CPLD_I2C_BUS,
            "{:04x}".format(self.i2c_dev[cpld_index].addr),
            cpld_attr)
        
        if cpld_port_index != -1:
            sysfs_path = sysfs_path + "_" + str(cpld_port_index)
        
        return sysfs_path
        
    def _read_sysfs(self, sysfs_path, data_type=DataType.INT):    
        
        reg_val = 0
        
        try:
            if os.path.exists(sysfs_path):
                with open(sysfs_path, "r") as f:
                    # read content
                    content = f.read()
                    
                    # convert data type
                    if data_type == DataType.INT:
                        reg_val = int(content.strip(), 0)
            else:
                raise IOError("sysfs_path does not exist: {0}".format(sysfs_path))                        
        except Exception as e:
            self.logger.error(e)
            raise
                                    
        return reg_val
    
    def _write_sysfs(self, sysfs_path, reg_val):    
                        
        try:
            if os.path.exists(sysfs_path):
                with open(sysfs_path, "w") as f:
                    f.write(str(reg_val))
            else:
                raise IOError("sysfs_path does not exist: {0}".format(sysfs_path))
        except Exception as e:
            self.logger.error(e)
            raise
    
    # read cpld reg from sysfs
    def _read_cpld_reg(self, cpld_index, cpld_attr, cpld_port_index=-1):
        sysfs_path = self._get_sysfs_path(cpld_index, cpld_attr, cpld_port_index)        
        reg_val = self._read_sysfs(sysfs_path)                
        
        return reg_val
    
    # write cpld reg via sysfs
    def _write_cpld_reg(self, cpld_index, cpld_attr, reg_val, cpld_port_index=-1):
        sysfs_path = self._get_sysfs_path(cpld_index, cpld_attr, cpld_port_index)
        self._write_sysfs(sysfs_path, reg_val)    
    
    # get bit shift from mask
    def _get_shift(self, reg_mask):
        mask_one = 1
        
        for i in range(8):
            if reg_mask & mask_one == 1:
                return i
            else:
                reg_mask >>= 1
        
        # not found
        return -1
                        
    ########## FOR CPLD UTILITY ##########
    def get_board_info(self):     
        cpld_index = CPLDConst.CPLD_1
                   
        try:
            # read board_id reg
            cpld_attr = self.ATTR_CPLD_BOARD_TYPE
            brd_reg_val = self._read_cpld_reg(cpld_index, cpld_attr)
            
            board_id = (brd_reg_val & self.CPLD_MODEL_ID_BIT) >> self._get_shift(self.CPLD_MODEL_ID_BIT)
            hw_rev = (brd_reg_val & self.CPLD_HW_REV_BIT) >> self._get_shift(self.CPLD_HW_REV_BIT)
            build_rev = (brd_reg_val & self.CPLD_BUILD_REV_BIT) >> self._get_shift(self.CPLD_BUILD_REV_BIT)
            
            # read ext_board_id reg
            cpld_attr = self.ATTR_CPLD_EXT_BOARD_TYPE
            ext_brd_reg_val = self._read_cpld_reg(cpld_index, cpld_attr)
            
            ext_board_id = (ext_brd_reg_val & self.CPLD_MODEL_ID_BIT) >> self._get_shift(self.CPLD_MODEL_ID_BIT)                       
            
            # board_id and board_id_str
            if board_id == self.EXT_BOARD_ID:
                if int(ext_board_id) in self.EXT_BOARD_ID_MAP.keys():
                    board_id_str = self.EXT_BOARD_ID_MAP[int(ext_board_id)]                    
                else:
                    board_id_str = "unknown"    
                board_id = ext_board_id
            else:
                if int(board_id) in self.BOARD_ID_MAP.keys():
                    board_id_str = self.BOARD_ID_MAP[int(board_id)]
                else:
                    board_id_str = "unknown"            
             
            # hw_rev and hw_rev_str   
            if hw_rev in self.HARDWARE_REV_MAP.keys():
                hw_rev_str = self.HARDWARE_REV_MAP[hw_rev]
            else:
                hw_rev_str = "unknown" 
            
            # build_rev and 
            if build_rev in self.BUILD_REV_MAP.keys():
                build_rev_str = self.BUILD_REV_MAP[build_rev]
            else:
                build_rev_str = "unknown"
                            
            return {"board_id": board_id,
                    "board_id_str": board_id_str,
                    "hw_rev": hw_rev,
                    "hw_rev_str": hw_rev_str,
                    "build_rev": build_rev,
                    "build_rev_str": build_rev_str} 
        except Exception as e:
            self.logger.error(e)
            raise

    def get_cpu_board_cpld_version(self):        
        try:
            reg_val = self.lpc.regGet(LPCDevType.CPLD_ON_CPU_BOARD,
                                       CPLDCPUReg.REG_CPLD_REVISION)
            return reg_val
        except Exception as e:
            self.logger.error(e)
            raise        
    
    def get_main_board_cpld_version(self):        
        cpld_index = CPLDConst.CPLD_1
        cpld_attr = self.ATTR_CPLD_VERSION
        reg_vals = []
        
        for cpld_index in range(CPLDConst.CPLD_MAX):            
            reg_val = self._read_cpld_reg(cpld_index, cpld_attr)
            reg_vals.append(reg_val)                           
        
        return reg_vals
    
    def get_main_board_cpld_id(self):        
        cpld_index = CPLDConst.CPLD_1
        cpld_attr = self.ATTR_CPLD_ID
        reg_vals = []
        
        for cpld_index in range(CPLDConst.CPLD_MAX):                          
            reg_val = self._read_cpld_reg(cpld_index, cpld_attr)
            reg_vals.append(reg_val)              
        
        return reg_vals
    
    def get_port_interrupt(self, cpld_index):
        cpld_attr = self.ATTR_CPLD_INT
        reg_mask = self.CPLD_PORT_INT_BIT        
        
        reg_val = self._read_cpld_reg(cpld_index, cpld_attr)        
        interrupt = (reg_val & reg_mask) >> self._get_shift(reg_mask)              
        
        return interrupt
    
    ########## FOR SFP+ ##########    
    def sfp_get_presence(self, port_num):
        cpld_index = CPLDConst.CPLD_1     
        cpld_attr = self.ATTR_CPLD_SFP_PORT_STATUS        
        mask = 0        
                
        reg_val = self._read_cpld_reg(cpld_index, cpld_attr)
        
        if port_num == 0:
            mask = self.CPLD_SFP0_STATUS_PRSNT_BIT
        else:
            mask = self.CPLD_SFP1_STATUS_PRSNT_BIT        
        
        presence = (reg_val & mask) >> self._get_shift(mask)              
        
        return presence
    
    def sfp_get_tx_fault(self, port_num):
        cpld_index = CPLDConst.CPLD_1     
        cpld_attr = self.ATTR_CPLD_SFP_PORT_STATUS          
        mask = 0        
        
        reg_val = self._read_cpld_reg(cpld_index, cpld_attr)
        
        if port_num == 0:
            mask = self.CPLD_SFP0_STATUS_TX_FAULT_BIT            
        else:
            mask = self.CPLD_SFP1_STATUS_TX_FAULT_BIT        
        
        tx_fault = (reg_val & mask) >> self._get_shift(mask)   
        
        return tx_fault
    
    def sfp_get_tx_disable(self, port_num):
        cpld_index = CPLDConst.CPLD_1               
        cpld_attr = self.ATTR_CPLD_SFP_PORT_CONFIG          
        mask = 0        
        
        reg_val = self._read_cpld_reg(cpld_index, cpld_attr)
        
        if port_num == 0:
            mask = self.CPLD_SFP0_CONFIG_TX_DIS_BIT
        else:
            mask = self.CPLD_SFP1_CONFIG_TX_DIS_BIT        
        
        tx_disable = (reg_val & mask) >> self._get_shift(mask) 
        
        return tx_disable
    
    def sfp_set_tx_disable(self, port_num, tx_disable):
        cpld_index = CPLDConst.CPLD_1               
        cpld_attr = self.ATTR_CPLD_SFP_PORT_CONFIG          
        mask = 0        
        
        reg_val = self._read_cpld_reg(cpld_index, cpld_attr)
        
        if port_num == 0:
            mask = self.CPLD_SFP0_CONFIG_TX_DIS_BIT            
        else:
            mask = self.CPLD_SFP1_CONFIG_TX_DIS_BIT            
                
        if tx_disable == SFP.DISABLED:
            reg_val |= mask
        else:
            reg_val &= ~mask
        
        self._write_cpld_reg(cpld_index, cpld_attr, reg_val)
    
    def sfp_get_rx_los(self, port_num):
        cpld_index = CPLDConst.CPLD_1     
        cpld_attr = self.ATTR_CPLD_SFP_PORT_STATUS          
        mask = 0
                
        reg_val = self._read_cpld_reg(cpld_index, cpld_attr)
        
        if port_num == 0:
            mask = self.CPLD_SFP0_STATUS_RX_LOS_BIT            
        else:
            mask = self.CPLD_SFP1_STATUS_RX_LOS_BIT 
        
        rx_los = (reg_val & mask) >> self._get_shift(mask)                
        
        return rx_los    
            
    ########## FOR QSFP ##########
    def _qsfp_port_fp2phy(self, fp_port):
        
        if 0 <= fp_port <= 19:
            phy_port = fp_port                    
        else:
            if fp_port % 2 == 0:
                phy_port = fp_port + 1
            else:
                phy_port = fp_port - 1    
        
        return phy_port
    
    def _qsfp_cpld_var_set(self, phy_port):                
        if 0 <= phy_port <= 11:
            cpld_index = CPLDConst.CPLD_1
            reg_port_base = 0   
        elif 12 <= phy_port <= 24:
            cpld_index = CPLDConst.CPLD_2   
            reg_port_base = 12     
        elif 25 <= phy_port <= 37:
            cpld_index = CPLDConst.CPLD_3
            reg_port_base = 25
        elif 38 <= phy_port <= 39:
            cpld_index = CPLDConst.CPLD_4   
            reg_port_base = 38        
        else:
            self.logger.error("invalid port number")
            
        cpld_var = {"cpld_index": cpld_index, "cpld_port_index": phy_port - reg_port_base}
        
        return cpld_var    
    
    def _read_qsfp_reg(self, port_num, cpld_attr, reg_mask, reg_shift):
        phy_port = self._qsfp_port_fp2phy(port_num)
        cpld_var = self._qsfp_cpld_var_set(phy_port)               
                        
        reg_val = self._read_cpld_reg(cpld_var["cpld_index"],
                            cpld_attr,
                            cpld_var["cpld_port_index"])
        masked_val = (reg_val & reg_mask) >> reg_shift                
        
        return masked_val
    
    def _write_qsfp_reg(self, port_num, cpld_attr, reg_val):
        phy_port = self._qsfp_port_fp2phy(port_num)
        cpld_var = self._qsfp_cpld_var_set(phy_port)               
                        
        self._write_cpld_reg(cpld_var["cpld_index"],
                            cpld_attr,
                            reg_val,
                            cpld_var["cpld_port_index"])
            
    def qsfp_get_presence(self, port_num):
        cpld_attr = self.ATTR_CPLD_QSFP_PORT_STATUS
        reg_mask = self.CPLD_QSFP_STATUS_ABS_BIT
        reg_shift = self._get_shift(reg_mask)
        
        presence = self._read_qsfp_reg(port_num, cpld_attr, reg_mask, reg_shift) 
        
        return presence
    
    def qsfp_get_interrupt(self, port_num):
        cpld_attr = self.ATTR_CPLD_QSFP_PORT_STATUS
        reg_mask = self.CPLD_QSFP_STATUS_INT_BIT
        reg_shift = self._get_shift(reg_mask)
        
        interrupt = self._read_qsfp_reg(port_num, cpld_attr, reg_mask, reg_shift) 
        
        return interrupt
    
    def qsfp_get_lp_mode(self, port_num):        
        cpld_attr = self.ATTR_CPLD_QSFP_PORT_CONFIG
        reg_mask = self.CPLD_QSFP_CONFIG_LP_BIT
        reg_shift = self._get_shift(reg_mask)
        
        lp_mode = self._read_qsfp_reg(port_num, cpld_attr, reg_mask, reg_shift)
                        
        return lp_mode
    
    def qsfp_set_lp_mode(self, port_num, lp_mode):  
        cpld_attr = self.ATTR_CPLD_QSFP_PORT_CONFIG
        reg_mask = 0xFF
        reg_shift = self._get_shift(reg_mask)
        
        reg_val = self._read_qsfp_reg(port_num, cpld_attr, reg_mask, reg_shift)

        if lp_mode == LPMode.ENABLE:
            reg_val |= self.CPLD_QSFP_CONFIG_LP_BIT
        else:          
            reg_val &= ~self.CPLD_QSFP_CONFIG_LP_BIT        
        
        self._write_qsfp_reg(port_num, cpld_attr, reg_val)
    
    def qsfp_get_reset(self, port_num):
        cpld_attr = self.ATTR_CPLD_QSFP_PORT_CONFIG
        reg_mask = self.CPLD_QSFP_CONFIG_RST_BIT
        reg_shift = self._get_shift(reg_mask)
        
        reset = self._read_qsfp_reg(port_num, cpld_attr, reg_mask, reg_shift)
        
        return reset
    
    def qsfp_set_reset(self, port_num, reset):
        cpld_attr = self.ATTR_CPLD_QSFP_PORT_CONFIG
        reg_mask = 0xFF
        reg_shift = self._get_shift(reg_mask)
        
        reg_val = self._read_qsfp_reg(port_num, cpld_attr, reg_mask, reg_shift)

        # high -> low, trigger reset
        if reset == PortStatus.RESET:
            reg_val &= ~self.CPLD_QSFP_CONFIG_RST_BIT
        else:
            reg_val |= self.CPLD_QSFP_CONFIG_RST_BIT
            
        self._write_qsfp_reg(port_num, cpld_attr, reg_val)
        
    def qsfp_reset_port(self, port_num):  
        cpld_attr = self.ATTR_CPLD_QSFP_PORT_CONFIG
        reg_mask = 0xFF
        reg_shift = self._get_shift(reg_mask)
        
        reg_val = self._read_qsfp_reg(port_num, cpld_attr, reg_mask, reg_shift)

        # high -> low, trigger reset
        reg_val &= ~self.CPLD_QSFP_CONFIG_RST_BIT        
        self._write_qsfp_reg(port_num, cpld_attr, reg_val)
        
        # By sff-8436, the execution of a reset is max 2000ms
        sleep(2)  
        
        # low -> high, release reset
        reg_val |= self.CPLD_QSFP_CONFIG_RST_BIT
        self._write_qsfp_reg(port_num, cpld_attr, reg_val)
        
    ########## FOR QSFPDD ##########
    def _qsfpdd_port_fp2phy(self, fp_port):
        phy_port = fp_port
                
        return phy_port
    
    def _qsfpdd_cpld_var_set(self, phy_port):        
        if 0 <= phy_port <= 2:
            cpld_index = CPLDConst.CPLD_4
            reg_port_base = 0   
        elif 3 <= phy_port <= 12:
            cpld_index = CPLDConst.CPLD_5   
            reg_port_base = 3        
        else:
            self.logger.error("invalid port number")
            
        cpld_var = {"cpld_index": cpld_index, "cpld_port_index": phy_port - reg_port_base}
        
        return cpld_var     
    
    def _read_qsfpdd_reg(self, port_num, cpld_attr, reg_mask, reg_shift):
        phy_port = self._qsfpdd_port_fp2phy(port_num)
        cpld_var = self._qsfpdd_cpld_var_set(phy_port)               
                        
        reg_val = self._read_cpld_reg(cpld_var["cpld_index"],
                            cpld_attr,
                            cpld_var["cpld_port_index"])
        masked_val = (reg_val & reg_mask) >> reg_shift                
        
        return masked_val
    
    def _write_qsfpdd_reg(self, port_num, cpld_attr, reg_val):
        phy_port = self._qsfpdd_port_fp2phy(port_num)
        cpld_var = self._qsfpdd_cpld_var_set(phy_port)               
                        
        self._write_cpld_reg(cpld_var["cpld_index"],
                            cpld_attr,
                            reg_val,
                            cpld_var["cpld_port_index"])
        
    def qsfpdd_get_presence(self, port_num):
        cpld_attr = self.ATTR_CPLD_QSFPDD_PORT_STATUS
        reg_mask = self.CPLD_QSFPDD_STATUS_ABS_BIT
        reg_shift = self._get_shift(reg_mask)
        
        presence = self._read_qsfpdd_reg(port_num, cpld_attr, reg_mask, reg_shift)
                
        return presence
    
    def qsfpdd_get_interrupt(self, port_num):
        cpld_attr = self.ATTR_CPLD_QSFPDD_PORT_STATUS
        reg_mask = self.CPLD_QSFPDD_STATUS_INT_BIT
        reg_shift = self._get_shift(reg_mask)
        
        interrupt = self._read_qsfpdd_reg(port_num, cpld_attr, reg_mask, reg_shift)
                
        return interrupt
    
    def qsfpdd_get_lp_mode(self, port_num):
        cpld_attr = self.ATTR_CPLD_QSFPDD_PORT_CONFIG
        reg_mask = self.CPLD_QSFPDD_CONFIG_LP_BIT
        reg_shift = self._get_shift(reg_mask)
        
        lp_mode = self._read_qsfpdd_reg(port_num, cpld_attr, reg_mask, reg_shift)               
                
        return lp_mode
    
    def qsfpdd_set_lp_mode(self, port_num, lp_mode):        
        cpld_attr = self.ATTR_CPLD_QSFPDD_PORT_CONFIG
        reg_mask = 0xFF
        reg_shift = self._get_shift(reg_mask)
        
        reg_val = self._read_qsfpdd_reg(port_num, cpld_attr, reg_mask, reg_shift)

        if lp_mode == LPMode.ENABLE:
            reg_val |= self.CPLD_QSFPDD_CONFIG_LP_BIT
        else:          
            reg_val &= ~self.CPLD_QSFPDD_CONFIG_LP_BIT        
        
        self._write_qsfpdd_reg(port_num, cpld_attr, reg_val)
    
    def qsfpdd_get_reset(self, port_num):
        cpld_attr = self.ATTR_CPLD_QSFPDD_PORT_CONFIG
        reg_mask = self.CPLD_QSFPDD_CONFIG_RST_BIT
        reg_shift = self._get_shift(reg_mask)
        
        reset = self._read_qsfpdd_reg(port_num, cpld_attr, reg_mask, reg_shift)               
                
        return reset
    
    def qsfpdd_set_reset(self, port_num, reset):
        cpld_attr = self.ATTR_CPLD_QSFPDD_PORT_CONFIG
        reg_mask = 0xFF
        reg_shift = self._get_shift(reg_mask)
        
        reg_val = self._read_qsfpdd_reg(port_num, cpld_attr, reg_mask, reg_shift)

        # high -> low, trigger reset
        if reset == PortStatus.RESET:
            reg_val &= ~self.CPLD_QSFPDD_CONFIG_RST_BIT
        else:
            reg_val |= self.CPLD_QSFPDD_CONFIG_RST_BIT
            
        self._write_qsfpdd_reg(port_num, cpld_attr, reg_val)
        
    def qsfpdd_reset_port(self, port_num):
        cpld_attr = self.ATTR_CPLD_QSFPDD_PORT_CONFIG
        reg_mask = 0xFF
        reg_shift = self._get_shift(reg_mask)
        
        reg_val = self._read_qsfpdd_reg(port_num, cpld_attr, reg_mask, reg_shift)

        # high -> low, trigger reset
        reg_val &= ~self.CPLD_QSFPDD_CONFIG_RST_BIT        
        self._write_qsfpdd_reg(port_num, cpld_attr, reg_val)
        
        # By sff-8436, the execution of a reset is max 2000ms
        sleep(2)  
        
        # low -> high, release reset
        reg_val |= self.CPLD_QSFPDD_CONFIG_RST_BIT
        self._write_qsfpdd_reg(port_num, cpld_attr, reg_val)
    
    ########## FOR PSU ##########    
    def get_psu_presence(self, psu_num):        
        cpld_index = CPLDConst.CPLD_1
        cpld_attr = self.ATTR_CPLD_PSU_STATUS
         
        reg_val = self._read_cpld_reg(cpld_index, cpld_attr, psu_num)
         
        if psu_num == PSU.PSU0:
            mask = self.CPLD_PSU0_STATUS_PRSNT_BIT
        else:
            mask = self.CPLD_PSU1_STATUS_PRSNT_BIT         
        
        presence = (reg_val & mask) >> self._get_shift(mask)        
         
        return presence    
        
    def get_psu_power_ok(self, psu_num):        
        cpld_index = CPLDConst.CPLD_1
        cpld_attr = self.ATTR_CPLD_PSU_STATUS        
        
        reg_val = self._read_cpld_reg(cpld_index, cpld_attr, psu_num)
        
        if psu_num == PSU.PSU0:
            mask = self.CPLD_PSU0_STATUS_POWER_BIT
        else:
            mask = self.CPLD_PSU1_STATUS_POWER_BIT
        
        power_ok = (reg_val & mask) >> self._get_shift(mask)
        
        return power_ok    
        
    ########## FOR QSFPDD LED ##########
    def set_qsfpdd_led(self, port, color, blink):
        cpld_attr = self.ATTR_CPLD_QSFPDD_LED       
        cpld_index = CPLDConst.CPLD_5
        mask = 0
        reg_shift = 0
        
        if color == Led.COLOR_OFF and blink == Led.BLINK_STATUS_BLINKING:
            raise ValueError("LED blinking off is invalid operation")
        
        reg_val = self._read_cpld_reg(cpld_index, cpld_attr, port)
        
        if port % 2 == 0:
            reg_shift = 0
            mask = 0b11111000
        else:
            reg_shift = 4
            mask = 0b10001111
        
        # clear color
        reg_val &= mask
        
        # set color  
        if color == Led.COLOR_GREEN:            
            reg_val |= (QSFPDD.LED_MASK_GREEN << reg_shift)
        elif color == Led.COLOR_RED:
            reg_val |= (QSFPDD.LED_MASK_RED << reg_shift)
        elif color == Led.COLOR_BLUE:
            reg_val |= (QSFPDD.LED_MASK_BLUE << reg_shift)    
        elif color == Led.COLOR_OFF:
            pass
        else:
            raise ValueError("LED color is out of range")
        
        # set blink  
        if blink == Led.BLINK_STATUS_BLINKING:                        
            reg_val |= (QSFPDD.LED_MASK_BLINK << reg_shift)        
        else:
            reg_val &= ~(QSFPDD.LED_MASK_BLINK << reg_shift)
                
        self._write_cpld_reg(cpld_index, cpld_attr, reg_val, port)
            
    def get_qsfpdd_led(self, port):        
        cpld_attr = self.ATTR_CPLD_QSFPDD_LED       
        cpld_index = CPLDConst.CPLD_5
        mask = 0 
        color = 0
        blink = 0
            
        reg_val = self._read_cpld_reg(cpld_index, cpld_attr, port)
        
        if port % 2 == 0:                        
            mask = 0x0F
        else:            
            mask = 0xF0 
        
        # put data in lower lower 4 bits regardless of port  
        reg_val = (reg_val & mask) >> self._get_shift(mask)
                
        # get color  
        if reg_val & QSFPDD.LED_MASK_GREEN == QSFPDD.LED_MASK_GREEN:            
            color = Led.COLOR_GREEN
        elif reg_val & QSFPDD.LED_MASK_RED == QSFPDD.LED_MASK_RED:
            color = Led.COLOR_RED
        elif reg_val & QSFPDD.LED_MASK_BLUE == QSFPDD.LED_MASK_BLUE:
            color = Led.COLOR_BLUE    
        else:
            color = Led.COLOR_OFF
        
        # get blink
        if reg_val & QSFPDD.LED_MASK_BLINK == QSFPDD.LED_MASK_BLINK:
            blink = Led.BLINK_STATUS_BLINKING         
        else:
            blink = Led.BLINK_STATUS_SOLID
                
        return (color, blink)    
    
    ########## FOR BMC ##########
    def get_bmc_presence(self):        
        cpld_index = CPLDConst.CPLD_1
        cpld_attr = self.ATTR_CPLD_BMC_PRSNT
                    
        reg_val = self._read_cpld_reg(cpld_index, cpld_attr)
        
        presence = (reg_val & self.CPLD_BMC_PRNST_BIT)
        
        return presence

    def reset_dev(self, devType):
        cpld_index = CPLDConst.CPLD_1;     
        
        if devType == DevType.J2:
            cpld_attr = self.ATTR_CPLD_RESET_MAC           
            mask = self.CPLD_J2_RESET_BIT
        elif devType == DevType.GEARBOX:
            cpld_attr = self.ATTR_CPLD_RESET_MAC
            mask = self.CPLD_GBX_RESET_BIT
        elif devType == DevType.RETIMER:
            cpld_attr = self.ATTR_CPLD_RESET_RETIMER
            mask = self.CPLD_RETIMER_RESET_BIT
        elif devType == DevType.CS4227:
            cpld_attr = self.ATTR_CPLD_RESET_MAC
            mask = self.CPLD_CS4227_RESET_BIT                   
        else:
            return
        
        board_info = self.get_board_info()
        
        # proto
        if board_info["hw_rev"] == 0:
            if devType == DevType.J2:
                try:
                    # reset J2
                    reg_val = self.lpc.regSet(LPCDevType.CPLD_ON_CPU_BOARD,
                                               CPLDCPUReg.REG_RESET_CTRL,
                                               0xF0)
                    sleep(0.1)
                    # unset J2
                    reg_val = self.lpc.regSet(LPCDevType.CPLD_ON_CPU_BOARD,
                                               CPLDCPUReg.REG_RESET_CTRL,
                                               0xF1)
                    return reg_val
                except Exception as e:
                    self.logger.error(e)
                    raise        
            else:
                pass
        else:  # alpha and later               
            reg_val = self._read_cpld_reg(cpld_index, cpld_attr)
                            
            # pull low the bit
            reg_val &= ~mask
                             
            self._write_cpld_reg(cpld_index,
                                cpld_attr,
                                reg_val)
            
    ########## FOR System LED ##########
    def set_sys_led(self, target, color, blink):
        cpld_attr = self.ATTR_CPLD_SYSTEM_LED       
        cpld_index = CPLDConst.CPLD_1
        reg_index = 0
        attr_index = 0
        mask = 0
        reg_shift = 0
        
        if target == Led.SYSTEM:
            attr_index = 0
            reg_index = 1            
        elif target == Led.FAN:
            attr_index = 0
            reg_index = 0
        else:
            attr_index = 1
            reg_index = target
        
        if color == Led.COLOR_OFF and blink == Led.BLINK_STATUS_BLINKING:
            raise ValueError("LED blinking off is invalid operation")
        
        reg_val = self._read_cpld_reg(cpld_index, cpld_attr, attr_index)
        
        if reg_index % 2 == 0:
            reg_shift = 0
            mask = 0b11110000
        else:
            reg_shift = 4
            mask = 0b00001111
        
        # clear color
        reg_val &= mask
        
        # set color  
        '''
        if color == Led.COLOR_GREEN:
            if target == Led.SYSTEM:
                reg_val &= ~(Led.MASK_COLOR << reg_shift)
            else:
                reg_val |= (Led.MASK_COLOR << reg_shift)
            reg_val |= (Led.MASK_ONOFF << reg_shift)
        elif color == Led.COLOR_YELLOW:
            if target == Led.SYSTEM:
                reg_val |= (Led.MASK_COLOR << reg_shift)
            else:
                reg_val &= ~(Led.MASK_COLOR << reg_shift)
            reg_val |= (Led.MASK_ONOFF << reg_shift)
        '''    
        if color == Led.COLOR_GREEN:
            reg_val |= (Led.MASK_COLOR << reg_shift)
            reg_val |= (Led.MASK_ONOFF << reg_shift)
        elif color == Led.COLOR_YELLOW:
            reg_val &= ~(Led.MASK_COLOR << reg_shift)
            reg_val |= (Led.MASK_ONOFF << reg_shift)
        elif color == Led.COLOR_OFF:
            reg_val &= ~(Led.MASK_ONOFF << reg_shift)
        else:
            raise ValueError("LED color is out of range")
        
        # set blink  
        if blink == Led.BLINK_STATUS_BLINKING:                        
            reg_val |= (Led.MASK_BLINK << reg_shift)        
        else:
            reg_val &= ~(Led.MASK_BLINK << reg_shift)
                        
        self._write_cpld_reg(cpld_index, cpld_attr, reg_val, attr_index)
