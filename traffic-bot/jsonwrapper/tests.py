import os
import json
import unittest
from pathlib import Path
from .autosavedict import AutoSaveDict


BASE_DIR = f"{os.sep}".join(__file__.split(os.sep)[:-1])


class TestAutoSaveDict(unittest.TestCase):
    def setUp(self) -> None:
        self.path = Path(BASE_DIR) / "test.json"
        self.default = {"a": 1, "b": 2}
        asd = AutoSaveDict(self.path, **self.default)
        asd.init()
        return super().setUp()

    def tearDown(self) -> None:
        os.remove(self.path)
        return super().tearDown()

    def test_init(self) -> None:
        asd = AutoSaveDict(self.path, **self.default)
        asd.init()
        self.assertTrue(os.path.exists(self.path))
        self.assertEqual(asd, self.default)
        self.assertEqual(asd._pairs, self.default)
        self.assertEqual(asd._read(), self.default)

    def test_restore(self) -> None:
        asd = AutoSaveDict(self.path, **self.default)
        asd["c"] = 3
        self.assertIn("c", asd)
        asd.restore()
        self.assertEqual(asd, self.default)
        self.assertEqual(asd._read(), self.default)
        self.assertEqual(asd._pairs, self.default)

    def test_pop(self) -> None:
        asd = AutoSaveDict(self.path, **self.default)
        asd.init()

        key = tuple(self.default.keys())[0]
        asd.pop(key)

        self.assertNotIn(key, asd._read())
        self.assertNotIn(key, asd._pairs)
        self.assertNotIn(key, asd)

    def test_popitem(self) -> None:
        asd = AutoSaveDict(self.path, **self.default)
        asd.init()
        key = tuple(asd.keys())[-1]
        val = asd[key]
        result = asd.popitem()
        self.assertEqual(result, (key, val))
        self.assertNotIn(key, asd)
        self.assertNotIn(key, asd._read())
        self.assertNotIn(key, asd._pairs)

    def test_update(self) -> None:
        asd = AutoSaveDict(self.path, **self.default)
        asd.init()
        new = {"b": 3}
        asd.update(new)
        self.assertEqual(asd["b"], new["b"])
        self.assertEqual(asd._read()["b"], new["b"])
        self.assertEqual(asd._pairs["b"], new["b"])

    def test_copy(self) -> None:
        copy_path = "test_copy.json"
        asd = AutoSaveDict(self.path, **self.default)
        asd_copy = asd.copy(copy_path)
        asd.init()
        asd_copy.init()

        self.assertEqual(asd_copy, asd)
        self.assertEqual(asd_copy, asd._read())
        self.assertEqual(asd_copy, asd._pairs)
        os.remove(copy_path)

    def test_fromfile(self) -> None:
        file = "test_fromfile.json"
        config = {"b": 3, "c": 4}

        with open(file, mode="w") as f:
            json.dump(config, f)
        os.remove(self.path)
        asd = AutoSaveDict.fromfile(file, self.path)
        asd.init()

        self.assertEqual(config, asd)
        self.assertEqual(config, asd._pairs)
        self.assertEqual(config, asd._read())
        self.assertIsInstance(asd, AutoSaveDict)
        os.remove(file)

    def test_frommapping(self) -> None:
        path = "test_frommapping.json"
        mapping = (
            ("a", 1),
            ("b", 2),
            ("c", 3),
        )
        expected = dict(mapping)

        asd = AutoSaveDict.frommapping(mapping, path)  # type: ignore
        asd.init()

        self.assertEqual(expected, asd)
        self.assertEqual(expected, asd._read())
        self.assertEqual(expected, asd._pairs)
        os.remove(path)

    def test_fromkeys(self) -> None:
        path = "test_fromkeys.json"
        keys = "test"
        expected = dict.fromkeys(keys)

        asd = AutoSaveDict.fromkeys(keys, file_path=path)
        asd.init()
        self.assertEqual(asd, expected)
        self.assertEqual(asd._read(), expected)
        self.assertEqual(asd._pairs, expected)
        os.remove(path)

    def test_setitem(self) -> None:
        expected = {**self.default, "z": 3}
        asd = AutoSaveDict(self.path, **self.default)
        asd["z"] = 3
        self.assertEqual(asd, expected)
        self.assertEqual(asd._read(), expected)
        self.assertEqual(asd._pairs, expected)

    def test_delitem(self) -> None:
        config = self.default.copy()
        key = tuple(config.keys())[0]
        asd = AutoSaveDict(self.path, **config)
        asd.init()

        del config[key]
        del asd[key]
        self.assertEqual(asd, config)
        self.assertEqual(asd._read(), config)
        self.assertEqual(asd._pairs, config)
