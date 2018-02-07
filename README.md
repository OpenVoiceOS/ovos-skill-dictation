# mycroft-dictation-skill

Saves what user is saying and sends by email

# usage

    start dictating - starts recording words
    we found ourselves in - records what you said
    auto complete -  "the streets of Wyoh."
    undo - reverts last dictation addition
    stop dictating - stops recording words and sends email
    read dictation - reads last dictated words

# char rnn auto complete

if you want to auto complete your dictations using a [char-rnn](https://karpathy.github.io/2015/05/21/rnn-effectiveness/) , install
[torch-rnn-server](https://github.com/robinsloan/torch-rnn-server) and provide
 the url in the skill settings

 Here are [10$ free in digital ocean](https://m.do.co/c/e9f00fee6aa5) if you
 want to try it, by default the skill points at my digital ocean instance which may go down without notice


# privacy

your emails can be read by Mycroft Home, if you desire privacy edit your
config file located at

        ~/.mycroft/mycroft.conf

if it does not exist create it, this file must be valid json, add the
following to it

        "email": {
            "email": "send_from@gmail.com",
            "password": "SECRET",
            "destinatary": "send_to@gmail.com"
        }

email will now be sent from here, the destinatary is the same email if not
provided

skill settings were not used or your email and password would be stored in
mycroft home backend


# TODOs

- skill settings meta
- redo
- use [PR#1351](https://github.com/MycroftAI/mycroft-core/pull/1351) in converse


# liked this?

- https://www.patreon.com/jarbasAI
- https://www.paypal.me/jarbasAI

