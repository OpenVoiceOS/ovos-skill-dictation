"""Golden-utterance end-to-end coverage for ovos-skill-dictation (en-US).

The golden corpus (``golden_utterances.jsonl``) is a vendored slice of the
shared ovoscope golden-utterance dataset, keyed by
``skill_id == "ovos-skill-dictation.openvoiceos"``. One shared ``MiniCroft``
(module-scoped fixture) is booted for the whole suite; every row is its own
parametrized test item, each in its own bus session (dictation is a
conversational skill -- an active dictation session would otherwise divert
later utterances into ``converse`` instead of intent matching, same
constraint as ``test_intents_en_us.py``).

Intent match is asserted directly off the ``ovos.intent.matched`` bus event's
``data.intent_name`` field, which is emitted as ``<skill_id>:<intent_label>``
with the ``.intent`` suffix already stripped (eg. ``start_dictation`` not
``start_dictation.intent``). Capture ends at ``mycroft.skill.handler.start``
(right after intent binding fires, before any handler body runs) so a row
never depends on a handler finishing.
"""
import json
from pathlib import Path

import pytest
from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovoscope import CaptureSession, get_minicroft

SKILL_ID = "ovos-skill-dictation.openvoiceos"
LANG = "en-US"

_PIPELINE = [
    "ovos-adapt-pipeline-plugin-high",
    "ovos-padatious-pipeline-plugin-high",
    "ovos-padacioso-pipeline-plugin-high",
    "ovos-adapt-pipeline-plugin-medium",
    "ovos-padacioso-pipeline-plugin-medium",
    "ovos-adapt-pipeline-plugin-low",
]

GOLDEN_PATH = Path(__file__).parent / "golden_utterances.jsonl"

# utterances lifted verbatim from OTHER skills' golden-utterance slices,
# picked for lexical overlap with dictation's "start/stop/end/activate/
# cancel ... dictation/text/notes/transcription" vocabulary.
NEGATIVE_UTTERANCES = [
    ("what's the weather like today", "ovos-skill-weather.openvoiceos"),
    ("set the volume to 50 percent", "ovos-skill-volume.openvoiceos"),
    ("tell me a joke", "ovos-skill-icanhazdadjokes.openvoiceos"),
    ("what is your cpu usage", "ovos-skill-diagnostics.openvoiceos"),
    ("set a timer for 5 minutes", "ovos-skill-alerts.openvoiceos"),
    ("play some music", "ovos-skill-music.openvoiceos"),
    ("stop the music", "ovos-skill-music.openvoiceos"),
]


def _expected_names(skill_id: str, intent_label: str) -> set:
    base = intent_label[:-len(".intent")] if intent_label.endswith(".intent") else intent_label
    return {f"{skill_id}:{base}"}


def _load_golden_rows():
    rows = []
    with open(GOLDEN_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("needs_manual"):
                continue
            rows.append(row)
    return rows


GOLDEN_ROWS = [pytest.param(r, id=r["utterance"]) for r in _load_golden_rows()]


@pytest.fixture(scope="module")
def minicroft():
    # padatious models take a while to train on CI runners; allow a
    # generous READY window (same as test_intents_en_us.py).
    mc = get_minicroft([SKILL_ID], max_wait=300)
    yield mc
    mc.stop()


def _matched_intent_names(mc, text, session_id):
    session = Session(session_id)
    session.lang = LANG
    session.pipeline = list(_PIPELINE)
    # blacklisted_intents defaults to None on a fresh Session, which crashes
    # the padacioso pipeline (NoneType membership test) - force an empty list.
    session.blacklisted_intents = []
    utterance = Message(
        "recognizer_loop:utterance",
        {"utterances": [text], "lang": LANG},
        {"session": session.serialize(), "source": "A", "destination": "B"},
    )
    capture = CaptureSession(
        mc,
        eof_msgs=["mycroft.skill.handler.start"],
    )
    capture.capture(utterance, timeout=30)
    msgs = capture.finish()
    return [
        m.data.get("intent_name")
        for m in msgs
        if m.msg_type == "ovos.intent.matched"
    ]


def _golden_id(row):
    return row["utterance"]


@pytest.mark.timeout(60)
@pytest.mark.parametrize("row", GOLDEN_ROWS, ids=_golden_id)
def test_golden_utterance(minicroft, row):
    expected = _expected_names(SKILL_ID, row["intent_label"])
    matched = _matched_intent_names(minicroft, row["utterance"], f"golden-{_golden_id(row)}")
    assert any(m in expected for m in matched), (
        f"{row['utterance']!r}: expected one of {sorted(expected)!r}, got {matched!r}"
    )


@pytest.mark.timeout(60)
@pytest.mark.parametrize("negative", NEGATIVE_UTTERANCES, ids=lambda n: n[0])
def test_negative_confusable_not_claimed(minicroft, negative):
    text, source_skill = negative
    matched = _matched_intent_names(minicroft, text, f"negative-{text}")
    claimed = any(m.startswith(f"{SKILL_ID}:") for m in matched if m)
    assert not claimed, f"{text!r} (from {source_skill}) was incorrectly claimed by {SKILL_ID}"
