Tagato: Lightweight HTML Generation
====================================

**Tagato** is a lightweight Python library for building HTML structures using 
a clean, nested syntax.
By leveraging Python's operator overloading, Tagato allows you to write code
that visually mirrors the resulting HTML tree.
Tagato is a standalone reimplementation of the
`tags.py <https://github.com/trmznt/rhombus/blob/master/rhombus/lib/tags.py>`_
module.

Installation
------------

Install Tagato via pip:

.. code-block:: bash

    pip install tagato

Basic Usage
-----------

Tagato uses square brackets ``[]`` for nesting children and parentheses ``()`` 
for defining attributes.
This creates a Domain Specific Language (DSL) that mirrors the tree structure of HTML.

.. code-block:: python

    from tagato.tags import html, body, div, p, h1

    # Compose your document
    doc = html[
        body[
            h1["Welcome to Tagato"],
            div(class_="container", id="main")[
                p["This is a paragraph generated with Python."],
                p(style="color: blue")["This one has inline styles!"]
            ]
        ]
    ]

    print(doc)

Dynamic Content
---------------

Because Tagato is pure Python, you can easily generate repetitive elements 
using list comprehensions:

.. code-block:: python

    from tagato.tags import ul, li

    items = ["Python", "HTML", "Tagato"]

    # Generate a list dynamically
    my_list = ul[
        [li[item] for item in items]
    ]

    print(my_list)

Key Features
------------

* **Zero Boilerplate**: No need for complex template loaders or external files.
* **Declarative**: The Python structure matches the HTML hierarchy.
* **Lightweight**: Minimal memory footprint with minimal external dependencies.
* **Pythonic**: Uses ``__getitem__`` and ``__call__`` for an intuitive DSL.

License
-------

MIT

