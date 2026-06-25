import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

_env = None

def _get_env():
    global _env
    if _env is None:
        _env = Environment(
            loader=FileSystemLoader(os.path.dirname(__file__)),
            autoescape=select_autoescape(),
        )
        _env.filters["map_attrs"] = _map_attrs
    return _env

def _map_attrs(attrs):
    if not attrs:
        return ""
    parts = []
    for k, v in attrs.items():
        if v is None or v is False:
            continue
        if v is True:
            parts.append(k)
        else:
            parts.append(f'{k}="{str(v).replace(chr(34), "&quot;")}"')
    return " ".join(parts)

class UiHelper:
    """Injected into Jinja2 globals as `ui`. Usage: {{ ui.button("Save") }}"""

    def button(self, label, variant="solid", tone="primary", size="md", class_="", loading=False, disabled=False, **attrs):
        return _get_env().get_template("button.html").render(
            label=label, variant=variant, tone=tone, size=size,
            class_=class_, loading=loading, disabled=disabled, attrs=attrs,
        )

    def badge(self, label, variant="solid", tone="primary", class_="", **attrs):
        return _get_env().get_template("badge.html").render(
            label=label, variant=variant, tone=tone, class_=class_, attrs=attrs,
        )

    def alert(self, message, tone="info", title="", class_="", **attrs):
        return _get_env().get_template("alert.html").render(
            message=message, tone=tone, title=title, class_=class_, attrs=attrs,
        )

    def card(self, title="", variant="bordered", class_="", **attrs):
        return _get_env().get_template("card_start.html").render(
            title=title, variant=variant, class_=class_, attrs=attrs,
        )

    def endcard(self):
        return '</div></div>'

    def modal(self, title="", id="", size="md", class_="", **attrs):
        return _get_env().get_template("modal_start.html").render(
            title=title, id=id, size=size, class_=class_, attrs=attrs,
        )

    def endmodal(self):
        return '</div></div></div>'

    def toast_container(self):
        return '<div id="galaxy-toast-container"></div>'

    def theme_switcher(self, class_=""):
        return _get_env().get_template("theme_switcher.html").render(class_=class_)

ui = UiHelper()
