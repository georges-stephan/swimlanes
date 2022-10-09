import unittest

from diagram.templates.DefaultTemplate import DefaultTemplate


class TestTemplate(unittest.TestCase):

    def test_attributes(self):
        df = DefaultTemplate()
        print(df.get_parameter_value('x_offset'))
        print(type(df.get_parameter_value('x_offset')))
