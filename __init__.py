import os.path
import time

from ovos_bus_client.message import Message
from ovos_config import Configuration
from ovos_utils import classproperty
from ovos_utils.intents import IntentBuilder
from ovos_utils.process_utils import RuntimeRequirements
from ovos_workshop.decorators import intent_handler, adds_context, removes_context
from ovos_workshop.skills import OVOSSkill


class DictationSkill(OVOSSkill):
    """
    - start dictation
      - enable continuous conversation mode
      - capture all utterances in converse method
    - converse
      - display dictation on screen live
    - stop dictation
      - restore listener mode
      - save dictation to file
      - display full dictation on screen
    """

    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(
            internet_before_load=False,
            network_before_load=False,
            gui_before_load=False,
            requires_internet=False,
            requires_network=False,
            requires_gui=False,
            no_internet_fallback=True,
            no_network_fallback=True,
            no_gui_fallback=True,
        )

    def initialize(self):
        self.dictating = False

    @property
    def default_listen_mode(self):
        listener_config = Configuration().get("listener", {})
        if listener_config.get("continuous_listen", False):
            return "continuous"
        elif listener_config.get("hybrid_listen", False):
            return "hybrid"
        else:
            return "wakeword"

    @adds_context("DictationKeyword", "dictation")
    def start_dictation(self, message=None):
        message = message or Message("")
        self.dictation_stack = []
        self.dictating = True
        self.bus.emit(message.forward("recognizer_loop:state.set",
                                      {"mode": "continuous"}))

    @removes_context("DictationKeyword")
    def stop_dictation(self, message=None):
        message = message or Message("")
        self.dictating = False
        self.bus.emit(message.forward("recognizer_loop:state.set",
                                      {"mode": self.default_listen_mode}))
        path = f"{os.path.expanduser('~')}/Documents/dictations"
        os.makedirs(path, exist_ok=True)
        name = time.time()  # TODO - allow name requested in intent
        with open(f"{path}/{name}.txt", "w") as f:
            f.write("\n".join(self.dictation_stack))
        self.gui.show_text(f"saved to {path}/{name}.txt")

    @intent_handler(IntentBuilder("StartDictationIntent")
                    .require("StartKeyword")
                    .require("DictationKeyword"))
    def handle_start_dictation_intent(self, message):
        if not self.dictating:
            self.speak_dialog("start", wait=True)
        else:
            self.speak_dialog("already_dictating", wait=True)
        self.start_dictation()  # enable continuous listening, no wake word needed

    @intent_handler(IntentBuilder("StopDictationIntent")
                    .require("StopKeyword")
                    .require("DictationKeyword"))
    def handle_stop_dictation_intent(self, message):
        if self.dictating:
            self.speak_dialog("stop")
        else:
            self.speak_dialog("not_dictating")
        self.stop_dictation()

    @intent_handler(IntentBuilder("ReadDictationIntent")
                    .require("ReadKeyword")
                    .require("DictationKeyword"))
    def handle_read_last_dictation_intent(self, message):
        self.speak_dialog("dictation")
        self.speak("".join(self.dictation_stack))

    def stop(self):
        if self.dictating:
            self.stop_dictation()
            return True

    def converse(self, message):
        utterance = message.data["utterances"][0]
        if self.dictating:
            if self.voc_match("StopKeyword", utterance):
                self.handle_stop_dictation_intent(message)
            else:
                self.gui.show_text(utterance)
                self.dictation_stack.append(utterance)
            return True
        return False
