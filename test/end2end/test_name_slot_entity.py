"""E2e coverage for the ``{name}`` slot in ``start_dictation.intent`` after
wiring ``self.register_entity_file("name.entity")`` into ``initialize()``
(requires ovos-workshop>=9.3.12a1 + ovos-padatious>=2.0.3a1).

Fixed upstream: ovos-padatious 2.0.3a1 (PyPI) corrected a bug where a
registered ``.entity`` file made a slot an effectively closed vocabulary
instead of the scoring hint it's documented to be (INTENT-1 §5.4). Under
2.0.3a1, an out-of-list slot value still matches, floored into the
padatious-medium confidence band (~[0.8, 0.92]); in-list values are
unaffected.

This skill was already proven immune to the pre-fix bug: its session
pipeline (``PIPELINE`` below, matching this repo's pre-existing
test_intents_en_us.py convention) always includes adapt and padacioso
bands alongside padatious, so even when padatious itself closed the
{name} slot to unlisted values, padacioso still routed them.
``test_out_of_list_value_still_routes_via_fallback`` below keeps asserting
that explicitly, so a future change that narrows this skill's pipeline to
padatious-only would still be caught by a fallback regression.

``test_out_of_list_value_routes_via_padatious_hint_alone`` adds the direct
padatious-hint proof from the sibling skills: with a padatious-only
pipeline (high + medium, no adapt/padacioso), the same unlisted title
still routes and fills the slot, via ovos-padatious's post-2.0.3a1 hint
semantics rather than the fallback path.

The registration-wiring proof itself (independent of padatious matching
behavior) is
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
    "ovos-padatious-pipeline-plugin-high",
    "ovos-padacioso-pipeline-plugin-high",
    "ovos-adapt-pipeline-plugin-medium",
    "ovos-padatious-pipeline-plugin-medium",
    "ovos-padacioso-pipeline-plugin-medium",
    "ovos-adapt-pipeline-plugin-low",
]

# Padatious-only, no adapt/padacioso fallback -- isolates the
# register_entity_file hint behavior itself (requires -medium in the
# pipeline for the hint band to fire, same as the sibling skill tests).
PADATIOUS_ONLY_PIPELINE = [
    "ovos-padatious-pipeline-plugin-high",
    "ovos-padatious-pipeline-plugin-medium",
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

    def test_out_of_list_value_still_routes_via_fallback(self):
        """This skill's mixed adapt+padatious+padacioso pipeline routes an
        unlisted, natural {name} value ("homework") -- proven immune to
        the pre-2.0.3a1 padatious closed-vocabulary bug via the
        adapt/padacioso fallback. If this starts failing, the pipeline
        lost its non-padatious fallback and is now exposed to the same
        risk as ovos-skill-audio-recording / ovos-skill-color-picker.
        """
        types = self._types("start dictation named homework", "name-slot-oov-fallback")
        self.assertIn(f"{SKILL_ID}:start_dictation", types)

    def test_out_of_list_value_routes_via_padatious_hint_alone(self):
        """Post ovos-padatious>=2.0.3a1: with a padatious-only pipeline
        (no adapt/padacioso fallback), registering name.entity is a
        scoring HINT, not a closed vocabulary -- an unlisted title
        ("homework") still matches start_dictation.intent and the
        {name} slot fills with the literal utterance value.
        """
        messages = self._capture(
            "start dictation named homework", "name-slot-hint-homework",
            pipeline=PADATIOUS_ONLY_PIPELINE,
        )
        matches = [m for m in messages if m.msg_type == f"{SKILL_ID}:start_dictation"]
        self.assertTrue(
            matches,
            "out-of-list slot value did not route via padatious-only pipeline "
            "-- ovos-padatious hint semantics (2.0.3a1+) may have regressed"
        )
        self.assertEqual(matches[0].data.get("name"), "homework")


if __name__ == "__main__":
    unittest.main()
