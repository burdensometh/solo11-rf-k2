import inspect
import os.path
import re
import sys
import unittest
from pathlib import Path

from ArgumentsPython import ArgumentsPython
from classes import __file__ as classes_source, ArgInfoLibrary, DocLibrary, NameLibrary

from robot.errors import DataError
from robot.running.librarykeyword import StaticKeyword
from robot.running.testlibraries import TestLibrary
from robot.utils import type_name
from robot.utils.asserts import assert_equal, assert_raises_with_msg, assert_true


def get_keyword_methods(lib):
    attrs = [getattr(lib, a) for a in dir(lib) if not a.startswith("_")]
    return [a for a in attrs if inspect.ismethod(a)]


def assert_argspec(
    argspec,
    minargs=0,
    maxargs=0,
    positional=(),
    varargs=None,
    named_only=(),
    var_named=None,
    defaults=None,
):
    assert_equal(argspec.minargs, minargs)
    assert_equal(argspec.maxargs, maxargs)
    assert_equal(argspec.positional, positional)
    assert_equal(argspec.var_positional, varargs)
    assert_equal(argspec.named_only, named_only)
    assert_equal(argspec.var_named, var_named)
    assert_equal(argspec.defaults, defaults or {})


class TestStaticKeyword(unittest.TestCase):

    def test_name(self):
        for method in get_keyword_methods(NameLibrary()):
            kw = StaticKeyword.from_name(
                method.__name__, TestLibrary.from_class(NameLibrary)
            )
            assert_equal(kw.name, method.__doc__)
            assert_equal(kw.full_name, f"NameLibrary.{method.__doc__}")

    def test_docs(self):
        for method in get_keyword_methods(DocLibrary()):
            kw = StaticKeyword.from_name(
                method.__name__, TestLibrary.from_class(DocLibrary)
            )
            assert_equal(kw.doc, method.expected_doc)
            assert_equal(kw.short_doc, method.expected_shortdoc)

    def test_arguments(self):
        for method in get_keyword_methods(ArgInfoLibrary()):
            kw = StaticKeyword.from_name(
                method.__name__, TestLibrary.from_class(ArgInfoLibrary)
            )
            args = (
                kw.args.positional,
                kw.args.defaults,
                kw.args.var_positional,
                kw.args.var_named,
            )
            expected = eval(method.__doc__)
            assert_equal(args, expected, method.__name__)

    def test_arg_limits(self):
        for method in get_keyword_methods(ArgumentsPython()):
            kw = StaticKeyword.from_name(
                method.__name__, TestLibrary.from_class(ArgumentsPython)
            )
            exp_mina, exp_maxa = eval(method.__doc__)
            assert_equal(kw.args.minargs, exp_mina)
            assert_equal(kw.args.maxargs, exp_maxa)

class TestSourceAndLineno(unittest.TestCase):

    def test_class_with_init(self):
        lib = TestLibrary.from_name("classes.RecordingLibrary")
        self._verify(lib, "kw", classes_source, 212)
        self._verify(lib, "init", classes_source, 208)

    def test_class_without_init(self):
        lib = TestLibrary.from_name("classes.NameLibrary")
        self._verify(lib, "simple1", classes_source, 12)
        self._verify(lib, "init", classes_source, None)

    def test_module(self):
        from module_library import __file__ as source

        lib = TestLibrary.from_name("module_library")
        self._verify(lib, "passing", source, 5)
        self._verify(lib, "init", source, None)

    def test_package(self):
        from robot.variables import __file__ as init_source
        from robot.variables.search import __file__ as source

        lib = TestLibrary.from_name("robot.variables")
        self._verify(lib, "search_variable", source, 23)
        self._verify(lib, "init", init_source, None)

    def test_decorated(self):
        lib = TestLibrary.from_name("classes.Decorated")
        self._verify(lib, "no_wrapper", classes_source, 340)
        self._verify(lib, "wrapper", classes_source, 347)
        self._verify(lib, "external", classes_source, 351)
        self._verify(lib, "no_def", classes_source, 354)

    def _verify(self, lib, name, source, lineno):
        if name == "init":
            kw = lib.init
        else:
            (kw,) = lib.find_keywords(name)
        if source:
            source = re.sub(r"(\.pyc|\$py\.class)$", ".py", str(source))
            source = Path(os.path.normpath(source))
        assert_equal(kw.source, source)
        assert_equal(kw.lineno, lineno)


class LoggerMock:

    def __init__(self):
        self.messages = []

    def write(self, message, level):
        self.messages.append((message, level))

    def info(self, message):
        self.write(message, "INFO")

    def debug(self, message):
        pass


if __name__ == "__main__":
    unittest.main()
