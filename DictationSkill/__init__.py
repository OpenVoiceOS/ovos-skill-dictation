# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.


from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
import time
import os

__author__ = 'jarbas'

logger = getLogger(__name__)


class DictationSkill(MycroftSkill):

    def __init__(self):
        super(DictationSkill, self).__init__(name="DictationSkill")
        self.dictating = False
        self.words = ""
        self.path = "/home/user/jarbas-core/mycroft/skills/DictationSkill/dictations"
        self.path = os.path.dirname(__file__) + "/dictations"
        self.reload_skill = False
        # check if folders exist
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def initialize(self):

        start_dict_intent = IntentBuilder("StartDictationIntent")\
            .require("StartDictationKeyword").build()

        self.register_intent(start_dict_intent,
                             self.handle_start_dict_intent)

        read_dict_intent = IntentBuilder("ReadDictationIntent") \
            .require("ReadDictationKeyword").build()

        self.register_intent(read_dict_intent,
                             self.handle_read_last_dictation_intent)

    def handle_start_dict_intent(self, message):
        self.dictating = True
        self.speak("Dictation Mode Started")
        self.words = ""

    def handle_read_last_dictation_intent(self, message):
        self.speak_dialog("dictation")
        self.speak(self.words)

    def save(self):
        # save
        #TODO let user set savefile name
        path = self.path + "/" + str(time.time()) + ".txt"
        wfile = open(path, "w")
        wfile.write(self.words)
        wfile.close()

    def stop(self):
        pass

    def Converse(self, transcript, lang="en-us"):
        if self.dictating:
            #TODO better stop handling, using keyword.voc
            if "stop" in transcript[0] or "end" in transcript[0]:
                self.save()
                self.speak("Dictation Mode Stopped")
                self.dictating = False
            else:
                self.words += (transcript[0]) + "\n"
            return True
        else:
            return False


def create_skill():
    return DictationSkill()