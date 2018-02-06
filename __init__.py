# no

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import LOG
from os.path import dirname, join
try:
    import yagmail
except ImportError:
    yagmail = None

__author__ = 'jarbas'


class DictationSkill(MycroftSkill):

    def __init__(self):
        super(DictationSkill, self).__init__()
        self.dictating = False
        self.parser = None
        self.words = ""
        self.dictation_name = None
        self.dictation_words = []
        path = join(dirname(__file__), "vocab", self.lang,
                    "DictationKeyword.voc")
        with open(path, 'r') as voc_file:
            for line in voc_file.readlines():
                parts = line.strip().split("|")
                entity = parts[0]
                self.dictation_words.append(entity)
                for alias in parts[1:]:
                    self.dictation_words.append(alias)
        # private email
        if yagmail is not None:
            mail_config = self.config_core.get("email", {})
            self.email = mail_config.get("email")
            self.password = mail_config.get("password")

    def initialize(self):

        start_dict_intent = IntentBuilder("StartDictationIntent")\
            .require("StartKeyword").require("DictationKeyword").build()

        self.register_intent(start_dict_intent,
                             self.handle_start_dictation_intent)

        stop_dict_intent = IntentBuilder("StopDictationIntent") \
            .require("StopKeyword").require("DictationKeyword").build()

        self.register_intent(stop_dict_intent,
                             self.handle_stop_dictation_intent)

        read_dict_intent = IntentBuilder("ReadDictationIntent") \
            .require("ReadKeyword").require("DictationKeyword").build()

        self.register_intent(read_dict_intent,
                             self.handle_read_last_dictation_intent)

    def handle_start_dictation_intent(self, message):
        if not self.dictating:
            self.words = ""
            self.dictating = True
            self.speak_dialog("start", expect_response=True)
        else:
            self.speak_dialog("already_dictating", expect_response=True)

    def handle_stop_dictation_intent(self, message):
        if self.dictating:
            self.dictating = False
            self.speak_dialog("stop")
            self.send()
        else:
            self.speak_dialog("not_dictating")

    def handle_read_last_dictation_intent(self, message):
        self.speak_dialog("dictation")
        self.speak(self.words)

    def send(self):
        title = "Mycroft Dictation Skill"
        body = " ".join(self.words)
        # try private sending
        if yagmail is not None and self.email and self.password:
            with yagmail.SMTP(self.email, self.password) as yag:
                yag.send(self.email, title, body)
        else:
            # else use mycroft home
            self.send_email(title, body)

        LOG.info("Dictation sent")
        self.speak_dialog("sent")

    def stop(self):
        if self.dictating:
            self.dictating = False
            self.send()

    def check_for_intent(self, utterance):
        # check if dictation intent will trigger
        for word in self.dictation_words:
            if word in utterance:
                return True
        return False

    def converse(self, utterances, lang="en-us"):
        if self.dictating:
            if self.check_for_intent(utterances[0]):
                return False
            else:
                self.words += (utterances[0]) + "\n"
                self.speak("", expect_response=True)
                LOG.info("Dictating: " + utterances[0])
                return True
        else:
            return False


def create_skill():
    return DictationSkill()

