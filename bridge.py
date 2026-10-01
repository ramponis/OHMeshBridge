import time

from ohmeshbridge.config import Config
from ohmeshbridge.logger import setup_logger, setup_audit_logger
from ohmeshbridge.openhab import OpenHabClient
from ohmeshbridge.command_engine import CommandEngine
from ohmeshbridge.meshtastic import MeshtasticClient
from ohmeshbridge.outgoing import OutgoingManager


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


        # Accetta solo comandi OH

        if not text.lower().startswith("oh"):

            return None


        # Controllo autorizzazione

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


        # Log comando ricevuto su OpenHAB

        try:

            openhab.send_command(
                cfg.command_item,
                text
            )

        except Exception:

            logger.exception(
                "Unable to update command item"
            )


        # Esecuzione comando

        response = engine.execute(text)


        audit_logger.info(
            f"{user} | {sender} | {text} | {response}"
        )


        # Log risposta su OpenHAB

        try:

            openhab.send_command(
                cfg.response_item,
                response or ""
            )

        except Exception:

            logger.exception(
                "Unable to update response item"
            )


        return response



    mesh = MeshtasticClient(
        cfg.meshtastic_host,
        on_message,
        logger
    )


    mesh.connect()


    outgoing = OutgoingManager(
        cfg,
        openhab,
        mesh,
        logger,
        audit_logger
    )


    logger.info(
        "Outgoing manager enabled"
    )


    logger.info(
        "OHMeshBridge running"
    )


    last_node_count = None
    last_active_node_count = None
    last_last_heard_age = None
    last_last_heard_node = None
    last_active_node_list = None


    def update_node_stats():

        nonlocal last_node_count
        nonlocal last_active_node_count
        nonlocal last_last_heard_age
        nonlocal last_last_heard_node
        nonlocal last_active_node_list


        if not mesh.connected:
            return


        # Aggiorna numero totale nodi

        if cfg.nodes_item:

            count = mesh.get_node_count()


            if count != last_node_count:

                openhab.send_command(
                    cfg.nodes_item,
                    str(count)
                )

                last_node_count = count



        # Aggiorna numero nodi attivi

        if cfg.active_nodes_item:

            active = mesh.get_active_node_count(
                cfg.active_timeout
            )


            if active != last_active_node_count:

                openhab.send_command(
                    cfg.active_nodes_item,
                    str(active)
                )

                last_active_node_count = active


        # Aggiorna informazioni ultimo nodo sentito

        if (
            cfg.last_heard_age_item
            or cfg.last_heard_node_item
        ):

            last_node, last_age = mesh.get_last_heard_info()


            if (
                cfg.last_heard_age_item
                and last_age != last_last_heard_age
            ):

                openhab.send_command(
                    cfg.last_heard_age_item,
                    str(last_age if last_age is not None else 0)
                )

                last_last_heard_age = last_age


            if (
                cfg.last_heard_node_item
                and last_node != last_last_heard_node
            ):

                openhab.send_command(
                    cfg.last_heard_node_item,
                    last_node or ""
                )

                last_last_heard_node = last_node


        # Aggiorna la lista dei nodi attivi

        if cfg.active_nodes_list:

            nodes = mesh.get_active_nodes(
                cfg.active_timeout
            )

            #logger.info(
            #    f"Active nodes found: {nodes}"
            #)

            node_list = ",".join(
                f"{label}={node_id}"
                for label, node_id in nodes
            )

            #logger.info(
            #    f"Active node list: {node_list}"
            #)


            if node_list != last_active_node_list:

                openhab.send_command(
                    cfg.active_nodes_list,
                    node_list
                )

                logger.info(
                    f"Updated OpenHAB item {cfg.active_nodes_list}"
                )

                last_active_node_list = node_list

    while True:


        if not mesh.connected:

            logger.warning(
                "Meshtastic disconnected, reconnecting"
            )

            mesh.connect()



        try:

            outgoing.check()


        except Exception:

            logger.exception(
                "Outgoing manager error"
            )



        try:

            update_node_stats()


        except Exception:

            logger.exception(
                "Node statistics update error"
            )



        time.sleep(5)



if __name__ == "__main__":
    main()