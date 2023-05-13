from colorsys import hsv_to_rgb
import uasyncio as asyncio
import time
from config import *
from primitives import WaitAny, Delay_ms


class PomodoroTimer:

    def __init__(self, np, nupud):
        self.neopixel = np
        self.not_paused = asyncio.Event()
        self.not_paused.set()
        self.nupud = nupud
        self.brightness = BRIGHTNESS
        self._time_since_long_break = 0
        self.color = (0.166667,1)


    def _show_fill(self, value):
        for x in range(len(self.neopixel)):
            self.neopixel[x] = value
        self.neopixel.write()

    async def main(self):
        asyncio.create_task(self.pause_toggler())
        asyncio.create_task(self.brightness_changer())
        while True:
            self.color = (0,1)
            await self.start_timer(WORK_LENGTH)
            if self._time_since_long_break >= LONG_BREAK_INTERVAL:
                self._time_since_long_break = 0
                self.color = (1/6, 1)
                await self.start_timer(LONG_BREAK_LENGTH)
            else:
                self._time_since_long_break += 1
                self.color = (1/3, 1)
                await self.start_timer(BREAK_LENGTH)

    async def pause_toggler(self):
        while True:
            await self.nupud.cp.wait()
            if self.status == 'running':
                self.nupud.cp.clear()
                if self.not_paused.is_set():
                    self.not_paused.clear()
                    print('ticking stopped')
                    self.remaining_time = time.ticks_diff(self.stop_time, time.ticks_ms())
                    self.elapsed_time = time.ticks_diff(time.ticks_ms(), self.start_time)
                    flasher = asyncio.create_task(self._play_animation_flash(-1, 1000, 1000))
                else:
                    print('ticking continued')
                    self.start_time = time.ticks_diff(time.ticks_ms(), self.elapsed_time)
                    self.stop_time = time.ticks_add(time.ticks_ms(), self.remaining_time)
                    flasher.cancel()
                    self.render_display()
                    self.not_paused.set()
            else:
                await asyncio.sleep_ms(0)

    async def brightness_changer(self):
        while True:
            event = await WaitAny((self.nupud.cw, self.nupud.ccw)).wait()
            if event is self.nupud.cw:
                self.nupud.cw.clear()
                self.brightness = min(self.brightness + 1, MAX_BRIGHTNESS)
                self.render_display()
            else:
                self.nupud.ccw.clear()
                self.brightness = max(self.brightness - 1, 1)
                self.render_display()

    async def start_timer(self, length):
        self.status = 'running'
        self.start_time = time.ticks_ms()
        self.stop_time = time.ticks_add(self.start_time, length * 60000)
        self._show_fill((0, 0, 0))
        await self._play_animation_ring(1000)
        await self.start_display_renderer()

    def render_display(self):
        current_time = time.ticks_diff(self.stop_time, time.ticks_ms())
        display_samm = len(self.neopixel)*self.brightness
        sammu_pikkus = time.ticks_diff(self.stop_time, self.start_time) / display_samm
        sammud = current_time / sammu_pikkus
        full_leds = int(sammud // self.brightness)
        last_led_brightness = max(1,int(sammud % self.brightness))
        # placeholder = current_time / (time.ticks_diff(self.start_time, self.stop_time) / (len(self.neopixel) * self.brightness))
        print(f'full_leds: {full_leds}')
        print(f'last_led_brightness: {last_led_brightness}')
        for x in range(len(self.neopixel)):
            self.neopixel[x] = (0, 0, 0)
        for x in range(len(self.neopixel)-1, len(self.neopixel) - full_leds - 1, -1):
            self.neopixel[x] = hsv_to_rgb(*self.color, self.brightness / 255)
        self.neopixel[len(self.neopixel) - full_leds - 1] = hsv_to_rgb(*self.color, last_led_brightness / 255)
        self.neopixel.write()

    async def start_display_renderer(self):
        sammu_pikkus = (time.ticks_diff(self.stop_time, self.start_time) / (len(self.neopixel) * self.brightness))
        while time.ticks_diff(self.stop_time, time.ticks_ms()) > 10:
            await self.not_paused.wait()
            self.render_display()
            await asyncio.sleep_ms(min(time.ticks_diff(self.stop_time, time.ticks_ms()), int(sammu_pikkus)))
        self.status = 'finished'
        await self._play_animation_flash(5, 50, 50, brightness = self.brightness + 10)
        await self.nupud.cp.wait()
        self.nupud.cp.clear()
    async def _play_animation_ring(self, duration, direction=0, *, brightness = None, color = None):
        if not brightness:
            brightness = self.brightness
        if not color:
            color = self.color
        sleep_length = int(duration / len(self.neopixel) / brightness)
        for x in range(len(self.neopixel)):
            for y in range(brightness+1):
                await self.not_paused.wait()
                self.neopixel[x] = hsv_to_rgb(*color, y/255)
                self.neopixel.write()
                await asyncio.sleep_ms(sleep_length)

    async def _play_animation_flash(self, count, on_time, off_time, *, brightness = None, color = None): 
        brightness = brightness or self.brightness
        color = color or self.color
        loop_count = count if count >= 0 else None
        while loop_count != 0:
            self._show_fill(hsv_to_rgb(*color, brightness / 255))
            await asyncio.sleep_ms(on_time)
            self._show_fill((0,0,0))
            await asyncio.sleep_ms(off_time)
            loop_count = loop_count - 1 if loop_count is not None else None


class ImprovedDelay(Delay_ms):
    
    def trigger(self, duration=0):  # Update absolute end time, 0-> ctor default
        if self._mtask is None:
            raise RuntimeError("Delay_ms.deinit() has run.")
        self._tend = time.ticks_add(ticks_ms(), duration if duration > 0 else self._durn)
        self._tdur = duration if duration > 0 else self._durn
        self._retn = None  # Default in case cancelled.
        self._busy = True
        self._trig.set()

    def change(self, duration=0):
        if self._mtask is None:
            raise RunTimeError("Delay_ms.deinit() has run.")
        self._tend = time.ticks_add(self._tend, duration if duration > 0 else self._durn - self._tdur)
        self._tdur = duration if duration > 0 else self._durn
        self._retn = None  # Default in case cancelled.
        self._busy = True
        self._trig.set()

    def pause(self):
        self._ttask.cancel()
        self._ttask = self._fake
        self._trem = time.ticks_diff(self._tend, time.ticks_ms())
        self._busy = False
        self._tout.clear()
        
    def _continue(self, duration=0):
        if self._mtask is None:
            raise RunTimeError("Delay_ms.deinit() has run.")
        self._tend = time.ticks_add(time.ticks_ms(), self._trem)
        self._tdur = duration if duration > 0 else self._durn
        self._retn = None  # Default in case cancelled.
        self._busy = True
        self._trig.set()
