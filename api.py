# -*- coding: utf-8 -*-
# 

import os.path
import sys
import traceback

from trac.core import *
from trac.util.translation import _


class IModuleProvider(Interface):

    def get_module(req):
        """
        `(category, page)`.
        """

    def render_module(req, category, page, path_info):
        """
        """
        


