#from pymodbus.client import ModbusTcpClient

#client = ModbusTcpClient('MyDevice.lan')
#client = ModbusTcpClient(host="localhost", port=502)
#client.connect()
#client.write_coil(1, True)
#result = client.read_coils(1,1)
#print(result.bits[0])
#client.close()

from pyModbusTCP.client import ModbusClient
# TCP auto connect on first modbus request
c = ModbusClient(host="localhost", port=502, unit_id=1, auto_open=True)
regs = c.read_holding_registers(0, 1)

if regs:
    print(regs)
else:
    print("read error")
