import unittest
import tree_sitter
import pathlib
from tentiris.features import semantic_tokens_from_utf8bytes

MD_LANGUAGE = tree_sitter.Language("build/my-languages.dll", "markdown")
HERE = pathlib.Path(__file__).absolute().parent


class TestStringMethods(unittest.TestCase):
    def test_upper(self):
        self.assertEqual("foo".upper(), "FOO")

    def test_isupper(self):
        self.assertTrue("FOO".isupper())
        self.assertFalse("Foo".isupper())

    def test_split(self):
        s = "hello world"
        self.assertEqual(s.split(), ["hello", "world"])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

    def test_treesitter(self):
        sample = HERE.parent / "docs/sample.md"

        data = semantic_tokens_from_utf8bytes(sample.read_bytes())

        self.assertEqual(3, len(data))


if __name__ == "__main__":
    unittest.main()
