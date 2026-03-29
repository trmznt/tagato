# SPDX-FileCopyrightText: 2025 Hidayat Trimarsanto <trimarsanto@gmail.com>
# SPDX-License-Identifier: MIT

from __future__ import annotations

__copyright__ = "(C) 2025 Hidayat Trimarsanto <trimarsanto@gmail.com>"
__author__ = "trimarsanto@gmail.com"
__license__ = "MIT"

from collections.abc import Callable, Awaitable
from typing import Any, Protocol, Self, runtime_checkable

from markupsafe import Markup, escape

from . import tags as t

# Re-export convenience aliases
fieldset = t.fieldset
legend = t.legend


# ---------------------------------------------------------------------------
# Protocols
# ---------------------------------------------------------------------------


@runtime_checkable
class InputProvider(Protocol):
    """Protocol for objects that supply input field values and metadata."""

    def get_value(self) -> str | tuple[int | str, str] | bool | None:
        """Return the current value.

        Can be a string, a (value, display_text) tuple for selects/radios,
        a boolean for checkboxes, or None if not set.
        """
        ...

    def get_options(self) -> list[tuple[str, str]]:
        """Return options as (value, display_text) pairs."""
        ...

    def is_required(self) -> bool:
        """Return whether the input is required."""
        ...

    def get_name(self) -> str:
        """Return the field name used for form submission."""
        ...


# ---------------------------------------------------------------------------
# CSS Theme abstraction
# ---------------------------------------------------------------------------


class CSSTheme:
    """Base class for CSS framework themes.

    Subclass this to provide CSS classes and structural helpers for a
    specific framework (Bootstrap, Tailwind, etc.).

    Methods returning ``str`` provide CSS class strings.
    Methods returning ``t.Tag`` provide framework-specific markup fragments
    for complex widgets (badges, popovers, info popups) whose HTML structure
    varies between frameworks.
    """

    # -- Layout --

    def form_row(self) -> str:
        """CSS classes for the outer wrapper row of a form field."""
        return ""

    def inline_input_wrapper(self) -> str:
        """CSS classes for an inline input group wrapper."""
        return ""

    def form_div(self) -> str:
        """CSS classes for a field-level div wrapper."""
        return ""

    # -- Labels --

    def label_class(self, offset: int) -> str:
        """CSS classes for a form label with the given column offset."""
        return ""

    # -- Input fields --

    def input_class(self, *, error: bool = False) -> str:
        """CSS classes for a text/password/email input."""
        return ""

    def select_class(self, *, error: bool = False) -> str:
        """CSS classes for a <select> element."""
        return ""

    def textarea_class(self, *, error: bool = False) -> str:
        """CSS classes for a <textarea> element."""
        return ""

    # -- Value column --

    def value_col(self, size: int) -> str:
        """CSS classes for the column wrapping the input control."""
        return ""

    # -- Checkbox / Radio --

    def check_wrapper(self) -> str:
        """CSS classes for the div wrapping a check/radio input pair."""
        return ""

    def check_input_class(self) -> str:
        """CSS classes for a checkbox or radio <input>."""
        return ""

    def check_label_class(self) -> str:
        """CSS classes for a checkbox or radio label."""
        return ""

    def check_group_label_class(self, offset: int) -> str:
        """CSS classes for the group label of a CheckboxGroupInput.

        Defaults to ``label_class(offset)``; override when the standard
        label padding does not vertically align with checkbox/radio items.
        """
        return self.label_class(offset)

    def check_group_value_col(self, size: int) -> str:
        """CSS classes for the value column wrapping grouped checkboxes.

        Defaults to ``value_col(size)``; override to add top padding that
        aligns checkbox items with the label text.
        """
        return self.value_col(size)

    # -- Feedback --

    def error_feedback(self, message: str) -> t.Tag | str:
        """Return markup for an error feedback message below an input."""
        if not message:
            return ""
        return t.span[message]

    def info_text(self, text: str) -> t.Tag | str:
        """Return markup for informational help text below a field."""
        if not text:
            return ""
        return t.small[escape(text)]

    def info_popup(self, url: str) -> t.Tag:
        """Return markup for a 'more info' popup link."""
        return t.a(href=escape(url))["?"]

    # -- Readonly badges --

    def badge_checked(self, label: str) -> t.Tag:
        """Badge for a checked checkbox in readonly mode."""
        return t.span[escape(label)]

    def badge_unchecked(self, label: str) -> t.Tag:
        """Badge for an unchecked checkbox in readonly mode."""
        return t.span[escape(label)]

    def badge_selected(self, text: str) -> t.Tag:
        """Badge for a selected radio option in readonly mode."""
        return t.span[escape(text)]

    # -- Popover --

    def popover_attrs(self, title: str, content: str) -> dict[str, str]:
        """Return extra HTML attributes to enable a popover on a label."""
        return {}


class Bootstrap53Theme(CSSTheme):
    """Bootstrap 5.3 CSS theme implementation."""

    # -- Layout --

    def form_row(self) -> str:
        return "row g-3 align-items-center mb-2"

    def inline_input_wrapper(self) -> str:
        return "row g-3 align-items-center mb-2"

    def form_div(self) -> str:
        return "mb-3"

    # -- Labels --

    def label_class(self, offset: int) -> str:
        return (
            f"col-md-{offset} col-form-label text-end "
            "align-self-start pt-2 ps-1 pe-0"
        )

    # -- Input fields --

    def input_class(self, *, error: bool = False) -> str:
        base = "form-control ps-2 pe-2"
        return f"{base} is-invalid" if error else base

    def select_class(self, *, error: bool = False) -> str:
        base = "form-select ps-2 pe-2"
        return f"{base} is-invalid" if error else base

    def textarea_class(self, *, error: bool = False) -> str:
        return self.input_class(error=error)

    # -- Value column --

    def value_col(self, size: int) -> str:
        col = size or 12
        return f"col-12 col-md-{col} ps-md-2 align-self-start"

    # -- Checkbox / Radio --

    def check_wrapper(self) -> str:
        return "form-check form-check-inline"

    def check_input_class(self) -> str:
        return "form-check-input"

    def check_label_class(self) -> str:
        return "form-check-label"

    def check_group_label_class(self, offset: int) -> str:
        # Same as label_class — consistent row height across all fields.
        return self.label_class(offset)

    def check_group_value_col(self, size: int) -> str:
        # Add pt-2 to match the label's top padding so checkbox items
        # start at the same vertical position as the label text.
        col = size or 12
        return f"col-12 col-md-{col} ps-md-2 pt-2 align-self-start"

    # -- Feedback --

    def error_feedback(self, message: str) -> t.Tag | str:
        if not message:
            return ""
        return t.span(class_="invalid-feedback")[message]

    def info_text(self, text: str) -> t.Tag | str:
        if not text:
            return ""
        return t.small(class_="form-text text-muted")[escape(text)]

    def info_popup(self, url: str) -> t.Tag:
        safe_url = escape(url)
        return t.div(class_="col-auto d-flex align-items-center")[
            t.a(
                class_="js-newWindow text-decoration-none",
                data_popup="width=400,height=200,scrollbars=yes",
                href=safe_url,
                aria_label="More info",
            )[t.span(class_="fw-semibold")["?"]]
        ]

    # -- Readonly badges --

    def badge_checked(self, label: str) -> t.Tag:
        return t.span(
            class_="badge bg-success-subtle text-success-emphasis border border-success"
        )[t.i(class_="bi bi-check-lg me-1"), escape(label)]

    def badge_unchecked(self, label: str) -> t.Tag:
        return t.span(
            class_=(
                "badge bg-secondary-subtle text-body-tertiary "
                "border border-secondary-subtle"
            )
        )[
            t.i(class_="bi bi-x-circle text-muted me-1", title="Disabled"),
            escape(label),
        ]

    def badge_selected(self, text: str) -> t.Tag:
        return t.span(
            class_="badge bg-success-subtle text-success-emphasis border border-primary"
        )[t.i(class_="bi bi-check-lg me-1"), escape(text)]

    # -- Popover --

    def popover_attrs(self, title: str, content: str) -> dict[str, str]:
        return {
            "data_bs_toggle": "popover",
            "data_bs_placement": "top",
            "data_bs_title": title,
            "data_bs_content": content,
        }


# ---------------------------------------------------------------------------
# Theme management
# ---------------------------------------------------------------------------

# Module-level active theme; defaults to Bootstrap 5.3 at bottom of file.
_current_theme: CSSTheme | None = None


def set_theme(theme: CSSTheme) -> None:
    """Set the active CSS theme for form rendering."""
    global _current_theme
    _current_theme = theme


def get_theme() -> CSSTheme:
    """Return the currently active CSS theme."""
    if _current_theme is None:
        raise RuntimeError(
            "No CSS theme is set. Call set_theme() before rendering forms."
        )
    return _current_theme


# ---------------------------------------------------------------------------
# Form container
# ---------------------------------------------------------------------------


class HTMLForm(t.pairedtag):
    """Top-level <form> element with preprocessing support.

    Acts as the root container for all form fields.
    Fields that require pre-populated values, eg. select input, can
    be populated later using opts(options=...) or an InputProvider callback,
    so the form can be rendered.
    """

    _newline: bool = True

    def __init__(
        self,
        *,
        action: str = "",
        method: str = "post",
        enctype: str = "application/x-www-form-urlencoded",
        _readonly: bool = False,
        _main_container: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            action=action,
            method=method,
            enctype=enctype,
            _main_container=_main_container,
            **kwargs,
        )
        self.readonly = _readonly
        # Slots for scripts/styles to be collected during rendering
        self.scriptlinks: list[str] = []
        self.jscode: list[str] = []
        self.pyscode: list[str] = []

    @property
    def _tag(self) -> str:
        """Render as <form> regardless of class name."""
        return "form"


# ---------------------------------------------------------------------------
# Inline input wrapper
# ---------------------------------------------------------------------------


class InlineInput(t.div):
    """Wrapper div for grouping multiple inputs on a single row."""

    def __init__(self, **kwargs: Any) -> None:
        theme = get_theme()
        super().__init__(class_=theme.inline_input_wrapper(), **kwargs)


# ---------------------------------------------------------------------------
# Base input field
# ---------------------------------------------------------------------------


class BaseInput(t.Tag):
    """Abstract base for all form input fields.

    Subclasses override ``_type`` and optionally ``render_input()`` to
    produce specific input types.  All CSS class strings and structural
    helpers are delegated to the active ``CSSTheme``, making the rendering
    framework-agnostic.

    **Value resolution order** (in ``get_value``):
    1. ``update_dict[name]`` — runtime overrides (e.g. POST data)
    2. ``input_provider.get_value()`` — data-layer binding
    3. ``self.value`` — explicit constructor value
    4. ``""`` — fallback default
    """

    _type: str = "text"

    def __init__(
        self,
        *,
        input_provider: InputProvider | None = None,
        name: str | None = None,
        label: str | None = None,
        value: Any = None,
        options: list[tuple[str, str]] | None = None,
        update_dict: dict[str, Any] | None = None,
        placeholder: str = "",
        info: str = "",
        size: int = 3,
        offset: int = 2,
        extra_control: str = "",
        readonly: bool | None = None,
        multiple: bool = False,
        input_style: str = "",
        popover: str = "",
        error: str = "",
        always_show_input: bool = False,
        override_theme: CSSTheme | None = None,
        **kwargs: Any,
    ) -> None:

        # Validate input_provider if given
        if input_provider is not None and not isinstance(input_provider, InputProvider):
            raise TypeError(
                f"input_provider must implement InputProvider protocol, "
                f"got {type(input_provider)}"
            )
        self.input_provider = input_provider
        self.label = label or name

        # Derive name from provider if not explicitly given
        name = name or (input_provider.get_name() if input_provider else None)

        super().__init__(name=name, **kwargs)

        self.value = value
        self.options = options
        self.update_dict = update_dict
        self.placeholder = placeholder
        self.error = error
        self.info = info
        self.size = size
        self.offset = offset
        self.extra_control = extra_control or ""
        self.readonly = readonly
        self.input_style = input_style
        self.popover = popover
        self.multiple = multiple
        self.always_show_input = always_show_input
        self._override_theme = override_theme

    # -- Value accessors --

    def get_value(
        self,
    ) -> str | tuple[int | str, str] | list[tuple[int | str, str]] | bool | None:
        """Return the field value using a deterministic precedence.

        Resolution order:
        1. ``update_dict[self.name]`` when present and not ``None``.
        2. ``input_provider.get_value()`` when no explicit ``self.value`` exists.
        3. Explicit ``self.value``.
        4. ``""`` as the final fallback.

        Returns:
            The resolved value for this field. Depending on field type this may
            be:
            a string,
            a ``(value, label)`` tuple for select fields,
            a list of such tuples for multi-selects,
            a boolean,
            or ``None`` (if provided by an input provider).
        """

        # Priority 1: update_dict overrides (e.g. from POST data)
        if self.update_dict is not None:
            val = self.update_dict.get(self.name)
            if val is not None:
                return val

        # Priority 2: input_provider (only if no explicit value was set)
        if self.input_provider is not None and self.value is None:
            return self.input_provider.get_value()

        # Priority 3: explicit value, or empty string fallback
        return self.value if self.value is not None else ""

    def get_options(self) -> list[tuple[str, str]] | None:
        """Return options list from self.options or input_provider."""
        if self.options is not None:
            return self.options
        if self.input_provider is not None:
            return self.input_provider.get_options()
        return None

    def is_readonly(self) -> bool:
        """Check readonly state: field-level override, then container default."""
        if self.readonly is not None:
            return self.readonly
        # Delegate to the form container's readonly flag
        container = self.get_container()
        return getattr(container, "readonly", False)

    def opts(self, **kwargs: Any) -> Self:
        """Set layout options (size, offset, error, info).

        Unlike the parent ``opts()``, this does NOT set HTML attributes
        since BaseInput is a composite (non-renderable) tag.
        """
        self.size = kwargs.pop("size", self.size)
        self.offset = kwargs.pop("offset", self.offset)
        self.error = kwargs.pop("error", self.error)
        self.info = kwargs.pop("info", self.info)
        self.options = kwargs.pop("options", self.options)
        self.value = kwargs.pop("value", self.value)

        if kwargs:
            raise ValueError(f"Unprocessed options: {', '.join(kwargs)}")

        return self

    # -- Theme shorthand --

    def _theme(self) -> CSSTheme:
        """Return the active theme instance."""
        if self._override_theme is not None:
            return self._override_theme
        return get_theme()

    # -- Rendering components --

    def render_label(self) -> t.Tag | str:
        """Render the <label> element, with optional popover support."""
        if self.label is None:
            return ""

        theme = self._theme()
        extra_attrs: dict[str, str] = {}

        # Attach popover data attributes if configured
        if self.popover:
            extra_attrs = theme.popover_attrs(title=self.label, content=self.popover)

        return t.label(
            class_=theme.label_class(self.offset),
            for_=self.name,
            **extra_attrs,
        )[escape(self.label)]

    def render_input(self, value: Any = None) -> t.Tag:
        """Render the input control wrapped in a value-column div."""
        theme = self._theme()
        readonly = self.is_readonly()
        resolved_value = value if value is not None else self.get_value()

        return t.div(class_=theme.value_col(self.size))[
            t.input(
                type=self._type,
                id=self.id,
                name=self.name,
                value=escape(resolved_value),
                class_=theme.input_class(error=bool(self.error)),
                placeholder=self.placeholder,
                style=self.input_style,
                readonly=readonly,
            ),
            theme.error_feedback(self.error),
        ]

    def render_info(self) -> t.Tag | str:
        """Render the info/help text or popup link."""
        if not self.info:
            return ""
        theme = self._theme()

        # "popup:URL" syntax triggers a popup link instead of inline text
        if self.info.startswith("popup:"):
            url = self.info[6:]
            return theme.info_popup(url)

        return theme.info_text(self.info)

    def _wrap_row(self, content: Markup) -> Markup:
        """Wrap rendered content in a form row div, unless inside InlineInput."""
        if isinstance(self.container, InlineInput):
            return content
        theme = self._theme()
        return t.div(class_=theme.form_row())[content].r()

    def r(self) -> Markup:
        """Render the complete form field (label + input + info)."""
        elements = t.fragment()[
            self.render_label(),
            self.render_input(),
            self.render_info(),
        ]
        return self._wrap_row(elements.r())


# ---------------------------------------------------------------------------
# Concrete input types
# ---------------------------------------------------------------------------


class HiddenInput(BaseInput):
    """Hidden <input> — renders without label, wrapper, or info text."""

    _type = "hidden"

    def r(self) -> Markup:
        return t.input(
            type=self._type,
            id=self.id,
            name=self.name,
            value=escape(self.get_value()),
        ).r()


class TextInput(BaseInput):
    """Standard text <input>."""

    _type = "text"


class PasswordInput(BaseInput):
    """Password <input>."""

    _type = "password"


class EmailInput(BaseInput):
    """Email <input>."""

    _type = "email"


class FileInput(BaseInput):
    """File <input>."""

    _type = "file"

    def render_input(self, value: Any = None) -> t.Tag:
        theme = self._theme()
        readonly = self.is_readonly()
        value = value if value is not None else self.get_value()
        filename = value if value else "No file"

        if readonly:
            # Show the filename as plain text in readonly mode (no input)
            return t.div(class_=theme.value_col(self.size))[
                t.div(class_="form-control-plaintext")[escape(filename)]
            ]

        return t.div(class_=theme.value_col(self.size))[
            t.div(class_="form-control-plaintext")[escape(filename)],
            t.input(
                type=self._type,
                id=self.id,
                name=self.name,
                class_=theme.input_class(error=bool(self.error)),
                placeholder=self.placeholder,
                style=self.input_style,
                readonly=readonly,
            ),
            theme.error_feedback(self.error),
        ]


class TextAreaInput(BaseInput):
    """<textarea> input field."""

    def render_input(self, value: Any = None) -> t.Tag:
        theme = self._theme()
        readonly = self.is_readonly()
        resolved_value = value if value is not None else self.get_value()

        return t.div(class_=theme.value_col(self.size))[
            t.textarea(
                id=self.id,
                name=self.name,
                class_=theme.textarea_class(error=bool(self.error)),
                placeholder=self.placeholder,
                style=self.input_style,
                readonly=readonly,
            )[escape(resolved_value)],
            theme.error_feedback(self.error),
        ]


class CheckboxInput(BaseInput):
    """Checkbox <input> with readonly badge support."""

    _type = "checkbox"

    def get_value(self) -> bool:
        """Coerce the raw value to a boolean."""
        val = super().get_value()
        if isinstance(val, str):
            return val.lower() in ("true", "1", "yes", "on")
        return bool(val)

    def render_label(self) -> t.Tag | str:
        """Suppress standalone label in readonly mode (badge includes it)."""
        if self.is_readonly():
            return ""
        theme = self._theme()
        return t.label(class_=theme.check_label_class(), for_=self.name)[
            escape(self.label)
        ]

    def _render_check(self) -> t.Tag | str:
        """Render the bare checkbox widget without a value-column wrapper.

        Used by CheckboxGroupInput to collect multiple checks into one column.
        """
        theme = self._theme()

        # Readonly: coloured badge instead of interactive checkbox
        if self.is_readonly():
            return (
                theme.badge_checked(self.label)
                if self.get_value()
                else theme.badge_unchecked(self.label)
            )

        # Editable: hidden fallback "off" + visible checkbox
        checked = True if self.get_value() else None
        return t.div(class_=theme.check_wrapper())[
            # Hidden input ensures "off" is submitted when unchecked
            t.input(type="hidden", name=self.name, _register=False, value="off"),
            t.input(
                type=self._type,
                id=self.id,
                name=self.name,
                value="on",
                checked=checked,
                readonly=False,
                class_=theme.check_input_class(),
            ),
            t.label(class_=theme.check_label_class(), for_=self.name)[
                escape(self.label)
            ],
        ]

    def render_input(self, value: Any = None) -> t.Tag:
        theme = self._theme()
        return t.div(class_=theme.value_col(self.size))[self._render_check()]

    def r(self) -> Markup:
        """Checkbox renders label as part of the input, not separately."""
        return self._wrap_row(self.render_input().r())


class CheckboxGroupInput(BaseInput):
    """Group of checkbox inputs sharing the same name (multi-select).

    Renders a single row: group label on the left, all checkbox items
    collected into one value column on the right.
    """

    def render_label(self) -> t.Tag | str:
        """Use the check-group label class for proper vertical alignment."""
        if self.label is None:
            return ""
        theme = self._theme()
        extra_attrs: dict[str, str] = {}
        if self.popover:
            extra_attrs = theme.popover_attrs(title=self.label, content=self.popover)
        return t.label(
            class_=theme.check_group_label_class(self.offset),
            for_=self.name,
            **extra_attrs,
        )[escape(self.label)]

    def render_input(self, value: Any = None) -> t.Tag:
        theme = self._theme()
        # Collect bare check widgets into one value column so they sit
        # inline with the group label instead of each getting its own row.
        # Uses check_group_value_col for vertical alignment with the label.
        return t.div(class_=theme.check_group_value_col(self.size))[
            *(
                item._render_check()
                for item in self.contents
                if isinstance(item, CheckboxInput)
            )
        ]


class RadioInput(BaseInput):
    """Radio button group input."""

    _type = "radio"

    def render_input(self, value: Any = None) -> t.Tag:
        theme = self._theme()
        readonly = self.is_readonly()

        # Resolve value; for radios the value selects which option is checked
        resolved_value = value if value is not None else self.get_value()
        options = self.get_options()

        # Readonly: show a badge for the selected option
        if readonly:
            selected_text = next(
                (text for val, text in options if val == resolved_value),
                str(resolved_value) if resolved_value else "",
            )
            return t.div(class_=theme.value_col(self.size))[
                theme.badge_selected(selected_text)
            ]

        # Editable: render radio buttons for each option
        return t.div(class_=theme.value_col(self.size))[
            *(
                t.div(class_=theme.check_wrapper())[
                    t.input(
                        type=self._type,
                        id=f"{self.id}_{val}",
                        name=self.name,
                        value=val,
                        checked=(val == resolved_value),
                        readonly=False,
                        class_=theme.check_input_class(),
                    ),
                    t.label(
                        class_=theme.check_label_class(),
                        for_=f"{self.id}_{val}",
                    )[escape(text)],
                ]
                for val, text in options
            )
        ]


class SelectInput(BaseInput):
    """<select> dropdown input with optional option loading."""

    def render_input(self, value: Any = None) -> t.Tag:
        theme = self._theme()
        readonly = self.is_readonly()

        raw_value = value if value is not None else self.get_value()
        # raw value can be a string or a (value, display_text) tuple;
        # normalize to tuple
        # for multiple selects, raw_value can be a list of strings or tuples;
        # normalize to list of tuples

        # Normalize value to a (key, display_text) tuple if not multiple
        if not self.multiple:
            if raw_value is None:
                norm_value: tuple[str, str] = ("", "")
            elif isinstance(raw_value, str):
                norm_value = (raw_value, raw_value)
            else:
                norm_value = raw_value  # already a tuple
        else:
            norm_value = raw_value if isinstance(raw_value, list) else []

        # Readonly: render as a plain-text input showing the display text
        if readonly and not self.always_show_input:
            if not self.multiple:
                return super().render_input(value=norm_value[1])
            else:
                return super().render_input(
                    value=", ".join(text for _, text in norm_value) or ""
                )

        options = self.get_options()
        if options is None:
            raise RuntimeError(
                "SelectInput options is None. Please populate options via "
                "the options parameter or input_provider if using callback."
            )

        if not self.multiple:
            selection = [norm_value[0]]
        else:
            selection = (
                [val for val, _ in norm_value] if isinstance(raw_value, list) else []
            )

        select_tag = t.select(
            id=self.id,
            name=self.name,
            class_=theme.select_class(error=bool(self.error)),
            style=self.input_style,
            disabled=readonly,
            multiple=self.multiple,
        )[
            [
                t.option(value=val, selected=(val in selection))[text]
                for val, text in options
            ]
        ]

        return t.div(class_=theme.value_col(self.size))[
            select_tag,
            theme.error_feedback(self.error),
        ]


# ---------------------------------------------------------------------------
# Default theme activation
# ---------------------------------------------------------------------------

# Set Bootstrap 5.3 as the default theme on import
set_theme(Bootstrap53Theme())

# EOF
