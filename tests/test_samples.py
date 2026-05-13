"""
Test suite for mxlit rendering pipeline, based on the samples/ folder.

Each test starts a fresh server process, exercises the HTTP endpoints,
and asserts that the expected HTML structures are present in the response.
"""

import os
import sys
import time
import subprocess
import requests
import pytest

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "samples")

BASE_PORT = 19800  # high port range to avoid conflicts


def _sample_path(name: str) -> str:
    return os.path.join(SAMPLES_DIR, name)


class ServerFixture:
    """Starts an mxlit server for a given script and tears it down after the test."""

    def __init__(self, script: str, port: int):
        self.script = script
        self.port = port
        self.proc = None

    def start(self):
        env = {**os.environ, "MXLIT_SCRIPT": self.script}
        self.proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "mxlit.server:app", "--port", str(self.port)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        # Wait for server to become ready
        deadline = time.time() + 15
        while time.time() < deadline:
            try:
                r = requests.get(f"http://127.0.0.1:{self.port}/initial", timeout=2)
                if r.status_code == 200:
                    return
            except Exception:
                pass
            time.sleep(0.3)
        raise RuntimeError(f"Server on port {self.port} did not start in time")

    def stop(self):
        if self.proc:
            self.proc.terminate()
            self.proc.wait(timeout=5)

    def get_initial(self) -> str:
        return requests.get(f"http://127.0.0.1:{self.port}/initial", timeout=5).text

    def post_interact(self, data: dict = None) -> str:
        return requests.post(
            f"http://127.0.0.1:{self.port}/interact", data=data or {}, timeout=5
        ).text


@pytest.fixture
def server_factory():
    servers = []

    def make(script_name: str, port: int):
        srv = ServerFixture(_sample_path(script_name), port)
        srv.start()
        servers.append(srv)
        return srv

    yield make

    for srv in servers:
        srv.stop()


# ---------------------------------------------------------------------------
# test_layouts.py sample
# ---------------------------------------------------------------------------

class TestLayouts:
    PORT = BASE_PORT + 1

    @pytest.fixture(autouse=True)
    def _server(self, server_factory):
        self.srv = server_factory("test_layouts.py", self.PORT)

    def test_initial_renders_sidebar(self):
        html = self.srv.get_initial()
        assert 'class="sidebar"' in html

    def test_initial_renders_main_content(self):
        html = self.srv.get_initial()
        assert "main-content" in html

    def test_initial_renders_columns(self):
        html = self.srv.get_initial()
        assert "st-columns" in html
        assert "Left Column" in html
        assert "Right Column" in html

    def test_initial_renders_tabs_with_headers(self):
        html = self.srv.get_initial()
        assert "st-tabs" in html
        assert "st-tab-headers" in html
        assert "Chart" in html
        assert "Data" in html

    def test_first_tab_content_is_active(self):
        html = self.srv.get_initial()
        # First tab content must have active class so it is visible
        assert "st-tab-content active" in html

    def test_initial_renders_expander(self):
        html = self.srv.get_initial()
        assert "st-expander" in html
        assert "Show more details" in html

    def test_initial_renders_horizontal_container(self):
        html = self.srv.get_initial()
        assert "st-container-horizontal" in html

    def test_interact_returns_full_layout(self):
        html = self.srv.post_interact()
        assert "main-content" in html
        assert "sidebar" in html

    def test_interact_with_checkbox_hides_metric(self):
        # Uncheck 'Show metrics'
        from mxlit.components.widgets import _generate_key
        key = _generate_key("Show metrics", "checkbox")
        html = self.srv.post_interact({key: "false"})
        # Metric should not appear
        assert "Users" not in html

    def test_buttons_have_no_duplicate_hx_post(self):
        html = self.srv.get_initial()
        # Buttons must NOT carry their own hx-post (the form handles it)
        # Find button elements and ensure they don't have hx-post
        import re
        buttons = re.findall(r'<button[^>]*>', html)
        for btn in buttons:
            assert 'hx-post' not in btn, f"Button should not have hx-post: {btn}"



# ---------------------------------------------------------------------------
# test_widgets.py sample
# ---------------------------------------------------------------------------

class TestWidgets:
    PORT = BASE_PORT + 2

    @pytest.fixture(autouse=True)
    def _server(self, server_factory):
        self.srv = server_factory("test_widgets.py", self.PORT)

    def test_initial_has_text_input(self):
        html = self.srv.get_initial()
        assert 'type="text"' in html
        assert "What is your name?" in html

    def test_initial_has_slider(self):
        html = self.srv.get_initial()
        assert 'type="range"' in html

    def test_initial_has_checkbox(self):
        html = self.srv.get_initial()
        assert 'type="checkbox"' in html

    def test_initial_has_buttons(self):
        html = self.srv.get_initial()
        assert "Click me!" in html
        assert "Increment Counter" in html

    def test_interact_updates_counter(self):
        from mxlit.components.widgets import _generate_key
        btn_key = _generate_key("Increment Counter", "button")
        html = self.srv.post_interact({btn_key: "true"})
        assert "main-content" in html
        assert "Counter" in html


# ---------------------------------------------------------------------------
# v2_demo.py sample (reactive callbacks)
# ---------------------------------------------------------------------------

class TestV2Demo:
    PORT = BASE_PORT + 3

    @pytest.fixture(autouse=True)
    def _server(self, server_factory):
        self.srv = server_factory("v2_demo.py", self.PORT)

    def test_initial_renders_sidebar_with_selectbox(self):
        html = self.srv.get_initial()
        assert 'class="sidebar"' in html
        assert "Select Region" in html

    def test_initial_renders_columns_with_metric(self):
        html = self.srv.get_initial()
        assert "st-columns" in html
        assert "st-metric" in html

    def test_interact_returns_updated_layout(self):
        html = self.srv.post_interact({"region": "East"})
        assert "main-content" in html


# ---------------------------------------------------------------------------
# demo_app.py sample (comprehensive)
# ---------------------------------------------------------------------------

class TestDemoApp:
    PORT = BASE_PORT + 4

    @pytest.fixture(autouse=True)
    def _server(self, server_factory):
        self.srv = server_factory("demo_app.py", self.PORT)

    def test_initial_renders_title(self):
        html = self.srv.get_initial()
        assert "Mxlit Advanced Demo" in html

    def test_initial_has_three_tabs(self):
        html = self.srv.get_initial()
        assert "Data Editor" in html
        assert "Streaming" in html

    def test_initial_tabs_first_is_active(self):
        html = self.srv.get_initial()
        assert "st-tab-content active" in html

    def test_initial_has_dashboard_metrics(self):
        html = self.srv.get_initial()
        assert "Total Views" in html
        assert "Active Users" in html

    def test_interact_ok(self):
        html = self.srv.post_interact()
        assert "main-content" in html
