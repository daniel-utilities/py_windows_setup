import pyregistryutils as reg

reg.DEBUG_LEVEL = 2

rootpath = "HKCU:Software\\Classes\\.abcd"

print("")

# Create subkeys
print("Creating keys...")
created_keys = []
created_keys.append(reg.create_key(rootpath+"\\lv0_a\\lv1_aa\\lv2_aaa"))
created_keys.append(reg.create_key(rootpath+"\\lv0_a\\lv1_aa\\lv2_aab"))
created_keys.append(reg.create_key(rootpath+"\\lv0_a\\lv1_ab"))
created_keys.append(reg.create_key(rootpath+"\\lv0_b\\lv1_ba"))
created_keys.append(reg.create_key(rootpath+"\\lv0_b\\lv1_bb\\lv2_bba"))
created_keys.append(reg.create_key(rootpath+"\\lv0_b\\lv1_bb\\lv2_bbb"))
created_keys.append(reg.create_key(rootpath+"\\lv0_c"))
for key in created_keys:
    print(key)
print("")


# List subkeys
print(f"Listing subkeys of {rootpath}...")
subkeys = reg.list_subkeys(rootpath, maxdepth=-1)
for subkey in subkeys:
    print(subkey)
print("")


# Delete subkeys
print(f"Deleting subkeys \"lv0_a\" and \"lv0_c\"...")
deleted_keys = []
deleted_keys += reg.delete_key(rootpath+"\\lv0_a")
deleted_keys += reg.delete_key(rootpath+"\\lv0_c")
for key in deleted_keys:
    print(key)
print("")


# Save values
print(f"Saving values of {rootpath}...")
modified_keys = []
modified_keys.append(reg.save_value(rootpath, reg.VALUE_DEFAULT, ("newval", reg.TYPE_REG_SZ) ) )
modified_keys.append(reg.save_value(rootpath, "num", (123, reg.TYPE_DWORD) ) )
for key in modified_keys:
    print(key)
print("")


# Load values
print(f"Loading values of {rootpath}...")
val1 = reg.load_value(rootpath, "")
val2 = reg.load_value(rootpath, "num")
print(f"(Default): {val1}")
print(f"      num: {val2}")
print("")


# Delete values
print(f"Deleting values of {rootpath}...")
modified_keys = []
modified_keys.append(reg.save_value(rootpath, reg.VALUE_DEFAULT, None) )
modified_keys.append(reg.save_value(rootpath, "num", None) )
for key in modified_keys:
    print(key)
print("")


# Save multiple values
print(f"Saving multiple values of {rootpath}...")
vals = {
    reg.VALUE_DEFAULT: ("asdf", reg.TYPE_EXPAND_SZ),
    "num": (456, reg.TYPE_QWORD)
}
modified_keys = []
modified_keys.append(reg.save_values(rootpath, vals) )
for key in modified_keys:
    print(key)
print("")


# List values
print(f"Listing values of {rootpath}...")
vals = reg.list_values(rootpath)
print(vals)
print("")


# Load multiple values
print(f"Loading multiple values of {rootpath}...")
vals = {
    reg.VALUE_DEFAULT: None,
    "num": None
}
vals = reg.load_values(rootpath, vals)
print(vals)
print("")


# Delete all values
print(f"Deleting all values of {rootpath}...")
modified_keys = []
modified_keys.append(reg.save_values(rootpath, None) )
for key in modified_keys:
    print(key)
print("")



# List values
print(f"Listing values of {rootpath}...")
vals = reg.list_values(rootpath)
print(vals)
print("")


# Delete key
print(f"Deleting key at {rootpath}...")
deleted_keys = []
deleted_keys += reg.delete_key(rootpath)
for key in deleted_keys:
    print(key)
print("")

