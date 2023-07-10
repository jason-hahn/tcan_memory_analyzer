# Author: Thomas Poms, 2023
#
# This program is free software: you can redistribute it and/or modify it under the terms of the 
# GNU General Public License as published by the Free Software Foundation, either version 3 of 
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. 
# If not, see <https://www.gnu.org/licenses/>.

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, ChoicesSetting, NumberSetting
from TcanRegisters import *

# states
STATE_START         = 0
STATE_CMD           = 1
STATE_ADDR_H        = 2
STATE_ADDR_M        = 3
STATE_ADDR_L        = 4
STATE_DATA          = 5
STATE_NO_DATA       = 6

STATE_TCAN_IDLE     = 0
STATE_TCAN_CMD      = 1
STATE_TCAN_REG1     = 2
STATE_TCAN_REG2     = 3
STATE_TCAN_WORDS    = 4
STATE_TCAN_DATA_READ    = 5
STATE_TCAN_DATA_WRITE   = 6

# supported commands
# if you add a new command here, ensure that you modify frame_config as well
SPI_MEMORY_CMD_READ_ARRAY                                  = b'\x03'             
SPI_MEMORY_CMD_PAGE_ERASE                                  = b'\x81'
SPI_MEMORY_CMD_BLOCK_ERASE_4K                              = b'\x20'
SPI_MEMORY_CMD_BLOCK_ERASE_32K                             = b'\x52'
SPI_MEMORY_CMD_BLOCK_ERASE_64K                             = b'\xD8'
SPI_MEMORY_CMD_CHIP_ERASE                                  = b'\xC7'
SPI_MEMORY_CMD_BYTE_PROGRAM                                = b'\x02'
SPI_MEMORY_CMD_WRITE_ENABLE                                = b'\x06'
SPI_MEMORY_CMD_WRITE_DISABLE                               = b'\x04'
SPI_MEMORY_CMD_READ_STATUS_REGISTER_1                      = b'\x05'
SPI_MEMORY_CMD_READ_STATUS_REGISTER_2                      = b'\x35'
SPI_MEMORY_CMD_READ_DEVICE_ID                              = b'\x9F'              
SPI_MEMORY_CMD_WRITE_STATUS_REGISTER                       = b'\x01'
SPI_MEMORY_CMD_WRITE_ENABLE_FOR_VOLATILE_STATUS_REGISTER   = b'\x50'

SPI_TCAN_WRITE                                              = b'\x61'
SPI_TCAN_READ                                               = b'\x41'

IDX_CMD_NAME            = 0
IDX_NEXT_STATE          = 1
IDX_LAST_STATE          = 2
IDX_FILTER              = 3
IDX_DATA_LINE           = 4

# possible frames:
# <CMD><ADDR><DATA>     --> STATE_CMD --> STATE_ADDR_H --> (STATE_ADDR_M) --> STATE_ADDR_L --> STATE_DATA
# <CMD>                 --> STATE_CMD --> STATE_NO_DATA
# <CMD><ADDR>           --> STATE_CMD --> STATE_ADDR_H --> (STATE_ADDR_M) --> STATE_ADDR_L --> --> STATE_NO_DATA
# <CMD><DATA>           --> STATE_CMD --> STATE_DATA

frame_config = {
    # cmd                                                        # readable name associated with the command    # next state            # last state            # filter name                                   # data line
    SPI_MEMORY_CMD_READ_ARRAY                                  : ["Read"                                        ,STATE_ADDR_H           ,STATE_DATA             ,'READ_ARRAY'                                   ,'miso'        ],
    SPI_MEMORY_CMD_PAGE_ERASE                                  : ["Page Erase"                                  ,STATE_ADDR_H           ,STATE_NO_DATA          ,'PAGE_ERASE'                                   ,''            ],
    SPI_MEMORY_CMD_BLOCK_ERASE_4K                              : ["Block Erase 4k"                              ,STATE_ADDR_H           ,STATE_NO_DATA          ,'ERASE_4K'                                     ,''            ],
    SPI_MEMORY_CMD_BLOCK_ERASE_32K                             : ["Block Erase 32k"                             ,STATE_ADDR_H           ,STATE_NO_DATA          ,'ERASE_32K'                                    ,''            ],
    SPI_MEMORY_CMD_BLOCK_ERASE_64K                             : ["Block Erase 64k"                             ,STATE_ADDR_H           ,STATE_NO_DATA          ,'ERASE_64K'                                    ,''            ],
    SPI_MEMORY_CMD_CHIP_ERASE                                  : ["Chip Erase"                                  ,STATE_NO_DATA          ,STATE_NO_DATA          ,'CHIP_ERASE'                                   ,''            ],
    SPI_MEMORY_CMD_BYTE_PROGRAM                                : ["Write"                                       ,STATE_ADDR_H           ,STATE_DATA             ,'BYTE_PROGRAM'                                 ,'mosi'        ],
    SPI_MEMORY_CMD_WRITE_ENABLE                                : ["Write Enable"                                ,STATE_NO_DATA          ,STATE_NO_DATA          ,'WRITE_ENABLE'                                 ,''            ],
    SPI_MEMORY_CMD_WRITE_DISABLE                               : ["Write Disable"                               ,STATE_NO_DATA          ,STATE_NO_DATA          ,'WRITE_DISABLE'                                ,''            ],
    SPI_MEMORY_CMD_READ_STATUS_REGISTER_1                      : ["Read Status Reg 1"                           ,STATE_DATA             ,STATE_NO_DATA          ,'READ_STATUS_REGISTER_1'                       ,'miso'        ],
    SPI_MEMORY_CMD_READ_STATUS_REGISTER_2                      : ["Read Status Reg 2"                           ,STATE_DATA             ,STATE_NO_DATA          ,'READ_STATUS_REGISTER_2'                       ,'miso'        ],
    SPI_MEMORY_CMD_READ_DEVICE_ID                              : ["Read Device ID"                              ,STATE_DATA             ,STATE_NO_DATA          ,'READ_DEVICE_ID'                               ,'miso'        ],
    SPI_MEMORY_CMD_WRITE_STATUS_REGISTER                       : ["Write Status Reg"                            ,STATE_DATA             ,STATE_NO_DATA          ,'WRITE_STATUS_REGISTER'                        ,'mosi'        ],
    SPI_MEMORY_CMD_WRITE_ENABLE_FOR_VOLATILE_STATUS_REGISTER   : ["Write Enable Volatile Status Reg"            ,STATE_NO_DATA          ,STATE_NO_DATA          ,'WRITE_ENABLE_FOR_VOLATILE_STATUS_REGISTER'    ,''            ],
}


# High level analyzers must subclass the HighLevelAnalyzer class.
class HLA_SPI_MEMORY(HighLevelAnalyzer):
  
    filter_strings = ["no filter"]
    for i in frame_config:
        filter_strings.append(frame_config[i][IDX_FILTER])
    filter_strings.append('Timing_Violations')
  
    address_size = ChoicesSetting(label='Address size [bytes]', choices=('3', '2'))
    filter_setting = ChoicesSetting(label='Filter settings', choices=(
                        filter_strings
                    ))
    highlight_cmd_only = ChoicesSetting(label='Mark command only', choices=('no', 'yes'))
    timeCsToFirstByte = NumberSetting(label='CS to first byte (tCSA_B) [ns]', min_value=0, max_value=10000000)    
    timelastByteToCs = NumberSetting(label='Last byte to CS (tB_CSIA) [ns]', min_value=0, max_value=10000000)    
    timeByteToByte = NumberSetting(label='Byte to byte (tB_B) [ns]', min_value=0, max_value=10000000)
    state = STATE_TCAN_CMD
    data = []
    dataString = ''
    dataCount = 0
    frameStartTime = 0
    frameEndTime = 0
    regString = ''
    regName = ''
    prevRegName = ''
    cmdString = ''
    id = ''
    firstDataFlag = 0
  
    result_types = {
        'Command': {'format': 'cmd: {{data.command}}'},
        'Address': {'format':  'addr: {{data.address}} ({{data.addressHex}})'},
        'Data': {'format': 'data:  {{data.data}}'},
        'TimingViolation': {'format': 'violation:  {{data.delta_ns}} > {{data.maxTiming}}'},
    }

    bytecounter = 0

    def __init__(self):
        print("### Settings ###")
        print('    address size: ', self.address_size)
        print('    filter: ', self.filter_setting)
        print('    mark command only: ', self.highlight_cmd_only)
        print('    cs to byte [ns]: ', int(self.timeCsToFirstByte))
        print('    byte to byte: ', int(self.timeByteToByte))
        print('    byte to cs: ', int(self.timelastByteToCs))
        state = STATE_TCAN_CMD

    def cmd_to_str(self, command):
        try:
            return frame_config[command][IDX_CMD_NAME]
        except:
          return 'Unknown'     
      
    def get_next_state(self, command):
        try:
            return frame_config[command][IDX_NEXT_STATE]
        except:
          return STATE_NO_DATA       
               
    def get_last_state(self, command):
        try:
            return frame_config[command][IDX_LAST_STATE]
        except:
          return STATE_NO_DATA  
          
    def calc_delta(self, timestampStart, timeStampEnd):
        if timestampStart == 0:
            return 0
        delta = timeStampEnd - timestampStart
        return (delta.__float__() * 1e09)
    
    def show_cmd(self, filter_name, command):
        if filter_name == 'no filter':
            return 1
        elif filter_name == 'Timing_Violations':
            return 0
        elif filter_name == frame_config[command][IDX_FILTER]:
            return 1
        else:
            return 2

    def indicate_violation(self, maxTiming, delta, framestart, frameend, start_time, end_time):
        self.last_end_time_byte = end_time
        self.last_start_time_byte = start_time 
        
        return AnalyzerFrame('TimingViolation',
            framestart,
            frameend, {
            'delta_ns': int(delta),
            'maxTiming' : int(maxTiming)
        })

    def decode(self, frame: AnalyzerFrame):
        # SPI frame types are: enable, result and disable
        # see https://support.saleae.com/extensions/analyzer-frame-types/spi-analyzer for further information
        
        # enable --> CS changes from inactive to active
        # result --> data exchange = the phase where CS is active
        # disable --> CS changes from active to inactive

        ############################
        # CHIP SELECT ASSERTED
        ############################ 
        if frame.type == 'enable':
            self.state = STATE_CMD
      
            # keep track when CS was asserted --> frame.start_time and frame.end_time are equal for this 
            # frame type, so you can use any of them
            self.last_cs_asserted = frame.start_time

            # initialize variables
            self.last_start_time_byte = 0
            self.last_end_time_byte = 0
            self.last_cs_deasserted = 0
            #self.data_frame_start = frame.start_time
            #self.data_frame_end = frame.end_time
        elif frame.type == 'result':
            ############################
            # COMMAND/INSTRUCTION
            ############################        
            
            # Read first four bytes to determine the functionality
            if self.state == STATE_TCAN_CMD:
                self.prevRegName = self.regString
                self.dataString = ''
                self.data1 = frame.data['mosi']
                self.frameStartTime = frame.start_time
                if self.data1 == SPI_TCAN_WRITE or self.data1 == SPI_TCAN_READ:
                    self.state = STATE_TCAN_REG1
                else:
                    return AnalyzerFrame('Error', frame.start_time, frame.end_time, {
                        'Type': 'Unexpected Data'
                    })
            elif self.state == STATE_TCAN_REG1:
                self.data2 = frame.data['mosi']
                self.state = STATE_TCAN_REG2
            elif self.state == STATE_TCAN_REG2:
                self.data3 = frame.data['mosi']
                self.state = STATE_TCAN_WORDS
            elif self.state == STATE_TCAN_WORDS:
                self.data4 = frame.data['mosi']
                self.dataCount = int.from_bytes(self.data4, "big") * 4

                if (self.data1 == SPI_TCAN_WRITE):
                    self.state = STATE_TCAN_DATA_WRITE
                    self.cmdString = 'Write '
                elif (self.data1 == SPI_TCAN_READ):
                    self.state = STATE_TCAN_DATA_READ
                    self.cmdString = 'Read '
                self.firstDataFlag = 1
                self.frameEndTime = frame.end_time
                self.regString = str("%0.2X" % int.from_bytes(self.data2, 'big')) + str("%0.2X" % int.from_bytes(self.data3, 'big'))
                self.regName = getRegisterString(self.regString)
                # return AnalyzerFrame(self.cmdString, self.frameStartTime, self.frameEndTime, {
                # 'Register': self.regString, 'Name': self.regName
                # })
            elif self.state == STATE_TCAN_DATA_READ:
                self.data.append(frame.data['miso'])
                self.dataString+=str("%0.2X" % int.from_bytes(frame.data['miso'], 'big'))
                self.dataCount-=1
                # if self.firstDataFlag:
                #     self.firstDataFlag = 0
                #     self.frameStartTime = frame.start_time
                if self.dataCount == 0:
                    self.frameEndTime = frame.end_time
                    self.state = STATE_TCAN_CMD
                    return AnalyzerFrame(self.cmdString, self.frameStartTime, self.frameEndTime, {
                    'Register': self.regString, 'Name' : self.regName, 'Data': self.dataString
                    })
            elif self.state == STATE_TCAN_DATA_WRITE:
                self.data.append(frame.data['mosi'])
                self.dataString+=str("%0.2X" % int.from_bytes(frame.data['mosi'], 'big'))
                self.dataCount-=1
                if self.firstDataFlag:
                    self.firstDataFlag = 0
                    self.frameStartTime = frame.start_time
                if self.dataCount == 0:
                    self.frameEndTime = frame.end_time
                    self.state = STATE_TCAN_CMD
                if self.dataCount == 0:
                    self.frameEndTime = frame.end_time
                    self.state = STATE_TCAN_CMD
                    if self.regString[0:2] == "84":
                        self.id = parseTcanTx(self.dataString).get("id", "None")
                        return AnalyzerFrame(self.cmdString, self.frameStartTime, self.frameEndTime, {
                        'Register': self.regString, 'Name' : self.regName, 'Data': self.dataString, 'ID' : str(self.id)
                        })
                    else:
                        return AnalyzerFrame(self.cmdString, self.frameStartTime, self.frameEndTime, {
                        'Register': self.regString, 'Name' : self.regName, 'Data': self.dataString
                        })

            
            # if self.state == STATE_CMD:
            #     self.command = frame.data['mosi'] 
            #     self.address = None              
            #     # self.data = b''                
            #     self.data_byte_cnt = 0
            #     self.showInstruction = 1
            #     self.timingViolation = 'violation'
            #     self.last_end_time_byte = frame.end_time
            #     self.last_start_time_byte = frame.start_time
                
              
            #     # get the proper state according to the received command      
            #     self.state = self.get_next_state(self.command)
        
            #     self.showInstruction = self.show_cmd(self.filter_setting, self.command);
            #     if self.showInstruction == 2:
            #         self.showInstruction = 0
            #         self.state = STATE_NO_DATA
            
            #     if self.showInstruction == 1:   
            #         return AnalyzerFrame('Command', frame.start_time, frame.end_time, {
            #             'command': self.cmd_to_str(self.command)
            #         })
            #     else:
            #         if self.filter_setting == 'Timing_Violations':
            #             delta = self.calc_delta(self.last_cs_asserted, self.last_start_time_byte)
            #             if delta > self.timeCsToFirstByte:
            #                 return self.indicate_violation(self.timeCsToFirstByte, delta, self.last_cs_asserted, self.last_start_time_byte, frame.start_time, frame.end_time)    
            
            # ############################
            # # ADDRESS
            # ############################        
            # elif self.state == STATE_ADDR_H:
            #     self.address_frame_start = frame.start_time

            #     if self.address_size == '2':
            #         self.state = STATE_ADDR_L           
            #         self.address = int.from_bytes(frame.data['mosi'], 'big') << 8
            #     else:
            #         self.state = STATE_ADDR_M           
            #         self.address = int.from_bytes(frame.data['mosi'], 'big') << 16
                    
            # elif self.state == STATE_ADDR_M:
            #     self.address = self.address | int.from_bytes(frame.data['mosi'], 'big') << 8
            #     self.state = STATE_ADDR_L           
            
            # elif self.state == STATE_ADDR_L:
            #     self.address = self.address | int.from_bytes(frame.data['mosi'], 'big')
            #     self.state = self.get_last_state(self.command)
            #     self.data_byte_cnt = 0

            #     if self.filter_setting != 'Timing_Violations':
            #         if self.highlight_cmd_only == 'no':
            #             return AnalyzerFrame('Address', self.address_frame_start, frame.end_time, {
            #                 'address': self.address,
            #                 'addressHex': hex(self.address)    
            #             })        
            ############################
            # DATA
            ############################        
            # elif self.state == STATE_DATA:                
            #     if self.data_byte_cnt == 0:             
            #         self.data_frame_start = frame.start_time                   
                    
            #     self.data_byte_cnt += 1
            #     self.data += frame.data[frame_config[self.command][IDX_DATA_LINE]]
            #     self.data_frame_end = frame.end_time
                
            #     # now we check for timing violations if the proper filter is set
            #     if self.filter_setting == 'Timing_Violations':
            #         delta = self.calc_delta(self.last_end_time_byte, frame.start_time)
            #         if delta > self.timeByteToByte:
            #             return self.indicate_violation(self.timeByteToByte, delta, self.last_end_time_byte, frame.start_time, frame.start_time, frame.end_time)    
          
            #     # keep track of the time stamps used for calculating timing violations
            #     self.last_end_time_byte = frame.end_time
            #     self.last_start_time_byte = frame.start_time  
        ############################
        # CHIP SELECT DEASSERTED
        ############################ 
        # elif frame.type == 'disable':
        #     self.last_cs_deasserted = frame.start_time
        #     if self.filter_setting == 'Timing_Violations':
        #         delta = self.calc_delta(self.last_end_time_byte, self.last_cs_deasserted)
        #         if delta > self.timelastByteToCs:
        #             return self.indicate_violation(self.timelastByteToCs, delta, self.last_end_time_byte, self.last_cs_deasserted, frame.start_time, frame.end_time)      
        #     else:
        #         if self.state == STATE_DATA:
        #             if self.highlight_cmd_only == 'no':
        #                 return AnalyzerFrame('Data',
        #                     self.data_frame_start,
        #                     self.data_frame_end, {
        #                     'data': self.data
        #                 })
        #         else:
        #             pass
