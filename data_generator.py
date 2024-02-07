import argparse
import datetime
import json
import math
import random
import requests
import socket
import time

HOSTNAME = socket.gethostname()

VALUE_ARRAY = [
   -1 * math.pi, -1 * math.pi/2, -1 * math.pi/3,
   -1,
   -1 * math.pi/4, -1 * math.pi/6, -1 * math.pi/8,
   0,
   math.pi/8, math.pi/6, math.pi/4,
   1,
   math.pi/3, math.pi/2, math.pi,
   math.pi, math.pi/2, math.pi/3,
   1,
   math.pi/4, math.pi/6, math.pi/8,
   0,
   -1 * math.pi/8, -1 * math.pi/6, -1 * math.pi/4,
   -1,
   -1 * math.pi/3, -1 * math.pi/2, -1 * math.pi
]


def __put_data(conn:str, payload:str=None, exception:bool=False,)->bool:
    """
    Publish data to AnyLog using PUT
    :args:
        conn:str - REST connection information
        payload:str - content to publish into AnyLog
        exception:bool - whether to print exceptions
    :params:
        status:bool
        headers:dict - REST header information
        r:requests.PUT - result for PUT request
    :return:
        status
    """
    status = False
    headers = {
        'type': 'json',
        'dbms': "lsd_lab",
        'table': "rand_data",
        'mode': "streaming",
        'Content-Type': 'text/plain'
    }

    try:
        r = requests.put(url=f'http://{conn}', headers=headers, data=payload)
    except Exception as error:
        if exception is True:
            print(f"Failed to PUT data against {conn} (Error: {error})")
    else:
        if int(r.status_code) != 200:
            if exception is True:
                print(f"Failed to PUT data against {conn} (Network Error: {r.status_code})")
        else:
            status = True

    return status


def __data_generator(batch_size:int=10, sleep:float=0.5, latest_value:float=None, amplitude:float=0)->(float, str):
    """
    Generate data set to be stored in AnyLog
    :args:
        batch_size:int - number of value sets per list
        sleep:float - wait time per row
        latest_value:float - latest value inputted by user
        amplitude:float - by default, the value is between -pi and pi for a cosine graph. The amplitude allows for users to change
        the amplitude of data coming in.
    :params:
        payloads:list - data to be stored in AnyLog
        value:float - generated value
    :return:
        latest_value and payloads as a list of JSON strings
    """
    payloads = []
    for i in range(batch_size):
        status = False

        while status is False:
            value = random.choice(VALUE_ARRAY)
            if amplitude != 0:
                value = value * random.choice([1 - amplitude, 1, 1 + amplitude])
            if value != latest_value:
                latest_value = value
                status = True

        payloads.append({
            "hostname": HOSTNAME,
            "timestamp": datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "value": value
        })

        time.sleep(sleep)

    return latest_value, json.dumps(payloads)



def main():
    parse = argparse.ArgumentParser()
    parse.add_argument('conn', type=str, default=None, help='REST connection information')
    parse.add_argument('--total-rows', type=int, default=100, help='Total rows to insert. If set to 0 run continuously')
    parse.add_argument('--batch-size', type=int, default=10, help='Number of rows per batch')
    parse.add_argument('--sleep', type=float, default=0.5, help='Wait time between each row')
    parse.add_argument('--amplitude', type=float, default=0, help='by default, the value is between -pi and pi for a cosine graph. The amplitude allows for users to change the amplitude of data coming in.')
    args = parse.parse_args()

    latest_value = None
    total_rows = 0
    is_last = False

    while True:
        latest_value, payloads = __data_generator(batch_size=args.batch_size, sleep=args.sleep,
                                                  latest_value=latest_value, amplitude=args.amplitude)
        __put_data(conn=args.conn, payload=payloads)

        if args.total_rows >  0:
            if is_last is True:
                exit(1)
            total_rows += args.batch_size
            if args.total_rows - total_rows < args.batch_size:
                args.batch_size = args.total_rows - total_rows
                is_last = True


if __name__ == '__main__':
    main()
