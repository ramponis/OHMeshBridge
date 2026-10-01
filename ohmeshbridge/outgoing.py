class OutgoingManager:

    def __init__(
        self,
        cfg,
        openhab,
        mesh,
        logger=None,
        audit_logger=None
    ):

        self.cfg = cfg
        self.openhab = openhab
        self.mesh = mesh
        self.logger = logger
        self.audit_logger = audit_logger


    def check(self):

        send = self.openhab.get_state(
            self.cfg.send_item
        )

        if send is None:
            return


        if send.strip().upper() != "ON":
            return


        # Reset immediato del trigger

        self.openhab.send_command(
            self.cfg.send_item,
            "OFF"
        )


        destination = self.openhab.get_state(
            self.cfg.client_item
        )


        if not destination:

            if self.logger:
                self.logger.warning(
                    "Outgoing message without destination"
                )

            return


        destination = destination.strip()


        message = self.openhab.get_state(
            self.cfg.message_item
        )


        if not message:

            if self.logger:
                self.logger.warning(
                    "Outgoing message empty"
                )

            return


        message = message.strip()


        if self.logger:

            self.logger.info(
                f"Sending Meshtastic message "
                f"to {destination}: {message}"
            )


        ok = self.mesh.send_message(
            destination,
            message
        )


        if ok:

            if self.audit_logger:

                self.audit_logger.info(
                    f"OUT | {destination} | {message}"
                )


            if self.logger:

                self.logger.info(
                    "Meshtastic message sent"
                )


        else:

            if self.logger:

                self.logger.error(
                    "Meshtastic message failed"
                )


            if self.audit_logger:

                self.audit_logger.info(
                    f"OUT ERROR | {destination} | {message}"
                )