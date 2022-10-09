import unittest

from diagram.components.Diagram import Diagram
from diagram.components.Task import Task


class MyTestCase(unittest.TestCase):
    def test_something(self):
        t1 = Task("Task_1")
        t1.new_location = 1
        t2 = Task("Task_2")
        t3 = Task("Task_3")
        t3.new_location = 0

        d = Diagram("Test Diagram")
        d.add_task(t1)
        d.add_task(t2)
        d.add_task(t3)

        print(str(d.items))

        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
