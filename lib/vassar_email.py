__author__ = 'romanovsky'

import sys
import simplemail
import ConfigParser


class VassarEmail:

    #based on input, create a new connection to that database
    def __init__(self):
        self.smtp_server = "localhost",
        self.smtp_user = "",
        self.smtp_password = "",
        self.from_address = "romanovsky@vassar.edu",
        self.to_address = "romanovsky@vassar.edu",
        self.subject = u"Problem: LDAP course enrollment.",
        print self.subject

    def send(self, mess):
        # str.join() ??? 
        simplemail.Email(
        smtp_server = self.smtp_server[0],
        smtp_user = self.smtp_user[0],
        smtp_password = self.smtp_password[0],
        from_address = self.from_address[0],
        to_address = self.to_address[0],
        subject = self.subject[0],
        message = mess
        ).send()
