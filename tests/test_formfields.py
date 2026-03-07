# SPDX-License-Identifier: MIT

"""Comprehensive unit tests for tagato.formfields module."""

from __future__ import annotations

import pytest
from markupsafe import Markup, escape

from tagato import tags as t
from tagato.formfields import (
    CSSTheme,
    Bootstrap53Theme,
    InputProvider,
    HTMLForm,
    InlineInput,
    BaseInput,
    HiddenInput,
    TextInput,
    PasswordInput,
    EmailInput,
    TextAreaInput,
    CheckboxInput,
    CheckboxGroupInput,
    RadioInput,
    SelectInput,
    set_theme,
    get_theme,
    fieldset,
    legend,
)


# =====================================================================
# Fixtures
# =====================================================================


@pytest.fixture(autouse=True)
def _reset_theme():
    """Ensure Bootstrap53Theme is active for every test."""
    set_theme(Bootstrap53Theme())
    yield


class FakeProvider:
    """Minimal InputProvider implementation for testing."""

    def __init__(
        self,
        *,
        name: str = "field1",
        value: str | tuple | bool | None = "default",
        options: list[tuple[str, str]] | None = None,
        required: bool = False,
    ):
        self._name = name
        self._value = value
        self._options = options or []
        self._required = required

    def get_value(self) -> str | tuple[int | str, str] | bool | None:
        return self._value

    def get_options(self) -> list[tuple[str, str]]:
        return self._options

    def is_required(self) -> bool:
        return self._required

    def get_name(self) -> str:
        return self._name


# =====================================================================
# InputProvider protocol
# =====================================================================


class TestInputProviderProtocol:
    def test_fake_provider_satisfies_protocol(self):
        provider = FakeProvider()
        assert isinstance(provider, InputProvider)

    def test_non_provider_fails(self):
        class NotAProvider:
            pass

        assert not isinstance(NotAProvider(), InputProvider)


# =====================================================================
# CSSTheme base class
# =====================================================================


class TestCSSThemeBase:
    def test_defaults_return_empty_strings(self):
        theme = CSSTheme()
        assert theme.form_row() == ""
        assert theme.inline_input_wrapper() == ""
        assert theme.form_div() == ""
        assert theme.label_class(2) == ""
        assert theme.input_class() == ""
        assert theme.select_class() == ""
        assert theme.textarea_class() == ""
        assert theme.value_col(3) == ""
        assert theme.check_wrapper() == ""
        assert theme.check_input_class() == ""
        assert theme.check_label_class() == ""

    def test_error_feedback_empty(self):
        theme = CSSTheme()
        assert theme.error_feedback("") == ""

    def test_error_feedback_nonempty(self):
        theme = CSSTheme()
        result = theme.error_feedback("Error!")
        assert "Error!" in str(result)

    def test_info_text_empty(self):
        theme = CSSTheme()
        assert theme.info_text("") == ""

    def test_info_text_nonempty(self):
        theme = CSSTheme()
        result = theme.info_text("help")
        assert "help" in str(result)

    def test_info_popup(self):
        theme = CSSTheme()
        result = theme.info_popup("/help")
        assert "?" in str(result.__html__())

    def test_badge_checked(self):
        theme = CSSTheme()
        result = theme.badge_checked("Yes")
        assert "Yes" in str(result.__html__())

    def test_badge_unchecked(self):
        theme = CSSTheme()
        result = theme.badge_unchecked("No")
        assert "No" in str(result.__html__())

    def test_badge_selected(self):
        theme = CSSTheme()
        result = theme.badge_selected("Opt")
        assert "Opt" in str(result.__html__())

    def test_popover_attrs_empty(self):
        theme = CSSTheme()
        assert theme.popover_attrs("Title", "Content") == {}

    def test_check_group_label_class_defaults(self):
        theme = CSSTheme()
        assert theme.check_group_label_class(2) == theme.label_class(2)

    def test_check_group_value_col_defaults(self):
        theme = CSSTheme()
        assert theme.check_group_value_col(3) == theme.value_col(3)


# =====================================================================
# Bootstrap53Theme
# =====================================================================


class TestBootstrap53Theme:
    def setup_method(self):
        self.theme = Bootstrap53Theme()

    def test_form_row(self):
        assert "row" in self.theme.form_row()

    def test_label_class(self):
        cls = self.theme.label_class(3)
        assert "col-md-3" in cls
        assert "col-form-label" in cls

    def test_input_class_no_error(self):
        cls = self.theme.input_class()
        assert "form-control" in cls
        assert "is-invalid" not in cls

    def test_input_class_with_error(self):
        cls = self.theme.input_class(error=True)
        assert "is-invalid" in cls

    def test_select_class_no_error(self):
        cls = self.theme.select_class()
        assert "form-select" in cls
        assert "is-invalid" not in cls

    def test_select_class_with_error(self):
        cls = self.theme.select_class(error=True)
        assert "is-invalid" in cls

    def test_textarea_class(self):
        assert self.theme.textarea_class() == self.theme.input_class()

    def test_value_col(self):
        cls = self.theme.value_col(6)
        assert "col-md-6" in cls

    def test_value_col_zero_default(self):
        cls = self.theme.value_col(0)
        assert "col-md-12" in cls

    def test_check_wrapper(self):
        assert "form-check" in self.theme.check_wrapper()

    def test_check_input_class(self):
        assert "form-check-input" in self.theme.check_input_class()

    def test_check_label_class(self):
        assert "form-check-label" in self.theme.check_label_class()

    def test_error_feedback_empty(self):
        assert self.theme.error_feedback("") == ""

    def test_error_feedback_rendered(self):
        result = self.theme.error_feedback("bad!")
        html_str = str(result.__html__())
        assert "invalid-feedback" in html_str
        assert "bad!" in html_str

    def test_info_text_empty(self):
        assert self.theme.info_text("") == ""

    def test_info_text_rendered(self):
        result = self.theme.info_text("help text")
        html_str = str(result.__html__())
        assert "form-text" in html_str
        assert "help text" in html_str

    def test_info_popup(self):
        result = self.theme.info_popup("/help")
        html_str = str(result.__html__())
        assert "js-newWindow" in html_str
        assert "/help" in html_str

    def test_badge_checked(self):
        result = self.theme.badge_checked("Active")
        html_str = str(result.__html__())
        assert "text-bg-success" in html_str
        assert "Active" in html_str

    def test_badge_unchecked(self):
        result = self.theme.badge_unchecked("Inactive")
        html_str = str(result.__html__())
        assert "bg-secondary-subtle" in html_str
        assert "Inactive" in html_str

    def test_badge_selected(self):
        result = self.theme.badge_selected("Option A")
        html_str = str(result.__html__())
        assert "text-bg-primary" in html_str
        assert "Option A" in html_str

    def test_popover_attrs(self):
        attrs = self.theme.popover_attrs("Title", "Content")
        assert attrs["data_bs_toggle"] == "popover"
        assert attrs["data_bs_title"] == "Title"
        assert attrs["data_bs_content"] == "Content"

    def test_check_group_value_col(self):
        cls = self.theme.check_group_value_col(6)
        assert "pt-2" in cls
        assert "col-md-6" in cls


# =====================================================================
# Theme management
# =====================================================================


class TestThemeManagement:
    def test_get_theme_returns_bootstrap(self):
        theme = get_theme()
        assert isinstance(theme, Bootstrap53Theme)

    def test_set_custom_theme(self):
        custom = CSSTheme()
        set_theme(custom)
        assert get_theme() is custom

    def test_no_theme_raises(self):
        from tagato import formfields

        old = formfields._current_theme
        formfields._current_theme = None
        try:
            with pytest.raises(RuntimeError, match="No CSS theme"):
                get_theme()
        finally:
            formfields._current_theme = old


# =====================================================================
# HTMLForm
# =====================================================================


class TestHTMLForm:
    def test_renders_form_tag(self):
        f = HTMLForm()
        result = str(f.r())
        assert "<form" in result
        assert "</form>" in result

    def test_default_attributes(self):
        f = HTMLForm()
        result = str(f.r())
        assert 'method="post"' in result
        assert 'action=""' in result

    def test_custom_action_method(self):
        f = HTMLForm(action="/submit", method="get")
        result = str(f.r())
        assert 'action="/submit"' in result
        assert 'method="get"' in result

    def test_enctype(self):
        f = HTMLForm(enctype="multipart/form-data")
        result = str(f.r())
        assert 'enctype="multipart/form-data"' in result

    def test_readonly_flag(self):
        f = HTMLForm(_readonly=True)
        assert f.readonly is True

    def test_form_has_script_slots(self):
        f = HTMLForm()
        assert f.scriptlinks == []
        assert f.jscode == []
        assert f.pyscode == []

    def test_tag_property(self):
        f = HTMLForm()
        assert f._tag == "form"

    def test_is_main_container(self):
        f = HTMLForm()
        assert f._main_container is True

    def test_form_with_children(self):
        f = HTMLForm()
        f.add(t.div["inner"])
        result = str(f.r())
        assert "<div>inner</div>" in result


# =====================================================================
# InlineInput
# =====================================================================


class TestInlineInput:
    def test_renders_as_tag(self):
        ii = InlineInput()
        result = str(ii.r())
        assert "row g-3" in result

    def test_has_theme_class(self):
        theme = get_theme()
        ii = InlineInput()
        assert ii.class_ == theme.inline_input_wrapper()


# =====================================================================
# BaseInput
# =====================================================================


class TestBaseInput:
    def test_init_defaults(self):
        inp = TextInput(name="test")
        assert inp.name == "test"
        assert inp.id == "test"
        assert inp.label == "test"
        assert inp.value is None
        assert inp.placeholder == ""
        assert inp.error == ""

    def test_label_overrides_name(self):
        inp = TextInput(name="field", label="Field Label")
        assert inp.label == "Field Label"

    def test_name_from_provider(self):
        provider = FakeProvider(name="prov_name")
        inp = TextInput(input_provider=provider)
        assert inp.name == "prov_name"

    def test_invalid_provider_raises(self):
        with pytest.raises(TypeError, match="InputProvider protocol"):
            TextInput(input_provider="not a provider")  # type: ignore[arg-type]


class TestBaseInputGetValue:
    def test_explicit_value(self):
        inp = TextInput(name="f", value="explicit")
        assert inp.get_value() == "explicit"

    def test_fallback_empty_string(self):
        inp = TextInput(name="f")
        assert inp.get_value() == ""

    def test_provider_value(self):
        provider = FakeProvider(value="from_provider")
        inp = TextInput(input_provider=provider)
        assert inp.get_value() == "from_provider"

    def test_update_dict_overrides(self):
        provider = FakeProvider(value="from_provider")
        inp = TextInput(
            input_provider=provider,
            update_dict={"field1": "from_dict"},
        )
        assert inp.get_value() == "from_dict"

    def test_explicit_value_beats_provider(self):
        provider = FakeProvider(value="from_provider")
        inp = TextInput(input_provider=provider, value="explicit")
        assert inp.get_value() == "explicit"


class TestBaseInputGetOptions:
    def test_explicit_options(self):
        inp = TextInput(name="f", options=[("a", "A"), ("b", "B")])
        assert inp.get_options() == [("a", "A"), ("b", "B")]

    def test_provider_options(self):
        provider = FakeProvider(options=[("x", "X")])
        inp = TextInput(input_provider=provider)
        assert inp.get_options() == [("x", "X")]

    def test_no_options(self):
        inp = TextInput(name="f")
        assert inp.get_options() == []


class TestBaseInputReadonly:
    def test_default_not_readonly(self):
        inp = TextInput(name="f")
        assert not inp.is_readonly()

    def test_explicit_readonly(self):
        inp = TextInput(name="f", readonly=True)
        assert inp.is_readonly() is True

    def test_inherits_from_container(self):
        form = HTMLForm(_readonly=True)
        inp = TextInput(name="f")
        form.add(inp)
        assert inp.is_readonly() is True

    def test_field_override_beats_container(self):
        form = HTMLForm(_readonly=True)
        inp = TextInput(name="f", readonly=False)
        form.add(inp)
        assert inp.is_readonly() is False


class TestBaseInputOpts:
    def test_set_size_offset(self):
        inp = TextInput(name="f")
        inp.opts(size=6, offset=4)
        assert inp.size == 6
        assert inp.offset == 4

    def test_set_error_info(self):
        inp = TextInput(name="f")
        inp.opts(error="bad", info="help")
        assert inp.error == "bad"
        assert inp.info == "help"

    def test_set_options(self):
        inp = TextInput(name="f")
        inp.opts(options=[("a", "A")])
        assert inp.options == [("a", "A")]

    def test_unknown_option_raises(self):
        inp = TextInput(name="f")
        with pytest.raises(ValueError, match="Unprocessed"):
            inp.opts(unknown="bad")


# =====================================================================
# Rendering individual inputs
# =====================================================================


class TestBaseInputRenderLabel:
    def test_label_rendered(self):
        inp = TextInput(name="f", label="My Field")
        result = str(inp.render_label().__html__())
        assert "My Field" in result
        assert "<label" in result
        assert 'for="f"' in result

    def test_no_label(self):
        inp = TextInput(name="f", label=None)
        # label defaults to name when not set explicitly via __init__
        # We need to force label to None after init
        inp.label = None
        result = inp.render_label()
        assert result == ""

    def test_label_with_popover(self):
        inp = TextInput(name="f", label="Pop", popover="Info here")
        result = str(inp.render_label().__html__())
        assert "data-bs-toggle" in result
        assert "popover" in result


class TestBaseInputRenderInfo:
    def test_no_info(self):
        inp = TextInput(name="f")
        assert inp.render_info() == ""

    def test_info_text(self):
        inp = TextInput(name="f", info="helpful")
        result = inp.render_info()
        assert "helpful" in str(result.__html__())

    def test_info_popup(self):
        inp = TextInput(name="f", info="popup:/details")
        result = inp.render_info()
        assert "/details" in str(result.__html__())


# =====================================================================
# HiddenInput
# =====================================================================


class TestHiddenInput:
    def test_renders_hidden_input(self):
        inp = HiddenInput(name="secret", value="42")
        result = str(inp.r())
        assert 'type="hidden"' in result
        assert 'name="secret"' in result
        assert 'value="42"' in result

    def test_no_label_or_wrapper(self):
        inp = HiddenInput(name="s", value="x")
        result = str(inp.r())
        assert "<label" not in result
        assert "form-row" not in result


# =====================================================================
# TextInput
# =====================================================================


class TestTextInput:
    def test_renders_text_input(self):
        inp = TextInput(name="username", value="john")
        result = str(inp.r())
        assert 'type="text"' in result
        assert 'name="username"' in result
        assert 'value="john"' in result

    def test_has_label(self):
        inp = TextInput(name="email", label="Email Address")
        result = str(inp.r())
        assert "Email Address" in result

    def test_with_error(self):
        inp = TextInput(name="f", error="Required")
        result = str(inp.r())
        assert "is-invalid" in result
        assert "Required" in result

    def test_with_placeholder(self):
        inp = TextInput(name="f", placeholder="Enter value")
        result = str(inp.r())
        assert 'placeholder="Enter value"' in result


# =====================================================================
# PasswordInput
# =====================================================================


class TestPasswordInput:
    def test_renders_password(self):
        inp = PasswordInput(name="pw")
        result = str(inp.r())
        assert 'type="password"' in result


# =====================================================================
# EmailInput
# =====================================================================


class TestEmailInput:
    def test_renders_email(self):
        inp = EmailInput(name="em")
        result = str(inp.r())
        assert 'type="email"' in result


# =====================================================================
# TextAreaInput
# =====================================================================


class TestTextAreaInput:
    def test_renders_textarea(self):
        inp = TextAreaInput(name="bio", value="Hello world")
        result = str(inp.r())
        assert "<textarea" in result
        assert "Hello world" in result
        assert "</textarea>" in result

    def test_textarea_with_error(self):
        inp = TextAreaInput(name="bio", error="Too short")
        result = str(inp.r())
        assert "is-invalid" in result
        assert "Too short" in result


# =====================================================================
# CheckboxInput
# =====================================================================


class TestCheckboxInput:
    def test_renders_checkbox(self):
        inp = CheckboxInput(name="agree", label="I agree", value=True)
        result = str(inp.r())
        assert 'type="checkbox"' in result
        assert "I agree" in result

    def test_checked_when_true(self):
        inp = CheckboxInput(name="agree", label="OK", value=True)
        result = str(inp.r())
        assert "checked" in result

    def test_unchecked_when_false(self):
        inp = CheckboxInput(name="agree", label="OK", value=False)
        result = str(inp.r())
        # The hidden fallback always appears; the main checkbox should not
        # have `checked`
        assert 'value="on"' in result

    def test_get_value_string_true(self):
        inp = CheckboxInput(name="f", value="true")
        assert inp.get_value() is True

    def test_get_value_string_false(self):
        inp = CheckboxInput(name="f", value="no")
        assert inp.get_value() is False

    def test_get_value_string_yes(self):
        inp = CheckboxInput(name="f", value="yes")
        assert inp.get_value() is True

    def test_get_value_bool(self):
        inp = CheckboxInput(name="f", value=True)
        assert inp.get_value() is True

    def test_hidden_fallback_input(self):
        """Unchecked submission sends 'off' via a hidden input."""
        inp = CheckboxInput(name="toggle", label="Toggle")
        result = str(inp.r())
        assert 'type="hidden"' in result
        assert 'value="off"' in result

    def test_readonly_badge_checked(self):
        form = HTMLForm(_readonly=True)
        inp = CheckboxInput(name="check", label="Check", value=True)
        form.add(inp)
        result = str(inp.r())
        assert "text-bg-success" in result
        assert "Check" in result

    def test_readonly_badge_unchecked(self):
        form = HTMLForm(_readonly=True)
        inp = CheckboxInput(name="check", label="Check", value=False)
        form.add(inp)
        result = str(inp.r())
        assert "bg-secondary-subtle" in result


# =====================================================================
# CheckboxGroupInput
# =====================================================================


class TestCheckboxGroupInput:
    def test_renders_group(self):
        group = CheckboxGroupInput(name="colors", label="Colors")
        group.add(
            CheckboxInput(name="red", label="Red", value=True),
            CheckboxInput(name="blue", label="Blue", value=False),
        )
        result = str(group.r())
        assert "Colors" in result
        assert "Red" in result
        assert "Blue" in result

    def test_uses_group_label_class(self):
        group = CheckboxGroupInput(name="g", label="Group")
        result = str(group.render_label().__html__())
        theme = get_theme()
        assert theme.check_group_label_class(group.offset) in result


# =====================================================================
# RadioInput
# =====================================================================


class TestRadioInput:
    def test_renders_radio_options(self):
        inp = RadioInput(
            name="color",
            label="Color",
            value="red",
            options=[("red", "Red"), ("blue", "Blue"), ("green", "Green")],
        )
        result = str(inp.r())
        assert 'type="radio"' in result
        assert "Red" in result
        assert "Blue" in result
        assert "Green" in result

    def test_selected_option_checked(self):
        inp = RadioInput(
            name="size",
            value="m",
            options=[("s", "Small"), ("m", "Medium"), ("l", "Large")],
        )
        result = str(inp.r())
        # The "m" option should have checked
        assert "checked" in result

    def test_readonly_shows_badge(self):
        form = HTMLForm(_readonly=True)
        inp = RadioInput(
            name="opt",
            label="Option",
            value="b",
            options=[("a", "Alpha"), ("b", "Beta")],
        )
        form.add(inp)
        result = str(inp.r())
        assert "text-bg-primary" in result
        assert "Beta" in result

    def test_readonly_no_matching_option(self):
        form = HTMLForm(_readonly=True)
        inp = RadioInput(
            name="opt",
            label="Option",
            value="missing",
            options=[("a", "Alpha")],
        )
        form.add(inp)
        result = str(inp.r())
        assert "missing" in result


# =====================================================================
# SelectInput
# =====================================================================


class TestSelectInput:
    def test_renders_select(self):
        inp = SelectInput(
            name="country",
            label="Country",
            value="us",
            options=[("us", "USA"), ("uk", "UK"), ("de", "Germany")],
        )
        result = str(inp.r())
        assert "<select" in result
        assert "</select>" in result
        assert "<option" in result
        assert "USA" in result
        assert "Germany" in result

    def test_selected_option(self):
        inp = SelectInput(
            name="lang",
            value="py",
            options=[("py", "Python"), ("js", "JS")],
        )
        result = str(inp.r())
        assert "selected" in result

    def test_no_options_raises(self):
        inp = SelectInput(name="empty")
        with pytest.raises(RuntimeError, match="no options"):
            inp.r()

    def test_tuple_value(self):
        inp = SelectInput(
            name="sel",
            value=("key", "Display"),
            options=[("key", "Display"), ("other", "Other")],
        )
        result = str(inp.r())
        assert "selected" in result

    def test_none_value(self):
        inp = SelectInput(
            name="sel",
            value=None,
            options=[("a", "Alpha")],
        )
        result = str(inp.r())
        assert "<select" in result

    def test_readonly_renders_text(self):
        form = HTMLForm(_readonly=True)
        inp = SelectInput(
            name="sel",
            label="Select",
            value=("us", "USA"),
            options=[("us", "USA")],
        )
        form.add(inp)
        result = str(inp.r())
        # Readonly renders as a plain text input showing display text
        assert 'type="text"' in result
        assert "USA" in result

    def test_with_error(self):
        inp = SelectInput(
            name="sel",
            error="Choose one",
            options=[("a", "A")],
        )
        result = str(inp.r())
        assert "is-invalid" in result
        assert "Choose one" in result

    def test_provider_options(self):
        provider = FakeProvider(
            name="sel",
            value="b",
            options=[("a", "A"), ("b", "B")],
        )
        inp = SelectInput(input_provider=provider)
        result = str(inp.r())
        assert "<select" in result
        assert "B" in result


# =====================================================================
# InlineInput wrapping
# =====================================================================


class TestInlineInputWrapping:
    def test_no_row_wrapper_inside_inline(self):
        """Inside an InlineInput, BaseInput should skip the row wrapper."""
        ii = InlineInput()
        inp = TextInput(name="f", value="v")
        ii.add(inp)
        result = str(inp.r())
        # Should NOT contain the form-row wrapper div
        assert "row g-3" not in result


# =====================================================================
# Re-exports
# =====================================================================


class TestReExports:
    def test_fieldset_is_tag(self):
        assert issubclass(fieldset, t.pairedtag)

    def test_legend_is_tag(self):
        assert issubclass(legend, t.pairedtag)


# =====================================================================
# Integration
# =====================================================================


class TestFormIntegration:
    def test_full_form_rendering(self):
        form = HTMLForm(action="/submit")
        form.add(
            HiddenInput(name="csrf", value="token123"),
            TextInput(name="username", label="Username", value=""),
            PasswordInput(name="password", label="Password"),
            SelectInput(
                name="role",
                label="Role",
                value="user",
                options=[("admin", "Admin"), ("user", "User")],
            ),
            CheckboxInput(name="agree", label="I agree", value=False),
        )
        result = str(form.r())
        assert "<form" in result
        assert 'action="/submit"' in result
        assert 'type="hidden"' in result
        assert "Username" in result
        assert "Password" in result
        assert "<select" in result
        assert "I agree" in result
        assert "</form>" in result

    def test_readonly_form(self):
        form = HTMLForm(_readonly=True)
        form.add(
            TextInput(name="name", label="Name", value="Alice"),
            CheckboxInput(name="active", label="Active", value=True),
        )
        result = str(form.r())
        assert "readonly" in result
        assert "text-bg-success" in result

    def test_form_with_provider(self):
        provider = FakeProvider(
            name="email",
            value="test@example.com",
        )
        form = HTMLForm()
        form.add(TextInput(input_provider=provider, label="Email"))
        result = str(form.r())
        assert "test@example.com" in result
        assert "Email" in result
