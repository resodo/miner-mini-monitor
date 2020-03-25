import urllib.request
import json
from datetime import datetime, timedelta

url_temp = "http://testnet-jsonrpc.conflux-chain.org:18084/api/account/{}/minedBlockList?pageNum=1&pageSize=10";

with open('miner_list.txt', 'r') as f:
    for line in f:
        address = line.strip('\n')
        contents = urllib.request.urlopen(url_temp.format(address)).read().decode('utf8').replace("'", '"')
        data = json.loads(contents)
        total = data['result']['total'];
        if total == 0:
            print("{}: total mined {} blocks".format(address, total))
        else:
            timestamp = data['result']['data'][0]['timestamp'];
            now_timestamp = datetime.now()
            sec = now_timestamp - datetime.fromtimestamp(timestamp)

            print("{}: total mined {} blocks, latest mined block at {}, {} ago".format(address, total, datetime.fromtimestamp(timestamp), str(sec)))

