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
from mycroft.skills.intent_service import IntentParser
import os, time

__author__ = 'jarbas'

logger = getLogger(__name__)


class DictationSkill(MycroftSkill):

    def __init__(self):
        super(DictationSkill, self).__init__()
        self.dictating = False
        self.parser = None
        self.words = ""
        self.dictation_name = None
        self.path = "/home/user/jarbas-core/mycroft/skills/DictationSkill/dictations"
        self.path = os.path.dirname(__file__) + "/dictations"
        self.reload_skill = False
        # check if folders exist
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def initialize(self):

        start_dict_intent = IntentBuilder("StartDictationIntent")\
            .require("StartKeyword").require(
            "DictationKeyword").optionally("DictationFileName").build()

        self.register_intent(start_dict_intent,
                             self.handle_start_dictation_intent)

        stop_dict_intent = IntentBuilder("StopDictationIntent") \
            .require("StopKeyword").require("DictationKeyword").build()

        self.register_intent(stop_dict_intent,
                             self.handle_stop_dictation_intent)

        read_dict_intent = IntentBuilder("StopDictationIntent") \
            .require("ReadKeyword").require("DictationKeyword").build()

        self.register_intent(read_dict_intent,
                             self.handle_read_last_dictation_intent)

        self.parser = IntentParser(self.emitter)

    def handle_start_dictation_intent(self, message):
        name = message.data.get("DictationFileName")
        if not name:
            self.dictation_name = time.asctime()
        else:
            self.dictation_name = name

        if not self.dictating:
            self.words = ""
            self.dictating = True
            self.speak("Dictation Mode Started", expect_response=True)
        else:
            self.speak("Dictation is already enabled")

    def handle_stop_dictation_intent(self, message):
        if self.dictating:
            self.dictating = False
            self.speak("Dictation Mode Stopped")
            self.save()
        else:
            self.speak("I am not dictating at this moment")

    def handle_read_last_dictation_intent(self, message):
        self.speak_dialog("dictation")
        self.speak(self.words)

    def save(self):
        # save
        path = self.path + "/" + self.dictation_name + ".txt"
        with open(path, "w") as f:
            f.write(self.words)
        self.log.info("Dictation saved: " + path)
        self.speak("Dictation saved with name " + self.dictation_name)

    def stop(self):
        if self.dictating:
            self.dictating = False
            self.save()
            self.speak("Dictation Mode Stopped")

    def converse(self, utterances, lang="en-us"):
        if self.dictating:
            intent, skill_id = self.parser.determine_intent(utterances[0])
            if skill_id == self.skill_id:
                return False
            else:
                self.words += (utterances[0]) + "\n"
                self.speak("", expect_response=True)
                self.log.info("Dictating: " + utterances[0])
                return True
        else:
            return False


def create_skill():
    return DictationSkill()

