# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)

import machine
import neopixel
import time
from config import *
import pomodoro
import multiwheel
import uasyncio as asyncio

def set_global_exception():
    def handle_exception(loop, context):
        import sys
        sys.print_exception(context["exception"])
        sys.exit()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)

async def main():

    set_global_exception()

    stop = asyncio.Event()
    np = neopixel.NeoPixel(machine.Pin(NEOPIXEL_PIN), NEOPIXEL_LEDS)
    nupud = multiwheel.NupudListener()
    pt = pomodoro.PomodoroTimer(np, nupud)
    

    asyncio.create_task(nupud.main())
    asyncio.create_task(pt.main())
    await stop.wait()

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
