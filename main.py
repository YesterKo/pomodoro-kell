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
    leds = neopixel.NeoPixel(machine.Pin(NEOPIXEL_PIN), NEOPIXEL_LEDS, reverse = REVERSE)
    nupud = multiwheel.NupudListener()
    piezo = machine.Pin(PIEZO_PIN, machine.Pin.OUT)
    pt = pomodoro.PomodoroTimer(leds, nupud, piezo)

    asyncio.create_task(nupud.main())
    asyncio.create_task(pt.main())
    await stop.wait()

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()

