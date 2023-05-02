from enum import IntEnum

from .common import *
from .key import Key


# File Type Association Priority Levels
class Priority(IntEnum):
    USER_CHOICE = 2     # User Choice Filetype Associations (highest priority)
    USER_DEFAULT = 1    # User Default Filetype Associations (medium priority)
    SYSTEM_DEFAULT = 0  # System Default Filetype Associations (lowest priority)

DEFAULT_PRIORITY = Priority.USER_CHOICE

# Paths
PATHS = [None] * len(Priority)
PATHS[Priority.USER_CHOICE] =    "HKCU:SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts"
PATHS[Priority.USER_DEFAULT] =   "HKCU:Software\\Classes"
PATHS[Priority.SYSTEM_DEFAULT] = "HKLM:SOFTWARE\\Classes"


class FileType(Key):
    class Priority(IntEnum):
        USER_CHOICE = 2     # User Choice Filetype Associations (highest priority)
        USER_DEFAULT = 1    # User Default Filetype Associations (medium priority)
        SYSTEM_DEFAULT = 0  # System Default Filetype Associations (lowest priority)


    PATHS[Priority.USER_CHOICE] =    "HKCU:SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts"
    PATHS[Priority.USER_DEFAULT] =   "HKCU:Software\\Classes"
    PATHS[Priority.SYSTEM_DEFAULT] = "HKLM:SOFTWARE\\Classes"
    
    def __init__(self,
            fileext:str,
            populate:bool|int|None=None
        )-> None:

        super().__init__(

        )

        self.priority = priority
        self.fileext = fileext
        self.typeref = None
        self.icon = None
        self.verbs = []
    
    def load(self):
        self.typeref = FileTypeReference()
        self.typeref.load(self.priority, self.fileext)
        self.icon = Icon()
        self.icon.load(self.priority, self.fileext)
        

    def save(self):
        pass

# The FileType data structures:
class FileTypeReference:
    REG_SUBKEY = {
        Priority.USER_CHOICE:    "UserChoice",
        Priority.USER_DEFAULT:   "",
        Priority.SYSTEM_DEFAULT: ""
    }
    REG_VALUE = {
        Priority.USER_CHOICE:    "ProgId",  # ProgId
        Priority.USER_DEFAULT:   "",        # (Default)
        Priority.SYSTEM_DEFAULT: ""         # (Default)
    }
    
    def __init__(self, typeref=None):
        self.typeref = typeref
    
    def __str__(self):
        return self.typeref
    def __repr__(self):
        return f"FileTypeReference(\"{self.typeref}\")"

    # Read the typeref
    def load(self, priority, fileext):    
        hive = HIVES[priority]
        root = PATHS[priority]
        subkey = FileTypeReference.REG_SUBKEY[priority]
        value = FileTypeReference.REG_VALUE[priority]
        if hive is None or root is None or fileext is None or subkey is None or value is None:
            self.typeref = None
            return
        
        regpath = root+"\\"+fileext+"\\"+subkey
        self.typeref = get_value(hive, regpath, value)

    # Write the typeref
    def save(self, priority, fileext):    
        hive = HIVES[priority]
        root = PATHS[priority]
        subkey = FileTypeReference.REG_SUBKEY[priority]
        value = FileTypeReference.REG_VALUE[priority]
        if hive is None or root is None or fileext is None or subkey is None or value is None:
            self.typeref = None
            return
        regpath = root+"\\"+fileext+"\\"+subkey



class Icon:
    REG_SUBKEY = {
        Priority.USER_CHOICE:    None,  # Icon is not allowed in USER_CHOICE
        Priority.USER_DEFAULT:   "DefaultIcon",
        Priority.SYSTEM_DEFAULT: "DefaultIcon"
    }
    REG_VALUE = {
        Priority.USER_CHOICE:    None,  # Icon is not allowed in USER_CHOICE
        Priority.USER_DEFAULT:   "",    # (Default)
        Priority.SYSTEM_DEFAULT: ""     # (Default)
    }
    
    def __init__(self, iconpath=None):
        self.iconpath = iconpath

    def __str__(self):
        return (self.iconpath)
    def __repr__(self):
        return f"Icon(\"{self.iconpath}\")"

    # Read the iconpath
    def load(self, priority, fileext):    
        hive = HIVES[priority]
        root = PATHS[priority]
        subkey = FileTypeReference.REG_SUBKEY[priority]
        value = FileTypeReference.REG_VALUE[priority]
        if hive is None or root is None or fileext is None or subkey is None or value is None:
            self.typeref = None
            return
        regpath = root+"\\"+fileext+"\\"+subkey
        self.iconpath = get_value(hive, regpath, value)

    # Write the iconpath
    def save(self, priority, fileext):    
        hive = HIVES[priority]
        root = PATHS[priority]
        subkey = Icon.REG_SUBKEY[priority]
        value = Icon.REG_VALUE[priority]
        if hive is None or root is None or fileext is None or subkey is None or value is None:
            self.typeref = None
            return
        regpath = root+"\\"+fileext+"\\"+subkey


class Verb:
    REG_SUBKEY = {
        Priority.USER_CHOICE:    None,  # Verb not allowed in USER_CHOICE
        Priority.USER_DEFAULT:   "shell",
        Priority.SYSTEM_DEFAULT: "shell"
    }

    REG_VALUE = {
        Priority.USER_CHOICE:    None,  # Verb not allowed in USER_CHOICE
        Priority.USER_DEFAULT:   "",    # (Default)
        Priority.SYSTEM_DEFAULT: ""     # (Default)
    }
    
    @staticmethod
    def load_all(priority, fileext):
        # Get a list of Verb objects under the specified fileext and priority level
        verbs = []
        hive = HIVES[priority]
        root = PATHS[priority]
        subkey = Verb.REG_SUBKEY[priority]
        if hive is None or root is None or fileext is None or subkey is None:
            return verbs 
        regpath = root+"\\"+fileext+"\\"+subkey
        verbnames = get_subkeys(hive, regpath)
        for verbname in verbnames:
            verb = Verb(verbname)
            verb.load(priority, fileext)
            verbs.append(verb)
        return verbs

    def __init__(self, verbname=None):
        self.verbname = verbname
    
    def __str__(self):
        return self.verbname
    def __repr__(self):
        return f"Verb(\"{self.verbname}\""

    # Read the verb
    def load(self, priority, fileext, verbname=None):    
        if verbname is None:
            verbname = self.verbname
        hive = HIVES[priority]
        root = PATHS[priority]
        subkey = Verb.REG_SUBKEY[priority]
        value = Verb.REG_VALUE[priority]
        if hive is None or root is None or fileext is None or subkey is None or verbname is None or value is None:
            self.typeref = None
            return
        regpath = root+"\\"+fileext+"\\"+subkey+"\\"+verbname
        self.verbname = verbname

    # Write the verb
    def save(self, priority, fileext, verbname=None):    
        if verbname is None:
            verbname = self.verbname
        hive = HIVES[priority]
        root = PATHS[priority]
        subkey = Verb.REG_SUBKEY[priority]
        value = Verb.REG_VALUE[priority]
        if hive is None or root is None or fileext is None or subkey is None or verbname is None or value is None:
            self.typeref = None
            return
        regpath = root+"\\"+fileext+"\\"+subkey+"\\"+verbname




class Command:
    REG_SUBKEY = {
        Priority.USER_CHOICE:    None,  # Command not allowed in USER_CHOICE
        Priority.USER_DEFAULT:   "command",
        Priority.SYSTEM_DEFAULT: "command"
    }
    REG_VALUE = {
        Priority.USER_CHOICE:    None,  # Command not allowed in USER_CHOICE
        Priority.USER_DEFAULT:   "",    # (Default)
        Priority.SYSTEM_DEFAULT: ""     # (Default)
    }
    
    def __init__(self, command=None):
        self.command = command
    
    def __str__(self):
        return self.command
    def __repr__(self):
        return f"Command(\"{self.command}\""

    # Read the command
    def load(self, priority, fileext, verb):    
        hive = HIVES[priority]
        root = PATHS[priority]
        verb_subkey = Verb.REG_SUBKEY[priority]
        subkey = FileTypeReference.REG_SUBKEY[priority]
        value = FileTypeReference.REG_VALUE[priority]
        if hive is None or root is None or fileext is None or verb_subkey is None or verb is None or subkey is None or value is None:
            self.command = None
            return
        regpath = root+"\\"+fileext+"\\"+verb_subkey+"\\"+verb+"\\"+subkey
        self.command = get_value(hive, regpath, value)

    # Write the command
    def load(self, priority, fileext, verb):    
        hive = HIVES[priority]
        root = PATHS[priority]
        verb_subkey = Verb.REG_SUBKEY[priority]
        subkey = Command.REG_SUBKEY[priority]
        value = Command.REG_VALUE[priority]
        if hive is None or root is None or fileext is None or verb_subkey is None or verb is None or subkey is None or value is None:
            self.command = None
            return
        regpath = root+"\\"+fileext+"\\"+verb_subkey+"\\"+verb+"\\"+subkey


