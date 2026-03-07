Usage Guide
===========

Installation
------------

.. code-block:: bash

    pip install tagato


Core Concepts
-------------

Tagato uses two Python operators to mirror HTML structure:

- **Square brackets** ``[]`` — add child content (text or nested tags)
- **Parentheses** ``()`` — set HTML attributes


Importing Tags
--------------

.. code-block:: python

    from tagato.tags import div, span, p, a, h1, ul, li, br, img, literal


Basic Tag Rendering
-------------------

Tags can be used directly as classes (no explicit instantiation required):

.. code-block:: python

    from tagato.tags import div, p, h1

    # Empty tag
    str(div)  # => "<div></div>"

    # With content
    str(h1["Hello"])  # => "<h1>Hello</h1>"

    # Multiple children
    str(div["Hello ", "World"])  # => "<div>Hello World</div>"


Setting HTML Attributes
-----------------------

Pass attributes as keyword arguments.  Use trailing underscores for
Python-reserved words (``class_``, ``for_``), and underscores for hyphens
(``data_value`` becomes ``data-value``):

.. code-block:: python

    from tagato.tags import div, a, input

    div(id="main", class_="container")
    # => <div id="main" class="container"></div>

    a(href="/page", class_="btn")["Click"]
    # => <a href="/page" class="btn">Click</a>

    input(type="text", data_bind="model")
    # => <input type="text" data-bind="model" />

Boolean attributes are handled naturally:

.. code-block:: python

    input(type="checkbox", checked=True)   # => <input type="checkbox" checked />
    input(type="checkbox", checked=False)  # => <input type="checkbox" />


Nesting Tags
------------

Tags nest naturally with the ``[]`` operator:

.. code-block:: python

    from tagato.tags import html, head, body, div, p, h1

    doc = html[
        head,
        body[
            h1["Welcome"],
            div(class_="content")[
                p["First paragraph."],
                p["Second paragraph."],
            ],
        ],
    ]

    print(doc)


Dynamic Content
---------------

Use standard Python to generate HTML dynamically:

.. code-block:: python

    from tagato.tags import ul, li, table, thead, tbody, tr, th, td

    # List comprehension
    items = ["Python", "HTML", "CSS"]
    my_list = ul[[li[item] for item in items]]

    # Table from data
    rows = [("Alice", 30), ("Bob", 25)]
    my_table = table[
        thead[tr[th["Name"], th["Age"]]],
        tbody[
            [tr[td[name], td[str(age)]] for name, age in rows]
        ],
    ]


Adding Content Incrementally
-----------------------------

Use ``.add()``, ``+=``, or ``.insert()`` to build tags step by step:

.. code-block:: python

    from tagato.tags import div, p

    page = div()
    page.add(p["First"])
    page += p["Second"]
    page.insert(0, p["Zeroth"])  # Insert at position 0

    # Chaining
    div().add("a").add("b").add("c")


Replacing Content
-----------------

.. code-block:: python

    from tagato.tags import div

    tag = div["old content"]
    tag.replace("new content")
    str(tag)  # => "<div>new content</div>"


Void (Self-Closing) Elements
-----------------------------

Void elements like ``<br>``, ``<hr>``, ``<img>``, ``<input>`` render as
self-closing tags and reject child content:

.. code-block:: python

    from tagato.tags import br, hr, img, input

    str(br())     # => "<br />"
    str(hr())     # => "<hr />"
    str(img(src="photo.jpg", alt="Photo"))
    # => '<img src="photo.jpg" alt="Photo" />'


Fragment (No Wrapper)
---------------------

``fragment`` renders its children without a wrapping element:

.. code-block:: python

    from tagato.tags import fragment, p

    frag = fragment[p["A"], p["B"]]
    str(frag)
    # => "<p>A</p>\n<p>B</p>"


Literal / Raw HTML
------------------

Use ``literal`` (alias for ``markupsafe.Markup``) to insert pre-escaped HTML:

.. code-block:: python

    from tagato.tags import div, literal

    raw = literal("<b>bold</b>")
    tag = div[raw]
    str(tag)  # => "<div><b>bold</b></div>"

All other string content is automatically escaped to prevent XSS:

.. code-block:: python

    tag = div["<script>alert(1)</script>"]
    str(tag)  # => "<div>&lt;script&gt;alert(1)&lt;/script&gt;</div>"


Pretty Printing
---------------

.. code-block:: python

    from tagato.tags import div, p, h1

    doc = div(id="root")[
        h1["Title"],
        p["Content"],
    ]

    print(doc.pretty())
    # <div id="root">
    #   <h1>Title</h1>
    #   <p>Content</p>
    # </div>

    print(doc.pretty(indent="    "))  # custom indent


Element Registry (ID Lookup)
-----------------------------

Tags with an ``id`` are registered in their root container for fast lookup:

.. code-block:: python

    from tagato.tags import div, span

    page = div()
    page.add(span(id="status")["OK"])

    # Lookup by id
    "status" in page        # => True
    page.get_element("status").replace("Error!")

    # Remove an element
    page.remove_element("status")


The ``__tag__`` Adapter Protocol
---------------------------------

Any object with a ``__tag__()`` method can be added to a tag tree:

.. code-block:: python

    from tagato.tags import div, span

    class MyWidget:
        def __tag__(self):
            return span(class_="widget")["Hello from widget"]

    page = div[MyWidget()]
    str(page)
    # => '<div><span class="widget">Hello from widget</span></div>'


Form Fields (``tagato.formfields``)
------------------------------------

Tagato includes a form-field abstraction layer with CSS theme support.
The default theme is Bootstrap 5.3.


Setting Up the Theme
~~~~~~~~~~~~~~~~~~~~

A Bootstrap 5.3 theme is activated on import. To use a custom theme:

.. code-block:: python

    from tagato.formfields import set_theme, CSSTheme

    class MyTheme(CSSTheme):
        def input_class(self, *, error=False):
            return "custom-input" + (" error" if error else "")
        # ... override other methods as needed

    set_theme(MyTheme())


Building a Form
~~~~~~~~~~~~~~~

.. code-block:: python

    from tagato.formfields import (
        HTMLForm, TextInput, PasswordInput, EmailInput,
        SelectInput, CheckboxInput, RadioInput, TextAreaInput,
        HiddenInput,
    )

    form = HTMLForm(action="/register", method="post")
    form.add(
        HiddenInput(name="csrf", value="abc123"),
        TextInput(name="username", label="Username", placeholder="Enter name"),
        EmailInput(name="email", label="Email"),
        PasswordInput(name="password", label="Password"),
        TextAreaInput(name="bio", label="Bio", value="Tell us about yourself"),
        SelectInput(
            name="role",
            label="Role",
            value="user",
            options=[("admin", "Admin"), ("user", "User"), ("guest", "Guest")],
        ),
        RadioInput(
            name="plan",
            label="Plan",
            value="free",
            options=[("free", "Free"), ("pro", "Pro"), ("enterprise", "Enterprise")],
        ),
        CheckboxInput(name="agree", label="I accept the terms", value=False),
    )

    print(form)


Readonly Forms
~~~~~~~~~~~~~~

Set ``_readonly=True`` on the form to render all fields as readonly.
Checkboxes and radios display as badges instead of interactive controls:

.. code-block:: python

    form = HTMLForm(_readonly=True)
    form.add(
        TextInput(name="name", label="Name", value="Alice"),
        CheckboxInput(name="active", label="Active", value=True),
    )
    print(form)


InputProvider Protocol
~~~~~~~~~~~~~~~~~~~~~~

For data-layer integration, implement the ``InputProvider`` protocol:

.. code-block:: python

    from tagato.formfields import InputProvider, TextInput

    class MyField:
        def get_value(self):
            return "loaded from DB"
        def get_options(self):
            return []
        def is_required(self):
            return True
        def get_name(self):
            return "db_field"

    inp = TextInput(input_provider=MyField(), label="DB Field")


Value resolution order:

1. ``update_dict[name]`` — runtime overrides (e.g. POST data)
2. ``input_provider.get_value()`` — data-layer binding
3. ``value`` — explicit constructor value
4. ``""`` — fallback


Field Options
~~~~~~~~~~~~~

.. code-block:: python

    inp = TextInput(name="f", label="Field")
    inp.opts(size=6, offset=3, error="Required!", info="Help text here")


Checkbox Groups
~~~~~~~~~~~~~~~

.. code-block:: python

    from tagato.formfields import CheckboxGroupInput, CheckboxInput

    group = CheckboxGroupInput(name="colors", label="Favorite colors")
    group.add(
        CheckboxInput(name="red", label="Red", value=True),
        CheckboxInput(name="green", label="Green", value=False),
        CheckboxInput(name="blue", label="Blue", value=True),
    )


Inline Inputs
~~~~~~~~~~~~~

Use ``InlineInput`` to group multiple fields on a single row:

.. code-block:: python

    from tagato.formfields import InlineInput, TextInput

    row = InlineInput()
    row.add(
        TextInput(name="first", label="First", size=3),
        TextInput(name="last", label="Last", size=3),
    )


Info Text & Popups
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Inline help text
    TextInput(name="f", label="Field", info="Enter your full name")

    # Popup link
    TextInput(name="f", label="Field", info="popup:/help/field")


Error Feedback
~~~~~~~~~~~~~~

.. code-block:: python

    TextInput(name="email", label="Email", error="Invalid email address")


Popover Labels
~~~~~~~~~~~~~~

.. code-block:: python

    TextInput(
        name="advanced",
        label="Advanced",
        popover="This setting controls the advanced mode behavior.",
    )


Custom CSS Themes
~~~~~~~~~~~~~~~~~

Subclass ``CSSTheme`` and override methods to adapt to any CSS framework:

.. code-block:: python

    from tagato.formfields import CSSTheme, set_theme

    class TailwindTheme(CSSTheme):
        def form_row(self):
            return "flex items-center gap-4 mb-4"

        def label_class(self, offset):
            return f"w-1/{offset} text-right font-medium"

        def input_class(self, *, error=False):
            base = "border rounded px-3 py-2"
            return f"{base} border-red-500" if error else base

        def select_class(self, *, error=False):
            return self.input_class(error=error)

        def value_col(self, size):
            return f"flex-1"

        def error_feedback(self, message):
            if not message:
                return ""
            from tagato.tags import span
            return span(class_="text-red-500 text-sm")[message]

    set_theme(TailwindTheme())
