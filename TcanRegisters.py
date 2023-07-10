RegisterStringsDict = {
    "0000" : 'DEVICE_ID0',
    "0004" : 'DEVICE_ID1',
    "0008" : 'REVISION',
    "000C" : 'STATUS',
    "0010" : 'ERROR_STATUS_MASK',
    "0800" : 'MODES_AND_PINS',
    "0804" : 'TIMESTAMP_PRESCALER',
    "0808" : 'TEST_REGISTERS',
    "0820" : 'DEV_IR',
    "0830" : 'DEV_IE',
    "1000" : 'MCAN_CREL',
    "1004" : 'MCAN_ENDN',
    "1008" : 'MCAN_CUST',
    "100C" : 'MCAN_DBTP',
    "1010" : 'MCAN_TEST',
    "1014" : 'MCAN_RWD',
    "1018" : 'MCAN_CCCR',
    "101C" : 'MCAN_NBTP',
    "1020" : 'MCAN_TSCC',
    "1024" : 'MCAN_TSCV',
    "1028" : 'MCAN_TOCC',
    "102C" : 'MCAN_TOCV',
    "1040" : 'MCAN_ECR',
    "1044" : 'MCAN_PSR',
    "1048" : 'MCAN_TDCR',
    "1050" : 'MCAN_IR',
    "1054" : 'MCAN_IE',
    "1058" : 'MCAN_ILS',
    "105C" : 'MCAN_ILE',
    "1080" : 'MCAN_GFC',
    "1084" : 'MCAN_SIDFC',
    "1088" : 'MCAN_XIDFC',
    "1090" : 'MCAN_XIDAM',
    "1094" : 'MCAN_HPMS',
    "1098" : 'MCAN_NDAT1',
    "109C" : 'MCAN_NDAT2',
    "10A0" : 'MCAN_RXF0C',
    "10A4" : 'MCAN_RXF0S',
    "10A8" : 'MCAN_RXF0A',
    "10AC" : 'MCAN_RXBC',
    "10B0" : 'MCAN_RXF1C',
    "10B4" : 'MCAN_RXF1S',
    "10B8" : 'MCAN_RXF1A',
    "10BC" : 'MCAN_RXESC',
    "10C0" : 'MCAN_TXBC',
    "10C4" : 'MCAN_TXFQS',
    "10C8" : 'MCAN_TXESC',
    "10CC" : 'MCAN_TXBRP',
    "10D0" : 'MCAN_TXBAR',
    "10D4" : 'MCAN_TXBCR',
    "10D8" : 'MCAN_TXBTO',
    "10DC" : 'MCAN_TXBCF',
    "10E0" : 'MCAN_TXBTIE',
    "10E4" : 'MCAN_TXBCIE',
    "10F0" : 'MCAN_TXEFC',
    "10F4" : 'MCAN_TXEFS',
    "10F8" : 'MCAN_TXEFA'
}

def getRegisterString(inputString):
    outputString = RegisterStringsDict.get(inputString, "None")
    return outputString

def parseTcanTx(inputString):
    idString = inputString[:8]
    idRawNum = int(idString, 16)
    id = idRawNum & 0x1FFFFFFF
    id = id >> 18
    return {"id" : id}