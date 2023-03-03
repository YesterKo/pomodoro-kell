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
    
    async def _show_startup_animation(this, length, brightness):
        sleep_length = int(1000 / len(this.neopixel) / brightness)
        for x in range(len(this.neopixel)):
            for y in range(brightness):
                await this.ticking.wait()
                this.neopixel[x] = (y+1,0,0)
                this.neopixel.write()
                await asyncio.sleep_ms(sleep_length)


    async def main(this):
        asyncio.create_task(this.toggle_ticking())
        while True:
            if this.status == 'work':
                await this.start_timer(WORK_LENGTH, BRIGHTNESS)
                this.status = 'break'
            elif this.status == 'break':
                await this.start_timer(BREAK_LENGTH, BRIGHTNESS)
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
    

    async def start_timer(this, length, brightness):
    
        for x in range(12):
            this.neopixel[x] = (0,0,0)
        this.neopixel.write()
        
        await this._show_startup_animation(0,brightness)
                
        delay = int(length * 60000 / 12 / brightness)
        
        for x in range(0,12):
            for y in range(brightness,-1,-1):
                this.neopixel[x] = (y,0,0)
                this.neopixel.write()
                #print(f'starting sleep for {delay}ms. Brightness is y.')
                await asyncio.sleep_ms(delay)


                
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
    
