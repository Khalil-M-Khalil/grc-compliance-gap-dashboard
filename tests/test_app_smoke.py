from pathlib import Path

from streamlit.testing.v1 import AppTest


APP = Path(__file__).parents[1] / "app.py"


def test_dashboard_renders():
    app = AppTest.from_file(str(APP), default_timeout=10).run()
    assert not app.exception
    assert any("Compliance Gap Analysis Dashboard" in block.value for block in app.markdown)
    assert len(app.metric) >= 5
