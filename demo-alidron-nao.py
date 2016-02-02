# -*- coding: utf-8 -*-

# Copyright (c) 2015-2016 Contributors as noted in the AUTHORS file
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from naoutil import broker, memory
from naoutil.naoenv import make_environment

from isac import IsacNode, IsacValue

import random
import signal
import sys
import time
from functools import partial
from isac.tools import green

BUTTON_URI = 'sensor://nucleo-sensor-demo/button'
BLUE_LIGHT_ON_URI = 'action://nucleo-sensor-demo/led/blue/on'
BLUE_LIGHT_OFF_URI = 'action://nucleo-sensor-demo/led/blue/off'
LAMP_URI = 'zwave://0xdefbc93b.power_strip001/switch_binary/1/switch'

class Demo(object):

    def __init__(self, env):
        self.env = env
        self.nb_touch = 0
        self.alidron_do_next = None

        self.node = IsacNode('demo-nao')
        green.signal(signal.SIGTERM, partial(self.sigterm_handler))

        self.values = {}
        self._make_value(BUTTON_URI)
        self._make_value(BLUE_LIGHT_ON_URI)
        self._make_value(BLUE_LIGHT_OFF_URI)
        self._make_value(LAMP_URI)

        self.env.tts.setLanguage('French')
        # self.env.memory.declareEvent('Alidron/demo/test')
        # self.env.memory.raiseEvent('Alidron/demo/test', self.nb_touch)
        # self.env.alife.setState('disabled')
        self.env.alife.setRobotOffsetFromFloor(0.75)
        # self.env.motion.stiffnessInterpolation(['Head', 'RArm', 'LArm'], 1.0, 1.0)

        memory.subscribeToEvent('blueLight', self.naoqi_callback)
        memory.subscribeToEvent('lamp', self.naoqi_callback)
        memory.subscribeToEvent('alidronDo', self.naoqi_callback)
        # memory.subscribeToEvent('RightBumperPressed', self.naoqi_callback) # This bumper is crunchy
        memory.subscribeToEvent('LeftBumperPressed', self.naoqi_callback)

    def naoqi_callback(self, event_name, value, message):
        print "Event", event_name, value
        try:
            if event_name in ['blueLight', 'lamp']:
                if event_name == 'blueLight':
                    self.alidron_do_next = {
                        'uri': BLUE_LIGHT_ON_URI if int(value) else BLUE_LIGHT_OFF_URI,
                        'value' : None
                    }
                elif event_name == 'lamp':
                    self.alidron_do_next = {
                        'uri': LAMP_URI,
                        'value' : bool(int(value))
                    }

                if int(value):
                    self.env.alife.switchFocus('alidrondemo-899c5f/tiens')
                else:
                    self.env.alife.switchFocus('alidrondemo-899c5f/et_voila')

            elif event_name == 'alidronDo':
                print 'status', self.alidron_do_next
                self.values[self.alidron_do_next['uri']].value = self.alidron_do_next['value']

            elif event_name in ['RightBumperPressed', 'LeftBumperPressed']:
                # self.env.alife.stopAll()
                self.env.alife.switchFocus('alidrondemo-899c5f/listen')


        except Exception, ex:
            print ex

    def _make_value(self, uri):
        self.values[uri] = IsacValue(self.node, uri, survey_last_value=False, survey_static_tags=False)
        self.values[uri].observers += self.value_update

    def value_update(self, iv, value, ts, tags):
        print '>>>', iv.uri, value
        if iv.uri == BUTTON_URI:
            self.nb_touch += 1

            self.blink_eyes()
            # self.env.alife.stopAll()

            if self.nb_touch == 1:
                # self.env.alife.switchFocus('alidrondemo-899c5f/button_1')
                to_say = '^startTag(hey) Eh! Tu as touché ce bouton! ^wait(hey)'
            elif self.nb_touch == 2:
                # self.env.alife.switchFocus('alidrondemo-899c5f/button_2')
                to_say = '^startTag(you) Tu as encore touché à ce bouton ! ^waitTag(you)'
            elif self.nb_touch == 3:
                # self.env.alife.switchFocus('alidrondemo-899c5f/button_3')
                to_say = '^startTag(please) Veux-tu bien arrêter de toucher à ce bouton ? ^waitTag(please)'
            else:
                # self.env.alife.switchFocus('alidrondemo-899c5f/button_' + str(random.randint(4, 7)))
                sentences = [
                    '^startTag(no) Arrête, je te l\'ai déjà dit ! ^waitTag(no)',
                    '^startTag(please) Arrête de toucher à ce bouton ! ^waitTag(please)',
                    '^startTag(explain) Tu es vraiment têtu ^waitTag(explain)',
                    '^startTag(you) Touche donc tes boutons ^waitTag(you)',
                ]
                to_say = random.choice(sentences)


            # id_ = self.env.animatedSpeech.post.say(to_say, {"bodyLanguageMode":"contextual"})
            # self.env.animatedSpeech.wait(id_, 0)
            self.env.animatedSpeech.say(to_say)
            print 'done'

    def blink_eyes(self):
        rDuration = 0.05
        self.env.leds.post.fadeRGB("FaceLed0", 0x000000, rDuration)
        self.env.leds.post.fadeRGB("FaceLed1", 0x000000, rDuration)
        self.env.leds.post.fadeRGB("FaceLed2", 0xffffff, rDuration)
        self.env.leds.post.fadeRGB("FaceLed3", 0x000000, rDuration)
        self.env.leds.post.fadeRGB("FaceLed4", 0x000000, rDuration)
        self.env.leds.post.fadeRGB("FaceLed5", 0x000000, rDuration)
        self.env.leds.post.fadeRGB("FaceLed6", 0xffffff, rDuration)
        self.env.leds.fadeRGB("FaceLed7", 0x000000, rDuration)
        time.sleep(0.1)
        self.env.leds.fadeRGB("FaceLeds", 0xffffff, rDuration)


    def sigterm_handler(self):
        # self.env.motion.rest()
        # self.env.alife.setState('solitary')
        self.node.shutdown()
        sys.exit(0)

if __name__ == '__main__':
    with broker.create('demo') as myBroker:
        env = make_environment(None)
        demo = Demo(env)

        try:
            demo.node.serve_forever()
        except KeyboardInterrupt:
            # demo.env.motion.rest()
            # demo.env.alife.setState('solitary')
            demo.node.shutdown()
            green.sleep(1)
