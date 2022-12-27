"""

 Copyright (c) 2022 Alan Yorinks All right reserved.

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

import sys
from python_banyan.banyan_base import BanyanBase


class PinInit(BanyanBase):
    """
    This class subscribes to receive messages to issue OneGPIO messages to set pin modes.
    """

    def __init__(self, publisher_topic='to_arduino_gateway', subscription_topic='pin_init'):
        """
        :param publisher_topic: topic to publish OneGPIO set_pin messages to

        :param subscription_topic: topic to subscribe to receive messages
        """

        # initialize the parent
        super(PinInit, self).__init__(process_name='Pin Initializer')

        self.publisher_topic = publisher_topic

        # subscribe to receive pin init messages
        self.set_subscriber_topic(subscription_topic)

        # digital output pins to be setup
        self.digital_output_pins = ({'pin': 9, 'tag': 'blue'},
                                    {'pin': 10, 'tag': 'green'},
                                    {'pin': 11, 'tag': 'red'})

        # command for digital output
        self.dig_out_command = {"command": "set_mode_digital_output", "pin": "PIN",
                                "tag": "TAG"}

        # pins to be setup for pwm output
        self.pwm_output_pins = ({'pin': 6, 'tag': 'white'},)

        # command for pwm output
        self.pwm_out_command = {"command": "set_mode_pwm", "pin": "PIN",
                                "tag": "TAG"}

        # pins to be setup for analog input
        self.analog_input_pins = ({'pin': 2, 'tag': 'potentiometer'},)

        # command for analog input
        self.analog_in_command = {"command": "set_mode_analog_input", "pin": "PIN",
                               "tag": "TAG"}
        # pin to be setup for servo mode
        self.servo_pins = ({'pin': 5, 'tag': 'servo'},)

        # command for servo mode
        self.servo_command = {"command": "set_mode_servo", "pin": "PIN",
                                "tag": "TAG"}

        # wait for messages to arrive
        try:
            self.receive_loop()
        except KeyboardInterrupt:
            self.clean_up()
            sys.exit(0)

    def incoming_message_processing(self, _topic, _payload):
        """
        Process incoming messages from the client
        :param _topic: message topic
        :param _payload: message payload
        """

        # send out mode setting commands
        self.pin_tag_messages(self.dig_out_command, self.digital_output_pins)
        self.pin_tag_messages(self.pwm_out_command, self.pwm_output_pins)
        self.pin_tag_messages(self.analog_in_command, self.analog_input_pins)
        self.pin_tag_messages(self.servo_command, self.servo_pins)

    def pin_tag_messages(self, command, pins):
        for pin_tags in pins:
            try:
                command['pin'] = pin_tags['pin']
                command['tag'] = pin_tags['tag']
            except TypeError:
                raise

            self.publish_payload(command, self.publisher_topic)


def pin_init():
    PinInit()


if __name__ == '__main__':
    pin_init()
