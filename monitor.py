from datetime import datetime, timedelta

import requests
import yaml

url_temp = "http://testnet-jsonrpc.conflux-chain.org:18084/api/account/{}/minedBlockList?pageNum=1&pageSize=10";

config = yaml.load(open('config.yml'), Loader=yaml.FullLoader)
dead_bar = timedelta(seconds=int(config["alert_bar_in_secs"]))


class MiningError(Exception):
    def __init__(self, message, miners):
        self.message = message
        self.miners = miners


class RequestError(Exception):
    def __init__(self):
        pass


def monitor(file_name):
    is_error = False
    error_msg = 'Something wrong in following nodes:\n'
    error_miners = []

    with open(file_name, 'r') as f:
        for line in f:
            address = line.strip('\n')
            try:
                data = requests.get(url_temp.format(address), timeout=60).json()
            except Exception:
                raise RequestError

            total = data['result']['total']

            if total == 0:
                msg = "{}: total mined {} blocks\n".format(address, total)
                print(msg)

                is_error = True
                error_msg += msg
                error_miners.append(address)
            else:
                timestamp = data['result']['data'][0]['timestamp']
                now_timestamp = datetime.now()
                sec = now_timestamp - datetime.fromtimestamp(timestamp)
                sec = max(sec, timedelta(seconds=0))

                msg = "{}: total mined {} blocks, latest mined block at {}, {} ago\n".format(address, total,
                                                                                             datetime.fromtimestamp(
                                                                                                 timestamp), str(sec))
                if sec > dead_bar:
                    is_error = True
                    error_msg += msg
                    error_miners.append(address)

                print(msg)

    if is_error:
        raise MiningError(error_msg, error_miners)


if __name__ == '__main__':
    monitor("miner_list.txt")
