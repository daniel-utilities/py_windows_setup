import winreg
import os
from typing import Any
from itertools import compress

# Error handling
DEBUG_LEVEL = 0

# Registry access modes
MODE_READ = 0
MODE_WRITE = 1
MODE_BOTH = 2
MODE_DELETE = 3

# Registry Value Types
TYPE_NONE = winreg.REG_NONE             # No defined value type.
TYPE_BINARY = winreg.REG_BINARY         # Binary data in any form.
TYPE_DWORD = winreg.REG_DWORD           # 32-bit number.
TYPE_DWORD_LITTLE_ENDIAN = winreg.REG_DWORD_LITTLE_ENDIAN   # A 32-bit number in little-endian format. Equivalent to REG_DWORD.
TYPE_DWORD_BIG_ENDIAN = winreg.REG_DWORD_BIG_ENDIAN         # A 32-bit number in big-endian format.
TYPE_QWORD = winreg.REG_QWORD           # A 64-bit number.
TYPE_QWORD_LITTLE_ENDIAN = winreg.REG_QWORD_LITTLE_ENDIAN   # A 64-bit number in little-endian format. Equivalent to REG_QWORD.
TYPE_REG_SZ = winreg.REG_SZ             # A null-terminated string.
TYPE_EXPAND_SZ = winreg.REG_EXPAND_SZ   # Null-terminated string containing references to environment variables (%PATH%).
TYPE_MULTI_SZ = winreg.REG_MULTI_SZ     # A sequence of null-terminated strings terminated by two null characters. (Python handles this termination automatically.)
TYPE_LINK = winreg.REG_LINK             # A Unicode symbolic link.
TYPE_RESOURCE_LIST = winreg.REG_RESOURCE_LIST               # A device-driver resource list.
TYPE_FULL_RESOURCE_DESCRIPTOR = winreg.REG_FULL_RESOURCE_DESCRIPTOR     # A hardware setting.
TYPE_RESOURCE_REQUIREMENTS_LIST = winreg.REG_RESOURCE_REQUIREMENTS_LIST  # A hardware resource list.

# Name which references the (Default) value
VALUE_DEFAULT = ""                  # Name which refers to the (Default) value in a registry key is "".

# Registry Hives
HKLM = winreg.HKEY_LOCAL_MACHINE    # Physical state of the computer, including data about the bus type, system memory, and installed hardware and software.
HKCU = winreg.HKEY_CURRENT_USER     # Preferences of the current user. These preferences include the settings of environment variables, data about program groups, colors, printers, network connections, and application preferences.
HKCR = winreg.HKEY_CLASSES_ROOT     # Types (or classes) of documents and the properties associated with those types
HKU  = winreg.HKEY_USERS            # Default user configuration for new users on the local computer and the user configuration for the current user
HKPD = winreg.HKEY_PERFORMANCE_DATA # Access performance data. The data is not actually stored in the registry; the registry functions cause the system to collect the data from its source.
HKCC = winreg.HKEY_CURRENT_CONFIG   # Contains information about the current hardware profile of the local computer system.
HKDD = winreg.HKEY_DYN_DATA         # This key is not used in versions of Windows after 98.

# Hive name formats
HIVE_SHORTNAME = 0  # HKLM:...
HIVE_LONGNAME = 1   # HKEY_LOCAL_MACHINE\...

# Maps hive handles (int) to hive names
HIVE_NAMES_LONG = {
    HKLM: "HKEY_LOCAL_MACHINE",
    HKCU: "HKEY_CURRENT_USER",
    HKCR: "HKEY_CLASSES_ROOT",
    HKU:  "HKEY_USERS",
    HKPD: "HKEY_PERFORMANCE_DATA",
    HKCC: "HKEY_CURRENT_CONFIG",
    HKDD: "HKEY_DYN_DATA"
}
HIVE_NAMES_SHORT = {
    HKLM: "HKLM",
    HKCU: "HKCU",
    HKCR: "HKCR",
    HKU:  "HKU",
    HKPD: "HKPD",
    HKCC: "HKCC",
    HKDD: "HKDD"
}

# Maps hive names to handles
HIVE_INTS = {v: k for k, v in HIVE_NAMES_LONG.items()}
HIVE_INTS_SHORT = {v: k for k, v in HIVE_NAMES_SHORT.items()}



###############################################################################
## Internal Functions
###############################################################################

def __print_error__(
        exception:Exception,
        message:str
    )-> None:

    if DEBUG_LEVEL >= 1:
        print(message)
    if DEBUG_LEVEL >= 2:
        raise exception


def __open_handle__(
        abspath:str,
        mode:int
    )-> winreg.HKEYType|None:
    """
    Opens an IO handle to the specified key.

    Parameters:
    -----------
    abspath
        Absolute path of a registry key (including hive).
    mode
        Access mode. Must be one of the following:
        - MODE_READ:   opens a handle for reading.
        - MODE_WRITE:  creates the key if it does not exist, and opens a handle for writing.
        - MODE_BOTH:   creates the key if it does not exist, and opens a handle for both reading and writing.
        - MODE_DELETE: deletes the key if it exists and has no subkeys. Also see delete_key().
    
    Returns:
    --------
    handle | None
        Handle object for the specified key, or None if errors occurred.
    """

    # Validate abspath
    tup = split_abspath(abspath)
    if tup is None:
        return None     # invalid abspath
    hive = tup[0]
    localpath = tup[1]
    abspath = tup[2]

    if mode == MODE_READ:
        try:    
            return winreg.OpenKeyEx(hive, localpath, 0, winreg.KEY_READ)
        except Exception as e:
            __print_error__(e, f"Error opening READ handle for key: \"{abspath}\"")
            return None

    elif mode == MODE_WRITE:
        try:    
            return winreg.CreateKeyEx(hive, localpath, 0, winreg.KEY_WRITE)
        except Exception as e:
            __print_error__(e, f"Error opening WRITE handle for key: \"{abspath}\"")
            return None

    elif mode == MODE_BOTH:
        try:    
            return winreg.CreateKeyEx(hive, localpath, 0, winreg.KEY_ALL_ACCESS)
        except Exception as e:
            __print_error__(e, f"Error opening READ/WRITE handle for key: \"{abspath}\"")
            return None

    elif mode == MODE_DELETE:
        try:    
            winreg.DeleteKeyEx(hive, localpath)
            return 0
        except Exception as e: # Error deleting key (it may not exist)
            __print_error__(e, f"Error deleting key: \"{abspath}\"")
            return None

    else:   # Invalid mode
        return None



def __close_handle__(
        handle:winreg.HKEYType
    )-> None:
    """
    Close an IO handle.

    Parameters:
    ----------
    handle
        Handle object for an open registry key.
    """

    if handle is not None:
        winreg.CloseKey(handle)
        handle = None



###############################################################################
## Utility Functions
###############################################################################



def split_abspath(
        abspath:str,
        hivename_mode:int = HIVE_SHORTNAME
    )-> tuple[int, str, str]|None:
    """
    Splits an absolute path into a hive handle (int), hive-relative localpath (str), and clean absolute path (str)
    
    Parameters:
    -----------
    abspath
        String containing an absolute registry path.
        
        Both formats are allowed:
         - HKEY_LOCAL_MACHINE\\relative\\path\\to\\key
         - HKLM:relative\\path\\to\\key

    hivename_mode (Optional; Default=HIVE_SHORTNAME)
        Sets output format for abspath. One of the following:
         - HIVE_LONGNAME: Results in HKEY_LOCAL_MACHINE\\relative\\path\\to\\key
         - HIVE_SHORTNAME: Results in HKLM:relative\\path\\to\\key
    
    Returns:
    --------
    (hive, localpath, abspath) | None
         - hive: One of the predefined Hive handles (HKLM, HKCU, etc.)
         - localpath: Path relative to the hive.
         - abspath: Absolute path to the key (including hive), cleaned and validated.

        Returns None if errors occurred.
    """

    # Sanitize input
    if abspath is None:
        return None
    abspath = abspath.replace("/","\\").strip().strip(os.sep)
    if abspath == "":
        return None

    # Split hive and local path
    split_short = abspath.split(":", 1)    # HKLM:...
    split_long  = abspath.split(os.sep, 1) # HKEY_LOCAL_MACHINE\...
    if split_short[0] in HIVE_INTS_SHORT:
        hive = HIVE_INTS_SHORT[split_short[0]]
        localpath = split_short[1] if len(split_short) == 2 else ""
    elif split_long[0] in HIVE_INTS:
        hive = HIVE_INTS[split_long[0]]
        localpath = split_long[1] if len(split_long) == 2 else ""
    else:
        return None # Invalid hive
    
    # Clean up localpath
    localpath = os.path.normpath(localpath.strip().strip(os.sep))
    if localpath == ".":
        localpath = ""
    if " " in localpath or ":" in localpath or ".." in localpath:
        return None # invalid localpath

    # Reconstruct abspath
    if hivename_mode == HIVE_LONGNAME:
        abspath = os.path.join(HIVE_NAMES_LONG[hive], localpath) if localpath != "" else HIVE_NAMES_LONG[hive]
    else: # hivename_mode == HIVE_SHORTNAME:
        abspath = HIVE_NAMES_SHORT[hive]+":"+localpath

    return hive, localpath, abspath



def join_abspath(
        hive:int,
        localpath:str,
        hivename_mode:int = HIVE_SHORTNAME
    )-> str|None:
    """
    Returns an absolute registry path from a hive and a hive-relative path.
    
    Parameters:
    -----------
    hive
        One of the predefined Hive handles (HKLM, HKCU, etc.)
    localpath
        Key path relative to the hive.
    hivename_mode (Optional; Default=HIVE_SHORTNAME)
        Sets output format for abspath. One of the following:
         - HIVE_LONGNAME: Results in HKEY_LOCAL_MACHINE\\relative\\path\\to\\key
         - HIVE_SHORTNAME: Results in HKLM:relative\\path\\to\\key
    
    Returns:
    --------
    abspath | None
        String containing an absolute registry path, or None if errors occurred.
    """

    if hive is None or localpath is None:
        return None

    # Clean up localpath
    localpath = os.path.normpath(localpath.replace("/","\\").strip().strip(os.sep))
    if localpath == ".":
        localpath = ""
    if " " in localpath or ":" in localpath or ".." in localpath:
        return None # invalid localpath

    # Attach hive name string
    if hivename_mode == HIVE_SHORTNAME and hive in HIVE_NAMES_SHORT:
        return HIVE_NAMES_SHORT[hive]+":"+localpath
    elif hivename_mode == HIVE_LONGNAME and hive in HIVE_NAMES_LONG:
        return os.path.join(HIVE_NAMES_LONG[hive], localpath) if localpath != "" else HIVE_NAMES_LONG[hive]
    else:
        return None # Invalid hive



def get_relpath(
        rootpath:str,
        subkeypath:str
    )-> str|None:
    """
    Returns the relative path from the root key to the subkey.
    
    Subkey must be below the root.

    Parameters:
    -----------
    rootpath
        Absolute path of a registry key (including hive).
    subkeypath
        Absolute path of a subkey.
    
    Returns:
    --------
    relpath | None
        Path of subkey within the root key.
        
        Returns None if paths are invalid, or if subkeypath is not a subkey of root key.
    """

    # Validate paths
    tup1 = split_abspath(rootpath, HIVE_LONGNAME)
    if tup1 is None:
        return None     # invalid rootpath
    rootpath = tup1[2]
    tup2 = split_abspath(subkeypath, HIVE_LONGNAME)
    if tup2 is None:
        return None     # invalid subkeypath
    subkeypath = tup2[2]

    # Get relative path
    relpath = os.path.relpath(subkeypath, rootpath)
    if ".." in relpath:
        return None     # subkeypath is not a subkey of root
    if relpath == ".":
        return ""       # subkeypath is the same as root
    return relpath





def list_subkeys(
        abspath:str,
        maxdepth:int = -1
    )-> list[str]:
    """
    Lists all subkeys under abspath.

    Parameters:
    -----------
    abspath
        Absolute path of a registry key (including hive).
    maxdepth (Optional; Default=-1)
        Search depth for subkeys.
          - maxdepth = -1 : List all subkeys underneath abspath.
          - maxdepth = 0  : List only subkeys immediately under abspath.
          - maxdepth > 0  : List all subkeys underneath abspath up to the specified depth.
    
    Returns:
    --------
    subkeys
        Absolute paths to subkeys of abspath.
    """

    # Validate abspath
    tup = split_abspath(abspath)
    if tup is None:
        return []     # invalid abspath
    abspath = tup[2]

    try:    # Open handle to root key (abspath)
        with __open_handle__(abspath, MODE_READ) as handle:
            # List subkeys
            subkeys = []
            for i in range(winreg.QueryInfoKey(handle)[0]):    # [0] is the number of subkeys this key has
                subkey = os.path.join(abspath, winreg.EnumKey(handle, i))
                subkeys.append(subkey)      # Add subkey which is directly underneath the root key
                if maxdepth != 0:
                    subkeys += list_subkeys(subkey, maxdepth=maxdepth-1)    # Search for more subkeys underneath subkey
            return subkeys
    except TypeError: # Error opening handle
        return []



# Reads a dict of value tuples {"name": (data, type)} from abspath.
#   Returns an empty dict {} if no values are present, or None if an error has occurred.
def list_values(
        abspath:str
    )-> dict[str, tuple[Any,int]|None] | None:
    """
    Lists all values under abspath.

    Parameters:
    -----------
    abspath
        Absolute path of a registry key (including hive).
    
    Returns:
    --------
    values | None
        Values dict containing {name: value} pairs from the registry.

        values = {"name": (data, type), ... }
    """

    try:    # Open handle to root key (abspath)
        with __open_handle__(abspath, MODE_READ) as handle:
            values = {}
            for i in range(winreg.QueryInfoKey(handle)[1]):    # [1] is the number of values this key has
                tup = winreg.EnumValue(handle, i)
                values[tup[0]] = (tup[1], tup[2])   # tup [0] is name, [1] is data, [2] is type 
            return values
    except TypeError: # Error opening handle
        return None




def create_key(
        abspath:str
    )-> str|None:
    """
    Creates a new key at abspath. Recursively creates all missing keys in the path.

    No changes are made to keys which already exist.

    Parameters:
    -----------
    abspath
        Absolute path of a registry key (including hive).
    
    Returns:
    --------
    new_key | None
        Absolute path of the new key, or None if errors occurred.
    """

    # Validate abspath
    tup = split_abspath(abspath)
    if tup is None:
        return None     # invalid abspath
    localpath = tup[1]
    abspath = tup[2]
    if localpath == "":
        return None     # cannot perform this operation on the hive root

    try:    # Open handle to root key (abspath)
        with __open_handle__(abspath, MODE_WRITE) as handle:
            return abspath
    except TypeError: # Error opening handle
        return None
        


# Deletes the key at abspath, including its values and subkeys.
#   Returns a list of paths of keys which were deleted.
def delete_key(
        abspath:str
    )-> list[str]:
    """
    Deletes a key at abspath. Recursively deletes all subkeys and values.

    Parameters:
    -----------
    abspath
        Absolute path of a registry key (including hive).
    
    Returns:
    --------
    deleted_keys | None
        List of paths of keys which were deleted.
    """

    # Validate abspath
    tup = split_abspath(abspath)
    if tup is None:
        return []     # invalid abspath
    localpath = tup[1]
    abspath = tup[2]
    if localpath == "":
        return []     # cannot perform this operation on the hive root

    # Delete subkeys before deleting the root key (abspath)
    keys   = [abspath] + list_subkeys(abspath, maxdepth=-1) # Paths of keys to delete, including the root key (abspath)
    depths = [key.count(os.sep) for key in keys]            # Key depths are the number of '\' in their paths.
    deleted_keys=[]
    for depth in range(max(depths), min(depths)-1, -1):     # Delete deepest keys first, and root key last
        for key in compress(keys, [e==depth for e in depths]):  # Select only keys at the current depth
            #print(f"Deleting: {key}")
            if __open_handle__(key, MODE_DELETE) is None:
                return deleted_keys
            deleted_keys.append(key)
    return deleted_keys



def load_value(
        abspath:str,
        name:str
    )-> tuple[Any,int]|None:
    """
    Loads an individual value from abspath.

    Parameters:
    -----------
    abspath
        Absolute path of a registry key (including hive).
    name
        Name of value to load from the key.
    
    Returns:
    --------
    value | None
        Value tuple (data, type) loaded from the registry.
        
        Returns None if the value does not exist, or if an error has occurred.
    """

    if name is None:
        return None

    try:    # Open handle to root key (abspath)
        with __open_handle__(abspath, MODE_READ) as handle:
            try:
                return winreg.QueryValueEx(handle, name)   # tup [0] is data, [1] is type
            except: # Value does not exist
                return None
    except TypeError: # Error opening handle
        return None



def save_value(
        abspath:str,
        name:str,
        value:tuple[Any,int]|None
    )-> str|None:
    """
    Saves an individual value to abspath.

    The key is created if it does not already exist.

    Parameters:
    -----------
    abspath
        Absolute path of a registry key (including hive).
    name
        Name of value to save to the key.
    value | None
        Value tuple (data, type) to save to the registry.

        Set to tuple to None to delete from the key.

    Returns:
    --------
    modified_key | None
        Absolute path of modified key, or None if errors occurred.
    """

    if name is None:
        return None

    # Validate abspath
    tup = split_abspath(abspath)
    if tup is None:
        return []     # invalid abspath
    abspath = tup[2]

    try:    # Open handle to root key (abspath)
        with __open_handle__(abspath, MODE_WRITE) as handle:
            if value is not None:   # Write a single value to the registry
                winreg.SetValueEx(handle, name, 0, value[1], value[0])   # value tuple must be (data, type)
            else:                   # Delete a single value from the registry
                try:
                    winreg.DeleteValue(handle, name)
                except FileNotFoundError:  # This is fine, because we were trying to delete the value anyway
                    pass
            return abspath
    except TypeError: # Error opening handle
        return None



def delete_value(
        abspath:str,
        name:str
    )-> str|None:
    """
    Deletes an individual value from abspath.

    Same as save_value(abspath, name, None).

    Parameters:
    -----------
    abspath
        Absolute path of a registry key (including hive).
    name
        Name of value to save to the key.

    Returns:
    --------
    modified_key | None
        Absolute path of modified key, or None if errors occurred.
    """

    return save_value(abspath, name, None)



def load_values(
        abspath:str,
        values:dict[str, tuple[Any,int]|None]
    )-> dict[str, tuple[Any,int]|None] | None:
    """
    Loads the specified values from abspath.

    Parameters:
    -----------
    abspath
        Absolute path of a registry key (including hive).
    values
        Values dict containing {name: value} pairs to load from the registry.

        values = {"name": (data, type), ... }
    
    Returns:
    --------
    values | None
        Values dict containing updated {name: value} pairs, or None if an error has occurred.

        Individual value tuples are None if they do not exist in abspath.

        values = {"name": (data, type), ... }
    """

    # Get all values in the key
    new_values = list_values(abspath)
    if new_values is None:
        return None # Could not access the key
    
    # Update values
    for name in values:
        if name in new_values:  # Value exists in key
            values[name] = new_values[name]
        else:                   # Value does not exist in key
            values[name] = None
    return values
    


def save_values(
        abspath:str,
        values:dict[str, tuple[Any,int]|None]
    )-> str|None:
    """
    Saves the specified values to abspath.

    The key is created if it does not already exist.

    Parameters:
    -----------
    abspath
        Absolute path of a registry key (including hive).
    values
        Values dict containing {name: value} pairs to save to the registry.
          - Set individual value tuples to None to delete from the key.
          - Set whole dict to None to delete all values from the key.

        values = {"name": (data, type), ... }
    
    Returns:
    --------
    modified_key | None
        Absolute path of modified key, or None if errors occurred.
    """

    # Validate abspath
    tup = split_abspath(abspath)
    if tup is None:
        return None     # invalid abspath
    abspath = tup[2]

    # Delete all values if values=None
    if values is None:
        values = list_values(abspath)
        if values is None:
            return None     # Error reading from key
        for name in values:
            values[name] = None # mark each value for deletion
    
    try:    # Open handle to root key (abspath)
        with __open_handle__(abspath, MODE_WRITE) as handle:
            for name in values:
                value = values[name]
                if value is not None:   # Write a single value to the registry
                    winreg.SetValueEx(handle, name, 0, value[1], value[0])   # value tuple must be (data, type)
                else:                   # Delete a single value from the registry
                    try:
                        winreg.DeleteValue(handle, name)
                    except FileNotFoundError:  # This is fine, because we were trying to delete the value anyway
                        pass
            return abspath
    except TypeError: # Error opening handle
        return None

    

def delete_all_values(
        abspath:str
    )-> str|None:
    """
    Deletes all values from abspath.

    Same as: save_values(abspath, None).

    Parameters:
    -----------
    abspath
        Absolute path of a registry key (including hive).
    
    Returns:
    --------
    modified_key | None
        Absolute path of modified key, or None if errors occurred.
    """

    return save_values(abspath, None)
