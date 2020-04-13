import yaml
import requests
from datetime import timedelta
from monitor import monitor, MiningError, RequestError
from timeloop import Timeloop

DINGTALK_URL = 'https://oapi.dingtalk.com/robot/send?access_token={}'
INITIAL_BAD_REQUEST_BAR = 10

config = yaml.load(open('config.yml'), Loader=yaml.FullLoader)
dingtalk_token = config['dingtalk_token']
time_interval = int(config['time_interval'])

bad_request_count = 0
bad_request_bar = INITIAL_BAD_REQUEST_BAR
tl = Timeloop()

def make_payload(msg, at_all = False):
    payload = {
        "msgtype": "text",
        "text": {
            "content": "ALERT: {}".format(msg)
        },
        "at": {
            "isAtAll": at_all
        }
    }
    return payload

@tl.job(interval=timedelta(seconds=time_interval))
def monitor_job():
    global bad_request_count
    global bad_request_bar
    try:
        monitor('miner_list.txt')
        bad_request_count = 0
        bad_request_bar = INITIAL_BAD_REQUEST_BAR
    except MiningError as err:
        bad_request_count = 0
        bad_request_bar = INITIAL_BAD_REQUEST_BAR
        requests.post(DINGTALK_URL.format(dingtalk_token), json=make_payload(err.message))
    except RequestError:
        bad_request_count += 1
        if bad_request_count >= bad_request_bar:
            requests.post(DINGTALK_URL.format(dingtalk_token), json=make_payload("bad request on ConfluxScan API for {} times.".format(bad_request_count)))
            bad_request_bar *= 2
    except Exception as e:
        print('Unexpected error: ', e)
        requests.post(DINGTALK_URL.format(dingtalk_token), json=make_payload("Unexpected error: {}.".format(str(e))))
        raise

tl.start(block=True)
