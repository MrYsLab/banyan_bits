"""
simple_echo_client.py

 Copyright (c) 2016-2019 Alan Yorinks All right reserved.

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

import sys
from python_banyan.banyan_base import BanyanBase


class PinInitTester(BanyanBase):
    """
    This is a simple echo client derived from the BanyanBase class. It sends out a series of messages and expects an
    echo reply from the server.
    """

    def __init__(self):

        # initialize the parent
        super(PinInitTester, self).__init__(process_name='EchoClient')

        # accept banyan messages with the topic of reply
        self.set_subscriber_topic('set_pin_mode')

        # send the first message - make sure that the server is already started
        self.publish_payload({'init_pins': 0}, 'pin_init')

        # get the reply messages
        try:
            self.receive_loop()
        except KeyboardInterrupt:
            self.clean_up()
            sys.exit(0)

    def incoming_message_processing(self, topic, payload):
        """
        Process incoming messages received from the echo client
        :param topic: Message Topic string
        :param payload: Message Data
        """

        # When a message is received and its number is zero, finish up.
        print(topic, payload)


def pin_init_tester():
    PinInitTester()


if __name__ == '__main__':
    pin_init_tester()
