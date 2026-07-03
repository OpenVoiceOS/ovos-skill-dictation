import unittest
from os.path import dirname

from ovos_plugin_manager.skills import find_skill_plugins
from ovos_utils.messagebus import FakeBus
from ovos_workshop.skill_launcher import SkillLoader

import ovos_skill_dictation
from ovos_skill_dictation import DictationSkill

SKILL_ID = "ovos-skill-dictation.openvoiceos"


class TestPlugin(unittest.TestCase):
    def test_find_plugin(self):
        self.assertIn(SKILL_ID, list(find_skill_plugins()))


class TestSkillLoading(unittest.TestCase):
    def setUp(self):
        # the source (__init__.py) and locale of this skill live at the package
        # root, so the SkillLoader is pointed at the installed package directory
        self.path = dirname(ovos_skill_dictation.__file__)

    def test_from_class(self):
        bus = FakeBus()
        skill = DictationSkill()
        skill._startup(bus, SKILL_ID)
        self.assertEqual(skill.bus, bus)
        self.assertEqual(skill.skill_id, SKILL_ID)

    def test_from_plugin(self):
        bus = FakeBus()
        for skill_id, plug in find_skill_plugins().items():
            if skill_id == SKILL_ID:
                skill = plug()
                skill._startup(bus, SKILL_ID)
                self.assertEqual(skill.bus, bus)
                self.assertEqual(skill.skill_id, SKILL_ID)
                break
        else:
            raise RuntimeError("plugin not found")

    def test_from_loader(self):
        bus = FakeBus()
        loader = SkillLoader(bus, self.path)
        loader.load()
        self.assertEqual(loader.instance.bus, bus)


class TestDictationState(unittest.TestCase):
    def setUp(self):
        self.skill = DictationSkill()
        self.skill._startup(FakeBus(), SKILL_ID)

    def test_starts_not_dictating(self):
        from ovos_bus_client.session import Session
        self.assertFalse(self.skill.is_dictating(Session("s")))

    def test_start_sets_dictating(self):
        from ovos_bus_client.message import Message
        from ovos_bus_client.session import Session, SessionManager
        sess = Session("s")
        msg = Message("start", {}, {"session": sess.serialize()})
        self.skill.start_dictation(msg)
        self.assertTrue(self.skill.is_dictating(SessionManager.get(msg)))

    def test_stop_without_start_does_not_raise(self):
        from ovos_bus_client.message import Message
        from ovos_bus_client.session import Session
        sess = Session("never-started")
        msg = Message("stop", {}, {"session": sess.serialize()})
        # a bare stop for an unknown session must restore the listener cleanly
        self.skill.stop_dictation(msg)
        self.assertFalse(self.skill.is_dictating(sess))
