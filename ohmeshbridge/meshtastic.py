import time

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



    def _get_nodes(self):

        """
        Restituisce il dizionario dei nodi conosciuti.
        Compatibile con diverse versioni della libreria Meshtastic.
        """

        if not self.interface:
            return {}

        try:

            nodes = getattr(
                self.interface,
                "nodes",
                None
            )

            if nodes is not None:
                return nodes


            return self.interface.nodesByNum


        except Exception as e:

            if self.logger:
                self.logger.error(
                    f"Unable to read nodes: {e}"
                )

            return {}



    def get_node_count(self):

        """
        Restituisce il numero totale dei nodi conosciuti.
        """

        nodes = self._get_nodes()

        return len(nodes)



    def get_active_nodes(self, max_age=7200):

        """
        Restituisce i nodi attivi come lista:

        [
            ("Nome (!nodeid)", "!nodeid"),
            ...
        ]

        Il nome viene sempre accompagnato dall'ID
        per garantire unicità.
        """

        nodes = self._get_nodes()

        if not nodes:
            return []


        now = time.time()
        active_nodes = []


        try:

            for node_id, node in nodes.items():

                last_heard = node.get(
                    "lastHeard"
                )


                if last_heard is None:
                    continue


                if now - last_heard > max_age:
                    continue


                user = node.get(
                    "user",
                    {}
                )


                name = (
                    user.get("longName")
                    or user.get("shortName")
                    or user.get("id")
                    or node_id
                )


                # Sanificazione per formato openHAB Nome=Valore

                name = (
                    name.replace(",", " ")
                        .replace("=", "-")
                        .strip()
                )


                label = f"{name} ({node_id})"


                active_nodes.append(
                    (
                        label,
                        node_id
                    )
                )


            # ordinamento alfabetico per visualizzazione stabile

            active_nodes.sort(
                key=lambda x: x[0].lower()
            )


            return active_nodes


        except Exception as e:

            if self.logger:
                self.logger.error(
                    f"Active nodes list error: {e}"
                )

            return []



    def get_active_node_count(self, max_age=7200):

        """
        Restituisce il numero di nodi sentiti negli ultimi max_age secondi.
        Default: 2 ore.
        """

        nodes = self._get_nodes()

        if not nodes:
            return 0


        now = time.time()
        count = 0


        try:

            for node in nodes.values():

                last_heard = node.get(
                    "lastHeard"
                )


                if last_heard is None:
                    continue


                if now - last_heard <= max_age:
                    count += 1


            return count


        except Exception as e:

            if self.logger:
                self.logger.error(
                    f"Active node count error: {e}"
                )

            return 0



    def get_last_heard_info(self):

        """
        Restituisce una tupla:

            (last_node, last_age)

        dove:

            last_node = nome del nodo sentito più recentemente
            last_age  = secondi trascorsi dall'ultimo pacchetto
        """

        nodes = self._get_nodes()

        if not nodes:
            return None, None


        now = time.time()

        newest = None
        last_node = None


        try:

            for node_id, node in nodes.items():

                last_heard = node.get(
                    "lastHeard"
                )


                if last_heard is None:
                    continue


                if newest is None or last_heard > newest:

                    newest = last_heard

                    user = node.get(
                        "user",
                        {}
                    )

                    last_node = (
                        user.get("longName")
                        or user.get("shortName")
                        or user.get("id")
                        or node_id
                    )


            if newest is None:
                return None, None


            last_age = int(
                now - newest
            )


            return last_node, last_age


        except Exception as e:

            if self.logger:
                self.logger.error(
                    f"Last heard info error: {e}"
                )

            return None, None



    def get_node_short_name(self, node_id):
        """Return the short name of a node."""
        try:
            nodes = self.interface.nodes

            if not nodes:
                return node_id

            node = nodes.get(node_id)

            if node:
                user = node.get("user", {})
                short_name = user.get("shortName")

                if short_name:
                    return short_name

        except Exception as e:
            if self.logger:
                self.logger.warning(
                    f"Unable to get short name for {node_id}: {e}"
                )

        return node_id
