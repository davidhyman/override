from tests.base import BaseCase
from updates import RuntimeUpdates


class TestUpdates(BaseCase):

    class MyClass:
        A = 1
        B = 2

        class MySubClass:
            C = 3
            D = {
                'e': 4,
                'f': 5
            }

    def test_shallow_class(self):
        expected = 'yes'
        RuntimeUpdates().module_update(self.MyClass, {'B': expected}, 'test')
        self.assertEqual(self.MyClass.B, expected)
        self.assertEqual(self.MyClass.A, 1)

    def test_deep_class(self):
        expected = 'yes'
        RuntimeUpdates().module_update(self.MyClass, {'MySubClass.D.e': expected}, 'test')
        self.assertEqual(self.MyClass.MySubClass.D['e'], expected)
        self.assertEqual(self.MyClass.MySubClass.D['f'], 5)

    def test_cast(self):
        RuntimeUpdates().module_update(self.MyClass, {'X': '5'}, 'test')
        self.assertEqual(self.MyClass.X, 5)
        RuntimeUpdates().module_update(self.MyClass, {'Y': '5.5'}, 'test')
        self.assertEqual(self.MyClass.Y, 5.5)
        RuntimeUpdates().module_update(self.MyClass, {'Z': "'5'"}, 'test')
        self.assertEqual(self.MyClass.Z, '5')
