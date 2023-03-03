import uasyncio as asyncio
from machine import UART

class NupudListener:

    def __init__(this):
        this.uart = UART(2,baudrate=9600,parity=0)

        this.up     = asyncio.Event()
        this.down   = asyncio.Event()
        this.left   = asyncio.Event()
        this.right  = asyncio.Event()
        this.cw     = asyncio.Event()
        this.ccw    = asyncio.Event()
        this.cp     = asyncio.Event()

    def main(this):
        while True:
            sisend = this.uart.read(1)
            if sisend != None:
                if sisend == b'\x14':
                    this.cw.set()
                elif sisend == b'\n':
                    this.ccw.set()
                elif sisend == b'\x01':
                    this.up.set()
                elif sisend == b'\x03':
                    this.right.set()
                elif sisend == b'\x05':
                    this.down.set()
                elif sisend == b'\x07':
                    this.left.set()
                elif sisend == b'\t':
                    this.cp.set()
                elif sisend == b'\x00': pass
                else:
                    print("Midagi on väga valesti, saan valesid käsklusi UART'ist?")
                    print(sisend)

            await asyncio.sleep(0)
