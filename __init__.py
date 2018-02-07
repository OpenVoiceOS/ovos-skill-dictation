# no

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import LOG
from os.path import dirname, join
import requests

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
        self.dictation_stack = []
        self.words = ""
        self.dictation_name = None
        self.dictation_words = []
        if "url" not in self.settings:
            self.settings["url"] = "http://165.227.224.64:8080"
        if "completions" not in self.settings:
            self.settings["completions"] = 2
        self.read_vocab("DictationKeyword.voc")
        self.read_vocab("AutocompleteKeyword.voc")
        # private email
        if yagmail is not None:
            mail_config = self.config_core.get("email", {})
            self.email = mail_config.get("email")
            self.password = mail_config.get("password")

    def read_vocab(self, name="DictationKeyword.voc"):
        path = join(dirname(__file__), "vocab", self.lang,
                    name)
        with open(path, 'r') as voc_file:
            for line in voc_file.readlines():
                parts = line.strip().split("|")
                entity = parts[0]
                self.dictation_words.append(entity)
                for alias in parts[1:]:
                    self.dictation_words.append(alias)

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

        complete_intent = IntentBuilder("AutoCompleteDictationIntent") \
            .require("AutocompleteKeyword").require(
            "DictationKeyword").build()

        self.register_intent(complete_intent,
                             self.handle_autocomplete_intent)

        undo_intent = IntentBuilder("UndoDictationIntent") \
            .require("UndoKeyword").require(
            "DictationKeyword").build()

        self.register_intent(undo_intent,
                             self.handle_undo_intent)

    def auto_complete(self, text):
        url = self.settings["url"] + "/generate?start_text=" + text + "&n=" + str(self.settings["completions"])
        response = requests.get(url)
        return dict(response.json())

    def handle_undo_intent(self, message):
        if self.dictating and len(self.dictation_stack):
            last = self.dictation_stack.pop()
            self.words = " ".join(self.dictation_stack)
            self.speak_dialog("undo")
        else:
            self.speak_dialog("undo.error")

    def handle_autocomplete_intent(self, message):
        if self.dictating:
            try:
                result = self.auto_complete(self.words)
                time = result["time"]
                LOG.info("auto completed in " + time)
                completions = result["completions"]
                self.words = self.words.rstrip("\n") + (completions[0]) + "\n"
                self.speak(completions[0], expect_response=True)
                LOG.info("Dictating: " + completions[0])
                self.dictation_stack.append(completions[0])
            except Exception as e:
                LOG.error(e)
                self.speak_dialog("autocomplete.fail")
        else:
            self.speak_dialog("not_dictating")

    def handle_start_dictation_intent(self, message):
        if not self.dictating:
            self.words = ""
            self.dictating = True
            self.speak_dialog("start", expect_response=True)
        else:
            self.speak_dialog("already_dictating", expect_response=True)
        self.set_context("DictationKeyword", "dictation")

    def handle_stop_dictation_intent(self, message):
        if self.dictating:
            self.dictating = False
            self.speak_dialog("stop")
            self.send()
        else:
            self.speak_dialog("not_dictating")
        self.remove_context("DictationKeyword")

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
            # keep intents working without dictation keyword being needed
            self.set_context("DictationKeyword", "dictation")
            if self.check_for_intent(utterances[0]):
                return False
            else:
                self.words += (utterances[0]) + "\n"
                self.speak("", expect_response=True)
                LOG.info("Dictating: " + utterances[0])
                self.dictation_stack.append(utterances[0])
                return True
        else:
            self.remove_context("DictationKeyword")
            return False


def create_skill():
    return DictationSkill()

