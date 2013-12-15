__author__ = 'Epsirom'

import os
os.environ.setdefault('SSAST_DEPLOYMENT', 'tsinghuatuan')

from app import app

application = app
