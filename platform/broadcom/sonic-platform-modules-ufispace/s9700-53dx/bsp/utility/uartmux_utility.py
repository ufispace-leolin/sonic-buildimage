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

from bsp.common.logger import Logger
from bsp.gpio.ioexp import IOExpander
from bsp.ipmi.ipmitool import IPMITool
from bsp.const.const import UARTMux
from bsp.const.const import BID

class UARTMuxUtility:

    def __init__(self):
        log = Logger(__name__)
        self.logger = log.getLogger()
        self.ioexp = IOExpander()
        self.ipmitool = IPMITool()
        self.board_id = self.ioexp.preinit_get_board_id()
    
    def set_uart_mux(self, source):
        try:
            if source not in [UARTMux.CPU, UARTMux.BMC]:
                raise ValueError("invalid uart source {0}, range is 0-1".format(source))
            if self.board_id == BID.NCP1_1_PROTO:
                self.ioexp.set_uart_mux(source)
            else:
                self.ipmitool.set_uart_mux(source)
        except Exception as e:
            print("set_uart_mux {0} failed, error: {1}".format(source, e))
