from typing import Union, Any

from .common import *



def parse_location(
        location:Union[str, int, "Key", tuple["Key",str], tuple[int,str] ]
    )-> tuple[int, str, str]|None:
    """
    Parses a "location" into a hive handle (int), hive-relative localpath (str), and absolute path (str).
    
    Parameters:
    -----------
    location
        One of the following:
         - abspath(str): Absolute path to a key (including hive)
         - hivehandle(int): One of the predefined Hive handles (HKLM, HKCU, etc.)
         - key(Key): Key object
         - (key(Key), relpath(str)): Key object and relative path
         - (hivehandle(int), localpath(str)): Hive handle and relative path
        
        Both formats are allowed for absolute paths:
         - HKEY_LOCAL_MACHINE\\relative\\path\\to\\key
         - HKLM:relative\\path\\to\\key
    
    Returns:
    --------
    (hive, localpath, abspath) | None
         - hive: One of the predefined Hive handles (HKLM, HKCU, etc.)
         - localpath: Path relative to the hive.
         - abspath: Absolute path to the key (including hive), cleaned and validated.

        Returns None if errors occurred.
    """

    if location is None:
        return None

    # Location (str) is an absolute registry path
    elif isinstance(location, str):
        abspath = location

    # Location (int) is a registry hive:
    elif isinstance(location, int):
        hive = location
        localpath = ""
        abspath = join_abspath(hive, localpath)

    # Location (Key) is a Key object:
    elif isinstance(location, Key):
        abspath = location.abspath

    # Location (Key, str) is path relative to another key
    elif isinstance(location, tuple) and len(location)==2 and isinstance(location[0], Key) and isinstance(location[1], str):
        rootpath = location[0].abspath
        relpath = location[1].strip().strip(os.sep)
        abspath = os.path.join(rootpath, relpath)
    
    # Location (int, str) is a path relative to a registry hive
    elif isinstance(location, tuple) and len(location)==2 and isinstance(location[0], int) and isinstance(location[1], str):
        hive = location[0]
        localpath = location[1]
        abspath = join_abspath(hive, localpath)
    
    # Invalid location
    else:
        return None
    
    return split_abspath(abspath)



class Key:
    """
    Class representing a Windows Registry key and its values.
    """

    POPULATE_ALL_SUBKEYS = True
    POPULATE_VALUES = False
    
    def __init__(self,
            location:Any|None = None,
            members:dict[str, "Key"]|None = None,
            values:dict[str, tuple[Any,int]|None]|None = None,
            populate:bool|int|None = None
        )-> None:
        """
        Create a new Key object.

        Parameters
        ----------
        location (Optional; Default=None)
            Absolute path (str) of this key, or some other value parsable by parse_location.
        members (Optional; Default={})
            Dict of Key objects to track: {"name": key_object}.
            Tracked members are loaded and saved with load() and save().
        values (Optional; Default={})
            Dict of Value tuples to track: {"name": (data, type)} .
            Tracked values are loaded and saved with load() and save().
        populate (Optional; Default=None)
            Argument to populate() function, or None to skip population.
        """
        
        self.location = location
        self.members = members
        self.values = values
        if populate is not None:
            self.populate(populate)
    

    # Properties (read-only) and attributes (may have special actions on write)
    @property
    def hive(self)-> int:
        tup = parse_location(self.location)
        if self.location is None:
            return None
        return tup[0]

    @property
    def localpath(self)-> str:
        tup = parse_location(self.location)
        if tup is None:
            return None
        return tup[1]

    @property
    def abspath(self)-> str:
        tup = parse_location(self.location)
        if tup is None:
            return None
        return tup[2]
    
    def __setattr__(self, __name:str, __value:Any)-> None:
        if __name == "members":
            __value = {} if __value is None else __value
        elif __name == "values":
            __value = {} if __value is None else __value

        self.__dict__[__name] = __value
    

    # Private methods
    def __str__(self)-> str:
        return self.abspath
    
    def __repr__(self)-> str:
        return self.__str__()



    # Public methods
    def populate(self,
            recurse:bool|int=-1
        )-> None:
        """
        Populates self.values and self.members with values and subkeys from the registry.

        All values in the referenced registry key are added to self.values, overwriting any existing values with the same names.

        All subkeys (up to the specified depth) are added to self.members, unless a member for that key already exists.
        Subkey members are populated with values, but 

        Parameters
        ----------
        recurse (Optional; default=-1)
            Search for subkeys up to the specified depth and add them as members.
             - True or Key.POPULATE_ALL_SUBKEYS: Same as recurse=-1
             - False or Key.POPULATE_VALUES: Do not add subkeys as members; only populate values
             - -1 (Default): Add all subkeys as members.
             - 0: Add only the subkeys immediately beneath this key.
             - >0: Add subkeys only up to the specified depth.
        """

        abspath = self.abspath

        # List all values in this key, and add them to self.values
        newvals = list_values(abspath)
        if newvals is None:
            return  # Could not access key
        self.values |= newvals

        if recurse is None or recurse is False:  
            return # Do not add subkeys as members
        
        # List subkeys and add them to self.members
        maxdepth = -1 if recurse is True else recurse
        subkeys = list_subkeys(abspath, maxdepth)
        if subkeys is None:
            return  # Could not access key
        for subkey_path in subkeys:
            tup = self.get_member_by_location(subkey_path)
            if tup is None: # member does not exist for the subkey
                self.add_member(Key(subkey_path, populate=Key.POPULATE_VALUES))
            else:           # member exists
                self.members[tup[0]].populate(recurse=Key.POPULATE_VALUES)
            
                 

    def load(self,
            recurse:bool = True
        )-> None:
        """
        Load from registry all values tracked by this key and its members.

        Parameters
        ----------
        recurse (Optional; Default=True)
            If True, also calls load(recurse=True) on each member key.
        """

        # Load all tracked values (if the key exists)
        values = load_values(self.abspath, self.values)
        if values is not None:
            self.values = values

        # Load all member keys
        if recurse is True:
            for name in self.members:
                self.members[name].load(recurse=recurse)
    


    def save(self, 
            recurse:bool = True
        )-> list[str]:
        """
        Save to the registry all values tracked by this key and its members.

        All missing keys and values are created during this process.       

        Parameters
        ----------
        recurse (Optional; Default=True)
            If True, also calls save(recurse=True) on each member key.
        
        Returns
        -------
        modified_keys
            Paths of keys which were modified.
        """

        modified_keys = []

        # Save all tracked values
        key = save_values(self.abspath, self.values)
        if key is not None:
            modified_keys.append(key)

        # Save all tracked member keys
        if recurse is True:
            for name in self.members:
                key = self.members[name].save(recurse=recurse)
                if key is not None:
                    modified_keys += (key)
        return modified_keys



    def delete(self,
            recurse:bool = True
        )-> list[str]:
        """
        Delete this key, its members, and all subkeys and values from the registry.

        Parameters
        ----------
        recurse (Optional; Default=True)
            If True, also calls delete(recurse=True) on each member key.
        
        Returns
        -------
        deleted_keys
            List of absolute paths of keys deleted from the registry.
        """

        deleted_keys = []
        
        # Delete this key
        keys = delete_key(self.abspath)
        if keys is not None:
            deleted_keys += keys

        # Delete all tracked members (recursively)
        if recurse is True:
            for name in self.members:
                deleted_keys += self.members[name].delete(recurse=recurse)
        return deleted_keys
    


    def add_member(self,
            key:"Key",
            name:str=None
        )-> tuple[str, "Key"]:
        """
        Add a key as a tracked member. Overwrites another member of the same name.
        
        If a name is not provided, a name will be chosen automatically.

        Parameters:
        -----------
        key
            Key object to add. Tracked members are loaded and saved with load() and save().
        name (Optional)
            Name of new member. If not provided, name is set to the key's relative path (if it is a subkey)
            or the absolute path (if not a subkey).
        
        Returns:
        --------
        (name, key)
            Tuple containing the name and member object.
        """
        
        if name is None:
            # Assume key is a subkey, and name it the same as its relative path
            name = get_relpath(self.abspath, key.abspath) 
        if name is None:
            # Key is not a subkey, so name it after its absolute path
            name = key.abspath
        
        self.members[name] = key
        return (name, key)


    
    def get_member(self,
            name:str
        )-> tuple[str,"Key"]|None:
        """
        Return tracked member key by name.

        Parameters:
        -----------
        name
            Name of the tracked member key.
        
        Returns:
        --------
        (name, key) | None
            Tuple containing the name and member object, or None if no member exists by that name.
        """

        if name in self.members:
            return (name, self.members[name])
        return None



    def get_member_by_location(self,
            location:Any
        )-> tuple[str,"Key"]|None:
        """
        Return tracked member key by location.

        Parameters:
        -----------
        location
            Absolute path (str) of the member key, or some other value parsable by parse_location.
        
        Returns:
        --------
        (name, key) | None
            Tuple containing the name and member object, or None if no member exists at that location.
        """

        tup = parse_location(location)
        if tup is None:
            return None # invalid location
        abspath = tup[2]

        for name in self.members:
            member = self.members[name]
            if abspath == member.abspath:
                return (name, member)
        return None # member not found

            

    def remove_member(self,
            name:str
        )-> tuple[str,"Key"]|None:
        """
        Remove a named member from tracking. Removes the name and key from self.members,
        but does not delete anything from the registry (see delete()).

        Parameters:
        -----------
        name
            Name of the tracked member key.
        
        Returns:
        --------
        (name, key) | None
            Tuple containing the name and member object, or None if no member exists by that name.
        """

        if name in self.members:
            return (name, self.members.pop(name))
        return None
    

    
    def add_value(self,
            name:str,
            value:tuple[Any,int]|None
        )-> tuple[ str, tuple[Any,int]|None ]:
        """
        Add a tracked value. Overwrites another value of the same name.

        Parameters:
        -----------
        name
            Name of new value.
        value | None
            Value tuple (data, type), or None to mark the value for deletion.

        Returns:
        --------
        (name, value)
            Tuple with name and value.
            
            "value" is a tuple containing (data, type), or None if unset or marked for deletion.
        """
        
        if name is None:
            return None
        self.values[name] = value
        return (name, value)


    
    def get_value(self,
            name:str
        )-> tuple[ str, tuple[Any,int]|None ]|None:
        """
        Return a tracked value by name.

        Parameters:
        -----------
        name
            Name of tracked value.
        
        Returns:
        --------
        (name, value) | None
            Tuple with name and value, or None if name is not tracked.

            "value" is a tuple containing (data, type), or None if unset or marked for deletion.
        """
        
        if name in self.values:
            return (name, self.values[name])
        return None



    def remove_value(self,
            name:str
        )-> tuple[ str, tuple[Any,int]|None ]|None:
        """
        Remove a named value from tracking. Removes the name and value from self.values,
        but does not modify the registry (see save()).

        Parameters:
        -----------
        name
            Name of the tracked value.
        
        Returns:
        --------
        (name, value) | None
            Tuple with name and value, or None if name is not tracked.
            
            "value" is a tuple containing (data, type), or None if unset or marked for deletion.
        """

        if name in self.values:
            return (name, self.values.pop(name))
        return None
    
