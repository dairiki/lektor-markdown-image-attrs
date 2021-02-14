# -*- coding: utf-8 -*-
"""Extend Markdown syntax to allow setting arbitrary HTML attributes
on images and links.

"""
import re

import lektor.pluginsystem


# Regex construction
_bits = {
    # attribute name
    'name': r'[_:a-z][-.0-9_:a-z]*',  # NB: more restrictive than HTML spec
    # unquoted attribute value
    'uvalue': r'[-.0-9_:a-z]+',       # NB: more restrictive than HTML sepc
    # quoted attribute value
    'qvalue1': r" ' [^'>]* ' ",
    'qvalue2': r' " [^">]* " ',
    }
_bits['value'] = r'(?: {uvalue} | {qvalue1} | {qvalue2})'.format(**_bits)
# non-empty attribute
_bits['nonempty_attribute'] = r'{name} \s* = \s* {value}'.format(**_bits)
# possibly-empty attribute
_bits['attribute'] = r'{name} (?: \s* = \s* {value})?'.format(**_bits)


# Trailing, possibly empty, list of attributes, surround by <>
trailing_attrs_re = re.compile(
    r'''
    \s* < \s* (?P<attrs>
        (?: {attribute} (?: \s+ {attribute} )* )?
    ) \s* > \s* \Z
    '''.format(**_bits), re.X | re.I)

# Nothing but a non-empty list of non-empty attribute (without angle brackets)
implicit_attrs_re = re.compile(
    r'''
    \A \s* (?P<attrs>
        {nonempty_attribute} (?: \s+ {nonempty_attribute} )*
    ) \s* \Z
    '''.format(**_bits), re.X | re.I)


def extract_attrs_from_title(title):
    attrs = None
    if title:
        m = (trailing_attrs_re.search(title)
             or implicit_attrs_re.match(title))
        if m is not None:
            attrs = m.group('attrs')
            title = title[:m.start()] if m.start() > 0 else None
    return attrs, title


class MarkdownRendererMixin(object):
    """This allows one to set attributes on image and link tags by
    including them in the markdown title for the image or link.

    Examples::

        ![my cat](cat.jpg "Fluffy, my cat <class='img-responsive'>")


        (Not to be confused with this one: ![my other cat][fluffy].)

        [fluffy]: other-cat.jpg (Not Fluffy <style="width: 25px;">)

    """
    def link(self, link, title, text):
        attrs, title = extract_attrs_from_title(title)
        markup = super(MarkdownRendererMixin, self).link(link, title, text)
        if attrs:
            # FIXME: hackish
            markup = markup.replace(' href=', ' %s href=' % attrs)
        return markup

    def image(self, src, title, text):
        attrs, title = extract_attrs_from_title(title)

        markup = super(MarkdownRendererMixin, self).image(src, title, text)
        if attrs:
            # FIXME: hackish
            markup = markup.replace(' src=', ' %s src=' % attrs)
        return markup


class LektorPlugin(lektor.pluginsystem.Plugin):
    name = 'Lektor Markdown Image and Link Attributes'
    description = (
        u'Extend Lektor’s Markdown syntax to allow setting '
        u'arbitrary HTML attributes on images and links.')

    def on_markdown_config(self, config, **extra):
        # XXX: This is fragile, but I'm not sure how better to do this.
        # Here we attempt to put our mixin the top of the MRO so that it
        # will be called above any calls to other mixins which affect
        # the rendering of images and/or links.
        config.renderer_mixins.insert(0, MarkdownRendererMixin)
