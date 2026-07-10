import streamlit.components.v1 as components
import os


_RELEASE = True


if not _RELEASE:
    _component_func = components.declare_component(
        "voice_component",
        url="http://localhost:5173",
    )

else:
    build_dir = os.path.join(
        os.path.dirname(__file__),
        "frontend",
        "dist"
    )

    _component_func = components.declare_component(
        "voice_component",
        path=build_dir
    )


def voice_component(key=None, default_text=""):
    return _component_func(
        key=key,
        default_text=default_text,
        default=default_text,
    )