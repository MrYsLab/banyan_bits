"""
simple_asyncio_echo_server.py

 Copyright (c) 20229 Alan Yorinks All right reserved.

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
import asyncio
import sys
from python_banyan.banyan_base_aio import BanyanBaseAIO


class EchoServer(BanyanBaseAIO):
    """
    This class is a simple BanyanBaseAIO asyncio_echo_client_server server

    To run the client/server demo, start the backplane and a monitor.
    Next, start the server and finally start the client. View the monitor output.
    """
    def __init__(self):

        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)

        # initialize the parent
        super(EchoServer, self).__init__(process_name='EchoServer',
                                         event_loop=self.event_loop)
        try:
            self.event_loop.run_until_complete(self.startup())
        except KeyboardInterrupt:
            sys.exit(0)

    async def startup(self):
        """
        Kick off the receive loop
        """
        await self.begin()
        # subscribe to receive 'asyncio_echo_client_server' messages from the client
        await self.set_subscriber_topic('asyncio_echo_client_server')

        # wait for messages to arrive
        try:
            await self.receive_loop()
        except KeyboardInterrupt:
            await self.clean_up()
            sys.exit(0)

    async def incoming_message_processing(self, _topic, payload):
        """
        Process incoming messages from the client
        :param _topic: message topic
        :param payload: message payload
        """
        # republish the message with a topic of reply
        await self.publish_payload(payload, 'reply')

        # extract the message number from the payload
        print('Message number:', payload['message_number'])


def echo_server():
    EchoServer()


if __name__ == '__main__':
    echo_server()
