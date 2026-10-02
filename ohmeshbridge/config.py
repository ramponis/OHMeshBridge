from pathlib import Path
import yaml


class Config:

    def __init__(self, config_file="config.yaml", commands_file="commands.yaml"):

        self.config = self._load_yaml(config_file)
        self.commands = self._load_yaml(commands_file)

    def _load_yaml(self, filename):

        path = Path(filename)

        if not path.exists():
            raise FileNotFoundError(f"Missing file: {filename}")

        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @property
    def meshtastic_host(self):
        return self.config["meshtastic"]["host"]

    @property
    def openhab_url(self):
        return self.config["openhab"]["url"]

    @property
    def log_level(self):
        return self.config["logging"]["level"]

    @property
    def technical_log(self):
        return self.config["logging"]["technical_log"]

    @property
    def audit_log(self):
        return self.config["logging"]["audit_log"]

    @property
    def users(self):
        return self.config["users"]

    @property
    def command_list(self):
        return self.commands["commands"]

    def get_command(self, name):
        return self.command_list.get(name.lower())

    @property
    def command_item(self):
        return self.config["openhab"].get(
            "command_item",
            "Meshtastic_Command"
        )

    @property
    def response_item(self):
        return self.config["openhab"].get(
            "response_item",
            "Meshtastic_Response"
        )
        
    @property
    def client_item(self):
        return self.config["openhab"].get(
            "client_item",
            "Meshtastic_Client"
        )

    @property
    def message_item(self):
        return self.config["openhab"].get(
            "message_item",
            "Meshtastic_Message"
        )

    @property
    def send_item(self):
        return self.config["openhab"].get(
            "send_item",
            "Meshtastic_Send"
        )
        
    @property
    def nodes_item(self):
        return self.config["openhab"].get(
            "nodes_item",
            "Meshtastic_Nodes"
        )

    @property
    def active_nodes_item(self):
        return self.config["openhab"].get(
            "active_nodes_item",
            "Meshtastic_ActiveNodes"
        )

    @property
    def active_timeout(self):
        return self.config["meshtastic"].get(
            "active_timeout",
            7200
        )

    @property
    def last_heard_age_item(self):
        return self.config["openhab"].get(
            "last_heard_age_item",
            "Meshtastic_LastHeardAge"
        )


    @property
    def last_heard_node_item(self):
        return self.config["openhab"].get(
            "last_heard_node_item",
            "Meshtastic_LastHeardNode"
        )


    @property
    def active_nodes_list(self):
        return self.config["openhab"].get(
            "active_nodes_list",
            "Meshtastic_ActiveNodeList"
        )

    @property
    def sender_item(self):
        return self.config["openhab"].get(
            "sender_item",
            "Meshtastic_Sender"
        )
