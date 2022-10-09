import unittest

from diagram.components.Diagram import Diagram
from diagram.components.Divider import Divider
from diagram.components.Note import Note
from diagram.svg.SVGGenerator import SVGRenderer
from diagram.components.Task import Task
from diagram.components.TaskConnection import TaskConnection
from PIL import ImageFont


class TestSVGGenerator(unittest.TestCase):

    def test_add_tasks(self):

        font = ImageFont.truetype('times.ttf', 12)
        size = font.getsize('Hello world')
        print(size)

        web_font = ImageFont.truetype('arial.ttf', 12)
        size = web_font.getsize('Hello world')
        print(size)

        task_one = Task("One")
        task_two = Task("Two")
        task_three = Task("Three")
        task_four = Task("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec ante ex, luctus non purus vitae, laoreet congue dolor.")
        diagram = Diagram("Test Diagram")
        diagram.add_task(task_one)
        diagram.add_task(task_two)
        diagram.add_task(task_three)
        diagram.add_task(task_four)

        connection_1_2 = TaskConnection("One to Two",task_one,task_two,task_number=1, bi_directional=True)
        connection_2_3 = TaskConnection("Two to Three", task_two, task_three, task_number=2, lost_message=True)
        connection_3_3 = TaskConnection("Three to Three", task_three, task_three, task_number=3, lost_message=False)
        connection_3_4 = TaskConnection("Three to Four", task_three, task_four, task_number=4, open_arrow=True)
        connection_4_3 = TaskConnection("Four to Three",task_four, task_three, task_number=5, style="Bold")
        connection_4_2 = TaskConnection("Four to Two", task_four, task_two, task_number=6)
        connection_1_4 = TaskConnection("One to Four", task_one, task_four, task_number=7, style="Dashed")

        divider_1 = Divider("Divider 1 : Call Customer", "Regular")
        divider_2 = Divider("Divider 2 : Manufacture Item", "Dashed")
        divider_3 = Divider("Divider 3 : Delay in Shipping Items", "Delay")

        note_1 = Note("""
        "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."
        """, start_task_id=1, end_task_id=2)

        note_2 = Note("""
        After introducing yourself, you want to grab the professors attention by providing a few lines about your 
        research interests and relevant experiences. These experiences may include but are not limited to a seasonal 
        """)

        diagram.add_diagram_item(divider_1)
        diagram.add_diagram_item(connection_1_2)

        diagram.add_diagram_item(connection_2_3)
        diagram.add_diagram_item(note_1)

        diagram.add_diagram_item(divider_2)
        diagram.add_diagram_item(connection_3_3)
        diagram.add_diagram_item(connection_3_4)
        diagram.add_diagram_item(connection_4_3)
        diagram.add_diagram_item(connection_4_2)
        diagram.add_diagram_item(divider_3)
        diagram.add_diagram_item(connection_1_4)
        diagram.add_diagram_item(note_2,)

        generator = SVGRenderer(diagram, 1024, 1324)
        with open("../../data/out/test_svg_generator.svg", 'w') as f:
            f.write(generator.get_svg_string())
        print("Done")