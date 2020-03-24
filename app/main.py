from nnt.manager.app import App
from nnt.core.kernel import corun


def launch():
    App.LoadConfig()

    app = App()
    app.assetDir = "~/assets/"
    corun(app.start)
