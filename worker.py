import time

from redis import Redis
from redis.exceptions import ConnectionError
from rq import Connection, Queue, Worker
import tomllib

from dplexapi.dcut import CutterInterface

with open("config.toml", mode="rb") as fp:
    cfg = tomllib.load(fp)

cutter = CutterInterface(cfg['fileserver'])

#redis_connection = Redis(host='localhost',port=6379,password=cfg['redispw'])
redis_connection = Redis(host='redis',port=6379)

if __name__ == '__main__':
    for i in range(10):
        try:
            with Connection(redis_connection):
                print(f"Worker connecting to redis ...")
                worker = Worker(Queue('VueCutter'))
                worker.work()
                break
        except (ConnectionError, ConnectionRefusedError) as err:
        #except Exception as err:
            print(str(err), f"... retry {i+1}/10 ...")
            time.sleep(5)
    print(f"giving up ... QuartCutter Worker Execution ended.")

#redis.exceptions.ConnectionError
