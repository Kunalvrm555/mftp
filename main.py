import update
import requests
import os
from concurrent.futures import ThreadPoolExecutor
import tornado.web
import tornado.ioloop
from tornado import gen
import requests
import datetime
import traceback
from datetime import datetime as dt, timedelta

requests.packages.urllib3.disable_warnings()

ioloop = tornado.ioloop.IOLoop.current()
UPDATE_PERIOD = 1000 * 60 * 1 # 1 minute

session = requests.Session()

@gen.coroutine
def run_updates():
    def func():
        try:
            print ('Checking notices...')
            update.check_notices(session)
        except:
            print ("Unhandled error occured :\n{}".format(traceback.format_exc()))

    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            yield gen.with_timeout(datetime.timedelta(UPDATE_PERIOD/1000.0),
                                   executor.submit(func))
        now = dt.now() + timedelta(hours=5, minutes=30) # Add 5 hours and 30 minutes for GMT +05:30
        current_time = now.strftime("%H:%M:%S")
        print ('run_updates done, last --> t= ' + current_time)
    except gen.TimeoutError:
        print ('run_updates timed out')


class PingHandler(tornado.web.RequestHandler):
    def head(self):
        return

    def get(self):
        return

if __name__ == '__main__':
    app = tornado.web.Application([
        (r'/', PingHandler)
    ])
    app.listen(os.environ['PORT'])
    run_updates()
    tornado.ioloop.PeriodicCallback(run_updates,
                                    UPDATE_PERIOD).start()
    ioloop.start()
