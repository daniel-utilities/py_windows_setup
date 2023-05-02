import pyregistryutils as reg

rootpath = "HKCU:Software\\Classes\\.abcd"

root   = reg.Key(rootpath,
                 values={
                     "":     ("root", reg.TYPE_REG_SZ),
                     "num":  (0, reg.TYPE_QWORD)
                 })


child1 = reg.Key((root, "relpath\\to\\child1"),
                 values={
                     "":     ("child1", reg.TYPE_REG_SZ),
                     "num":  (1, reg.TYPE_QWORD)
                 })
root.members["child1"] = child1


child2 = reg.Key((root, "relpath\\to\\child2"),
                 values={
                     "":     ("child2", reg.TYPE_REG_SZ),
                     "num":  (2, reg.TYPE_QWORD)
                 })
root.members["child2"] = child2


grandchild1 = reg.Key((child2, "grandchild1"),
                 values={
                     "":     ("grandchild1", reg.TYPE_REG_SZ),
                     "num":  (3, reg.TYPE_QWORD)
                 })
child2.members["grandchild1"] = grandchild1




# Save recursively
print(f"Saving root key and members...")
modified_keys = root.save()
for key in modified_keys:
    print(key)
print("")


# List subkeys
print(f"Listing subkeys of {rootpath}...")
subkeys = reg.list_subkeys(rootpath, maxdepth=-1)
for subkey in subkeys:
    print(subkey)
print("")


# List values
print(f"Listing values of root...")
vals = reg.list_values(root.abspath)
print(vals)
print("")


# List values
print(f"Listing values of grandchild1...")
vals = reg.list_values(grandchild1.abspath)
print(vals)
print("")


# Change a value separately
reg.save_value(grandchild1.abspath, reg.VALUE_DEFAULT, ("changed default value", reg.TYPE_REG_SZ))


# Load recursively
print(f"Reloading root key and members...")
root.load()
print("")


# Track a new value
grandchild1.values["newval"] = ("new string!", reg.TYPE_REG_SZ)


# Save individual
print(f"Saving grandchild1 values...")
grandchild1.save(recurse=False)
print("")


# List values
print(f"Listing values of grandchild1...")
vals = reg.list_values(grandchild1.abspath)
print(vals)
print("")


# Delete recursively
print(f"Deleting root key and members...")
deleted_keys = root.delete()
for key in deleted_keys:
    print(key)
print("")

