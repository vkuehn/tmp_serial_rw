import json
import os
from time import sleep

import tornado.web
import tornado.websocket
import tornado.httpserver
from tornado.ioloop import IOLoop

from resources_local import bye
from resources_local import Logger
from resources_local import SerialHandler

CONFIG_NAME = 'robot_config.json'
NODE_NAME = 'base'
ROBOT_NAME = 'OpenBot'

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

sh = SerialHandler()


# helper------------------------------------------
def check_message_from_socket(msg):
    try:
        message = json.loads(msg)
        if debug:
            log(message)
        if 'motors' in message:
            serial_data_to = 'c' + str(message['motors']['left']) + ',' + str(message['motors']['right'])
            sh.write(serial_data_to)
            sleep(0.1)
    except Exception as e:
        log('error %s', e)

# end of Helper-------------------------------------------------------


class ConfigHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(json.dumps(robotConfig[ROBOT_NAME]))


class IndexPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class ShutdownHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("shutdown.html", title="Shutdown", item="shutdown of " + ROBOT_NAME)
        bye.bye(__file__)


# -- async
async def websocket_write_loop():
    log("start websocket_write_loop")
    while True:
        sh.read()
        serial_data_from = str(sh.data)
        if len(serial_data_from) > 0:
            if debug:
                log('serial read:' + serial_data_from)
            [con.write_message(serial_data_from) for con in WebSocketHandler.connections]


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    connections = set()

    def open(self):
        self.connections.add(self)
        log('new connection was opened')

    def on_message(self, message):
        if debug:
            log('on_message: received ' + str(message))
        check_message_from_socket(message)

    def on_close(self):
        self.connections.remove(self)
        log('connection closed')


class WebApplication(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', IndexPageHandler),
            (r"/config", ConfigHandler),
            (r"/shutdown", ShutdownHandler),
            (r'/websocket', WebSocketHandler),
            (r'/(.*)', tornado.web.StaticFileHandler, {'path': resourcesWeb})
        ]

        settings = {
            'debug': debug,
            'static_path': resourcesWeb,
            'template_path': 'templates'
        }
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == '__main__':
    try:
        if debug:
            log('debug is true')
        log('init')
        log('Start web on ' + ROBOT_NAME + ' address ' + SERVER_IP + ':' + str(SERVER_PORT))
        ws_app = WebApplication()
        server = tornado.httpserver.HTTPServer(ws_app)
        server.listen(SERVER_PORT)

        #IOLoop.current().spawn_callback(websocket_write_loop)
        IOLoop.instance().start()
    except KeyboardInterrupt:
        log('Keyboard Interrupt received wait 3 seconds')
        sleep(3)
    except Exception as e:
        log('error:' + str(e))
    finally:
        bye.bye(__file__)
