import unittest

# Module to import:
# from mypackage import mymodule

#   All test*.py functions under /test are scanned for TestCase classes.
#   All classes inheriting from unittest.TestCase are scanned for "test_" functions.
#   All "test_" functions should contain one or more assertions:
#       self.assertEqual(a,b)
#       self.assertNotEqual(a,b)
#       self.assertTrue(x)
#       self.assertFalse(x)
#       self.assertIs(a,b)
#       self.assertIs(a,b)
#       self.assertIsNot(a, b)
#       self.assertIsNone(x)
#       self.assertIsNotNone(x)
#       self.assertIn(a, b)
#       self.assertNotIn(a, b)
#       self.assertIsInstance(a, b)
#       self.assertNotIsInstance(a, b)

def myfunc(arg1, arg2):
    return "Correct Response"

class Test_mymodule(unittest.TestCase):

    def test_myfunc(self):
        correct = "Correct Response"
        actual = myfunc("test_arg1", "test_arg2")
        self.assertEqual(actual, correct)
    

    def test_equals(self):
        testcases = [
        #   [ (input_args),                 (correct_output)     ],
            [ ("test1_arg1", "test1_arg2"), ("Correct Response") ],
            [ ("test2_arg1", "test2_arg2"), ("Correct Response") ]
        ]
        for testcase in testcases:
            args = testcase[0] if isinstance(testcase[0], tuple) else (testcase[0],) # handle single-element tuples
            correct = testcase[1]
            actual = myfunc(*args)
            with self.subTest(msg=f"TEST INPUT: args={args}"):
                self.assertEqual(actual, correct)
        
