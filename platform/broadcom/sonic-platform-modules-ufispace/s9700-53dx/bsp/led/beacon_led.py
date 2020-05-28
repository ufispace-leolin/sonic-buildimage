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
class BEACON_LED:        
    
    SEG7_L = [[1,1,1,1,0,1,1], #0
              [1,1,0,0,0,0,0], #1
              [0,1,1,1,1,0,1], #2
              [1,1,0,1,1,0,1], #3
              [1,1,0,0,1,1,0], #4
              [1,0,0,1,1,1,1], #5
              [1,0,1,1,1,1,1], #6
              [1,1,0,0,0,1,1], #7
              [1,1,1,1,1,1,1], #8
              [1,1,0,0,1,1,1], #9
              [1,1,1,0,1,1,1], #a
              [1,0,1,1,1,1,0], #b
              [0,0,1,1,0,1,1], #c
              [1,1,1,1,1,0,0], #d
              [0,0,1,1,1,1,1], #e
              [0,0,1,0,1,1,1]] #f
    SEG7_R = [[1,1,1,1,1,1,0], #0
              [0,0,1,0,0,1,0], #1
              [1,1,0,0,1,1,1], #2
              [1,0,1,0,1,1,1], #3                     
              [0,0,1,1,0,1,1], #4                     
              [1,0,1,1,1,0,1], #5
              [1,1,1,1,1,0,1], #6
              [1,0,1,1,0,1,0], #7
              [1,1,1,1,1,1,1], #8
              [1,0,1,1,0,1,1], #9
              [1,1,1,1,0,1,1], #a
              [0,1,1,1,1,0,1], #b
              [1,1,0,1,1,0,0], #c
              [0,1,1,0,1,1,1], #d
              [1,1,0,1,1,0,1], #e
              [1,1,0,1,0,0,1]] #f
                  
    def __init__(self):
        log = Logger(__name__)
        self.logger = log.getLogger()
        self.ioexp = IOExpander()        
                     
    def set_beacon_num(self, beacon_num):
        #int to hex string
        beacon_hex = '{:02x}'.format(beacon_num)
                
        try:
            #left/right 7-seg led
            seg7_left = self.SEG7_L[int(beacon_hex[0], 16)]            
            seg7_right = self.SEG7_R[int(beacon_hex[1], 16)]
            
            self.ioexp.set_beacon_led(seg7_left, seg7_right)
        except Exception as e:  
            self.logger.error(e)          
            raise       
    
    def init(self):
        pass

    def deinit(self):
        pass
