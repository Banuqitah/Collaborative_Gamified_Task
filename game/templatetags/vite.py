import re
import json
from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe

register = template.Library()


def is_abs_url(url):
    return re.match("^https?://", url)


def vite_manifest(entries_names):
    manifest_filepath = 'static/manifest.json'

    with open(manifest_filepath) as fp:
        manifest = json.load(fp)
    _processed = set()

    def _process_entries(names):
        scripts = []
        styles = []

        for name in names:
            if name in _processed:
                continue
            chunk = manifest[name]
            import_scripts, import_styles = _process_entries(chunk.get('imports', []))
            scripts += import_scripts
            styles += import_styles

            scripts += [chunk['file']]
            styles += [css for css in chunk.get('css', [])]

            _processed.add(name)
        return scripts, styles
    return _process_entries(entries_names)


@register.simple_tag
def vite_styles(*entries_names):
    _, styles = vite_manifest(entries_names)
    styles = map(lambda href: href if is_abs_url(href) else static(href), styles)
    return mark_safe("\n".join(map(lambda href: f'<link rel="stylesheet" href="{href}"/>', styles)))


@register.simple_tag
def vite_scripts(*entries_names):
    scripts, _ = vite_manifest(entries_names)
    scripts = map(lambda href: href if is_abs_url(href) else static(href), scripts)
    return mark_safe("\n".join(map(lambda href: f'<script type="module" src="{href}"></script>', scripts)))
