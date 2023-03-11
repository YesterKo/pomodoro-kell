import colorsys
import uasyncio as asyncio
import time
from config import *

class PomodoroTimer:

    def __init__(this, np, nupud):
        this.neopixel = np
        this.ticking = asyncio.Event()
        this.nupud = nupud
        this.status = 'work'
    
    async def _show_startup_animation(this, length):
        sleep_length = int(1000 / len(this.neopixel) / this.brightness)
        for x in range(len(this.neopixel)):
            for y in range(this.brightness):
                await this.ticking.wait()
                this.neopixel[x] = (y+1,0,0)
                this.neopixel.write()
                await asyncio.sleep_ms(sleep_length)

    def _show_fill(this,value):
        for x in range(len(this.neopixel)):
            this.neopixel[x] = value
        this.neopixel.write()


    async def main(this):
        asyncio.create_task(this.toggle_ticking())
        while True:
            if this.status == 'work':
                await this.start_timer(WORK_LENGTH)
                this.status = 'break'
            elif this.status == 'break':
                await this.start_timer(BREAK_LENGTH)
                this.status = 'work'
    

    async def toggle_ticking(this):
        while True:
            await this.nupud.cp.wait()
            this.nupud.cp.clear()
            if this.status == 'work':
                this.status = 'work_paused'
                this.ticking.clear()
                print('ticking stopped')
            elif this.status == 'work_paused':
                this.status = 'work'
                this.ticking.set()
                print('ticking continued')
    

    async def start_timer(this, length):
    
        this.start_time = time.ticks_ms()
        this.stop_time = time.ticks_add(this.start_time, length * 60000)

        this._show_fill((0,0,0))

        await this._show_startup_animation(0)
                
        await start_display_renderer()
        #delay = int(length * 60000 / 12 / brightness)
        #
        #for x in range(0,12):
        #    for y in range(brightness,-1,-1):
        #        this.neopixel[x] = (y,0,0)
        #        this.neopixel.write()
        #        #print(f'starting sleep for {delay}ms. Brightness is y.')
        #        await asyncio.sleep_ms(delay)

    async def render_display():
        current_time = time.ticks_diff(this.start_time, time.ticks_ms())
        display_samm = len(this.neopixel)*256
        sammu_pikkus = time.ticks_diff(this.start_time,this.stop_time) / display_samm
        sammud = current_time / sammu_pikkus
        full_leds = sammud // 256
        last_led_brightness = sammud % 256
        #placeholder = current_time / (time.ticks_diff(this.start_time, this.stop_time) / (len(this.neopixel) * 256))

        for x in range(full_leds):
            this.neopixel[x] = (this.brightness,0,0)

        this.neopixel[full_leds+1] = last_led_brightness
        
        for x in range(full_leds+1, len(this.neopixel)):
            this.neopixel[x] = (0,0,0)

        this.neopixel.write()

    async def start_display_renderer():
        sammu_pikkus = (time.ticks_diff(this.start_time, this.stop_time) / (len(this.neopixel) * 256))
        
        while time.ticks_diff(time.tick_ms(),this.stop_time) < 10:
            this.render_display()
            await min(time.ticks_diff(time.tick_ms(), this.stop_time),sammu_pikkus)

        this._show_fill((this.brightness,0,0))
        await time.sleep_ms(500)
        this._show_fill((0,0,0))
        await time.sleep_ms(500)
        this._show_fill((this.brightness,0,0))
        await time.sleep_ms(500)
        this._show_fill((0,0,0))
        await time.sleep_ms(500)
        



                
# Võta Hetke time.ms.
# Arvuta lõpus olev time.ms, saad suure arvu.
# jaga ledi kogusammude arv suure arvuga.
# jaga hetke time.ms jagatisega, saad teada ledide tulemuse.
# ledide tulemuse jagades yhe ledi väärtuste arvuga saan teada, mitu ledi full brightnessil põleb
# Jääk on n+1 ledi poolik põlemine
    
#     for x in range(0,12):
#         np[x] = (brightness,0,0)
#     np.write()
#     time.sleep_ms(250)
#     for x in range(0,12):
#         np[x] = (0,0,0)
#     np.write()
#     time.sleep_ms(250)
#     for x in range(0,12):
#         np[x] = (brightness,0,0)
#     np.write()
#     time.sleep_ms(250)
#     for x in range(0,12):
#         np[x] = (0,0,0)
#     np.write()
    
