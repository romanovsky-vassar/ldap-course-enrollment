__author__ = 'romanovsky'

import sys
import cx_Oracle
import ConfigParser

class Database:
    valid_database = {"oracle" : "oracle",
                      "mysql" : "mysql"}

    #based on input, create a new connection to that database
    def __init__(self, database_platform):
        try:
            db = self.valid_database[database_platform]
        except KeyError:
            self.error = "invalid database"
        else:
            settings = ConfigParser.ConfigParser()
            settings.read('./assets/auth/auth.ini')
            self.dbuser = settings.get(db,'User')
            self.dbpw = settings.get(db, 'PW')
            self.dbhost = settings.get(db, 'host')
            self.dbport = settings.get(db,'port')
            self.servicename = settings.get(db,'service_name')

        try:
            self.cn = cx_Oracle.connect('%s/%s@%s:%s/%s' % (self.dbuser, self.dbpw, \
            self.dbhost, self.dbport, self.servicename ))
            self.c1 = self.cn.cursor()
            self.course_collection = self.cn.cursor()

        except cx_Oracle.DatabaseError as exc:
            #self.error = "no database connection"
            #self.error = e.message
            error, = exc.args
            self.error = error.message

    def course(self, term, status):
        if status == 'new':
            self.c1.callproc("VASSAR_IAM.get_new_courses", ['26-JUL-2018 15:50:00',self.course_collection])
            self.c1.close()
        else:
            return null
        return self.course_collection



    #close the database connection
    def close(self):
        self.cn.close()
