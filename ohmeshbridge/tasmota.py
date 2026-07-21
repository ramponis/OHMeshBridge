import requests


class TasmotaClient:

    def __init__(self, timeout=5, logger=None):

        self.timeout = timeout
        self.logger = logger


    def get_switch(self, ip):

        url = (
            f"http://{ip}/cm"
            f"?cmnd=Power"
        )

        try:

            response = requests.get(
                url,
                timeout=self.timeout
            )

            response.raise_for_status()

            data = response.json()

            return (
                data.get("POWER")
                or data.get("POWER1")
                or data.get("Power")
            )

        except Exception as e:

            if self.logger:
                self.logger.error(
                    f"Tasmota read error {ip}: {e}"
                )

            return None



    def send_switch(self, ip, state):

        state = state.upper()

        if state == "ON":
            command = "Power%20On"

        elif state == "OFF":
            command = "Power%20Off"

        else:
            return False


        url = (
            f"http://{ip}/cm"
            f"?cmnd={command}"
        )

        try:

            response = requests.get(
                url,
                timeout=self.timeout
            )

            response.raise_for_status()

            return True


        except Exception as e:

            if self.logger:
                self.logger.error(
                    f"Tasmota error {ip}: {e}"
                )

            return False