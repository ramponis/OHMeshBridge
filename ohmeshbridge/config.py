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