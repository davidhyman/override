from tests.base import BaseCase


class TestFunctionalExample(BaseCase):
    def test_example(self):
        from example import example
        example.run()
        from example import my_project
        result = my_project.run()

        self.assertEqual(result.colour, 'orange')
