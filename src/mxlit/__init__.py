import sys

from mxlit.context import get_context
from mxlit.state import session_state
from mxlit.components.text import write, title, header, subheader, text, markdown, code, html, write_stream, ner_text, latex, badge
from mxlit.components.data import dataframe, table, json, metric
from mxlit.components.widgets import button, text_input, checkbox, slider, number_input, text_area, radio, selectbox, toggle, color_picker, date_input
from mxlit.components.layout import sidebar, columns, tabs, expander, container
from mxlit.components.media import image, audio, video, logo
from mxlit.components.charts import line_chart, bar_chart, area_chart, scatter_chart
from mxlit.components.status import error, warning, info, success, exception

def stop():
    """Stop execution immediately."""
    sys.exit(0)

def rerun():
    """Rerun script immediately."""
    # Since we are reacting to HTMX, we can signal the server to rerun.
    # We could implement a custom exception that the server catches to trigger a rerun,
    # but for simplicity, raising an exception stops the script, and since the state is already updated,
    # the frontend state is consistent. In a true implementation, we'd raise a StopException,
    # catch it in `server.py`, and return the current component tree without rendering the error.
    class RerunException(Exception):
        pass
    raise RerunException("Rerun triggered")
