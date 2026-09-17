"""Multilingual golden-utterance end-to-end coverage for ovos-skill-dictation.

Each row fires in its own bus session: dictation is a conversational
skill, so an active dictation session would otherwise divert later
utterances into ``converse`` instead of intent matching (same constraint
as this repo's own ``test_intents_en_us.py``). Intent match is asserted
directly off the ``ovos.intent.matched`` bus event's ``data.intent_name``
field, matching this repo's own (now-replaced) ``test_golden_utterances.py``.

One MiniCroft is booted per locale (``get_minicroft([SKILL_ID], max_wait=150,
lang=LANG)``) and torn down before moving to the next locale, avoiding the
open ovoscope harness bug in the shared secondary_langs boot path that
keeps ovos-skill-alerts' own multilang suite skipped upstream.
"""
import json
from pathlib import Path

import pytest
from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovoscope import CaptureSession, get_minicroft

SKILL_ID = "ovos-skill-dictation.openvoiceos"

_PIPELINE = [
    "ovos-adapt-pipeline-plugin-high",
    "ovos-padatious-pipeline-plugin-high",
    "ovos-padacioso-pipeline-plugin-high",
    "ovos-adapt-pipeline-plugin-medium",
    "ovos-padacioso-pipeline-plugin-medium",
    "ovos-adapt-pipeline-plugin-low",
]

END2END_DIR = Path(__file__).parent

LANGS = [
    "en-US", "ca-ES", "da-DK", "de-DE", "es-ES", "eu-ES", "fr-FR", "gl-ES",
    "it-IT", "kab", "nl-NL", "oc-FR", "pt-BR", "pt-PT", "sv-SE",
]


def _load_rows(lang):
    path = END2END_DIR / f"golden_utterances_{lang}.jsonl"
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("needs_manual"):
                continue
            rows.append(row)
    return rows


ALL_ROWS = []
for _lang in LANGS:
    for _row in _load_rows(_lang):
        ALL_ROWS.append(_row)


def _golden_id(row):
    return f"{row['lang']}-{row['intent_label']}-{row['utterance']}"


GOLDEN_ROWS = [pytest.param(r, id=_golden_id(r)) for r in ALL_ROWS]

# Real locale-content defects found and fixed in-place during this pass
# (red-before/green-after verified), keyed by (lang, utterance):
KNOWN_BUGS = {}


@pytest.fixture(scope="module")
def minicroft_factory():
    cache = {"lang": None, "mc": None}

    def _get(lang):
        if cache["lang"] != lang:
            if cache["mc"] is not None:
                cache["mc"].stop()
            cache["mc"] = get_minicroft([SKILL_ID], max_wait=300, lang=lang)
            cache["lang"] = lang
        return cache["mc"]

    yield _get
    if cache["mc"] is not None:
        cache["mc"].stop()


def _matched_intent_names(mc, text, lang, session_id):
    session = Session(session_id)
    session.lang = lang
    session.pipeline = list(_PIPELINE)
    session.blacklisted_intents = []
    utterance = Message(
        "recognizer_loop:utterance",
        {"utterances": [text], "lang": lang},
        {"session": session.serialize(), "source": "A", "destination": "B"},
    )
    capture = CaptureSession(mc, eof_msgs=["mycroft.skill.handler.start"])
    capture.capture(utterance, timeout=30)
    msgs = capture.finish()
    return [m.data.get("intent_name") for m in msgs if m.msg_type == "ovos.intent.matched"]


@pytest.mark.timeout(600)
@pytest.mark.parametrize("row", GOLDEN_ROWS, ids=_golden_id)
def test_golden_utterance_multilang(minicroft_factory, row):
    mc = minicroft_factory(row["lang"])
    expected = f"{SKILL_ID}:{row['intent_label']}"
    matched = _matched_intent_names(mc, row["utterance"], row["lang"], f"golden-{_golden_id(row)}")
    ok = expected in matched
    bug_key = (row["lang"], row["utterance"])
    if bug_key in KNOWN_BUGS and not ok:
        pytest.xfail(reason=f"known-bug: {KNOWN_BUGS[bug_key]}")
    assert ok, f"[{row['lang']}] {row['utterance']!r}: expected {expected!r}, got {matched!r}"
