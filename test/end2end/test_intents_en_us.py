"""End-to-end intent routing tests for the en-US locale.

Each canonical utterance is fired through a real MiniCroft and asserted to
route to the expected intent on the padacioso pipeline. Dictation is a conversational skill,
so every case runs in its own session to keep an active dictation session
from diverting later utterances into ``converse``.
"""
import unittest

from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovoscope import CaptureSession, get_minicroft

SKILL_ID = "ovos-skill-dictation.openvoiceos"


class TestDictationIntentsEnUS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # allow a generous READY window on slow CI runners
        cls.minicroft = get_minicroft([SKILL_ID], max_wait=300)

    @classmethod
    def tearDownClass(cls):
        cls.minicroft.stop()

    def _run(self, text, session_id):
        session = Session(session_id)
        # This skill's intents are ``.intent`` sample files, not adapt
        # keywords, so the adapt entries never match; padacioso does the
        # routing.
        session.pipeline = [
            "ovos-adapt-pipeline-plugin-high",
            "ovos-padacioso-pipeline-plugin-high",
            "ovos-adapt-pipeline-plugin-medium",
            "ovos-padacioso-pipeline-plugin-medium",
            "ovos-adapt-pipeline-plugin-low",
        ]
        # blacklisted_intents defaults to None on a fresh Session, which
        # crashes the padacioso pipeline (NoneType membership test).
        session.blacklisted_intents = []
        utterance = Message(
            "recognizer_loop:utterance",
            {"utterances": [text], "lang": "en-US"},
            {"session": session.serialize(), "source": "A", "destination": "B"},
        )
        capture = CaptureSession(self.minicroft)
        capture.capture(utterance, timeout=30)
        return capture.finish()

    def _assert_intent(self, text, intent_file):
        # The bus event actually dispatched by the matched pipeline drops
        # the ".intent" filename suffix (eg. "start_dictation" not
        # "start_dictation.intent") -- normalize before comparing so this
        # observes real routing rather than a name that is never emitted.
        intent_name = intent_file[:-len(".intent")] if intent_file.endswith(".intent") else intent_file
        session_id = f"e2e-{intent_file}-{abs(hash(text))}"
        messages = self._run(text, session_id)
        types = [m.msg_type for m in messages]
        self.assertIn(f"{SKILL_ID}:{intent_name}", types)

    def test_start_dictation(self):
        self._assert_intent("start dictation", "start_dictation.intent")

    def test_begin_dictation(self):
        self._assert_intent("begin dictation", "start_dictation.intent")

    def test_activate_dictation(self):
        self._assert_intent("activate dictation", "start_dictation.intent")

    def test_stop_dictation(self):
        self._assert_intent("stop dictation", "stop_dictation.intent")

    def test_end_dictation(self):
        self._assert_intent("end dictation", "stop_dictation.intent")

    def test_cancel_dictation(self):
        self._assert_intent("cancel dictation", "stop_dictation.intent")

    def test_stop_taking_notes(self):
        self._assert_intent("stop taking notes", "stop_dictation.intent")
