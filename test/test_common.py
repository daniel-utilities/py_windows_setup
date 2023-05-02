import unittest

#   Import modules
from pyregistryutils.common import *

#   All test*.py functions under /test are scanned for TestCase classes.
#   All classes inheriting from unittest.TestCase are scanned for "test_" functions.
#   All "test_" functions should contain one or more assertions:
#       self.assertEqual              a == b 	
#       self.assertNotEqual           a != b 	
#       self.assertTrue               bool(x) is True 	
#       self.assertFalse              bool(x) is False 	
#       self.assertIs                 a is b 	
#       self.assertIsNot              a is not b 	
#       self.assertIsNone             x is None 	
#       self.assertIsNotNone          x is not None 	
#       self.assertIn                 a in b 	
#       self.assertNotIn              a not in b 	
#       self.assertIsInstance         is instance(a,b) 	
#       self.assertNotIsInstance      not is instance(a,b) 	
#       self.assertRaises             fun(*args,**kwds) raises exc 	
#       self.assertRaisesRegexp       fun(*args,**kwds) raises exc(regex) 	
#       self.assertAlmostEqual        round(a-b,7) == 0 	
#       self.assertNotAlmostEqual     round(a-b,7) != 0 	
#       self.assertGreater            a > b 	
#       self.assertGreaterEqual       a >= b 	
#       self.assertLess               a < b 	
#       self.assertLessEqual          a <= b 	
#       self.assertRegexpMatches      r.search(s) 	
#       self.assertNotRegexpMatches   not r.search(s) 	
#       self.assertItemsEqual         sorted(a) == sorted(b) 	
#       self.assertDictContainsSubset all the key/value pairs in a exist in b 	
#       self.assertMultiLineEqual     strings 	
#       self.assertSequenceEqual      sequences 	
#       self.assertListEqual          lists 	
#       self.assertTupleEqual         tuples 	
#       self.assertSetEqual           sets or frozensets 	
#       self.assertDictEqual          dicts 	

class Test_join_abspath(unittest.TestCase):

    def test_equals(self):
        testcases = [
        #   [ (input_args),     (correct_output)      ],
            # Different hives, different name formats
            [ (HKCU, "Software\\Classes", HIVE_SHORTNAME), ("HKCU:Software\\Classes")                ],
            [ (HKCU, "Software\\Classes", HIVE_LONGNAME ), ("HKEY_CURRENT_USER\\Software\\Classes")  ],
            [ (HKLM, "Software\\Classes", HIVE_SHORTNAME), ("HKLM:Software\\Classes")                ],
            [ (HKLM, "Software\\Classes", HIVE_LONGNAME ), ("HKEY_LOCAL_MACHINE\\Software\\Classes") ],
            [ (HKCR, "Software\\Classes", HIVE_SHORTNAME), ("HKCR:Software\\Classes")                ],
            [ (HKCR, "Software\\Classes", HIVE_LONGNAME ), ("HKEY_CLASSES_ROOT\\Software\\Classes")  ],
            # Extra slashes, leading/trailing whitespace
            [ (HKCU, "  \\Software\\\\Classes\\  ", HIVE_SHORTNAME), ("HKCU:Software\\Classes")                ],
            [ (HKCU, "  \\Software\\\\Classes\\  ", HIVE_LONGNAME ), ("HKEY_CURRENT_USER\\Software\\Classes")  ],
            # Empty localpath
            [ (HKCU, "", HIVE_SHORTNAME),       ("HKCU:")              ],
            [ (HKCU, " \\", HIVE_SHORTNAME),    ("HKCU:")              ],
            [ (HKCU, "", HIVE_LONGNAME ),       ("HKEY_CURRENT_USER")  ],
            [ (HKCU, " \\", HIVE_LONGNAME ),    ("HKEY_CURRENT_USER")  ],
            # Relative paths (. , ..)
            [ (HKCU, ".\\Software\\\\Classes\\", HIVE_SHORTNAME),            ("HKCU:Software\\Classes")                 ],
            [ (HKCU, "\\.\\Software\\Classes\\  ", HIVE_LONGNAME ),          ("HKEY_CURRENT_USER\\Software\\Classes")   ],
            [ (HKCU, ".\\Software\\..\\Other\\Classes  ", HIVE_SHORTNAME),   ("HKCU:Other\\Classes")                    ],
            [ (HKCU, "\\.\\Software\\..\\Other\\Classes  ", HIVE_LONGNAME ), ("HKEY_CURRENT_USER\\Other\\Classes")      ],
            # Forward slashes
            [ (HKCU, "Software/Classes", HIVE_SHORTNAME),   ("HKCU:Software\\Classes")                  ],
            [ (HKCU, "\\Software/Classes", HIVE_LONGNAME ), ("HKEY_CURRENT_USER\\Software\\Classes")    ]
        ]
        for testcase in testcases:
            args = testcase[0] if isinstance(testcase[0], tuple) else (testcase[0],) # handle single-element tuples
            correct = testcase[1]
            actual = join_abspath(*args)
            with self.subTest(msg=f"TEST INPUT: args={args}"):
                self.assertEqual(actual, correct)
    
    def test_none(self):
        testcases = [
        #   [ (input_args) ],
            # Null inputs
            [ (None, None) ],
            [ (None, "Software\\Classes", HIVE_SHORTNAME)   ],
            [ (HKLM, None, HIVE_SHORTNAME)                  ],
            [ (HKLM, "Software\\Classes", None)             ],
            # Invalid paths
            [ (HKCU, "..") ],
            [ (HKCU, " \\..\\  ") ],
            [ (HKCU, "asdf\\..\\..\\asdf") ],
            # Invalid characters
            [ (HKLM, "Path with spaces", HIVE_SHORTNAME)    ],
            [ (HKLM, "Path\\wi:th\\colons", HIVE_SHORTNAME) ],
            # Invalid hive
            [ (1234, "Software\\Classes", HIVE_SHORTNAME) ],
            [ ("",   "Software\\Classes", HIVE_SHORTNAME) ],
            [ (None, "Software\\Classes", HIVE_LONGNAME ) ],
            [ (None, "Software\\Classes", -1 ) ]
        ]
        for testcase in testcases:
            args = testcase[0] if isinstance(testcase[0], tuple) else (testcase[0],) # handle single-element tuples
            actual = join_abspath(*args)
            with self.subTest(msg=f"TEST INPUT: args={args}"):
                self.assertIsNone(actual)






    
class Test_split_abspath(unittest.TestCase):

    def test_equals(self):
        testcases = [
        #   [ (input_args),     (correct_output)      ],
            # Different hives, different name formats
            [ ("HKCU:Software\\Classes"),               (HKCU, "Software\\Classes", "HKCU:Software\\Classes") ],
            [ ("HKEY_CURRENT_USER\\Software\\Classes"), (HKCU, "Software\\Classes", "HKCU:Software\\Classes") ],
            [ ("HKLM:Software\\Classes"),               (HKLM, "Software\\Classes", "HKLM:Software\\Classes") ],
            [ ("HKEY_LOCAL_MACHINE\\Software\\Classes"), (HKLM, "Software\\Classes", "HKLM:Software\\Classes") ],
            [ ("HKCR:Software\\Classes"),               (HKCR, "Software\\Classes", "HKCR:Software\\Classes") ],
            [ ("HKEY_CLASSES_ROOT\\Software\\Classes"), (HKCR, "Software\\Classes", "HKCR:Software\\Classes") ],
            # Extra slashes, leading/trailing whitespace
            [ ("  \\HKCU:\\Software\\\\Classes\\  "), (HKCU, "Software\\Classes", "HKCU:Software\\Classes") ],
            [ ("  \\HKEY_CURRENT_USER\\Software\\Classes\\  "), (HKCU, "Software\\Classes", "HKCU:Software\\Classes") ],
            # Empty localpath
            [ ("HKCU"),                 (HKCU, "", "HKCU:") ],
            [ ("HKCU:"),                (HKCU, "", "HKCU:") ],
            [ (" HKCU:\\ "),            (HKCU, "", "HKCU:") ],
            [ ("HKEY_CURRENT_USER"),    (HKCU, "", "HKCU:") ],
            [ (" HKEY_CURRENT_USER\\ "), (HKCU, "", "HKCU:") ],
            # Relative paths (. , ..)
            [ ("HKCU:.\\Software\\\\Classes\\  "), (HKCU, "Software\\Classes", "HKCU:Software\\Classes") ],
            [ ("HKEY_CURRENT_USER\\.\\Software\\Classes\\  "), (HKCU, "Software\\Classes", "HKCU:Software\\Classes") ],
            [ ("HKCU:.\\Software\\..\\Other\\Classes  "), (HKCU, "Other\\Classes", "HKCU:Other\\Classes") ],
            [ ("HKEY_CURRENT_USER\\.\\Software\\..\\Other\\Classes  "), (HKCU, "Other\\Classes", "HKCU:Other\\Classes") ],
            # Forward slashes
            [ ("HKCU:Software/Classes"), (HKCU, "Software\\Classes", "HKCU:Software\\Classes") ],
            [ ("HKEY_CURRENT_USER\\Software/Classes"), (HKCU, "Software\\Classes", "HKCU:Software\\Classes") ]
        ]
        for testcase in testcases:
            args = testcase[0] if isinstance(testcase[0], tuple) else (testcase[0],) # handle single-element tuples
            correct = testcase[1]
            actual = split_abspath(*args, hivename_mode=HIVE_SHORTNAME)
            with self.subTest(msg=f"TEST INPUT: args={args}"):
                self.assertEqual(actual, correct)

    def test_none(self):
        testcases = [
        #   [ (input_args) ],
            # Empty
            [ (None) ],
            [ ("") ],
            [ ("   ") ],
            [ (" \\  ") ],
            [ ("HKLM:..") ],
            [ ("HKEY_LOCAL_MACHINE\\asdf\\..\\..") ],
            # Invalid characters
            [ ("HKLM:Path with spaces") ],
            [ ("HKLM:Path\\wi:th\\colons") ],
            # Invalid hive
            [ ("HK:Software\\Classes") ],
            [ ("HKEY_LOCAL_MACHINE_") ]
        ]
        for testcase in testcases:
            args = testcase[0] if isinstance(testcase[0], tuple) else (testcase[0],) # handle single-element tuples
            actual = split_abspath(*args, hivename_mode=HIVE_SHORTNAME)
            with self.subTest(msg=f"TEST INPUT: args={args}"):
                self.assertIsNone(actual)



class Test_get_relpath(unittest.TestCase):

    def test_equals(self):
        testcases = [
        #   [ (input_args),     (correct_output)      ],
            # Same hive, different name formats
            [ ("HKCU:Software", "HKEY_CURRENT_USER\\Software\\Classes"), ("Classes") ],
            [ ("HKEY_CURRENT_USER\\Software", "HKCU:Software\\Classes"), ("Classes") ],
            # Empty localpath
            [ ("HKCU:", "HKCU:Software\\Classes"),               ("Software\\Classes") ],
            [ ("HKEY_CURRENT_USER\\", "HKCU:Software\\Classes"), ("Software\\Classes") ],
            # Relative paths (. , ..)
            [ ("HKCU:Software\\..", "HKCU:.\\Software\\Classes\\..\\..\\Other\\Classes"), ("Other\\Classes") ],
            # Same location
            [ ("HKCU:Software", "HKEY_CURRENT_USER\\Software\\Classes\\.."), ("") ],
            [ ("HKCU:Software", "HKEY_CURRENT_USER\\Software\\."), ("") ],
            [ ("HKCU:", "HKEY_CURRENT_USER\\"), ("") ],
        ]
        for testcase in testcases:
            args = testcase[0] if isinstance(testcase[0], tuple) else (testcase[0],) # handle single-element tuples
            correct = testcase[1]
            actual = get_relpath(*args)
            with self.subTest(msg=f"TEST INPUT: args={args}"):
                self.assertEqual(actual, correct)

    def test_none(self):
        testcases = [
        #   [ (input_args) ],
            # Empty
            [ ("HKLM:", None) ],
            [ ("", "HKLM:") ],
            [ ("HKEY_LOCAL_MACHINE\\asdf\\..\\..", "HKLM") ],
            # Invalid characters
            [ ("HKLM:", "HKLM:Path with spaces") ],
            [ ("HKLM:", "HKLM:Path\\wi:th\\colons") ],
            # Invalid hive
            [ ("HKLM:", "HK:Software\\Classes") ],
            [ ("HKLM:", "HKEY_LOCAL_MACHINE_") ],
            # Not a subkey
            [ ("HKLM:Software\\Classes", "HKLM:Software") ],
            [ ("HKLM:Software\\Classes", "HKLM:") ],
            [ ("HKLM:Software\\Classes", "HKCU:Software\\Classes") ],
        ]
        for testcase in testcases:
            args = testcase[0] if isinstance(testcase[0], tuple) else (testcase[0],) # handle single-element tuples
            actual = get_relpath(*args)
            with self.subTest(msg=f"TEST INPUT: args={args}"):
                self.assertIsNone(actual)





if __name__ == '__main__':
    unittest.main()
