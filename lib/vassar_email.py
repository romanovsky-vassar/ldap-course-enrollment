__author__ = 'romanovsky'

import sys
import simplemail
import ConfigParser


class VassarEmail:

    @staticmethod
    def send(subj, mess):
        # str.join() ???
        simplemail.Email(
        smtp_server = "localhost",
        from_address = "noreply@vassar.edu",
        to_address = "romanovsky@vassar.edu, mark.romanovsky@gmail.com",
        subject = subj,
        message = mess
        ).send()
