#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Optional base classes for libraries and other extensions.

Module contents:

- :class:`DynamicLibrary` for libraries using the `dynamic library API`__.
- :class:`HybridLibrary` for libraries using the `hybrid library API`__.
- :class:`ListenerV2` for `listener interface version 2`__.
- :class:`ListenerV3` for `listener interface version 3`__.
- :class:`Parser` for `custom parsers`__. Also
  :class:`~robot.running.builder.settings.TestDefaults` used in :class:`Parser`
  type hints is exposed via this module.
- Type definitions used by the aforementioned classes.

Main benefit of using these base classes is that editors can provide automatic
completion, documentation and type information. Their usage is not required.
Notice also that libraries typically use the static API and do not need any
base class.

.. note:: These classes are not exposed via the top level :mod:`robot.api`
          package and need to imported via :mod:`robot.api.interfaces`.

This module is new in Robot Framework 6.1.

__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#dynamic-library-api
__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#hybrid-library-api
__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#listener-version-2
__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#listener-version-3
__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#parser-interface
"""

import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Mapping, Sequence, TypedDict, Union

if sys.version_info >= (3, 10):
    from types import UnionType
else:
    UnionType = type

from robot import result, running
from robot.output import ResultFile as ResultFile
from robot.running import TestDefaults as TestDefaults, TestSuite

# Type aliases used by DynamicLibrary and HybridLibrary.
Name = str
PositArgs = Sequence[Any]
NamedArgs = Mapping[str, Any]
Documentation = str
Arguments = Sequence[
    Union[
        str,                   # Name with possible default like `"arg"` or `"arg=1"`.
        "tuple[str]",          # Name without a default like `("arg",)`.
        "tuple[str, Any]"      # Name and default like `("arg", 1)`.
    ]
]  # fmt: skip
TypeHint = Union[
    type,                      # Actual type.
    str,                       # Type name or alias.
    UnionType,                 # Union syntax (e.g. `int | float`).
    "tuple[TypeHint, ...]"     # Tuple of type hints. Behaves like a union.
]  # fmt: skip
TypeHints = Union[
    Mapping[str, TypeHint],    # Types by name.
    Sequence["TypeHint | None"]  # Types by position.
]  # fmt: skip
Tags = Sequence[str]
Source = str



class StartSuiteAttributes(TypedDict):
    """Attributes passed to listener v2 ``start_suite`` method.

    See the User Guide for more information.
    """

    id: str
    longname: str
    doc: str
    metadata: "dict[str, str]"
    source: str
    suites: "list[str]"
    tests: "list[str]"
    totaltests: int
    starttime: str


class EndSuiteAttributes(StartSuiteAttributes):
    """Attributes passed to listener v2 ``end_suite`` method.

    See the User Guide for more information.
    """

    endtime: str
    elapsedtime: int
    status: str
    statistics: str
    message: str


class StartTestAttributes(TypedDict):
    """Attributes passed to listener v2 ``start_test`` method.

    See the User Guide for more information.
    """

    id: str
    longname: str
    originalname: str
    doc: str
    tags: "list[str]"
    metadata: "dict[str, str]"
    template: str
    source: str
    lineno: int
    starttime: str


class EndTestAttributes(StartTestAttributes):
    """Attributes passed to listener v2 ``end_test`` method.

    See the User Guide for more information.
    """

    endtime: str
    elapedtime: int
    status: str
    message: str


class OptionalKeywordAttributes(TypedDict, total=False):
    """Extra attributes passed to listener v2 ``start/end_keyword`` methods.

    These attributes are included with control structures. For example, with
    IF structures attributes include ``condition``.
    """

    # FOR / ITERATION with FOR
    variables: "list[str] | dict[str, str]"
    flavor: str
    values: "list[str]"  # Also RETURN
    # WHILE and IF
    condition: str
    # WHILE
    limit: str
    # EXCEPT
    patterns: "list[str]"
    pattern_type: str
    variable: str


class StartKeywordAttributes(OptionalKeywordAttributes):
    """Attributes passed to listener v2 ``start_keyword`` method.

    See the User Guide for more information.
    """

    type: str
    kwname: str
    libname: str
    doc: str
    args: "list[str]"
    assign: "list[str]"
    tags: "list[str]"
    source: str
    lineno: "int | None"
    status: str
    starttime: str


class EndKeywordAttributes(StartKeywordAttributes):
    """Attributes passed to listener v2 ``end_keyword`` method.

    See the User Guide for more information.
    """

    endtime: str
    elapsedtime: int


class MessageAttributes(TypedDict):
    """Attributes passed to listener v2 ``log_message`` and ``messages`` methods.

    See the User Guide for more information.
    """

    message: str
    level: str
    timestamp: str
    html: str


class LibraryAttributes(TypedDict):
    """Attributes passed to listener v2 ``library_import`` method.

    See the User Guide for more information.
    """

    args: "list[str]"
    originalname: str
    source: str
    importer: "str | None"


class ResourceAttributes(TypedDict):
    """Attributes passed to listener v2 ``resource_import`` method.

    See the User Guide for more information.
    """

    source: str
    importer: "str | None"


class VariablesAttributes(TypedDict):
    """Attributes passed to listener v2 ``variables_import`` method.

    See the User Guide for more information.
    """

    args: "list[str]"
    source: str
    importer: "str | None"


class ListenerV2:
    """Optional base class for listeners using the listener API version 2."""

    ROBOT_LISTENER_API_VERSION = 2

    def start_suite(self, name: str, attributes: StartSuiteAttributes):
        """Called when a suite starts."""

    def end_suite(self, name: str, attributes: EndSuiteAttributes):
        """Called when a suite end."""

    def start_test(self, name: str, attributes: StartTestAttributes):
        """Called when a test or task starts."""

    def end_test(self, name: str, attributes: EndTestAttributes):
        """Called when a test or task ends."""

    def start_keyword(self, name: str, attributes: StartKeywordAttributes):
        """Called when a keyword or a control structure like IF starts.

        The type of the started item is in ``attributes['type']``. Control
        structures can contain extra attributes that are only relevant to them.
        """

    def end_keyword(self, name: str, attributes: EndKeywordAttributes):
        """Called when a keyword or a control structure like IF ends.

        The type of the started item is in ``attributes['type']``. Control
        structures can contain extra attributes that are only relevant to them.
        """

    def log_message(self, message: MessageAttributes):
        """Called when a normal log message are emitted.

        The messages are typically logged by keywords, but also the framework
        itself logs some messages. These messages end up to output.xml and
        log.html.
        """

    def message(self, message: MessageAttributes):
        """Called when framework's internal messages are emitted.

        Only logged by the framework itself. These messages end up to the syslog
        if it is enabled.
        """

    def library_import(self, name: str, attributes: LibraryAttributes):
        """Called after a library has been imported."""

    def resource_import(self, name: str, attributes: ResourceAttributes):
        """Called after a resource file has been imported."""

    def variables_import(self, name: str, attributes: VariablesAttributes):
        """Called after a variable file has been imported."""

    def output_file(self, path: str):
        """Called when the output file is ready.

        :param path: An absolute path to the output file or
            a string ``None`` if creating the output file is disabled.
        """

    def log_file(self, path: str):
        """Called when the log file is ready.

        :param path: An absolute path to the log file.

        Not called if creating the log file is disabled.
        """

    def report_file(self, path: str):
        """Called when the report file is ready.

        :param path: An absolute path to the report file.

        Not called if creating the report file is disabled.
        """

    def xunit_file(self, path: str):
        """Called when the xunit compatible output file is ready.

        :param path: An absolute path to the xunit file.

        Only called if creating the xunit file is enabled.
        """

    def debug_file(self, path: str):
        """Called when the debug file is ready.

        :param path: An absolute path to the debug file.

        Only called if creating the debug file is enabled.
        """

    def close(self):
        """Called when the whole execution ends.

        With library listeners called when the library goes out of scope.
        """


class ListenerV3:
    """Optional base class for listeners using the listener API version 3."""

    ROBOT_LISTENER_API_VERSION = 3

    def start_suite(self, data: running.TestSuite, result: result.TestSuite):
        """Called when a suite starts."""

    def end_suite(self, data: running.TestSuite, result: result.TestSuite):
        """Called when a suite ends."""

    def start_test(self, data: running.TestCase, result: result.TestCase):
        """Called when a test or task starts."""

    def end_test(self, data: running.TestCase, result: result.TestCase):
        """Called when a test or tasks ends."""

    def start_keyword(self, data: running.Keyword, result: result.Keyword):
        """Called when a keyword starts by default.

        This method is called, by default, with user keywords, library keywords
        and when a keyword call is invalid. It is not called, however, if a more
        specific :meth:`start_user_keyword`, :meth:`start_library_keyword` or
        :meth:`start_invalid_keyword` method is implemented.

        The default implementation calls :meth:`start_body_item`.

        New in Robot Framework 7.0.
        """
        self.start_body_item(data, result)

    def end_keyword(self, data: running.Keyword, result: result.Keyword):
        """Called when a keyword ends by default.

        This method is called, by default, with user keywords, library keywords
        and when a keyword call is invalid. It is not called, however, if a more
        specific :meth:`end_user_keyword`, :meth:`end_library_keyword` or
        :meth:`end_invalid_keyword` method is implemented.

        The default implementation calls :meth:`end_body_item`.

        New in Robot Framework 7.0.
        """
        self.end_body_item(data, result)

    def start_user_keyword(
        self,
        data: running.Keyword,
        implementation: running.UserKeyword,
        result: result.Keyword,
    ):
        """Called when a user keyword starts.

        The default implementation calls :meth:`start_keyword`.

        New in Robot Framework 7.0.
        """
        self.start_keyword(data, result)

    def end_user_keyword(
        self,
        data: running.Keyword,
        implementation: running.UserKeyword,
        result: result.Keyword,
    ):
        """Called when a user keyword ends.

        The default implementation calls :meth:`end_keyword`.

        New in Robot Framework 7.0.
        """
        self.end_keyword(data, result)

    def start_library_keyword(
        self,
        data: running.Keyword,
        implementation: running.LibraryKeyword,
        result: result.Keyword,
    ):
        """Called when a library keyword starts.

        The default implementation calls :meth:`start_keyword`.

        New in Robot Framework 7.0.
        """
        self.start_keyword(data, result)

    def end_library_keyword(
        self,
        data: running.Keyword,
        implementation: running.LibraryKeyword,
        result: result.Keyword,
    ):
        """Called when a library keyword ends.

        The default implementation calls :meth:`start_keyword`.

        New in Robot Framework 7.0.
        """
        self.end_keyword(data, result)

    def start_invalid_keyword(
        self,
        data: running.Keyword,
        implementation: running.KeywordImplementation,
        result: result.Keyword,
    ):
        """Called when an invalid keyword call starts.

        Keyword may not have been found, there could have been multiple matches,
        or the keyword call itself could have been invalid.

        The default implementation calls :meth:`start_keyword`.

        New in Robot Framework 7.0.
        """
        self.start_keyword(data, result)

    def end_invalid_keyword(
        self,
        data: running.Keyword,
        implementation: running.KeywordImplementation,
        result: result.Keyword,
    ):
        """Called when an invalid keyword call ends.

        Keyword may not have been found, there could have been multiple matches,
        or the keyword call itself could have been invalid.

        The default implementation calls :meth:`end_keyword`.

        New in Robot Framework 7.0.
        """
        self.end_keyword(data, result)

    def start_for(self, data: running.For, result: result.For):
        """Called when a FOR loop starts.

        The default implementation calls :meth:`start_body_item`.

        New in Robot Framework 7.0.
        """
        self.start_body_item(data, result)

    def end_for(self, data: running.For, result: result.For):
        """Called when a FOR loop ends.

        The default implementation calls :meth:`end_body_item`.

        New in Robot Framework 7.0.
        """
        self.end_body_item(data, result)

    def start_for_iteration(
        self,
        data: running.ForIteration,
        result: result.ForIteration,
    ):
        """Called when a FOR loop iteration starts.

        The default implementation calls :meth:`start_body_item`.

        New in Robot Framework 7.0.
        """
        self.start_body_item(data, result)

    def end_for_iteration(
        self,
        data: running.ForIteration,
        result: result.ForIteration,
    ):
        """Called when a FOR loop iteration ends.

        The default implementation calls :meth:`end_body_item`.

        New in Robot Framework 7.0.
        """
        self.end_body_item(data, result)

    def start_while(self, data: running.While, result: result.While):
        """Called when a WHILE loop starts.

        The default implementation calls :meth:`start_body_item`.

        New in Robot Framework 7.0.
        """
        self.start_body_item(data, result)

    def end_while(self, data: running.While, result: result.While):
        """Called when a WHILE loop ends.

        The default implementation calls :meth:`end_body_item`.

        New in Robot Framework 7.0.
        """
        self.end_body_item(data, result)

    def start_while_iteration(
        self,
        data: running.WhileIteration,
        result: result.WhileIteration,
    ):
        """Called when a WHILE loop iteration starts.

        The default implementation calls :meth:`start_body_item`.

        New in Robot Framework 7.0.
        """
        self.start_body_item(data, result)

    def end_while_iteration(
        self,
        data: running.WhileIteration,
        result: result.WhileIteration,
    ):
        """Called when a WHILE loop iteration ends.

        The default implementation calls :meth:`end_body_item`.

        New in Robot Framework 7.0.
        """
        self.end_body_item(data, result)

    def start_group(self, data: running.Group, result: result.Group):
        """Called when a GROUP starts.

        The default implementation calls :meth:`start_body_item`.

        New in Robot Framework 7.2.
        """
        self.start_body_item(data, result)

    def end_group(self, data: running.Group, result: result.Group):
        """Called when a GROUP ends.

        The default implementation calls :meth:`end_body_item`.

        New in Robot Framework 7.2.
        """
        self.end_body_item(data, result)

    def start_if(self, data: running.If, result: result.If):
        """Called when an IF/ELSE structure starts.

        The default implementation calls :meth:`start_body_item`.

        New in Robot Framework 7.0.
        """
        self.start_body_item(data, result)

    def end_if(self, data: running.If, result: result.If):
        """Called when an IF/ELSE structure ends.

        The default implementation calls :meth:`end_body_item`.

        New in Robot Framework 7.0.
        """
        self.end_body_item(data, result)

    def start_if_branch(self, data: running.IfBranch, result: result.IfBranch):
        """Called when an individual IF/ELSE branch starts.

        The default implementation calls :meth:`start_body_item`.

        New in Robot Framework 7.0.
        """
        self.start_body_item(data, result)

    def end_if_branch(self, data: running.IfBranch, result: result.IfBranch):
        """Called when an individual IF/ELSE branch ends.

        The default implementation calls :meth:`end_body_item`.

        New in Robot Framework 7.0.
        """
        self.end_body_item(data, result)

    def start_try(self, data: running.Try, result: result.Try):
        """Called when a TRY/EXCEPT structure starts.

        The default implementation calls :meth:`start_body_item`.

        New in Robot Framework 7.0.
        """
        self.start_body_item(data, result)

    def end_try(self, data: running.Try, result: result.Try):
        """Called when a TRY/EXCEPT structure ends.

        The default implementation calls :meth:`end_body_item`.

        New in Robot Framework 7.0.
        """
        self.end_body_item(data, result)

    def start_try_branch(self, data: running.TryBranch, result: result.TryBranch):
        """Called when an individual TRY/EXCEPT branch starts.

        The default implementation calls :meth:`start_body_item`.

        New in Robot Framework 7.0.
        """
        self.start_body_item(data, result)

    def end_try_branch(self, data: running.TryBranch, result: result.TryBranch):
        """Called when an individual TRY/EXCEPT branch ends.

        The default implementation calls :meth:`end_body_item`.

        New in Robot Framework 7.0.
        """
        self.end_body_item(data, result)

    def start_var(self, data: running.Var, result: result.Var):
        """Called when VAR starts.

        The default implementation calls :meth:`start_body_item`.

        New in Robot Framework 7.0.
        """
        self.start_body_item(data, result)

    def end_var(self, data: running.Var, result: result.Var):
        """Called when VAR ends.

        The default implementation calls :meth:`end_body_item`.

        New in Robot Framework 7.0.
        """
        self.end_body_item(data, result)

    def start_break(self, data: running.Break, result: result.Break):
        """Called when BREAK starts.

        The default implementation calls :meth:`start_body_item`.

        New in Robot Framework 7.0.
        """
        self.start_body_item(data, result)

    def end_break(self, data: running.Break, result: result.Break):
        """Called when BREAK ends.

        The default implementation calls :meth:`end_body_item`.

        New in Robot Framework 7.0.
        """
        self.end_body_item(data, result)

    def start_continue(self, data: running.Continue, result: result.Continue):
        """Called when CONTINUE starts.

        The default implementation calls :meth:`start_body_item`.

        New in Robot Framework 7.0.
        """
        self.start_body_item(data, result)

    def end_continue(self, data: running.Continue, result: result.Continue):
        """Called when CONTINUE ends.

        The default implementation calls :meth:`end_body_item`.

        New in Robot Framework 7.0.
        """
        self.end_body_item(data, result)

    def start_return(self, data: running.Return, result: result.Return):
        """Called when RETURN starts.

        The default implementation calls :meth:`start_body_item`.

        New in Robot Framework 7.0.
        """
        self.start_body_item(data, result)

    def end_return(self, data: running.Return, result: result.Return):
        """Called when RETURN ends.

        The default implementation calls :meth:`end_body_item`.

        New in Robot Framework 7.0.
        """
        self.end_body_item(data, result)

    def start_error(self, data: running.Error, result: result.Error):
        """Called when encountered invalid syntax starts.

        The default implementation calls :meth:`start_body_item`.

        New in Robot Framework 7.0.
        """
        self.start_body_item(data, result)

    def end_error(self, data: running.Error, result: result.Error):
        """Called when encountered invalid syntax ends.

        The default implementation calls :meth:`end_body_item`.

        New in Robot Framework 7.0.
        """
        self.end_body_item(data, result)

    def start_body_item(self, data, result):
        """Called by default when a keyword or a control structure starts.

        New in Robot Framework 7.0.
        """

    def end_body_item(self, data, result):
        """Called by default when a keyword or a control structure ends.

        New in Robot Framework 7.0.
        """

    def log_message(self, message: result.Message):
        """Called when a normal log message are emitted.

        The messages are typically logged by keywords, but also the framework
        itself logs some messages. These messages end up to output.xml and
        log.html.
        """

    def message(self, message: result.Message):
        """Called when framework's internal messages are emitted.

        Only logged by the framework itself. These messages end up to the syslog
        if it is enabled.
        """

    def library_import(self, library: running.TestLibrary, importer: running.Import):
        """Called after a library has been imported.

        ``library`` represents the imported library. It can be inspected and
        also modified. ``importer`` contains information about the location where
        the library was imported.

        New in Robot Framework 7.1.
        """

    def resource_import(self, resource: running.ResourceFile, importer: running.Import):
        """Called after a resource file has been imported.

        ``resource`` represents the imported resource file. It can be inspected and
        also modified. ``importer`` contains information about the location where
        the resource was imported.

        New in Robot Framework 7.1.
        """

    def variables_import(self, attrs: dict, importer: running.Import):
        """Called after a variable file has been imported.

        ``attrs`` contains information about the imported variable file. It can be
        inspected, but modifications to it have no effect. `importer`` contains
        information about the location where the variable file was imported.

        New in Robot Framework 7.1. This method will be changed in the future
        so that the ``attrs`` dictionary is replaced with an object representing
        the imported variable file.
        """

    def result_file(self, kind: ResultFile, path: Path):
        """Called, by default, when a result file like output or log is ready.

        :param kind: The result file type.
        :param path: An absolute path to the result file.

        Not called if a more specific result file related method like
        :meth:`output_file` or :meth:`log_file` has been implemented or
        when creating a result file is disabled.

        New in Robot Framework 7.5.
        """

    def output_file(self, path: "Path | None"):
        """Called when the output file is ready.

        :param path: An absolute path to the output file or
          ``None`` if creating the output file is disabled.

        Starting from Robot Framework 7.5, the default implementation calls
        :meth:`result_file` if creating the output file is not disabled.
        """
        if path is not None:
            self.result_file("OUTPUT", path)

    def log_file(self, path: Path):
        """Called when the log file is ready.

        :param path: An absolute path to the log file.

        Not called if creating the log file is disabled.

        Starting from Robot Framework 7.5, the default implementation calls
        :meth:`result_file`.
        """
        self.result_file("LOG", path)

    def report_file(self, path: Path):
        """Called when the report file is ready.

        :param path: An absolute path to the report file.

        Not called if creating the report file is disabled.

        Starting from Robot Framework 7.5, the default implementation calls
        :meth:`result_file`.
        """
        self.result_file("REPORT", path)

    def xunit_file(self, path: Path):
        """Called when the xunit compatible output file is ready.

        :param path: An absolute path to the xunit file.

        Only called if creating the xunit file is enabled.

        Starting from Robot Framework 7.5, the default implementation calls
        :meth:`result_file`.
        """
        self.result_file("XUNIT", path)

    def debug_file(self, path: Path):
        """Called when the debug file is ready.

        :param path: An absolute path to the debug file.

        Only called if creating the debug file is enabled.

        Starting from Robot Framework 7.5, the default implementation calls
        :meth:`result_file`.
        """
        self.result_file("DEBUG", path)

    def close(self):
        """Called when the whole execution ends.

        With library listeners called when the library goes out of scope.
        """


class Parser(ABC):
    """Optional base class for custom parsers.

    Parsers do not need to explicitly extend this class and in simple cases
    it is possible to implement them as modules. Regardless how a parser is
    implemented, it must have :attr:`extension` attribute and :meth:`parse`
    method. The :meth:`parse_init` method is optional and only needed if
    a parser supports parsing suite initialization files.

    The mandatory :attr:`extension` attribute specifies what file extension or
    extensions a parser supports. It can be set either as a class or instance
    attribute, and it can be either a string or a sequence of strings. The
    attribute can also be named ``EXTENSION``, which typically works better
    when a parser is implemented as a module.

    Example::

        from pathlib import Path
        from robot.api import TestSuite
        from robot.api.interfaces import Parser, TestDefaults


        class ExampleParser(Parser):
            extension = '.example'

            def parse(self, source: Path, defaults: TestDefaults) -> TestSuite:
                suite = TestSuite(TestSuite.name_from_source(source), source=source)
                # parse the source file and add tests to the created suite
                return suite

    The support for custom parsers is new in Robot Framework 6.1.
    """

    extension: "str | Sequence[str]"

    @abstractmethod
    def parse(self, source: Path, defaults: TestDefaults) -> TestSuite:
        """Mandatory method for parsing suite files.

        :param source: Path to the file to parse.
        :param defaults: Default values set for test in init files.

        The ``defaults`` argument is optional. It is possible to implement
        this method also so that it accepts only ``source``.
        """
        raise NotImplementedError

    def parse_init(self, source: Path, defaults: TestDefaults) -> TestSuite:
        """Optional method for parsing suite initialization files.

        :param source: Path to the file to parse.
        :param defaults: Default values to used with tests in child suites.

        The ``defaults`` argument is optional. It is possible to implement
        this method also so that it accepts only ``source``.

        If this method is not implemented, possible initialization files cause
        an error.
        """
        raise NotImplementedError
