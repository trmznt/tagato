# SPDX-FileCopyrightText: 2025 Hidayat Trimarsanto <trimarsanto@gmail.com>
# SPDX-License-Identifier: MIT

from __future__ import annotations

__copyright__ = "(C) 2025 Hidayat Trimarsanto <trimarsanto@gmail.com>"
__author__ = "trimarsanto@gmail.com"
__license__ = "MIT"


from typing import Self, Any
from markupsafe import Markup, escape

literal = Markup


def _render_content(content: Tag | str) -> str:
    """Render a single content item to its HTML string representation.

    Uses the __html__ protocol when available (Tag and Markup objects),
    otherwise escapes the content to prevent XSS.
    """
    if hasattr(content, "__html__"):
        return content.__html__()  # type: ignore[union-attr]
    return escape(content)  # type: ignore[arg-type]


def _pretty_render(
    content: Tag | str,
    level: int,
    indent: str,
) -> str:
    """Render a single content item with indentation for pretty output.

    Tags delegate to their own ``pretty()`` method; raw strings are
    escaped and indented to the current level.
    """
    if isinstance(content, Tag):
        return content.pretty(level=level, indent=indent)
    return f"{indent * level}{escape(content)}"


class _SelfInstantiating(type):
    """Metaclass that allows Tag classes to be used without explicit instantiation.

    Enables syntax like ``div["hello"]`` instead of ``div()["hello"]``.
    """

    def __str__(cls) -> str:
        # Create a temp instance and return its string representation
        return str(cls())

    def __getitem__(cls, args: Any) -> Tag:
        # Create a temp instance and return the result of its __getitem__
        return cls()[args]

    def __iadd__(cls, other: Any) -> Tag:
        # Create instance, apply addition, and return the instance
        instance = cls()
        instance += other
        return instance


class Tag(metaclass=_SelfInstantiating):
    """Base class for all HTML tag representations.

    Provides content management (add, insert, replace), attribute handling,
    and a hierarchical element registry for id-based lookup.
    """

    _newline: bool = False
    _main_container: bool = False
    _inline: bool = False

    def __init__(
        self,
        *args: Any,
        id: str | None = None,
        name: str | None = None,
        class_: str | None = None,
        _enabled: bool = True,
        _main_container: bool = False,
        _register: bool = True,
        **kwargs: Any,
    ) -> None:

        if any(args):
            for arg in args:
                # check if arg is a dict (of attributes) or a string starts with # (for id and name)
                if isinstance(arg, dict):
                    kwargs.update(arg)
                elif isinstance(arg, str) and arg.startswith("#"):
                    name = arg[1:]
                else:
                    raise ValueError(
                        "Invalid positional arguments: expected a dict of attributes or "
                        "a string starting with '#' for id. "
                        f"Got {type(arg).__name__}: {arg!r}"
                    )

        # Normalize identity attributes by stripping whitespace
        self.name = name.strip() if name else None
        self.id = id.strip() if id else self.name
        self.class_ = class_.strip() if class_ else None

        self._enabled = _enabled
        self._main_container = _main_container
        self._register = _register

        # Child content (tags and raw strings) in insertion order
        self.contents: list[Tag | str] = []
        # Registry of id -> Tag for fast lookup within this subtree
        self.elements: dict[str, Tag] = {}
        # Extra HTML attributes (e.g. href, data-*, etc.)
        self.attrs: dict[str, Any] = {}

        # Parent tag that owns this element (set during registration)
        self.container: Tag | None = None

        self.set_attributes(kwargs)

    def __repr__(self) -> str:
        return (
            f"{self._tag}(name='{self.name or ''}', "
            f"id='{self.id or ''}', class='{self.class_ or ''}')"
        )

    def __str__(self) -> str:
        return str(self.__html__())  # pragma: no cover - convenience

    # -- Content manipulation methods --

    def add(self, *elements: Tag | Markup | str) -> Self:
        """Append elements to this tag and register any Tag children by id."""
        for element in elements:
            # Auto-instantiate Tag classes passed without parentheses (e.g. br)
            if isinstance(element, type) and issubclass(element, Tag):
                element = element()
            # Support objects that expose a __tag__ factory (adapter protocol)
            elif hasattr(element, "__tag__"):
                element = element.__tag__()  # type: ignore[union-attr]
            self.contents.append(element)
            # Only register Tag instances that opt in to registration
            if isinstance(element, Tag) and element._register:
                self.register_element(element)
        return self

    def __iadd__(self, element: Any) -> Self:
        self.add(element)
        return self

    def __getitem__(self, arg: Any) -> Self:
        if isinstance(arg, (tuple, list, set)):
            self.add(*arg)
        else:
            self.add(arg)
        return self

    def insert(self, index: int, *elements: Tag | Markup | str) -> Self:
        """Insert elements at the given index in content order."""
        for element in reversed(elements):
            # Auto-instantiate Tag classes passed without parentheses
            if isinstance(element, type) and issubclass(element, Tag):
                element = element()
            # Support the __tag__ adapter protocol, same as add()
            elif hasattr(element, "__tag__"):
                element = element.__tag__()  # type: ignore[union-attr]
            self.contents.insert(index, element)
            if isinstance(element, Tag) and element._register:
                self.register_element(element)
        return self

    def replace(self, *elements: Tag | Markup | str) -> Self:
        """Replace all contents with new elements.

        Uses ``remove_element`` to properly unregister each child and its
        descendants from every ancestor up to the root container.
        """
        # Remove all registered Tag children (iterate over a snapshot)
        for ident in list(self.elements):
            # Only remove elements that are direct children of this node;
            # remove_element will cascade their descendants automatically.
            element = self.elements.get(ident)
            if element is not None and element.container is self:
                self.remove_element(ident)

        self.contents.clear()
        self.elements.clear()
        self.add(*elements)
        return self

    def nonreg_add(self, *elements: Tag | Markup | str) -> Self:
        """Append elements without registering them in the element registry."""
        for element in elements:
            # Auto-instantiate Tag classes passed without parentheses
            if isinstance(element, type) and issubclass(element, Tag):
                element = element()
            # Support the __tag__ adapter protocol for consistency with add()
            elif hasattr(element, "__tag__"):
                element = element.__tag__()  # type: ignore[union-attr]
            self.contents.append(element)
        return self

    # -- Attribute handling --

    def set_attributes(self, kwargs: dict[str, Any]) -> Self:
        """Set HTML attributes from keyword arguments.

        Keys are normalized: trailing underscores are stripped (to allow
        Python-reserved words like ``class_``), and internal underscores
        are converted to hyphens (e.g. ``data_value`` -> ``data-value``).
        Leading underscores indicate internal parameters and are rejected.
        """
        for key, val in kwargs.items():
            if key.startswith("_"):
                raise ValueError(
                    f"Argument '{key}' is not being consumed by internal process, "
                    "please correct!"
                )
            # Normalize: strip trailing underscore, convert inner _ to -
            key = key.lower().removesuffix("_")
            if "_" in key:
                key = key.replace("_", "-")
            self.attrs[key] = val
        return self

    def attributes(self, attrs_only: bool = False) -> str:
        """Return the serialized HTML attribute string (without outer brackets).

        When *attrs_only* is True, the id/name/class built-in attributes are
        omitted and only extra attrs set via ``set_attributes`` are included.
        """
        parts: list[str] = []

        # Emit the core identity/class attributes first
        if not attrs_only:
            if self.id:
                parts.append(f'id="{escape(self.id)}"')
            if self.name:
                parts.append(f'name="{escape(self.name)}"')
            if self.class_:
                parts.append(f'class="{escape(self.class_)}"')

        # Emit extra attributes; boolean True -> valueless, False/None -> skip
        for key, val in self.attrs.items():
            safe_key = str(escape(key))
            if val is True:
                parts.append(safe_key)
            elif val is not None and val is not False:
                parts.append(f'{safe_key}="{escape(val)}"')

        return " ".join(parts)

    def opts(self, **kwargs: Any) -> Self:
        """Shorthand for ``set_attributes``."""
        return self.set_attributes(kwargs)

    @property
    def _tag(self) -> str:
        """Return the lowercase HTML tag name derived from the class name."""
        return self.__class__.__name__.lower()

    def __html__(self) -> Markup:
        return self.r()

    def pretty(self, *, level: int = 0, indent: str = "  ") -> str:
        """Return a pretty-printed HTML string with indentation.

        Override in subclasses (``fragment``, ``singletag``, ``pairedtag``)
        to provide concrete rendering.  The base implementation falls back
        to the compact ``r()`` output.
        """
        return f"{indent * level}{self.r()}"

    # -- Container / element registry methods --

    def get_container(self) -> Tag:
        """Walk up the parent chain and return the root container."""
        return self.container.get_container() if self.container else self

    def __contains__(self, identifier: str) -> bool:
        return identifier in self.elements

    def register_element(self, element: Any) -> None:
        """Register *element* (and its descendants) in this tag's registry.

        Elements marked as main containers are skipped to avoid
        polluting the global registry with structural wrappers.
        """
        if not isinstance(element, Tag):
            return

        # Skip main-container elements to prevent registration conflicts
        if element._main_container:
            return

        container = self.get_container()
        # Set the direct parent, NOT the root — remove_element() and
        # replace() rely on this pointing to the immediate parent.
        element.container = self

        def _register(target: Tag, node: Tag) -> None:
            """Recursively register *node* and its children into *target*."""
            if ident := node.id:
                existing = target.elements.get(ident)
                if existing is not None and existing is not node:
                    raise ValueError(
                        f"Element with id '{ident}' is already registered "
                        "in this container."
                    )
                target.elements[ident] = node

            # Propagate child registrations upward
            for child in node.elements.values():
                _register(target, child)

        # Register into both the immediate parent and the root container
        _register(self, element)
        if container is not self:
            _register(container, element)

    def unregister_element(self, identifier: str) -> None:
        """Remove *identifier* from this tag's element registry (if present)."""
        self.elements.pop(identifier, None)

    def get_element(self, identifier: str) -> Tag:
        """Retrieve a registered element by its identifier.

        Raises ``KeyError`` if the identifier is not found.
        """
        return self.elements[identifier]

    def remove_element(self, identifier: str) -> Self:
        """Remove an element by its identifier from the tree.

        Performs a deep removal: walks down the content tree to find and
        remove the element from its direct parent's contents list, then
        unregisters it (and all its descendants) from every ancestor's
        element registry up to the root container.
        """
        element = self.elements.get(identifier)
        if element is None:
            raise KeyError(f"No element with id '{identifier}' found for removal.")

        # Collect all ids to unregister: the element itself + its descendants
        ids_to_remove: set[str] = set()
        if element.id:
            ids_to_remove.add(element.id)
        for child_id in element.elements:
            ids_to_remove.add(child_id)

        # Remove the element from its direct parent's contents list
        parent = element.container or self
        parent.contents = [c for c in parent.contents if c is not element]

        # Walk up the ancestor chain and unregister all collected ids
        node: Tag | None = parent
        while node is not None:
            for eid in ids_to_remove:
                node.elements.pop(eid, None)
            node = node.container

        # Clear the removed element's parent reference
        element.container = None

        return self


# ---------------------------------------------------------------------------
# Concrete tag renderers
# ---------------------------------------------------------------------------


class fragment(Tag):
    """A non-tag container that renders its children separated by newlines."""

    def r(self) -> Markup:
        """Render children joined by newlines (no wrapping element)."""
        return Markup("\n".join(_render_content(content) for content in self.contents))

    def pretty(self, *, level: int = 0, indent: str = "  ") -> str:
        """Pretty-print children at the current indentation level."""
        return "\n".join(
            _pretty_render(content, level, indent) for content in self.contents
        )


class singletag(Tag):
    """Base class for void / self-closing HTML elements (e.g. <br />).

    Void elements cannot have children. Attempting to add content via
    ``add()``, ``insert()``, ``replace()``, or the ``[]`` operator will
    raise a ``TypeError``.
    """

    # Void elements are inline in HTML; keeps pretty() from forcing block mode
    _inline: bool = True

    def _reject_content(self) -> None:
        """Raise TypeError when content is added to a void element."""
        raise TypeError(f"<{self._tag}> is a void element and cannot have children.")

    def add(self, *elements: Tag | Markup | str) -> Self:
        if elements:
            self._reject_content()
        return self

    def insert(self, index: int, *elements: Tag | Markup | str) -> Self:
        if elements:
            self._reject_content()
        return self

    def replace(self, *elements: Tag | Markup | str) -> Self:
        if elements:
            self._reject_content()
        return self

    def nonreg_add(self, *elements: Tag | Markup | str) -> Self:
        if elements:
            self._reject_content()
        return self

    def r(self) -> Markup:
        """Render as a self-closing HTML tag."""
        attrs = self.attributes()
        attrs_part = f" {attrs}" if attrs else ""
        tail = "\n" if self._newline else ""
        return Markup(f"<{self._tag}{attrs_part} />{tail}")

    def pretty(self, *, level: int = 0, indent: str = "  ") -> str:
        """Pretty-print a self-closing tag at the given indentation level."""
        attrs = self.attributes()
        attrs_part = f" {attrs}" if attrs else ""
        return f"{indent * level}<{self._tag}{attrs_part} />"


class pairedtag(Tag):
    """Base class for normal paired HTML elements (e.g. <div>...</div>)."""

    def r(self) -> Markup:
        """Render as an opening tag, inner content, and closing tag."""
        attrs = self.attributes()
        attrs_part = f" {attrs}" if attrs else ""
        inner_html = "".join(_render_content(content) for content in self.contents)
        tail = "\n" if self._newline else ""
        return Markup(f"<{self._tag}{attrs_part}>{inner_html}</{self._tag}>{tail}")

    def pretty(self, *, level: int = 0, indent: str = "  ") -> str:
        """Pretty-print a paired tag with indented children.

        Inline tags (``_inline = True``) or tags whose contents are all
        raw strings / inline children render on a single line.  Block
        tags get their children on separate indented lines.
        """
        attrs = self.attributes()
        attrs_part = f" {attrs}" if attrs else ""
        pad = indent * level
        tag = self._tag

        # Determine if contents should be kept inline:
        # - this tag is itself inline, OR
        # - every child is either a raw string or an inline tag
        all_inline = self._inline or all(
            isinstance(c, str) or (isinstance(c, Tag) and c._inline)
            for c in self.contents
        )

        if not self.contents:
            return f"{pad}<{tag}{attrs_part}></{tag}>"

        if all_inline:
            # Render everything on one line (compact inner content)
            inner = "".join(_render_content(c) for c in self.contents)
            return f"{pad}<{tag}{attrs_part}>{inner}</{tag}>"

        # Block mode: children on separate lines, indented one level deeper
        lines: list[str] = [f"{pad}<{tag}{attrs_part}>"]
        for content in self.contents:
            lines.append(_pretty_render(content, level + 1, indent))
        lines.append(f"{pad}</{tag}>")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Dynamically generated concrete tag classes for standard HTML elements
# ---------------------------------------------------------------------------

_single_tags = [
    "img",
    "input",
    "br",
    "hr",
    "meta",
    "link",
    "source",
    "track",
    "wbr",
    "param",
    "col",
    "embed",
    "area",
    "base",
]
for _tag_name in _single_tags:
    globals()[_tag_name] = type(_tag_name, (singletag,), {})

# Inline elements render on the same line as their parent in pretty output
_inline_tags = frozenset(
    {
        "span",
        "a",
        "b",
        "i",
        "strong",
        "label",
        "time",
        "code",
    }
)

_paired_tags = [
    "div",
    "span",
    "p",
    "a",
    "b",
    "i",
    "table",
    "thead",
    "tbody",
    "tr",
    "td",
    "th",
    "form",
    "label",
    "button",
    "textarea",
    "select",
    "option",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "nav",
    "footer",
    "header",
    "section",
    "article",
    "aside",
    "dl",
    "dt",
    "dd",
    "fieldset",
    "legend",
    "pre",
    "code",
    "blockquote",
    "html",
    "head",
    "body",
    "time",
    "strong",
    "small",
    "template",
]
for _tag_name in _paired_tags:
    attrs = {"_inline": True} if _tag_name in _inline_tags else {}
    globals()[_tag_name] = type(_tag_name, (pairedtag,), attrs)


# ---------------------------------------------------------------------------
# Special-case tags with validation logic
# ---------------------------------------------------------------------------


class li(pairedtag):
    """List item element."""


class ul(pairedtag):
    """Unordered list — only accepts ``li`` children."""

    def add(self, *args: Tag | Markup | str) -> Self:
        for arg in args:
            if not isinstance(arg, li):
                raise ValueError(f"{self._tag.upper()} should only have LI content")
            super().add(arg)
        return self


class ol(ul):
    """Ordered list — inherits ``li``-only validation from ``ul``."""


# EOF
