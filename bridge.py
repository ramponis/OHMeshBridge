import time

from ohmeshbridge.config import Config
from ohmeshbridge.logger import setup_logger, setup_audit_logger
from ohmeshbridge.openhab import OpenHabClient
from ohmeshbridge.command_engine import CommandEngine
from ohmeshbridge.meshtastic import MeshtasticClient


def main():

    cfg = Config()


    logger = setup_logger(
        cfg.technical_log,
        cfg.log_level
    )
    
    audit_logger = setup_audit_logger(
        cfg.audit_log
    )


    logger.info("OHMeshBridge starting")


    openhab = OpenHabClient(
        cfg.openhab_url,
        logger=logger
    )


    engine = CommandEngine(
        cfg,
        openhab,
        logger=logger
    )


    def on_message(sender, text):

        logger.info(
            f"Command from {sender}: {text}"
        )


        # accetta solo comandi OH

        if not text.lower().startswith("oh"):
            return None


        # controllo autorizzazione

        if sender not in cfg.users:

            logger.warning(
                f"Unauthorized node {sender}"
            )

            return "✗ Non autorizzato"


        user = cfg.users[sender].get(
            "name",
            sender
        )


        logger.info(
            f"User {user}"
        )


        response = engine.execute(text)


        audit_logger.info(
            f"{user} | {sender} | {text} | {response}"
        )


        return response



    mesh = MeshtasticClient(
        cfg.meshtastic_host,
        on_message,
        logger
    )


    mesh.connect()


    logger.info(
        "OHMeshBridge running"
    )


    while True:

        if not mesh.connected:

            logger.warning(
                "Meshtastic disconnected, reconnecting"
            )

            mesh.connect()


        time.sleep(10)



if __name__ == "__main__":
    main()