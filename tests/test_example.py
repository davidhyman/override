from unittest import mock
from tests.base import BaseCase


class TestFunctionalExample(BaseCase):
    def test_example(self):
        from examples import example
        with mock.patch('examples.example.after_configuration_write') as mocked:
            example.run()
        self.assertEqual(mocked.call_count, 1)
        from examples import my_project
        result = my_project.run()

        self.assertEqual(result.colour, 'orange')
