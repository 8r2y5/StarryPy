from base_plugin import BasePlugin


class Announcer(BasePlugin):
    '''
    Broadcasts a message whenever a player joins or leaves the server.
    '''
    name = 'announcer_plugin'

    def activate(self):
        super(Announcer, self).activate()

    def after_connect_success(self, data):
        self.factory.broadcast(
            '{} logged in.'.format(
                self.protocol.player.colored_name(self.config.colors),
                0,
                'Announcer'
            )
        )

    def on_client_disconnect_request(self, data):
        if self.protocol.player is not None:
            self.factory.broadcast(
                self.factory.broadcast(
                    '{} logged out.'.format(
                        self.protocol.player.colored_name(self.config.colors),
                        0,
                        'Announcer'
                    )
                )
            )
