# Dictation skill

This skill transcribes user speech to a text file while it is active. It is made for [OpenVoiceOS/ovos-dinkum-listener](https://github.com/OpenVoiceOS/ovos-dinkum-listener).

A related skill, [OpenVoiceOS/skill-ovos-audio-recording](https://github.com/OpenVoiceOS/skill-ovos-audio-recording), records audio instead of text transcriptions.

## About

The skill captures utterances and disables wake words while dictation is active.

- start dictation
  - enable continuous conversation mode
  - capture all utterances in the converse method
- converse
  - show the dictation on screen live
- stop dictation
  - restore listener mode
  - save the dictation to a file
  - show the full dictation on screen

## Examples
* "start dictation"
* "end dictation"

## Entity hints

The skill ships `locale/<lang>/intents/name.entity`, a list of example transcript titles ("shopping list", "meeting notes", "grocery list", ...) for the optional `{name}` slot in `start_dictation.intent`. These are hints, not a closed list: any title you say, including one not on the list, still fills the slot and is used as the saved file name; listed titles simply match with more confidence. `ovos-workshop` (>=9.5.0a1) registers every shipped `.entity` file automatically when the skill's language resources are loaded, so nothing needs to be configured for this.

## Credits
JarbasAI
