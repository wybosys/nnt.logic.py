from nnt.core.kernel import corun
from nnt.manager.app import App


def launch():
    App.LoadConfig()

    app = App()
    app.assetDir = "~/assets/"
    corun(app.start)
