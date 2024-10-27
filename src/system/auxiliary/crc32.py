
def crc32(data: bytes) -> int:     
    POLYNOMIAL = 0x04C11DB7      
    crc = 0xFFFFFFFF

    for byte in data:
        crc ^= byte << 24
        for _ in range(8):
            if crc & 0x80000000:
                crc = (crc << 1) ^ POLYNOMIAL
            else:
                crc <<= 1
            crc &= 0xFFFFFFFF 
    
    return crc ^ 0xFFFFFFFF