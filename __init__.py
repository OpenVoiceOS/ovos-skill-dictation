import os.path
import time

from ovos_bus_client.message import Message
from ovos_bus_client.session import SessionManager, Session
from ovos_config import Configuration
from ovos_utils import classproperty
from ovos_utils.process_utils import RuntimeRequirements
from ovos_workshop.decorators import intent_handler, adds_context, removes_context
from ovos_workshop.skills.converse import ConversationalSkill


class DictationSkill(ConversationalSkill):
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
        self.dictation_sessions = {}

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
        sess = SessionManager.get(message)
        self.dictation_sessions[sess.session_id] = dict(
            file_name=message.data.get("name", str(time.time())),
            dictating=True,
            dictation_stack=[]
        )
        self.bus.emit(message.forward("recognizer_loop:state.set",
                                      {"mode": "continuous"}))

    @removes_context("DictationKeyword")
    def stop_dictation(self, message=None):
        message = message or Message("")
        sess = SessionManager.get(message)
        self.bus.emit(message.forward("recognizer_loop:state.set",
                                      {"mode": self.default_listen_mode}))

        path = f"{os.path.expanduser('~')}/Documents/dictations"
        os.makedirs(path, exist_ok=True)
        name = self.dictation_sessions[sess.session_id]["file_name"] or time.time()
        with open(f"{path}/{name}.txt", "w") as f:
            f.write("\n".join(self.dictation_sessions[sess.session_id]["dictation_stack"]))

        if sess.session_id == "default":
            self.gui.show_text(f"saved to {path}/{name}.txt")

        self.dictation_sessions[sess.session_id]["dictating"] = False

    @intent_handler("start_dictation.intent")
    def handle_start_dictation_intent(self, message):
        if not self.dictating:
            self.speak_dialog("start", wait=True)
        else:
            self.speak_dialog("already_dictating", wait=True)
        self.start_dictation(message)  # enable continuous listening, no wake word needed

    @intent_handler("stop_dictation.intent")
    def handle_stop_dictation_intent(self, message):
        if self.dictating:
            self.speak_dialog("stop")
        else:
            self.speak_dialog("not_dictating")
        self.stop_dictation(message)

    def can_stop(self, message: Message) -> bool:
        session = SessionManager.get(message)
        return session.session_id in self.dictation_sessions and self.dictation_sessions[session.session_id]["dictating"]

    def stop_session(self, session: Session):
        if session.session_id in self.dictation_sessions and \
                self.dictation_sessions[session.session_id]["dictating"]:
            self.dictation_sessions[session.session_id]["dictating"] = False
            self.stop_dictation()
            return True
        return False

    def can_converse(self, message: Message) -> bool:
        """
        Determines if the skill can handle the given utterances in the specified language in the converse method.

        Override this method to implement custom logic for assessing whether the skill is capable of answering a query.

        Returns:
            True if the skill can handle the query during converse; otherwise, False.
        """
        return self.can_stop(message) # same logic

    def converse(self, message):
        utterance = message.data["utterances"][0]
        sess = SessionManager.get(message)
        if self.voc_match(utterance, "StopKeyword"):
            self.handle_stop_dictation_intent(message)
        else:
            if sess.session_id == "default":
                self.gui.show_text(utterance)
            self.dictation_sessions[sess.session_id]["dictation_stack"].append(utterance)
