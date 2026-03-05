# SPDX-FileCopyrightText: 2025 Hidayat Trimarsanto <trimarsanto@gmail.com>
# SPDX-License-Identifier: MIT

from __future__ import annotations

__copyright__ = "(C) 2025 Hidayat Trimarsanto <trimarsanto@gmail.com>"
__author__ = "trimarsanto@gmail.com"
__license__ = "MIT"

from collections.abc import Callable, Awaitable
from typing import Any, TYPE_CHECKING, Protocol, Self, runtime_checkable

from markupsafe import Markup, escape

from . import tags as t

fieldset = t.fieldset
legend = t.legend

# generate protocols for validator and inputfield for type hinting purposes


@runtime_checkable
class InputProvider(Protocol):

    def get_value(self) -> str | tuple[int | str, str] | bool | None:
        """
        Return the current value of the input, which can be a string,
        a tuple (for select inputs and radio buttons), a boolean (for checkboxes),
        or None if no value is set.
        """
        ...

    def get_options(self) -> list[tuple[str, str]]:
        """
        Return a list of options for select inputs and radio buttons,
        where each option is a tuple of (value, display_text).
        """
        ...

    def is_required(self) -> bool:
        """
        Return whether the input is required.
        """
        ...

    def get_name(self) -> str:
        """
        Return the name of the input field, used for form submission.
        """
        ...


# CSS helper functions

__current_css_set__ = None


def set_css_set(css_set: dict[type, str]):
    global __current_css_set__
    __current_css_set__ = css_set


def get_css_set() -> dict[type, str]:
    global __current_css_set__
    if __current_css_set__ is None:
        raise RuntimeError(
            "CSS set is not defined. Please call set_css_set() to define it."
        )
    return __current_css_set__


def get_css(cls: type) -> str:
    css_set = get_css_set()
    return css_set.get(cls, "")


class HTMLForm(t.pairedtag):

    _tag: str = "form"
    _newline: bool = True

    def __init__(
        self,
        *,
        action: str = "",
        method: str = "post",
        enctype: str = "application/x-www-form-urlencoded",
        _readonly: bool = False,
        _main_container: bool = True,
        **kwargs: dict,
    ) -> None:
        super().__init__(
            action=action,
            method=method,
            enctype=enctype,
            _main_container=_main_container,
            **kwargs,
        )
        self.readonly = _readonly
        self.scriptlinks: list[str] = []
        self.jscode: list[str] = []
        self.pyscode: list[str] = []

    def preprocess(self) -> None:
        for element in self.elements.values():
            if hasattr(element, "preprocess"):
                element.preprocess()

    async def async_preprocess(self) -> None:
        print("Starting async preprocessing of form elements...")
        for element in self.elements.values():
            print(f"Checking element: {element!r}")
            if hasattr(element, "async_preprocess"):
                print(f"Preprocessing async element: {element!r}")
                await element.async_preprocess()


class InlineInput(t.div):
    _tag = "div"

    def __init__(self, **kwargs):
        super().__init__(class_=get_css(self.__class__), **kwargs)


class BaseInput(t.Tag):

    _tag = "BaseInput"
    _type = "text"

    def __init__(
        self,
        *,
        input_provider: InputProvider | None = None,
        name: str | None = None,
        label: str | None = None,
        value: Any = None,
        update_dict: dict | None = None,
        placeholder: str = "",
        info: str = "",
        size: int = 3,
        offset: int = 2,
        extra_control: str = "",
        readonly: bool | None = None,  # if None, follow container
        input_style: str = "",
        popover: str = "",
        error: str = "",
        **kwargs: dict,
    ) -> None:
        if input_provider is not None:
            if not isinstance(input_provider, InputProvider):
                raise TypeError(
                    f"input_provider must implement InputProvider protocol, got {type(input_provider)}"
                )
        self.input_provider = input_provider
        self.label = label or name
        name = name or (input_provider.get_name() if input_provider else None)

        super().__init__(name=name, **kwargs)

        self.value = value
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

    # accessor

    def get_value(self) -> str | tuple[int | str, str] | bool | None:
        if self.update_dict is not None:
            val = self.update_dict.get(self.name, None)
            if val is not None:
                return val
        if self.input_provider is not None and self.value is None:
            return self.input_provider.get_value()

        if self.value is not None:
            return self.value

        raise RuntimeError("get_value() is None, needs to be recoded")

    def get_options(self) -> list[tuple[str, str]]:
        if self.options is not None:
            return self.options
        if self.input_provider is not None:
            return self.input_provider.get_options()

        return None

    def is_readonly(self) -> bool:
        if self.readonly is not None:
            return self.readonly
        return self.get_container().readonly

    def opts(self, **kwargs: Any) -> Self:
        """
        opts() method will not call the parent class as this is
        a composite tag
        """

        self.size = kwargs.pop("size", self.size)
        self.offset = kwargs.pop("offset", self.offset)
        self.error = kwargs.pop("error", self.error)
        self.info = kwargs.pop("info", self.info)

        if any(kwargs):
            raise ValueError(f"Unprocessed options: {', '.join(kwargs.keys())}")

        return self

    # CSS classes and styles

    def class_value(self) -> str:
        classes = ["col-sm-2", "col-form-label"]
        return " ".join(classes)

    def class_value(self, size=None):
        col = self.size if size is None else size
        col = col or 12
        return f"col-12 col-md-{col} ps-md-2 align-self-start"

    def class_label(self):
        return f"col-md-{self.offset} col-form-label text-end align-self-start pt-2 ps-1 pe-0"

    def class_input(self):
        base = "form-control ps-2 pe-2"
        return base + (" is-invalid" if self.error else "")

    def class_div(self):
        return "mb-3"

    def style(self):
        return self.input_style  # or "width:100%"

    # additional text elements

    def error_text(self):
        if not self.error:
            return ""
        return t.span(class_="invalid-feedback")[self.error]

    def info_text(self):
        if not self.info:
            return ""
        if self.info.startswith("popup:"):
            url = escape(self.info[6:])
            return t.div(class_="col-auto d-flex align-items-center")[
                t.a(
                    class_="js-newWindow text-decoration-none",
                    data_popup="width=400,height=200,scrollbars=yes",
                    href=url,
                    aria_label="More info",
                )[t.span(class_="fw-semibold")["?"]]
            ].r()

        return t.small(class_="form-text text-muted")[escape(self.info)].r()

    def render_label(self) -> Markup | t.Tag:

        pop_title = pop_content = ""
        if self.popover:
            pop_title = self.label or ""
            pop_content = self.popover

        return (
            t.label(
                class_=self.class_label(),
                for_=self.name,
                data_bs_toggle="popover",
                data_bs_placement="top",
                data_bs_title=pop_title,
                data_bs_content=pop_content,
            )[escape(self.label)]
            if self.label is not None
            else ""
        )

    def render_input(self, value=None) -> Markup | t.Tag:
        if self.error:
            input_class = "form-control is-invalid"
        else:
            input_class = "form-control"

        readonly = self.is_readonly()

        # food for thought: <input type="text" readonly class="form-control-plaintext">
        # will render a readonly input as plain text (no boxes nor decorations)

        return t.div(class_=self.class_value())[
            t.input(
                type=self._type,
                id=self.id,
                name=self.name,
                value=escape(value if value is not None else self.get_value()),
                class_=self.class_input(),
                placeholder=self.placeholder,
                style=self.style(),
                readonly=readonly,
            ),
            self.error_text(),
        ]

    def r(self) -> Markup:

        elements = t.fragment()[
            self.render_label(),
            self.render_input(),
            self.info_text(),
        ]

        return self.div_wrap(elements.r())

    def div_wrap(self, markup) -> Markup:
        if not isinstance(self.container, InlineInput):
            return t.div(class_="row g-3 align-items-center mb-2")[markup].r()
        return markup


class HiddenInput(BaseInput):
    _type = "hidden"

    def r(self) -> Markup:
        return t.input(
            type=self._type, id=self.id, name=self.name, value=escape(self.get_value())
        ).r()


class TextInput(BaseInput):
    _type = "text"


class PasswordInput(BaseInput):
    _type = "password"


class EmailInput(BaseInput):
    _type = "email"


class TextAreaInput(BaseInput):
    _tag = "textarea"

    def render_input(self, value=None) -> Markup | t.Tag:
        readonly = self.is_readonly()

        return t.div(class_=self.class_value())[
            t.textarea(
                id=self.id,
                name=self.name,
                class_=self.class_input(),
                placeholder=self.placeholder,
                style=self.style(),
                readonly=readonly,
            )[escape(value if value is not None else self.get_value())],
            self.error_text(),
        ]


class CheckboxInput(BaseInput):
    _type = "checkbox"

    def get_value(self) -> bool:
        val = super().get_value()
        if isinstance(val, str):
            return val.lower() in ("true", "1", "yes", "on")
        return bool(val)

    def render_input(self, value=None) -> Markup | t.Tag:
        readonly = self.is_readonly()

        if readonly:
            if self.get_value():
                return t.div(class_=self.class_value())[
                    t.span(class_="badge text-bg-success border border-success")[
                        t.i(class_="bi bi-check-lg me-1"), self.label
                    ]
                ]
            return t.div(class_=self.class_value())[
                t.span(
                    class_="badge bg-secondary-subtle text-body-tertiary border border-secondary-subtle"
                )[
                    t.i(class_="bi bi-x-circle text-muted me-1", title="Disabled"),
                    self.label,
                ]
            ]

        checked = True if self.get_value() else None
        return t.div(class_=self.class_value())[
            t.div(class_="form-check form-check-inline")[
                t.input(type="hidden", name=self.name, _register=False, value="off"),
                t.input(
                    type=self._type,
                    id=self.id,
                    name=self.name,
                    value="on",
                    checked=checked,
                    readonly=False,
                    class_="form-check-input",
                ),
                t.label(class_="form-check-label", for_=self.name)[escape(self.label)],
            ]
        ]

    def render_label(self) -> Markup | t.Tag:

        if self.is_readonly():
            # label is rendered as part of the badge in render_input when readonly
            return Markup("")

        return t.label(class_="form-check-label", for_=self.name)[escape(self.label)]

    def r(self) -> Markup:

        # checkbox is a special case where the label is rendered after the input,
        # hence label is not rendered in render_label() but in render_input()

        elements = self.render_input()
        return elements.r()

        return self.div_wrap(elements.r())


class CheckboxGroupInput(BaseInput):
    _type = None  # type is determined by individual checkboxes

    # this class renders a group of checkboxes, each with its own label and value,
    # but all sharing the same name (as a list)

    def render_label(self):
        return super().render_label()

    def render_input(self, value=None) -> Markup | t.Tag:
        return t.fragment()[
            *[item.r() for item in self.contents if isinstance(item, CheckboxInput)]
        ]


class RadioInput(BaseInput):
    _type = "radio"

    def render_input(self, value=None) -> Markup | t.Tag:
        readonly = self.is_readonly()

        if readonly:
            selected_option = next(
                (text for val, text in self.options if val == value), None
            )
            return t.div(class_=self.class_value())[
                t.span(class_="badge text-bg-primary border border-primary")[
                    t.i(class_="bi bi-check-lg me-1"), escape(selected_option or value)
                ]
            ]
        return t.div(class_=self.class_value())[
            *[
                t.div(class_="form-check form-check-inline")[
                    t.input(
                        type=self._type,
                        id=f"{self.id}_{val}",
                        name=self.name,
                        value=val,
                        checked=(val == value),
                        readonly=False,
                        class_="form-check-input",
                    ),
                    t.label(class_="form-check-label", for_=f"{self.id}_{val}")[
                        escape(text)
                    ],
                ]
                for val, text in self.options
            ]
        ]


class SelectInput(BaseInput):

    def __init__(
        self,
        options: list[tuple[str, str]] | None = None,
        option_callback: Callable[[], Awaitable[list[tuple[str, str]]]] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.options = options
        self.option_callback = option_callback

    def class_input(self):
        base = "form-select ps-2 pe-2"
        return base + (" is-invalid" if self.error else "")

    def render_input(self) -> Markup | t.Tag:

        readonly = self.is_readonly()
        value = self.get_value()

        if value is None:
            value = ("", "")
        elif isinstance(value, str):
            value = (value, value)

        if readonly:
            return super().render_input(value=value[1])

        options = self.get_options()

        if not any(options):
            raise RuntimeError(
                "SelectInput requires calling to async_preprocess to populate options"
            )

        select_tag = t.select(
            id=self.id,
            name=self.name,
            class_=self.class_input(),
            style=self.style(),
            disabled=readonly,
        )[
            [
                t.option(value=val, selected=(val == value[0]))[text]
                for val, text in options
            ]
        ]

        return t.div(class_=self.class_value())[select_tag, self.error_text()]

    async def async_preprocess(self) -> None:
        if self.options is None and self.option_callback is not None:
            print("Fetching options for SelectInput...")
            self.options = await self.option_callback()
            if self.input_provider and not self.input_provider.is_required():
                self.options = [("", "")] + self.options


class EnumKeyInput(SelectInput):
    _type = "text"

    async def async_preprocess(self) -> None:
        # do nothing, options are set in render_input() without the need to do async call
        pass

    def get_options(self) -> list[tuple[str, str]]:

        options = super().get_options()
        if not any(options):
            raise RuntimeError(
                "EnumKeyInput requires options to be set, either through input_provider or directly"
            )
        return options


## bootstrap 5.3 classes

bootstrap_5_3_css_set = {
    InlineInput: "row g-3 align-items-center mb-2",
}

set_css_set(bootstrap_5_3_css_set)

# EOF
