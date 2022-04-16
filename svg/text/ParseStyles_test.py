import unittest

from svg.text.ParseStyles import ParseStyles


class MyTestCase(unittest.TestCase):

    def test_something(self):
        self.assertEqual(True, True)  # add assertion here

    def test_scenario_all_styles(self):
        self.assertEqual(True, True)  # add assertion here
        sample_text_1 = "This **is bold**, this *is italic*, this `is some code` and this ~~is strike through~~"
        ps = ParseStyles(sample_text_1);
        ps.parse()
        print(str(ps))
        self.assertEqual(str(ps),"Text is:This **is bold**, this *is italic*, this `is some code` and this ~~is strike through~~, styles are [<class 'svg.text.StyledText.StyledText'>, ['bold'] applied to This is bold, ['italic'] applied to , this is italic, ['strike-through'] applied to , this is some code and this is strike through]")


if __name__ == '__main__':
    unittest.main()
