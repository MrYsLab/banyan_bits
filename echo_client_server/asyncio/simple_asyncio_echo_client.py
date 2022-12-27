"""
simple_asyncio_echo_client.py

 Copyright (c) 2022 Alan Yorinks All right reserved.

 This program is free software; you can redistribute it and/or
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


class EchoClient(BanyanBaseAIO):
    """
    This is a simple asyncio_echo_client_server client derived from the BanyanBaseAIO class.
    It sends out a series of messages and expects an
    asyncio_echo_client_server reply from the server.

    To run the demo, first start the backplane, monitor and the server.
    Finrally run the client.
    """

    def __init__(self):
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)

        # initialize the parent
        super(EchoClient, self).__init__(process_name='EchoClient',
                                         event_loop=self.event_loop)

        # sequence number of messages and total number of messages to send
        self.message_number = self.number_of_messages = 10

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
        await self.set_subscriber_topic('reply')

        # send the first message - make sure that the server is already started
        await self.publish_payload({'message_number': self.message_number}, 'asyncio_echo_client_server')

        # wait for messages to arrive
        try:
            await self.receive_loop()
        except KeyboardInterrupt:
            await self.clean_up()
            sys.exit(0)

    async def incoming_message_processing(self, topic, payload):
        """
        Process incoming messages received from the asyncio_echo_client_server client
        :param topic: Message Topic string
        :param payload: Message Data
        """

        # When a message is received and its number is zero, finish up.
        if payload['message_number'] == 0:
            print(str(self.number_of_messages) + ' messages sent and received. ')
        # bump the message number and send the message out
        else:
            self.message_number -= 1
            if self.message_number >= 0:
                await self.publish_payload({'message_number': self.message_number},
                                           'asyncio_echo_client_server')


def echo_client():
    EchoClient()


if __name__ == '__main__':
    echo_client()
