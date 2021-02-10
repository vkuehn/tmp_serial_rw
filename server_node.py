import json
import multiprocessing
import os

from concurrent.futures import ThreadPoolExecutor
from time import sleep

from tornado import ioloop
from tornado import web, websocket

from resources_local import bye
from resources_local import Logger
from resources_local import SerialHandler

CONFIG_NAME = 'robot_config.json'
NODE_NAME = 'base'
ROBOT_NAME = 'OpenBot'
CMD_STOP = "server:stop"

logger = Logger(ROBOT_NAME)
log = logger.log

currentPath = os.path.dirname(os.path.abspath(__file__))
configPath = currentPath + '/config'
resourcesWeb = currentPath + '/resources_web'
with open(configPath + '/' + CONFIG_NAME) as json_data:
    robotConfig = json.load(json_data)

debug = bool(robotConfig[ROBOT_NAME]['debug'])
SERVER_IP = str(robotConfig[ROBOT_NAME]['ip'])
SERVER_PORT = robotConfig[ROBOT_NAME]['port']

# -- Serial -----------------------------------------------
sh = SerialHandler()
qSerialTo = multiprocessing.Queue()
qSerialFrom = multiprocessing.Queue()


def check_message_from_socket(msg):
    try:
        message = json.loads(msg)
        if debug:
            log(message)
        if 'motors' in message:
            serial_data_to = 'c' + str(message['motors']['left']) + ',' + str(message['motors']['right'])
            qSerialTo.put(serial_data_to)
    except Exception as e:
        log('error %s', e)


def process_serial_worker():
    log("start process_serial_worker")
    running = True
    while running:
        _msg_to_ser = qSerialTo.get()
        if str(_msg_to_ser).startswith(CMD_STOP):
            running = False
        sh.write(_msg_to_ser)
        sh.read()
        serial_data_from = str(sh.data)
        if len(serial_data_from) > 0:
            if debug:
                log('serial read:' + serial_data_from)
            qSerialFrom.put(str(serial_data_from))
        sleep(0.1)
    log("stop process_serial_worker")


# -- web ------------------------------------------------------------
def periodic_websocket_write_loop():
    # no logs in periodics !
    if not qSerialFrom.empty():
        serial_data_from = qSerialFrom.get()
        if len(WebSocketHandler.connections) > 0:
            [con.write_message(serial_data_from) for con in WebSocketHandler.connections]



class ConfigHandler(web.RequestHandler):
    def get(self):
        self.write(json.dumps(robotConfig[ROBOT_NAME]))


class IndexPageHandler(web.RequestHandler):
    def get(self):
        self.render("index.html")


class ShutdownHandler(web.RequestHandler):
    def get(self):
        self.render("shutdown.html", title="Shutdown", item="shutdown of " + ROBOT_NAME)
        bye.bye(__file__)


class WebSocketHandler(websocket.WebSocketHandler):
    connections = set()

    def open(self):
        self.connections.add(self)
        log('new connection was opened')

    def on_message(self, message):
        if debug:
            log('ws message: ' + str(message))
        check_message_from_socket(message)

    def on_close(self):
        self.connections.remove(self)
        log('connection closed')


class WebApplication(web.Application):
    def __init__(self, autostart=True):
        handlers = [
            (r'/', IndexPageHandler),
            (r"/config", ConfigHandler),
            (r"/shutdown", ShutdownHandler),
            (r'/websocket', WebSocketHandler),
            (r'/(.*)', web.StaticFileHandler, {'path': resourcesWeb})
        ]

        settings = {
            'debug': debug,
            'static_path': resourcesWeb,
            'template_path': 'templates'
        }

        web.Application.__init__(self, handlers, **settings)


if __name__ == '__main__':
    if debug:
        log('debug is true')
    log('Start web on ' + ROBOT_NAME + ' address ' + SERVER_IP + ':' + str(SERVER_PORT))
    ws_app = WebApplication()
    ws_app.listen(SERVER_PORT)
    reader_executor = ThreadPoolExecutor(1)

    pW = multiprocessing.Process(target=process_serial_worker)
    pW.daemon = True

    try:
        pW.start()

        scheduler = ioloop.PeriodicCallback(callback=periodic_websocket_write_loop, callback_time=300, jitter=0.1)
        scheduler.start()

        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        # try clean stop
        for con in WebSocketHandler.connections:
            con.close()
        scheduler.stop()
        ioloop.IOLoop.instance().stop()
        qSerialFrom.close()
        qSerialTo.put(CMD_STOP)
        log('Keyboard Interrupt received wait 3 seconds')
        sleep(10)
        pW.join()
    except Exception as e:
        log('error:' + str(e))
    finally:
        bye.bye(__file__)
