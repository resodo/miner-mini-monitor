import requests
import json
import yaml
from datetime import datetime, timedelta

url_temp = "http://testnet-jsonrpc.conflux-chain.org:18084/api/account/{}/minedBlockList?pageNum=1&pageSize=10";

config = yaml.load(open('config.yml'), Loader = yaml.FullLoader)
dead_bar = timedelta(int(config["alert_bar_in_secs"]))

class MiningError(Exception):
    def __init__(self, message):
        self.message = message

class RequestError(Exception):
    def __init__(self):
        pass

def monitor(file_name):
    is_error = False
    error_msg = 'Something wrong in following nodes:\n'

    with open(file_name, 'r') as f:
        for line in f:
            address = line.strip('\n')
            try:
                data = requests.get(url_temp.format(address), timeout = 60).json()
            except Exception:
                raise RequestError

            total = data['result']['total']

            if total == 0:
                msg = "{}: total mined {} blocks\n".format(address, total)
                error_msg += msg
                is_error = True
                print(msg)
            else:
                timestamp = data['result']['data'][0]['timestamp']
                now_timestamp = datetime.now()
                sec = now_timestamp - datetime.fromtimestamp(timestamp)
                sec = max(sec, timedelta(0))

                msg = "{}: total mined {} blocks, latest mined block at {}, {} ago\n".format(address, total, datetime.fromtimestamp(timestamp), str(sec))
                if sec > dead_bar:
                    is_error = True
                    error_msg += msg

                print(msg)

    if is_error:
        raise MiningError(error_msg)

if __name__ == '__main__':
    monitor("miner_list.txt")
