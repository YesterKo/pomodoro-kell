import colorsys
import uasyncio as asyncio
import time
from config import *
from primitives import WaitAny


class PomodoroTimer:

    def __init__(self, np, nupud):
        self.neopixel = np
        self.ticking = asyncio.Event()
        self.nupud = nupud
        self.status = 'work'
        self.brightness = BRIGHTNESS

    async def _show_startup_animation(self, length):
        sleep_length = int(1000 / len(self.neopixel) / self.brightness)
        for x in range(len(self.neopixel)):
            for y in range(self.brightness):
                await self.ticking.wait()
                self.neopixel[x] = (y+1, 0, 0)
                self.neopixel.write()
                await asyncio.sleep_ms(sleep_length)

    def _show_fill(self, value):
        for x in range(len(self.neopixel)):
            self.neopixel[x] = value
        self.neopixel.write()

    async def main(self):
        asyncio.create_task(self.ticking_toggler())
        asyncio.create_task(self.brightness_changer())
        while True:
            if self.status == 'work':
                await self.start_timer(WORK_LENGTH)
                self.status = 'break'
            elif self.status == 'break':
                await self.start_timer(BREAK_LENGTH)
                self.status = 'work'

    async def ticking_toggler(self):
        while True:
            await self.nupud.cp.wait()
            self.nupud.cp.clear()
            if self.status == 'work':
                self.status = 'work_paused'
                self.ticking.clear()
                print('ticking stopped')
            elif self.status == 'work_paused':
                self.status = 'work'
                self.ticking.set()
                print('ticking continued')

    async def brightness_changer(self):
        while True:
            event = await WaitAny((self.nupud.cw, self.nupud.ccw)).wait()
            if event is self.nupud.cw:
                self.nupud.cw.clear()
                self.brightness = min(self.brightness + 1, 255)
                self.render_display()
            else:
                self.nupud.ccw.clear()
                self.brightness = max(self.brightness - 1, 1)
                self.render_display()

    async def start_timer(self, length):
        self.start_time = time.ticks_ms()
        self.stop_time = time.ticks_add(self.start_time, length * 60000)
        self._show_fill((0, 0, 0))
        await self._show_startup_animation(0)
        await self.start_display_renderer()

    def render_display(self):
        current_time = time.ticks_diff(self.stop_time, time.ticks_ms())
        display_samm = len(self.neopixel)*self.brightness
        sammu_pikkus = time.ticks_diff(self.stop_time, self.start_time) / display_samm
        sammud = current_time / sammu_pikkus
        full_leds = int(sammud // self.brightness)
        last_led_brightness = int(sammud % self.brightness)
        # placeholder = current_time / (time.ticks_diff(self.start_time, self.stop_time) / (len(self.neopixel) * self.brightness))
        print(f'full_leds: {full_leds}')
        print(f'last_led_brightness: {last_led_brightness}')
        for x in range(len(self.neopixel)):
            self.neopixel[x] = (0, 0, 0)
        for x in range(len(self.neopixel)-1, len(self.neopixel) - full_leds - 1, -1):
            self.neopixel[x] = (self.brightness, 0, 0)
        self.neopixel[len(self.neopixel) - full_leds - 1] = (last_led_brightness, 0, 0)
        self.neopixel.write()

    async def start_display_renderer(self):
        sammu_pikkus = (time.ticks_diff(self.stop_time, self.start_time) / (len(self.neopixel) * self.brightness))
        while time.ticks_diff(self.stop_time, time.ticks_ms()) > 10:
            self.render_display()
            await asyncio.sleep_ms(min(time.ticks_diff(self.stop_time, time.ticks_ms()), int(sammu_pikkus)))
        self._show_fill((self.brightness, 0, 0))
        await asyncio.sleep_ms(500)
        self._show_fill((0, 0, 0))
        await asyncio.sleep_ms(500)
        self._show_fill((self.brightness, 0, 0))
        await asyncio.sleep_ms(500)
        self._show_fill((0, 0, 0))
        await asyncio.sleep_ms(500)
