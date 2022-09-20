import re

import lektor.context
import lektor.project
import pytest

from lektor_markdown_image_attrs import (
    extract_attrs_from_title,
    LektorPlugin,
    )


@pytest.fixture
def test_site(tmp_path):
    return test_site


@pytest.fixture
def lektor_env(tmp_path):
    test_site = tmp_path
    project_file = test_site / 'test_site.lektorproject'
    project_file.touch()
    proj = lektor.project.Project.from_path(str(test_site))
    return proj.make_env(load_plugins=False)


@pytest.fixture
def our_plugin(lektor_env):
    plugin_id = "lektor-markdown-image-attrs"
    controller = lektor_env.plugin_controller
    controller.instanciate_plugin(plugin_id, LektorPlugin)
    controller.emit("setup-env")
    return lektor_env.plugins[plugin_id]


@pytest.fixture
def lektor_context(lektor_env):
    with lektor.context.Context(pad=lektor_env.new_pad()):
        yield


@pytest.fixture
def render_markdown(lektor_context):
    def render_markdown(source):
        md = lektor.markdown.Markdown(source)
        return md.html
    return render_markdown


@pytest.mark.parametrize('title, expected', [
    ("Fluffy, my cat <class='img-responsive'>",
     ("class='img-responsive'", "Fluffy, my cat")),
    ("  <class=noquotes>", ("class=noquotes", None)),
    ('Fluffy <class="dquotes">', ('class="dquotes"', "Fluffy")),
    ('Fluffy < hidden class=hide >  ', ('hidden class=hide', "Fluffy")),
    ('No attrs', (None, 'No attrs')),
    (' class=img ', ("class=img", None)),
    ('hidden class=img', (None, "hidden class=img")),
])
def test_extract_attrs_from_title(title, expected):
    assert extract_attrs_from_title(title) == expected


@pytest.mark.usefixtures('our_plugin')
def test_render_image(render_markdown):
    rendered = render_markdown('![cat](cat.jpg "Fluffy <class=img>")')
    assert re.search(r"<img [^>]*\bclass=img\b", rendered)
    assert re.search(r'<img [^>]*\bsrc="cat.jpg"', rendered)


@pytest.mark.usefixtures('our_plugin')
def test_render_link(render_markdown):
    rendered = render_markdown('[cat](cat.jpg "Fluffy <class=img>")')
    assert re.search(r"<a [^>]*\bclass=img\b", rendered)
    assert re.search(r'<a [^>]*\bhref="cat.jpg"', rendered)
