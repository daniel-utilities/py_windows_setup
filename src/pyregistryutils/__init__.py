from .common import *
from .key import *
from .filetype import *

# To import from this package: use
# A)
#   import pyregistryutils as reg
#   key = reg.Key(...)      # from "key.py"
#   hive = reg.HKLM         # from "common.py"
#
# B)
#   from pyregistryutils import *
#   key = Key(...)          # from "key.py"
#   hive = HKLM             # from "common.py"
#   