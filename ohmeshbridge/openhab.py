import requests


class OpenHabClient:

    def __init__(self, url, timeout=5, logger=None):

        self.url = url.rstrip("/")
        self.timeout = timeout
        self.logger = logger


    def get_state(self, item):

        try:
            response = requests.get(
                f"{self.url}/rest/items/{item}/state",
                timeout=self.timeout
            )

            response.raise_for_status()

            return response.text


        except Exception as e:

            if self.logger:
                self.logger.error(
                    f"OpenHAB read error {item}: {e}"
                )

            return None



    def send_command(self, item, command):

        try:

            response = requests.post(
                f"{self.url}/rest/items/{item}",
                data=command,
                headers={
                    "Content-Type": "text/plain"
                },
                timeout=self.timeout
            )

            response.raise_for_status()

            return True


        except Exception as e:

            if self.logger:
                self.logger.error(
                    f"OpenHAB command error {item} {command}: {e}"
                )

            return False