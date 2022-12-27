#!/usr/bin/env python3

"""
  This is file implements a  bidirectional WebSocket Gateway between node-red flows and
  python_banyan messaging.

 Copyright (c) 2019 Alan Yorinks All right reserved.

 Python Banyan is free software; you can redistribute it and/or
 modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
 Version 3 as published by the Free Software Foundation; either
 or (at your option) any later version.
 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.

 You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
 along with this library; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""

import argparse
import asyncio
import datetime
import json
import logging
import pathlib
import signal
import sys
import websockets

from python_banyan.banyan_base_aio import BanyanBaseAIO


class NrWsGateway(BanyanBaseAIO):
    """
    This class is a gateway between a node-red websocket client and the
    Banyan network.

    """

    def __init__(self, subscription_list, back_plane_ip_address=None,
                 subscriber_port='43125',
                 publisher_port='43124', process_name='nr_pb_Gateway',
                 event_loop=None, server_ip_port=9000, log=False):
        """
        These are all the normal base class parameters
        :param back_plane_ip_address: banyan_base back_planeIP Address -
                                      if not specified, it will be set to the
                                      local computer.
        :param subscriber_port: banyan_base back plane subscriber port.
               This must match that of the banyan_base backplane
        :param publisher_port: banyan_base back plane publisher port.
                               This must match that of the banyan_base backplane.
        :param process_name: Component identifier in banner at component startup.
        :param connect_time: a short delay to allow the component to connect to the Backplane
        :param event_loop: asyncio event loop. If none specified, one will be
                           auto-assigned.
        :param server_ip_port: WebSocket port number
        :param log: switch to enable logging
        """

        # set up logging if requested
        self.log = log
        self.event_loop = event_loop

        # a kludge to shut down the socket on control C
        self.wsocket = None

        self.publisher_topic = None

        if self.log:
            fn = str(pathlib.Path.home()) + "/nrpbgw.log"
            self.logger = logging.getLogger(__name__)
            logging.basicConfig(filename=fn, filemode='w', level=logging.DEBUG)
            sys.excepthook = self.my_handler

        # initialize the base class
        super(NrWsGateway, self).__init__(subscriber_list=subscription_list,
                                        back_plane_ip_address=back_plane_ip_address,
                                        subscriber_port=subscriber_port,
                                        publisher_port=publisher_port,
                                        process_name=process_name,
                                        event_loop=self.event_loop)

        # save the server port number
        self.server_ip_port = server_ip_port

        # array of active sockets
        self.active_sockets = []
        try:
            self.start_server = websockets.serve(self.wsg,
                                                 '0.0.0.0',
                                                 self.server_ip_port)
            print('WebSocket using: ' + self.back_plane_ip_address
                  + ':' + self.server_ip_port)
            # start the websocket server and call the main task, wsg
            self.event_loop.run_until_complete(self.start_server)
            self.event_loop.create_task(self.wakeup())
            self.event_loop.run_forever()
        except (websockets.exceptions.ConnectionClosed,
                RuntimeError,
                KeyboardInterrupt):
            if self.log:
                logging.exception("Exception occurred", exc_info=True)
            self.event_loop.stop()
            self.event_loop.close()

    async def wakeup(self):
        while True:
            try:
                await asyncio.sleep(1)
            except KeyboardInterrupt:
                for task in asyncio.Task.all_tasks():
                    task.cancel()
                await self.wsocket.close()
                self.event_loop.stop()
                self.event_loop.close()
                sys.exit(0)

    async def wsg(self, websocket, _path):
        """
        This method handles connections and will be used to send
        messages to the client
        :param websocket: websocket for connected client
        :param _path: required, but unused
        """
        data = None
        self.wsocket = websocket
        self.publisher_topic = "to_arduino_gateway"
        # start up banyan
        await self.begin()

        # wait for a connection
        # try:
        #     data = await websocket.recv()
        # except websockets.exceptions.ConnectionClosedOK:
        #     pass

        # create a task to receive messages from the client
        await asyncio.create_task(self.receive_data(websocket))

        # create the banyan receive loop
        # await self.start_the_receive_loop()

    async def receive_data(self, websocket):
        """
        This method processes a received WebSocket command message
        and translates it to a Banyan command message.
        :param websocket: The currently active websocket
        """
        while True:
            try:
                data = await websocket.recv()

                data = json.loads(data)
                pub_data = data['payload']
            except (websockets.exceptions.ConnectionClosed, TypeError):
                break
            print(f'pub_data = {pub_data}')
            await self.publish_payload(pub_data, self.publisher_topic)

    async def incoming_message_processing(self, topic, payload):
        """
        This method converts the incoming messages to ws messages
        and sends them to the ws client

        :param topic: Message Topic string.

        :param payload: Message Data.
        """
        x = {'payload': payload}
        ws_data = json.dumps(x)
        print(x)

        await self.wsocket.send(ws_data)

    def my_handler(self, _the_type, _value, _tb):
        """
        For logging uncaught exceptions
        :param _the_type: exception type
        :param _value: exception value
        :param _tb: exception traceback
        :return:
        """
        self.logger.exception("Uncaught exception: {0}".format(str(value)))


def nr_ws_gateway():
    # allow user to bypass the IP address auto-discovery. This is necessary if the component resides on a computer
    # other than the computing running the backplane.

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    # allow the user to specify a name for the component and have it shown on the console banner.
    # modify the default process name to one you wish to see on the banner.
    # change the default in the derived class to set the name

    parser.add_argument("-e", dest='event_loop', default="None",
                        help="OptionalAsyncio event loop")
    parser.add_argument("-i", dest="server_ip_port", default="9000",
                        help="Set the WebSocket Server IP Port number")
    parser.add_argument("-l", dest="log", default="False",
                        help="Set to True to turn logging on.")
    parser.add_argument("-n", dest="process_name", default="NodeRed WebSocket Gateway",
                        help="Set process name in banner")
    parser.add_argument("-p", dest="publisher_port", default='43124',
                        help="Publisher IP port")
    parser.add_argument("-s", dest="subscriber_port", default='43125',
                        help="Subscriber IP port")

    args = parser.parse_args()
    
    # create a subscriber topic by concatenating the WebSocket IP port number with
    # 'to_node_red_'
    
    # subscriber_topic = 'from_arduino_gateway' + args.server_ip_port
    subscriber_topic = 'from_arduino_gateway'
    subscription_list = [subscriber_topic]

    kw_options = {
        'publisher_port': args.publisher_port,
        'subscriber_port': args.subscriber_port,
        'process_name': args.process_name,
        'server_ip_port': args.server_ip_port,
    }

    log = args.log.lower()
    if log == 'false':
        log = False
    else:
        log = True
    kw_options['log'] = log

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address
    if args.event_loop == 'None':
        kw_options['event_loop'] = None

    # get the event loop
    # this is for python 3.8
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)

    try:
        NrWsGateway(subscription_list, **kw_options)
    except KeyboardInterrupt:
        for task in asyncio.Task.all_tasks():
            task.cancel()
        loop.stop()
        loop.close()
        sys.exit(0)


def signal_handler(_sig, _frame):
    print('Exiting Through Signal Handler')
    sys.exit(0)


# listen for SIGINT
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    nr_ws_gateway()
