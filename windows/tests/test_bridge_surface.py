"""What the window is actually allowed to call.

pywebview builds the JavaScript bridge by walking dir() on the Api object: every public name is fetched
with getattr, every bound method is published to the page, and - the part that surprises people -
every public attribute that is *not* callable is recursed into and its methods published too.

So `self.store` published the Store, and the Store's `charts_dir` is a pathlib.Path, and a Path has
chmod, unlink, rmdir and hardlink_to. The page was being handed a thousand functions, including those.
It is a local page this project wrote, so nothing was exploiting it, but a bridge should carry what it
means to carry and nothing else - and a surface that large is slow to build and hard to reason about.

These tests reproduce pywebview's own walk (util.py, get_functions) and pin the result.
"""
import inspect
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jyotish_win.api import Api        # noqa: E402
from jyotish_win.storage import Store  # noqa: E402


def published(api) -> dict:
    """Exactly what pywebview's get_functions would publish for this object."""
    seen = []

    def walk(obj, base="", found=None):
        if obj in seen:
            return found
        seen.append(obj)
        if found is None:
            found = {}
        for name in dir(obj):
            full = f"{base}.{name}" if base else name
            if name.startswith("_"):
                continue
            attr = getattr(obj, name)
            if inspect.ismethod(attr):
                found[full] = list(inspect.getfullargspec(attr).args)[1:]
            elif inspect.isclass(attr) or (
                    isinstance(attr, object) and not callable(attr) and hasattr(attr, "__module__")):
                walk(attr, full, found)
        return found

    return walk(api)


class BridgeSurfaceTest(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.api = Api(store=Store(Path(self._tmp.name)))
        self.surface = published(self.api)

    def tearDown(self):
        self._tmp.cleanup()

    def test_nothing_of_the_app_s_insides_reaches_the_page(self):
        """A dotted name means pywebview walked into one of this object's attributes. There should be
        none: everything the Api holds is private, so the walk stops at the methods it defines."""
        leaked = sorted(n for n in self.surface if "." in n)
        self.assertEqual(leaked, [], f"{len(leaked)} internal methods reach the page, e.g. {leaked[:5]}")

    def test_the_page_cannot_reach_the_filesystem_through_the_bridge(self):
        """The specific thing that was wrong: pathlib's API, published because the Store was public."""
        dangerous = ("unlink", "rmdir", "chmod", "hardlink_to", "symlink_to", "write_text",
                     "write_bytes", "rename", "replace", "touch", "mkdir")
        reachable = sorted(n for n in self.surface if n.rsplit(".", 1)[-1] in dangerous)
        self.assertEqual(reachable, [], f"the page can call {reachable}")

    def test_the_bridge_carries_the_methods_the_class_defines_and_no_others(self):
        own = {name for name, value in vars(Api).items()
               if callable(value) and not name.startswith("_")}
        self.assertEqual(set(self.surface), own)

    def test_loading_the_engine_is_not_a_side_effect_of_building_the_bridge(self):
        """The engine used to be a property, so pywebview's getattr walk loaded Swiss Ephemeris and 55
        modules before the window had opened - and then published the engine's own methods as well."""
        fresh = Api(store=Store(Path(self._tmp.name) / "another"))
        published(fresh)
        self.assertIsNone(fresh._engine, "building the bridge loaded the engine")

    def test_every_method_the_interface_calls_is_one_the_bridge_publishes(self):
        """The contract from the other side: app.js calling something the bridge does not carry fails
        only when a person presses the button, which is how "add_person is not a function" reached a
        screenshot instead of a test."""
        import re
        web = Path(__file__).resolve().parent.parent / "web"
        called = set()
        for name in ("app.js", "sections.js", "kundli.js"):
            called |= set(re.findall(r"api\(\)\.(\w+)\(", (web / name).read_text(encoding="utf-8")))
        self.assertTrue(called, "no API calls found; has app.js been rewritten?")
        missing = sorted(called - set(self.surface))
        self.assertEqual(missing, [], f"the interface calls {missing}, which the bridge does not carry")


    def test_the_startup_check_lists_what_the_interface_truly_needs(self):
        """app.js checks the bridge before using it, against a list written down in the page. A list
        that drifts from the methods actually called would pass a broken bridge or fail a sound one."""
        import re
        web = Path(__file__).resolve().parent.parent / "web"
        js = (web / "app.js").read_text(encoding="utf-8")
        listed = set(re.findall(r'"(\w+)"', js[js.index("const NEEDED = ["):js.index("];", js.index("const NEEDED = ["))]))
        called = set()
        for name in ("app.js", "sections.js", "kundli.js"):
            called |= set(re.findall(r"api\(\)\.(\w+)\(", (web / name).read_text(encoding="utf-8")))
        self.assertEqual(called - listed, set(), "the interface calls methods the startup check misses")
        self.assertEqual(listed - set(self.surface), set(), "the startup check lists methods that do not exist")


if __name__ == "__main__":
    unittest.main()
