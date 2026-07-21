from ohmeshbridge.tasmota import TasmotaClient


class CommandEngine:

    def __init__(self, config, openhab, logger=None):

        self.config = config
        self.openhab = openhab
        self.logger = logger

        self.tasmota = TasmotaClient(
            logger=logger
        )


    def _send_and_readback(
        self,
        command,
        definition,
        value
    ):

        item = definition["item"]

        protocol = definition.get(
            "protocol",
            "openhab"
        ).lower()


        # -------------------------
        # TASMOTA
        # -------------------------

        if protocol == "tasmota":

            if not self.tasmota.send_switch(
                item,
                value
            ):
                return "✗ Errore Tasmota"

            return (
                f"✓ {command.upper()}="
                f"{value.upper()}"
            )


        # -------------------------
        # OPENHAB
        # -------------------------

        ok = self.openhab.send_command(
            item,
            value
        )

        if not ok:
            return "✗ Errore OpenHAB"


        state = self.openhab.get_state(item)

        if state is None:
            return "✓ OK"


        return f"✓ {command.upper()}={state}"


    def _validate_number(self, value):

        try:
            float(value)
            return True

        except ValueError:
            return False


    def _validate_percent(self, value):

        if not self._validate_number(value):
            return False

        number = float(value)

        return 0 <= number <= 100


    def execute(self, text):

        parts = text.strip().split()

        if len(parts) == 0:
            return "✗ Comando vuoto"


        # elimina "oh"
        if parts[0].lower() == "oh":
            parts.pop(0)


        if len(parts) == 0:
            return self.help()


        if parts[0].lower() == "help":
            return self.help()


        command = None
        definition = None
        action = ""


        # Cerca il comando più lungo presente nel file YAML

        for i in range(len(parts), 0, -1):

            candidate = " ".join(parts[:i]).lower()

            definition = self.config.get_command(candidate)

            if definition is not None:

                command = candidate
                action = " ".join(parts[i:])

                break


        if definition is None:
            return "✗ Comando sconosciuto"


        item = definition["item"]
        item_type = definition["type"].lower()

        read_only = definition.get(
            "read_only",
            False
        )


        if action == "":
            action = "status"



        # -------------------------
        # STATUS
        # -------------------------

        if action.lower() == "status":

            protocol = definition.get(
                "protocol",
                "openhab"
            ).lower()


            if protocol == "openhab":

                value = self.openhab.get_state(
                    item
                )

                if value is None:
                    return "✗ Errore OpenHAB"

                return (
                    f"ℹ {command.upper()}="
                    f"{value}"
                )


            if protocol == "tasmota":

                value = self.tasmota.get_switch(item)

                if value is None:
                    return "✗ Errore Tasmota"

                return (
                    f"ℹ {command.upper()}="
                    f"{value}"
                )



        # -------------------------
        # READ ONLY
        # -------------------------

        if read_only:
            return "✗ Item in sola lettura"



        # -------------------------
        # SWITCH
        # -------------------------

        if item_type == "switch":

            cmd = action.upper()

            if cmd not in [
                "ON",
                "OFF"
            ]:

                return "✗ Valori ammessi: ON OFF"


            return self._send_and_readback(
                command,
                definition,
                cmd
            )



        # -------------------------
        # NUMBER
        # -------------------------

        if item_type == "number":

            if not self._validate_number(action):
                return "✗ Valore numerico non valido"


            return self._send_and_readback(
                command,
                definition,
                action
            )



        # -------------------------
        # STRING
        # -------------------------

        if item_type == "string":

            return self._send_and_readback(
                command,
                definition,
                action
            )



        # -------------------------
        # CONTACT
        # -------------------------

        if item_type == "contact":

            return "✗ Contact solo lettura"



        # -------------------------
        # DIMMER
        # -------------------------

        if item_type == "dimmer":

            cmd = action.upper()

            if cmd in [
                "ON",
                "OFF",
                "INCREASE",
                "DECREASE"
            ]:

                return self._send_and_readback(
                    command,
                    definition,
                    cmd
                )


            if not self._validate_percent(action):

                return (
                    "✗ Dimmer valori ammessi: "
                    "ON OFF INCREASE DECREASE 0-100"
                )


            return self._send_and_readback(
                command,
                definition,
                action
            )



        # -------------------------
        # ROLLERSHUTTER
        # -------------------------

        if item_type == "rollershutter":

            cmd = action.upper()

            if cmd in [
                "UP",
                "DOWN",
                "STOP"
            ]:

                return self._send_and_readback(
                    command,
                    definition,
                    cmd
                )


            if not self._validate_percent(action):

                return (
                    "✗ Roller valori ammessi: "
                    "UP DOWN STOP 0-100"
                )


            return self._send_and_readback(
                command,
                definition,
                action
            )


        return "✗ Tipo non supportato"



    def help(self):

        result = [
            "Comandi disponibili:"
        ]


        for name, data in self.config.command_list.items():

            desc = data.get(
                "description",
                ""
            )

            if desc:

                result.append(
                    f"{name} - {desc}"
                )

            else:

                result.append(name)


        result.append("")
        result.append("Sintassi:")
        result.append("oh <comando>")
        result.append("oh <comando> <valore>")


        return "\n".join(result)