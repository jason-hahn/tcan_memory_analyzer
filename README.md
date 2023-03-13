# SPI Memory Analyzer

This analyzer can be used to decode SPI memory frames, e.g. for the AT25EU0041A and compatible. It might
also work with other serial devices (SRAM, FRAM, MRAM, etc.), but you need to check if the commands
are supported. See listing below. Modify HighLevelAnalyzer.py included in this extension just in case your
type of SPI memory uses different commands.

## Supported functionality

- Decoding of frames (command, address, data)  
- Supports address lengths of 2 and 3 bytes
- Filtering commands  
- Indicating timing violations  
    - CS to first byte
    - byte to byte
    - last byte to CS



## Supported commands

- [0x03] read byte/array                                  
- [0x81] erase page                                  
- [0x20] erase 4k block                              
- [0x52] erase 32k block
- [0xD8] erase 64k block
- [0xC7] erase chip                                  
- [0x02] program byte/array                                
- [0x06] write enable                                
- [0x04] write disable                               
- [0x05] read status register 1                      
- [0x35] read status register 2                      
- [0x9F] read device ID                              
- [0x01] write status register                       
- [0x50] write enable for volatile status register   

*It is quite easy to modify this extension to support additional commands.*

## General usage

### 1. Load the extension

### 2. Enable SPI analyze

![](/images/enable_spi_analyzer.png)

### 3. Configure SPI analyzer
![](/images/spi_analyzer_configuration.png)

### 4. Enable SPI memory analyzer
![](/images/enable_spi_memory_analyzer.png)  

### 5. Configure SPI memory analyzer
![](/images/enable_spi_memory_analyzer.png)

## Settings examples

#### Standard settings, highlight any command, address and data  
![](/images/no_filter.png)

#### Only highlight command  
![](/images/no_filter_cmd_only.png)

#### Only show specific command  
![](/images/filter_cmd.png)

#### Show timing violations   
![](/images/timing_violation.png)
![](/images/timing_violation_param.png)
