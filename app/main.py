# -*- coding:utf-8 -*-

from nnt.manager.app import App
import asyncio

def launch():
    App.LoadConfig()

    app = App()
    app.entryDir = "~/"
    app.assetDir = "~/assets/"

    loop = asyncio.get_event_loop()    
    loop.run_until_complete(app.start())
    loop.close()    
