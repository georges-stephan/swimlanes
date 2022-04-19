import unittest

from svg.text.ParseStyles import ParseStyles


class MyTestCase(unittest.TestCase):

    def test_something(self):
        self.assertEqual(True, True)  # add assertion here

    def test_scenario_all_styles(self):
        self.assertEqual(True, True)  # add assertion here
        sample_text_1 = "This **is bold**, this *is italic*, this `is some~ code` and this ~~is strike through~~ and " \
                        "**bold***italic*`keude` and ** bold * with star** "
        ps = ParseStyles(sample_text_1);
        ps.parse()
        print(str(ps))
        self.assertEqual(str(ps), "Text to style is:This **is bold**, this *is italic*, this `is some~ code` and this "
                                  "~~is strike through~~ and **bold***italic*`keude` and ** bold * with star** .The "
                                  "styles are: [<class 'svg.text.StyledText.StyledText'>, The style {'normal': "
                                  "'normal'} is applied to \"This \", The style {'bold': 'bold'} is applied to \"is "
                                  "bold\", The style {'normal': 'normal'} is applied to \", this \", The style {"
                                  "'italic': 'italic'} is applied to \"is italic\", The style {'normal': 'normal'} is "
                                  "applied to \", this \", The style {'code': 'code'} is applied to \"is some~ "
                                  "code\", The style {'normal': 'normal'} is applied to \" and this \", The style {"
                                  "'strike-through': 'strike-through'} is applied to \"is strike through\", "
                                  "The style {'normal': 'normal'} is applied to \" and \", The style {'bold': 'bold'} "
                                  "is applied to \"bold\", The style {'normal': 'normal'} is applied to \"\", "
                                  "The style {'italic': 'italic'} is applied to \"italic\", The style {'normal': "
                                  "'normal'} is applied to \"\", The style {'code': 'code'} is applied to \"keude\", "
                                  "The style {'normal': 'normal'} is applied to \" and \", The style {'bold': 'bold'} "
                                  "is applied to \" bold  with star\"]")


if __name__ == '__main__':
    unittest.main()
