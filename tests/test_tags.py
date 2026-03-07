# SPDX-License-Identifier: MIT

"""Comprehensive unit tests for tagato.tags module."""

from __future__ import annotations

import pytest
from markupsafe import Markup

from tagato.tags import (
    Tag,
    fragment,
    singletag,
    pairedtag,
    literal,
    # Paired tags
    div,
    span,
    p,
    a,
    b,
    h1,
    h2,
    ul,
    li,
    ol,
    html,
    body,
    head,
    table,
    thead,
    tbody,
    tr,
    td,
    th,
    form,
    label,
    button,
    textarea,
    select,
    option,
    nav,
    footer,
    header,
    section,
    article,
    fieldset,
    legend,
    pre,
    code,
    small,
    strong,
    # Single tags
    img,
    input,
    br,
    hr,
    meta,
    link,
)


# =====================================================================
# Helper / literal
# =====================================================================


class TestLiteral:
    def test_literal_is_markup(self):
        assert literal is Markup

    def test_literal_prevents_escaping(self):
        raw = literal("<b>bold</b>")
        assert str(raw) == "<b>bold</b>"


# =====================================================================
# _SelfInstantiating metaclass
# =====================================================================


class TestSelfInstantiatingMetaclass:
    """Tag classes can be used without calling the constructor."""

    def test_class_getitem_creates_instance(self):
        result = div["hello"]
        assert isinstance(result, div)
        assert "<div>hello</div>" in str(result)

    def test_class_str_creates_instance(self):
        result = str(div)
        assert result == "<div></div>"

    def test_class_iadd(self):
        result = div
        result += "hello"
        assert isinstance(result, div)
        assert "hello" in str(result)


# =====================================================================
# Tag base class
# =====================================================================


class TestTagInit:
    def test_basic_init(self):
        tag = div()
        assert tag.id is None
        assert tag.name is None
        assert tag.class_ is None
        assert tag.contents == []
        assert tag.elements == {}

    def test_id_from_name(self):
        tag = div(name="myname")
        assert tag.name == "myname"
        assert tag.id == "myname"

    def test_explicit_id_and_name(self):
        tag = div(id="myid", name="myname")
        assert tag.id == "myid"
        assert tag.name == "myname"

    def test_whitespace_stripping(self):
        tag = div(id="  myid  ", name="  myname  ", class_="  cls  ")
        assert tag.id == "myid"
        assert tag.name == "myname"
        assert tag.class_ == "cls"

    def test_class_attribute(self):
        tag = div(class_="container")
        assert tag.class_ == "container"

    def test_enabled_default(self):
        tag = div()
        assert tag._enabled is True

    def test_disabled(self):
        tag = div(_enabled=False)
        assert tag._enabled is False


class TestTagRepr:
    def test_repr_empty(self):
        tag = div()
        assert repr(tag) == "div(name='', id='', class='')"

    def test_repr_with_attrs(self):
        tag = div(id="x", name="y", class_="z")
        assert repr(tag) == "div(name='y', id='x', class='z')"


# =====================================================================
# Content manipulation
# =====================================================================


class TestTagAdd:
    def test_add_string(self):
        tag = div()
        tag.add("hello")
        assert len(tag.contents) == 1
        assert tag.contents[0] == "hello"

    def test_add_tag(self):
        child = span()
        parent = div()
        parent.add(child)
        assert child in parent.contents
        assert child.container is parent

    def test_add_tag_class_without_instantiation(self):
        """Passing a Tag class (not instance) auto-instantiates it."""
        parent = div()
        parent.add(br)
        assert len(parent.contents) == 1
        assert isinstance(parent.contents[0], br)

    def test_add_returns_self(self):
        tag = div()
        result = tag.add("hello")
        assert result is tag

    def test_chained_add(self):
        tag = div()
        tag.add("a").add("b")
        assert len(tag.contents) == 2

    def test_add_multiple(self):
        tag = div()
        tag.add("one", "two", "three")
        assert len(tag.contents) == 3

    def test_add_with_tag_protocol(self):
        """Objects with __tag__ method are adapted."""

        class Adaptable:
            def __tag__(self):
                return span()

        parent = div()
        parent.add(Adaptable())
        assert len(parent.contents) == 1
        assert isinstance(parent.contents[0], span)


class TestTagIAdd:
    def test_iadd(self):
        tag = div()
        tag += "hello"
        assert "hello" in tag.contents

    def test_iadd_tag(self):
        tag = div()
        child = span()
        tag += child
        assert child in tag.contents


class TestTagGetItem:
    def test_getitem_single(self):
        tag = div["hello"]
        assert "hello" in tag.contents

    def test_getitem_tuple(self):
        tag = div["a", "b"]
        assert len(tag.contents) == 2

    def test_getitem_list(self):
        tag = div[["a", "b", "c"]]
        assert len(tag.contents) == 3

    def test_getitem_returns_self(self):
        tag = div()
        result = tag["hello"]
        assert result is tag

    def test_nested_tags(self):
        doc = div[span["inner"]]
        html_str = str(doc.__html__())
        assert "<div><span>inner</span></div>" == html_str


class TestTagInsert:
    def test_insert_at_beginning(self):
        tag = div()
        tag.add("second")
        tag.insert(0, "first")
        assert tag.contents[0] == "first"
        assert tag.contents[1] == "second"

    def test_insert_at_middle(self):
        tag = div()
        tag.add("first", "third")
        tag.insert(1, "second")
        assert tag.contents == ["first", "second", "third"]

    def test_insert_tag_class(self):
        tag = div()
        tag.insert(0, br)
        assert isinstance(tag.contents[0], br)

    def test_insert_tag_protocol(self):
        class Adaptable:
            def __tag__(self):
                return span()

        tag = div()
        tag.insert(0, Adaptable())
        assert isinstance(tag.contents[0], span)

    def test_insert_returns_self(self):
        tag = div()
        result = tag.insert(0, "hello")
        assert result is tag


class TestTagReplace:
    def test_replace_contents(self):
        tag = div()
        tag.add("old content")
        tag.replace("new content")
        assert len(tag.contents) == 1
        assert tag.contents[0] == "new content"

    def test_replace_unregisters_old_elements(self):
        parent = div()
        child = span(id="child1")
        parent.add(child)
        assert "child1" in parent.elements
        parent.replace("new")
        assert "child1" not in parent.elements

    def test_replace_returns_self(self):
        tag = div()
        tag.add("old")
        assert tag.replace("new") is tag


class TestNonregAdd:
    def test_nonreg_add(self):
        parent = div()
        child = span(id="unreg")
        parent.nonreg_add(child)
        assert child in parent.contents
        assert "unreg" not in parent.elements

    def test_nonreg_add_auto_instantiate(self):
        parent = div()
        parent.nonreg_add(br)
        assert isinstance(parent.contents[0], br)

    def test_nonreg_add_tag_protocol(self):
        class Adaptable:
            def __tag__(self):
                return span()

        parent = div()
        parent.nonreg_add(Adaptable())
        assert isinstance(parent.contents[0], span)


# =====================================================================
# Attributes
# =====================================================================


class TestSetAttributes:
    def test_basic_attributes(self):
        tag = div()
        tag.set_attributes({"href": "http://example.com"})
        assert tag.attrs["href"] == "http://example.com"

    def test_trailing_underscore_stripped(self):
        tag = div()
        tag.set_attributes({"class_": "container"})
        assert "class" in tag.attrs

    def test_underscore_to_hyphen(self):
        tag = div()
        tag.set_attributes({"data_value": "42"})
        assert "data-value" in tag.attrs

    def test_leading_underscore_rejected(self):
        tag = div()
        with pytest.raises(ValueError, match="is not being consumed"):
            tag.set_attributes({"_private": "bad"})

    def test_returns_self(self):
        tag = div()
        assert tag.set_attributes({}) is tag


class TestAttributes:
    def test_empty_attributes(self):
        tag = div()
        assert tag.attributes() == ""

    def test_id_name_class_order(self):
        tag = div(id="myid", name="myname", class_="cls")
        attrs = tag.attributes()
        assert 'id="myid"' in attrs
        assert 'name="myname"' in attrs
        assert 'class="cls"' in attrs

    def test_boolean_true_valueless(self):
        tag = div()
        tag.set_attributes({"disabled": True})
        assert "disabled" in tag.attributes()
        assert "=" not in tag.attributes().split("disabled")[1][:1]

    def test_boolean_false_omitted(self):
        tag = div()
        tag.set_attributes({"disabled": False})
        assert "disabled" not in tag.attributes()

    def test_none_omitted(self):
        tag = div()
        tag.set_attributes({"data_val": None})
        assert "data-val" not in tag.attributes()

    def test_attrs_only(self):
        tag = div(id="myid", name="myname", class_="cls")
        tag.set_attributes({"href": "/link"})
        attrs = tag.attributes(attrs_only=True)
        assert "id" not in attrs
        assert "name" not in attrs
        assert "class" not in attrs
        assert 'href="/link"' in attrs


class TestOpts:
    def test_opts_sets_attrs(self):
        tag = div()
        tag.opts(data_value="42")
        assert tag.attrs["data-value"] == "42"

    def test_opts_returns_self(self):
        tag = div()
        assert tag.opts() is tag


class TestTagProperty:
    def test_tag_name_from_class(self):
        assert div()._tag == "div"
        assert span()._tag == "span"
        assert h1()._tag == "h1"


# =====================================================================
# XSS / Escaping
# =====================================================================


class TestXSSPrevention:
    def test_content_escaped(self):
        tag = div["<script>alert(1)</script>"]
        html_out = str(tag.__html__())
        assert "<script>" not in html_out
        assert "&lt;script&gt;" in html_out

    def test_attribute_escaped(self):
        tag = div(id='"><script>alert(1)</script>')
        attrs = tag.attributes()
        assert "<script>" not in attrs

    def test_literal_bypasses_escaping(self):
        tag = div[literal("<b>bold</b>")]
        html_out = str(tag.__html__())
        assert "<b>bold</b>" in html_out


# =====================================================================
# Element registry
# =====================================================================


class TestElementRegistry:
    def test_register_by_id(self):
        parent = div()
        child = span(id="child1")
        parent.add(child)
        assert "child1" in parent.elements
        assert parent.elements["child1"] is child

    def test_nested_registration(self):
        root = div()
        child = div(id="c1")
        grandchild = span(id="gc1")
        child.add(grandchild)
        root.add(child)
        assert "c1" in root.elements
        assert "gc1" in root.elements

    def test_duplicate_id_raises(self):
        parent = div()
        parent.add(span(id="dup"))
        with pytest.raises(ValueError, match="already registered"):
            parent.add(span(id="dup"))

    def test_contains(self):
        parent = div()
        parent.add(span(id="x"))
        assert "x" in parent
        assert "y" not in parent

    def test_get_element(self):
        parent = div()
        child = span(id="findme")
        parent.add(child)
        assert parent.get_element("findme") is child

    def test_get_element_not_found(self):
        parent = div()
        with pytest.raises(KeyError):
            parent.get_element("nonexistent")

    def test_unregister_element(self):
        parent = div()
        child = span(id="rem")
        parent.add(child)
        parent.unregister_element("rem")
        assert "rem" not in parent.elements

    def test_remove_element(self):
        parent = div()
        child = span(id="child")
        parent.add(child)
        parent.remove_element("child")
        assert "child" not in parent.elements
        assert child not in parent.contents
        assert child.container is None

    def test_remove_element_cascades_descendants(self):
        root = div()
        parent_tag = div(id="p1")
        child = span(id="c1")
        parent_tag.add(child)
        root.add(parent_tag)
        assert "c1" in root.elements
        root.remove_element("p1")
        assert "p1" not in root.elements
        assert "c1" not in root.elements

    def test_remove_nonexistent_raises(self):
        parent = div()
        with pytest.raises(KeyError, match="No element with id"):
            parent.remove_element("nope")

    def test_get_container_root(self):
        root = div()
        child = span(id="a")
        grandchild = p(id="b")
        child.add(grandchild)
        root.add(child)
        assert grandchild.get_container() is root

    def test_main_container_not_registered(self):
        root = div()
        wrapper = div(id="wrap", _main_container=True)
        root.add(wrapper)
        assert "wrap" not in root.elements

    def test_register_false_skips(self):
        parent = div()
        child = span(id="noreg", _register=False)
        parent.add(child)
        assert "noreg" not in parent.elements


# =====================================================================
# fragment
# =====================================================================


class TestFragment:
    def test_render_empty(self):
        frag = fragment()
        assert str(frag.r()) == ""

    def test_render_strings(self):
        frag = fragment()
        frag.add("hello", "world")
        result = str(frag.r())
        assert "hello" in result
        assert "world" in result
        assert "\n" in result

    def test_render_tags(self):
        frag = fragment()
        frag.add(div["a"], span["b"])
        result = str(frag.r())
        assert "<div>a</div>" in result
        assert "<span>b</span>" in result

    def test_pretty(self):
        frag = fragment()
        frag.add(div["hello"], p["world"])
        pretty = frag.pretty()
        assert "<div>hello</div>" in pretty
        assert "<p>world</p>" in pretty


# =====================================================================
# singletag (void elements)
# =====================================================================


class TestSingletag:
    def test_render_br(self):
        tag = br()
        result = str(tag.r())
        assert "<br />" in result

    def test_render_img_with_attrs(self):
        tag = img(src="photo.jpg", alt="Photo")
        result = str(tag.r())
        assert "<img" in result
        assert 'src="photo.jpg"' in result
        assert 'alt="Photo"' in result
        assert "/>" in result

    def test_render_hr(self):
        result = str(hr().r())
        assert "<hr />" in result

    def test_render_input_tag(self):
        tag = input(type="text", name="field")
        result = str(tag.r())
        assert "<input" in result
        assert 'type="text"' in result

    def test_render_meta(self):
        tag = meta(charset="utf-8")
        result = str(tag.r())
        assert 'charset="utf-8"' in result

    def test_add_to_void_raises(self):
        with pytest.raises(TypeError, match="void element"):
            br().add("content")

    def test_insert_to_void_raises(self):
        with pytest.raises(TypeError, match="void element"):
            br().insert(0, "content")

    def test_replace_to_void_raises(self):
        with pytest.raises(TypeError, match="void element"):
            br().replace("content")

    def test_nonreg_add_to_void_raises(self):
        with pytest.raises(TypeError, match="void element"):
            br().nonreg_add("content")

    def test_add_empty_ok(self):
        """add() with no args should not raise."""
        assert br().add() is not None

    def test_pretty(self):
        tag = br()
        pretty = tag.pretty(level=2, indent="  ")
        assert pretty == "    <br />"

    def test_is_inline(self):
        assert br._inline is True


# =====================================================================
# pairedtag
# =====================================================================


class TestPairedtag:
    def test_render_empty(self):
        tag = div()
        result = str(tag.r())
        assert result == "<div></div>"

    def test_render_with_content(self):
        tag = p["Hello world"]
        result = str(tag.r())
        assert result == "<p>Hello world</p>"

    def test_render_with_attrs(self):
        tag = div(id="main", class_="container")
        result = str(tag.r())
        assert 'id="main"' in result
        assert 'class="container"' in result

    def test_render_nested(self):
        doc = div[p["inner"]]
        result = str(doc.r())
        assert "<div><p>inner</p></div>" == result

    def test_render_deeply_nested(self):
        doc = div[div[div[span["deep"]]]]
        result = str(doc.r())
        assert "<div><div><div><span>deep</span></div></div></div>" == result

    def test_newline_tags(self):
        """Tags with _newline=True append a newline after closing tag."""

        class NewlineTag(pairedtag):
            _newline = True

        tag = NewlineTag()
        result = str(tag.r())
        assert result.endswith("\n")


class TestPairedtagPretty:
    def test_pretty_empty(self):
        tag = div()
        assert tag.pretty() == "<div></div>"

    def test_pretty_inline(self):
        tag = span["text"]
        assert tag.pretty() == "<span>text</span>"

    def test_pretty_block_with_children(self):
        tag = div[p["a"], p["b"]]
        pretty = tag.pretty()
        assert "<div>" in pretty
        assert "  <p>a</p>" in pretty
        assert "  <p>b</p>" in pretty
        assert "</div>" in pretty

    def test_pretty_custom_indent(self):
        tag = div[p["content"]]
        pretty = tag.pretty(indent="    ")
        assert "    <p>content</p>" in pretty

    def test_pretty_level(self):
        tag = div["hello"]
        pretty = tag.pretty(level=1, indent="  ")
        assert pretty.startswith("  <div>")


# =====================================================================
# Dynamic tag generation
# =====================================================================


class TestDynamicTags:
    def test_paired_tags_exist(self):
        expected = [
            "div",
            "span",
            "p",
            "a",
            "b",
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
            "fieldset",
            "legend",
            "pre",
            "code",
            "small",
            "strong",
        ]
        import tagato.tags as tags_module

        for name in expected:
            cls = getattr(tags_module, name)
            assert issubclass(cls, pairedtag), f"{name} should be a pairedtag"

    def test_single_tags_exist(self):
        expected = [
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
        import tagato.tags as tags_module

        for name in expected:
            cls = getattr(tags_module, name)
            assert issubclass(cls, singletag), f"{name} should be a singletag"

    def test_inline_tags_marked(self):
        inline_names = ["span", "a", "b", "i", "strong", "label", "time", "code"]
        import tagato.tags as tags_module

        for name in inline_names:
            cls = getattr(tags_module, name)
            assert cls._inline is True, f"{name} should be inline"


# =====================================================================
# ul / ol (list tags with validation)
# =====================================================================


class TestListTags:
    def test_ul_accepts_li(self):
        tag = ul[li["item1"], li["item2"]]
        result = str(tag.r())
        assert "<ul>" in result
        assert "<li>item1</li>" in result
        assert "<li>item2</li>" in result

    def test_ul_rejects_non_li(self):
        with pytest.raises(ValueError, match="should only have LI content"):
            ul().add("not an li")

    def test_ul_rejects_string_via_getitem(self):
        with pytest.raises(ValueError, match="should only have LI content"):
            ul["bad"]

    def test_ol_accepts_li(self):
        tag = ol[li["first"], li["second"]]
        result = str(tag.r())
        assert "<ol>" in result
        assert "<li>" in result

    def test_ol_rejects_non_li(self):
        with pytest.raises(ValueError, match="should only have LI content"):
            ol().add(div["bad"])


# =====================================================================
# __html__ protocol
# =====================================================================


class TestHTMLProtocol:
    def test_html_returns_markup(self):
        tag = div["content"]
        result = tag.__html__()
        assert isinstance(result, Markup)

    def test_html_renders_correctly(self):
        tag = p["paragraph"]
        assert str(tag.__html__()) == "<p>paragraph</p>"


# =====================================================================
# Functional / integration tests
# =====================================================================


class TestIntegration:
    def test_full_document(self):
        doc = html[
            head,
            body[
                h1["Title"],
                div(class_="content")[
                    p["Paragraph 1"],
                    p["Paragraph 2"],
                ],
            ],
        ]
        result = str(doc.__html__())
        assert "<html>" in result
        assert "<head></head>" in result
        assert "<body>" in result
        assert "<h1>Title</h1>" in result
        assert "</html>" in result

    def test_dynamic_list_comprehension(self):
        items = ["A", "B", "C"]
        tag = ul[[li[item] for item in items]]
        result = str(tag.r())
        assert "<li>A</li>" in result
        assert "<li>B</li>" in result
        assert "<li>C</li>" in result

    def test_attributes_on_nested_tags(self):
        doc = div(id="outer")[a(href="/link", class_="btn")["Click me"]]
        result = str(doc.r())
        assert 'id="outer"' in result
        assert 'href="/link"' in result
        assert 'class="btn"' in result
        assert "Click me" in result

    def test_mixed_content(self):
        tag = div["Text ", span["bold"], " more text"]
        result = str(tag.r())
        assert "Text " in result
        assert "<span>bold</span>" in result
        assert " more text" in result

    def test_register_and_replace_workflow(self):
        page = div()
        content = div(id="content")["Initial"]
        page.add(content)
        assert "content" in page.elements
        page.get_element("content").replace("Updated")
        result = str(page.r())
        assert "Updated" in result
        assert "Initial" not in result

    def test_pretty_print_full(self):
        doc = div(id="root")[
            h1["Title"],
            p["para"],
        ]
        pretty = doc.pretty()
        lines = pretty.split("\n")
        assert lines[0] == '<div id="root">'
        assert lines[-1] == "</div>"

    def test_table_construction(self):
        t = table[
            thead[tr[th["Name"], th["Age"]]],
            tbody[
                tr[td["Alice"], td["30"]],
                tr[td["Bob"], td["25"]],
            ],
        ]
        result = str(t.r())
        assert "<table>" in result
        assert "<thead>" in result
        assert "<th>Name</th>" in result
        assert "<td>Alice</td>" in result
