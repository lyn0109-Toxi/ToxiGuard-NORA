from __future__ import annotations

import os
import runpy
import sys
import types
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class StreamlitAPIException(RuntimeError):
    pass


class RerunRequested(RuntimeError):
    pass


class SessionState(dict):
    def __init__(self):
        super().__init__()
        object.__setattr__(self, "_owner", None)

    def bind(self, owner):
        object.__setattr__(self, "_owner", owner)

    def __getattr__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        owner = object.__getattribute__(self, "_owner")
        if owner and owner.is_locked_widget_key(key):
            raise StreamlitAPIException(
                f"st.session_state.{key} cannot be modified after widget creation in the same run."
            )
        super().__setitem__(key, value)

    def __setattr__(self, key, value):
        if key.startswith("_"):
            object.__setattr__(self, key, value)
        else:
            self[key] = value


class Context:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def __getattr__(self, name):
        return getattr(STUB, name)


class ColumnConfig:
    def __getattr__(self, _name):
        return lambda *_args, **_kwargs: None


class StreamlitStub(types.ModuleType):
    def __init__(self):
        super().__init__("streamlit")
        self.session_state = SessionState()
        self.session_state.bind(self)
        self.sidebar = Context()
        self.column_config = ColumnConfig()
        self.errors = types.SimpleNamespace(StreamlitAPIException=StreamlitAPIException)
        self._active_widget_key = None
        self._instantiated_widget_keys = set()

    def begin_run(self, clear_state=False):
        self._active_widget_key = None
        self._instantiated_widget_keys.clear()
        if clear_state:
            self.session_state.clear()

    def is_locked_widget_key(self, key):
        return key in self._instantiated_widget_keys and self._active_widget_key != key

    def _register_widget(self, key, value):
        if not key:
            return value
        previous_key = self._active_widget_key
        self._active_widget_key = key
        try:
            if key not in self.session_state:
                self.session_state[key] = value
            return self.session_state[key]
        finally:
            self._active_widget_key = previous_key
            self._instantiated_widget_keys.add(key)

    def cache_resource(self, func=None, **_kwargs):
        return (lambda item: item) if func is None else func

    def cache_data(self, func=None, **_kwargs):
        return (lambda item: item) if func is None else func

    def __getattr__(self, name):
        if name in {"columns", "tabs", "container", "expander", "form", "spinner"}:
            return getattr(self, name)
        if name in {"text_input", "text_area", "selectbox", "multiselect", "slider", "checkbox", "radio"}:
            return getattr(self, name)
        return lambda *_args, **_kwargs: None

    def columns(self, spec, *_args, **_kwargs):
        count = spec if isinstance(spec, int) else len(spec)
        return [Context() for _ in range(count)]

    def tabs(self, names, *_args, **_kwargs):
        return [Context() for _ in names]

    def container(self, *_args, **_kwargs):
        return Context()

    def expander(self, *_args, **_kwargs):
        return Context()

    def form(self, *_args, **_kwargs):
        return Context()

    def spinner(self, *_args, **_kwargs):
        return Context()

    def text_input(self, _label, value="", key=None, **_kwargs):
        return self._register_widget(key, value)

    def text_area(self, _label, value="", key=None, **_kwargs):
        return self._register_widget(key, value)

    def selectbox(self, _label, options, index=0, key=None, **_kwargs):
        value = options[index] if options else None
        return self._register_widget(key, value)

    def multiselect(self, _label, _options, default=None, key=None, **_kwargs):
        value = list(default or [])
        return self._register_widget(key, value)

    def slider(self, _label, _min, _max, value, key=None, **_kwargs):
        return self._register_widget(key, value)

    def checkbox(self, _label, value=False, key=None, **_kwargs):
        return self._register_widget(key, value)

    def radio(self, label, options, key=None, **_kwargs):
        is_workspace = set(options) == {"overview", "consulting", "documents", "assertions", "assessment", "results", "rules"}
        if key == "nora_language":
            value = os.environ.get("NORA_SMOKE_LANGUAGE", options[0])
        elif is_workspace:
            value = os.environ.get("NORA_SMOKE_PAGE", options[0])
        else:
            value = options[0]
        return self._register_widget(key, value)

    def button(self, label, *_args, key=None, **_kwargs):
        click_key = os.environ.get("NORA_SMOKE_CLICK_KEY")
        click_label = os.environ.get("NORA_SMOKE_CLICK_LABEL")
        return bool((click_key and key == click_key) or (click_label and label == click_label))

    def form_submit_button(self, label, *_args, **kwargs):
        return self.button(label, *_args, **kwargs)

    def download_button(self, *_args, **_kwargs):
        return False

    def file_uploader(self, *_args, **_kwargs):
        return None

    def data_editor(self, data, *_args, key=None, **_kwargs):
        if key:
            self._register_widget(key, data)
        return data

    def rerun(self):
        raise RerunRequested("Streamlit rerun requested.")


STUB = StreamlitStub()


def run_page(page: str, clear_state: bool = False) -> None:
    os.environ["NORA_SMOKE_PAGE"] = page
    sys.modules["streamlit"] = STUB
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    STUB.begin_run(clear_state=clear_state)
    runpy.run_path(str(ROOT / "streamlit_app.py"), run_name="__main__")


if __name__ == "__main__":
    temp_dir = tempfile.TemporaryDirectory(prefix="nora-smoke-")
    os.environ["NORA_DATA_DIR"] = temp_dir.name
    pages = ["overview", "consulting", "documents", "assertions", "assessment", "results", "rules"]
    for language in ["한국어", "English"]:
        os.environ["NORA_SMOKE_LANGUAGE"] = language
        for page in pages:
            run_page(page, clear_state=True)
            print(f"PASS - {language} - {page}")
    temp_dir.cleanup()
