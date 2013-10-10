# -*- coding: utf-8 -*-

import re
import os
import MySQLdb
import shutil
import pickle

import base_model

class Filler(base_model.base):

    def __init__(self, id, db):
        self.fields = []
        self.fields.append({'name':'HR_User', 'control':'input'})
        self.fields.append({'name':'Filler', 'control':'input'})
        base_model.base.__init__(self, id, 'Filler',self.fields, db)

    def Get_All_Agent(self, Owner, all_Agent):
        all_Agent.append(Owner)
        cursor = self.db.cursor()
        sql = 'SELECT Filler  from Filler where HR_User=%s'
        cursor.execute(sql , (Owner,))
        for Filler  in cursor:
            if Filler[0] not in all_Agent:
                self.Get_All_Agent(Filler[0] ,all_Agent)

    def Get_All_Agent_UnAgentSelf(self, Owner, all_Agent):
        cursor = self.db.cursor()
        sql = 'SELECT Filler  from Filler where HR_User=%s'
        cursor.execute(sql , (Owner,))
        for Filler  in cursor:
            if Filler[0] not in all_Agent:
                all_Agent.append(Filler[0])
                self.Get_All_Agent(Filler[0] ,all_Agent)
                
    def Get_Direct_Agent(self, Owner):
        all_Agent = []
        cursor = self.db.cursor()
        sql = 'SELECT Filler  from Filler where HR_User=%s'
        cursor.execute(sql , (Owner,))
        for Filler  in cursor:
            all_Agent.append(Filler[0])
        return all_Agent
