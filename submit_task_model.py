# -*- coding: utf-8 -*-

import re
import os
import MySQLdb
import shutil
import pickle

import base_model

class Task_Perm(base_model.base):

    def __init__(self, id, db):
        self.fields = []
        self.fields.append({'name':'UserName', 'control':'input'})
        self.fields.append({'name':'Perm', 'control':'input'})
        base_model.base.__init__(self, id, 'Task_Perm',self.fields, db)

            
