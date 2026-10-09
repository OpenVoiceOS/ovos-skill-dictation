"""E2e coverage for the ``{name}`` slot in ``start_dictation.intent``.

``name.entity`` lists example titles. An entity file is a scoring hint, not
a closed vocabulary (INTENT-1 §5.4), so a title that is not in the list must
still route to ``start_dictation`` and fill the slot.

``PIPELINE`` matches this repo's ``test_intents_en_us.py``: adapt and
padacioso bands. ``PADACIOSO_ONLY_PIPELINE`` drops adapt, so the slot test
shows that the ``.intent`` template alone routes the unlisted title and
fills ``{name}``.

The registration-wiring proof is
``test/unittests/test_skill_loading.py::TestNameEntityRegistration``.
"""
import unittest

from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovoscope import CaptureSession, get_minicroft

SKILL_ID = "ovos-skill-dictation.openvoiceos"
LANG = "en-US"

PIPELINE = [
    "ovos-adapt-pipeline-plugin-high",
    "ovos-padacioso-pipeline-plugin-high",
    "ovos-adapt-pipeline-plugin-medium",
    "ovos-padacioso-pipeline-plugin-medium",
    "ovos-adapt-pipeline-plugin-low",
]

PADACIOSO_ONLY_PIPELINE = [
    "ovos-padacioso-pipeline-plugin-high",
    "ovos-padacioso-pipeline-plugin-medium",
]


class TestNameSlotKnownValuesRoute(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.minicroft = get_minicroft([SKILL_ID], max_wait=300)

    @classmethod
    def tearDownClass(cls):
        cls.minicroft.stop()

    def _capture(self, text, session_id, pipeline=PIPELINE):
        session = Session(session_id)
        session.lang = LANG
        session.pipeline = list(pipeline)
        session.blacklisted_intents = []
        utterance = Message(
            "recognizer_loop:utterance",
            {"utterances": [text], "lang": LANG},
            {"session": session.serialize(), "source": "A", "destination": "B"},
        )
        capture = CaptureSession(self.minicroft)
        capture.capture(utterance, timeout=30)
        return capture.finish()

    def _types(self, text, session_id, pipeline=PIPELINE):
        return [m.msg_type for m in self._capture(text, session_id, pipeline)]

    def test_known_title_shopping_list_matches(self):
        """"shopping list" is a real sample value in
        locale/en-US/intents/name.entity."""
        types = self._types("start dictation named shopping list", "name-slot-pos-shopping")
        self.assertIn(f"{SKILL_ID}:start_dictation", types)

    def test_known_title_meeting_notes_matches(self):
        """"meeting notes" -- another real sample value from name.entity."""
        types = self._types("start dictation named meeting notes", "name-slot-pos-meeting")
        self.assertIn(f"{SKILL_ID}:start_dictation", types)

    def test_out_of_list_value_still_routes(self):
        """An unlisted, natural {name} value ("homework") routes on the
        mixed adapt and padacioso pipeline."""
        types = self._types("start dictation named homework", "name-slot-oov-fallback")
        self.assertIn(f"{SKILL_ID}:start_dictation", types)

    def test_out_of_list_value_routes_and_fills_slot_on_padacioso_alone(self):
        """With padacioso alone, an unlisted title still matches
        start_dictation.intent and the {name} slot holds the spoken value."""
        messages = self._capture(
            "start dictation named homework", "name-slot-hint-homework",
            pipeline=PADACIOSO_ONLY_PIPELINE,
        )
        matches = [m for m in messages if m.msg_type == f"{SKILL_ID}:start_dictation"]
        self.assertTrue(matches, "out-of-list slot value did not route on the padacioso-only pipeline")
        self.assertEqual(matches[0].data.get("name"), "homework")


if __name__ == "__main__":
    unittest.main()
