"""E2e coverage for the ``{name}`` slot in ``start_dictation.intent``.

``name.entity`` lists example titles. An entity file is a scoring hint, not
a closed vocabulary (INTENT-1 §5.4), so a title that is not in the list must
still route to ``start_dictation`` and fill the slot.

The slot test shows that the ``.intent`` template alone routes the unlisted
title and fills ``{name}``.

The registration-wiring proof is
``test/unittests/test_skill_loading.py::TestNameEntityRegistration``.
"""
import unittest

from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovoscope import CaptureSession
from ovoscope.routing import PIPELINE, TALLY, get_prototype_minicroft

SKILL_ID = "ovos-skill-dictation.openvoiceos"
LANG = "en-US"

START_DICTATION = f"{SKILL_ID}:start_dictation"


class TestNameSlotKnownValuesRoute(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.minicroft = get_prototype_minicroft([SKILL_ID], max_wait=300)

    @classmethod
    def tearDownClass(cls):
        cls.minicroft.stop()

    def _capture(self, text, session_id):
        session = Session(session_id)
        session.lang = LANG
        session.pipeline = PIPELINE
        session.blacklisted_intents = []
        utterance = Message(
            "recognizer_loop:utterance",
            {"utterances": [text], "lang": LANG},
            {"session": session.serialize(), "source": "A", "destination": "B"},
        )
        capture = CaptureSession(self.minicroft)
        capture.capture(utterance, timeout=30)
        return capture.finish()

    def _types(self, text, session_id):
        return [m.msg_type for m in self._capture(text, session_id)]

    def test_known_title_shopping_list_matches(self):
        """"shopping list" is a real sample value in
        locale/en-US/intents/name.entity."""
        text = "start dictation named shopping list"
        TALLY.assert_routed(text, START_DICTATION, self._types(text, "name-slot-pos-shopping"))

    def test_known_title_meeting_notes_matches(self):
        """"meeting notes" -- another real sample value from name.entity."""
        text = "start dictation named meeting notes"
        TALLY.assert_routed(text, START_DICTATION, self._types(text, "name-slot-pos-meeting"))

    def test_out_of_list_value_routes_and_fills_slot(self):
        """An unlisted title still matches start_dictation.intent and the
        {name} slot holds the spoken value."""
        text = "start dictation named homework"
        messages = self._capture(text, "name-slot-hint-homework")
        TALLY.assert_routed(text, START_DICTATION, [m.msg_type for m in messages])
        matches = [m for m in messages if m.msg_type.removesuffix(".intent") == START_DICTATION]
        self.assertEqual(matches[0].data.get("name"), "homework")


if __name__ == "__main__":
    unittest.main()
