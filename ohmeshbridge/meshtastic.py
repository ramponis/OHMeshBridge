import time

import meshtastic
import meshtastic.tcp_interface

from pubsub import pub


class MeshtasticClient:

    def __init__(self, host, message_callback, logger=None):

        self.host = host
        self.callback = message_callback
        self.logger = logger

        self.interface = None
        self.connected = False


    def connect(self):

        while True:

            try:

                if self.interface:
                    try:
                        self.interface.close()
                    except:
                        pass


                self.interface = meshtastic.tcp_interface.TCPInterface(
                    hostname=self.host
                )


                pub.subscribe(
                    self._on_receive,
                    "meshtastic.receive"
                )


                self.connected = True


                if self.logger:
                    self.logger.info(
                        f"Connected to Meshtastic {self.host}"
                    )


                return


            except Exception as e:

                self.connected = False

                if self.logger:
                    self.logger.error(
                        f"Meshtastic connection failed: {e}"
                    )


                time.sleep(10)



    def _on_receive(self, packet, interface):

        try:

            decoded = packet.get("decoded", {})


            if decoded.get("portnum") != "TEXT_MESSAGE_APP":
                return


            text = decoded.get("text")


            if not text:
                return


            sender = packet.get("fromId")


            if self.logger:
                self.logger.info(
                    f"RX {sender}: {text}"
                )


            response = self.callback(
                sender,
                text
            )


            if response:

                interface.sendText(
                    response,
                    destinationId=packet["from"]
                )


        except Exception as e:

            if self.logger:
                self.logger.error(
                    f"Receive error: {e}"
                )



    def send_message(self, destination, text):

        if not self.interface:

            return False


        try:

            self.interface.sendText(
                text,
                destinationId=destination
            )

            return True


        except Exception as e:

            if self.logger:
                self.logger.error(
                    f"Send error: {e}"
                )


            self.connected = False

            return False