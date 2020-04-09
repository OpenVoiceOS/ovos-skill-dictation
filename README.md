## dictation

saves user speech and sends by email

NOTE: this is OLD and UNMAINTAINED, a proof of concept for reference only

I will be revisiting this soon

## Description
  char-rnn auto complete for human + machine writing included

## Examples
* "start dictation"
* "once upon a time"
* "auto complete"
* "end dictation"

## Credits
JarbasAI



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

