# mycroft-dictation-skill

Saves what user is saying and sends by email

# usage

    start dictating - starts recording words
    stop dictating - stops recording words and sends email
    read dictation - reads last dictated words
    
# privacy

your emails can be read by Mycroft Home, if you desire privacy edit your
config file located at

        ~/.mycroft/mycroft.conf

if it does not exist create it, this file must be valid json, add the
following to it

        "email": {
            "email": "my_mail@fakemail.com",
            "password": "SECRET"
        }

email will now be sent from here, the destinatary is the same email

skill settings were not used or your email and password would be stored in
mycroft home backend

