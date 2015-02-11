from base_plugin import BasePlugin
from packets import connect_response


class Announcer(BasePlugin):
    """
    Broadcasts a message whenever a player joins or leaves the server.
    """
    name = "announcer_plugin"
    auto_activate = True

    def activate(self):
        super(Announcer, self).activate()

    def after_connect_response(self, data):
        try:
            c = connect_response().parse(data.data)
            if c.success:
                self.factory.broadcast(
                    self.protocol.player.colored_name(self.config.colors) + " logged in.", 0, "Announcer")
        except AttributeError:
            return
        except:
            self.logger.exception("Unknown error in after_connect_response.")
            return

    def on_client_disconnect_request(self, data):
        if self.protocol.player is not None:
            self.factory.broadcast(self.protocol.player.colored_name(self.config.colors) + " logged out.", 0,
                                   "Announcer")