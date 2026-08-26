from __future__ import annotations

import os
import runpy
import sys
import types
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SessionState(dict):
    __getattr__ = dict.get

    def __setattr__(self, key, value):
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
        self.sidebar = Context()
        self.column_config = ColumnConfig()

    def cache_resource(self, func=None, **_kwargs):
        return (lambda item: item) if func is None else func

    def __getattr__(self, name):
        if name in {"columns", "tabs", "container", "expander", "form", "spinner"}:
            return getattr(self, name)
        if name in {"text_input", "text_area", "selectbox", "multiselect", "slider", "checkbox", "radio"}:
            return getattr(self, name)
        if name in {"button", "form_submit_button", "download_button", "file_uploader"}:
            return lambda *_args, **_kwargs: False if name != "file_uploader" else None
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
        if key:
            self.session_state.setdefault(key, value)
            return self.session_state[key]
        return value

    def text_area(self, _label, value="", key=None, **_kwargs):
        if key:
            self.session_state.setdefault(key, value)
            return self.session_state[key]
        return value

    def selectbox(self, _label, options, index=0, key=None, **_kwargs):
        value = options[index] if options else None
        if key:
            self.session_state.setdefault(key, value)
            return self.session_state[key]
        return value

    def multiselect(self, _label, _options, default=None, key=None, **_kwargs):
        value = list(default or [])
        if key:
            self.session_state.setdefault(key, value)
            return self.session_state[key]
        return value

    def slider(self, _label, _min, _max, value, key=None, **_kwargs):
        if key:
            self.session_state.setdefault(key, value)
            return self.session_state[key]
        return value

    def checkbox(self, _label, value=False, key=None, **_kwargs):
        if key:
            self.session_state.setdefault(key, value)
            return self.session_state[key]
        return value

    def radio(self, label, options, key=None, **_kwargs):
        value = os.environ.get("NORA_SMOKE_PAGE", options[0]) if label == "작업공간" else options[0]
        if key:
            self.session_state[key] = value
        return value

    def data_editor(self, data, *_args, **_kwargs):
        return data

    def rerun(self):
        raise RuntimeError("Smoke test에서 예상하지 않은 rerun이 호출되었습니다.")


STUB = StreamlitStub()


def run_page(page: str) -> None:
    os.environ["NORA_SMOKE_PAGE"] = page
    sys.modules["streamlit"] = STUB
    sys.path.insert(0, str(ROOT))
    runpy.run_path(str(ROOT / "streamlit_app.py"), run_name="__main__")


if __name__ == "__main__":
    temp_dir = tempfile.TemporaryDirectory(prefix="nora-smoke-")
    os.environ["NORA_DATA_DIR"] = temp_dir.name
    pages = ["프로젝트 개요", "문서 근거", "근거 검토", "평가 입력", "결과·보고서", "규칙·온톨로지"]
    for page in pages:
        STUB.session_state.clear()
        run_page(page)
        print(f"PASS - {page}")
    temp_dir.cleanup()
