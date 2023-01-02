import ast
import importlib
import inspect
import textwrap
from collections.abc import Callable, Generator, Iterable
from itertools import chain
from types import ModuleType
from typing import Any, TypeVar

from fastapi import status  # noqa
from fastapi.routing import APIRoute
from starlette.exceptions import HTTPException

ErrType = TypeVar("ErrType", bound=Exception)
AstType = TypeVar("AstType", bound=ast.AST)


def find_nodes(
    tree: ast.Module,
    node_type: type[AstType],
    attr_filter: dict[str, type[ast.AST]] | None = None,
) -> Generator[AstType, None, None]:
    if attr_filter:
        for node in ast.walk(tree):
            if isinstance(node, node_type) and all(
                hasattr(node, node_attr)
                and isinstance(getattr(node, node_attr), attr_type)
                for node_attr, attr_type in attr_filter.items()
            ):
                yield node
    else:
        for node in ast.walk(tree):
            if isinstance(node, node_type):
                yield node


def is_function_or_coroutine(obj: Any) -> bool:
    return inspect.isfunction(obj) or inspect.iscoroutinefunction(obj)


def is_subclass_of_any(klass: type, classes: Iterable[type] | Iterable[str]) -> bool:
    base_names = (
        [base.__name__ for base in klass.__bases__]
        if hasattr(klass, "__bases__")
        else []
    )
    base_names.append(type(klass).__name__)
    if all(isinstance(cls, str) for cls in classes):
        class_names = classes
    else:
        class_names = [cls.__name__ for cls in classes if hasattr(cls, "__name__")]
    return any(base_name in class_names for base_name in base_names)


def is_callable_instance(obj: object) -> bool:
    return hasattr(obj, "__call__") and not isinstance(obj, type)


def create_exc_instance(
    exc_class: type[Exception], exc_args: list[Any] | None = None
) -> Exception | None:
    importlib.import_module(exc_class.__module__)
    value = exc_class(*exc_args) if exc_args else exc_class()
    return value if isinstance(value, Exception) else None


def eval_ast_exc_instance(
    exc_class: type[Exception], ast_exec_inst: ast.expr
) -> Exception | None:
    importlib.import_module(exc_class.__module__)
    value = eval(ast.unparse(ast_exec_inst))
    return value if isinstance(value, Exception) else None


class RouteExcFinder:
    def __init__(
        self,
        customError: type[ErrType] | None = None,
        dependencyClasses: tuple[type] | None = None,
        serviceClasses: tuple[type] | None = None,
    ):
        self.customError = customError
        self.dependencyClasses = dependencyClasses
        self.serviceClasses = serviceClasses

        self.exceptions_to_find: tuple[str, ...] = (
            ("HTTPException", self.customError.__name__)
            if self.customError
            else ("HTTPException",)
        )

        self.functions: list[Callable] = []
        self.exceptions: list[HTTPException | ErrType] = []

    def extract_exceptions(
        self,
        route: APIRoute,
    ) -> list[HTTPException | ErrType]:
        self.functions.append(getattr(route, "endpoint", route))
        self.functions.extend(self.find_functions(route))
        while len(self.functions) > 0:
            function = self.functions.pop(0)
            self.functions.extend(self.find_functions(function))
            self.exceptions.extend(self.find_exceptions(function))
        if self.dependencyClasses:
            self.exceptions += self.find_dependency_exceptions(route)
        if self.serviceClasses:
            self.exceptions += self.find_service_exceptions(route)
        return self.exceptions

    @staticmethod
    def find_functions(route: Callable) -> list[Callable]:
        _functions = []
        func = getattr(route, "endpoint", route)
        source = inspect.getsource(func)
        tree = ast.parse(source)
        module = importlib.import_module(func.__module__)
        for node in ast.walk(tree):
            try:
                obj = getattr(module, node.id) if hasattr(node, "id") else None
                if is_function_or_coroutine(obj) and obj is not func:
                    _functions.append(obj)
            except (AttributeError, ValueError):
                ...
        return _functions

    def find_exceptions(
        self,
        callable: APIRoute | Callable | str,
        owner: type | ModuleType | None = None,
    ) -> list[HTTPException]:
        _exceptions = []
        callable = callable.endpoint if hasattr(callable, "endpoint") else callable

        if isinstance(callable, str):
            if owner is None:
                raise ValueError("owner must be provided if callable is a string")
            callable = getattr(owner, callable)

        if module := inspect.getmodule(callable) if owner is not ModuleType else owner:
            unwrapped = inspect.unwrap(callable)
            source = textwrap.dedent(inspect.getsource(unwrapped))
            tree = ast.parse(source)

            for node in find_nodes(tree, ast.Raise, attr_filter={"exc": ast.Call}):
                http_exec_instance = self.create_exc_inst_from_raise_stmt(node, module)
                if http_exec_instance:
                    _exceptions.append(http_exec_instance)
        return _exceptions

    def find_service_exceptions(
        self,
        route: APIRoute | Callable,
    ) -> list[HTTPException]:
        exceptions = []
        assert self.serviceClasses is not None
        func = route.endpoint if hasattr(route, "endpoint") else route
        module = inspect.getmodule(func)
        source = inspect.getsource(func)
        tree = ast.parse(source)

        for node in find_nodes(tree, ast.Call, attr_filter={"func": ast.Attribute}):
            assert isinstance(method := node.func, ast.Attribute)

            cls = None
            if hasattr(method.value, "func") and hasattr(method.value.func, "id"):
                try:
                    cls = getattr(module, method.value.func.id)
                except (AttributeError, NameError):
                    ...

            elif hasattr(method.value, "id"):
                try:
                    cls = getattr(module, method.value.id)
                except (AttributeError, NameError):
                    instance_name = method.value.id
                    for assignment_node in find_nodes(tree, ast.Assign):
                        if (
                            hasattr(assignment_node.targets[0], "id")
                            and assignment_node.targets[0].id == instance_name
                        ):
                            if hasattr(assignment_node.value, "func") and hasattr(
                                assignment_node.value.func, "id"
                            ):
                                try:
                                    cls = getattr(module, assignment_node.value.func.id)
                                    break
                                except (AttributeError, NameError):
                                    ...

            if cls:
                _exceptions = self.search_method_for_excs(
                    cls, method, self.serviceClasses
                )
                if _exceptions:
                    exceptions.extend(_exceptions)

        return exceptions

    def find_dependency_exceptions(
        self,
        route: APIRoute | Callable,
    ) -> list[HTTPException]:
        exceptions = []
        assert self.dependencyClasses is not None
        func = route.endpoint if hasattr(route, "endpoint") else route
        module = inspect.getmodule(func)
        source = inspect.getsource(func)
        tree = ast.parse(source)

        for node in find_nodes(tree, ast.FunctionDef):
            for kwarg in chain(node.args.defaults, node.args.kw_defaults):
                if (
                    kwarg
                    and hasattr(kwarg, "func")
                    and hasattr(kwarg.func, "id")
                    and kwarg.func.id == "Depends"
                ):
                    if method := kwarg.args[0] if hasattr(kwarg, "args") else None:
                        cls = None
                        if hasattr(method, "value") and hasattr(method.value, "id"):
                            try:
                                cls = getattr(module, method.value.id)
                            except (AttributeError, NameError):
                                ...
                        elif hasattr(method, "id"):
                            try:
                                cls = getattr(module, method.id)
                            except (AttributeError, NameError):
                                ...
                        if cls:
                            _exceptions = self.search_method_for_excs(
                                cls, method, self.dependencyClasses
                            )
                            if _exceptions:
                                exceptions.extend(_exceptions)
        return exceptions

    def create_exc_inst_from_raise_stmt(
        self,
        raise_stmt: ast.Raise,
        module: ModuleType | type,
    ) -> Exception | None:
        if raise_stmt.exc and hasattr(raise_stmt.exc, "func"):

            if hasattr(raise_stmt.exc.func, "attr"):
                outer_exc_class = getattr(
                    module,
                    raise_stmt.exc.func.value.id,
                )
                http_exc = getattr(outer_exc_class, raise_stmt.exc.func.attr)
                if is_subclass_of_any(http_exc, self.exceptions_to_find):
                    http_exec_instance = create_exc_instance(http_exc)
                    return http_exec_instance

            elif http_exc := getattr(module, raise_stmt.exc.func.id):
                if is_subclass_of_any(http_exc, self.exceptions_to_find):
                    try:
                        http_exec_instance = eval_ast_exc_instance(
                            http_exc, raise_stmt.exc
                        )
                    except NameError:
                        http_exec_instance = create_exc_instance(http_exc)
                    return http_exec_instance

        return None

    def get_class_and_callable(
        self, cls: type, method: ast.Attribute, types_to_find: tuple[type, ...]
    ) -> tuple[type, str]:
        callable = ""

        if isinstance(cls, types_to_find):
            if is_callable_instance(cls):
                assert hasattr(cls, "__call__")
                callable = cls.__call__.__name__
            else:
                callable = method.attr
            cls = cls.__class__

        elif is_subclass_of_any(cls, types_to_find):
            callable = method.attr

        return cls, callable

    def search_method_for_excs(
        self, cls: type, method: ast.Attribute, types_to_find: tuple[type, ...]
    ) -> list[HTTPException | ErrType]:
        exceptions = []

        cls, callable = self.get_class_and_callable(cls, method, types_to_find)

        nested_to_search = (
            self.serviceClasses
            if types_to_find == self.dependencyClasses
            else self.dependencyClasses
        )
        if nested_to_search and (callable or is_subclass_of_any(cls, nested_to_search)):
            if nested_to_search == self.dependencyClasses:
                _exceptions = self.find_dependency_exceptions(cls)
            else:
                _exceptions = self.find_service_exceptions(cls)
            exceptions.extend(_exceptions)

        if callable:
            if _exceptions := self.find_exceptions(callable, cls):
                exceptions.extend(_exceptions)

        return exceptions

    def clear(self) -> None:
        self.functions.clear()
        self.exceptions.clear()
