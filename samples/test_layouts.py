import mxlit as mt

mt.title("Altlit Layouts Test")

with mt.sidebar:
    mt.header("Sidebar Settings")
    show_metrics = mt.checkbox("Show metrics", value=True)
    theme = mt.text_input("Theme", "Light")

mt.write("Welcome to the layouts test.")

if show_metrics:
    mt.metric("Users", 1024, "5%")

mt.header("Columns")
col1, col2 = mt.columns(2)

with col1:
    mt.subheader("Left Column")
    mt.write("This is the left side.")
    mt.button("Click Left")

with col2:
    mt.subheader("Right Column")
    mt.write("This is the right side.")
    mt.button("Click Right")

mt.header("Tabs")
tab1, tab2 = mt.tabs(["Chart", "Data"])

with tab1:
    mt.write("Imagine a chart here.")
    mt.slider("Chart sensitivity", 0, 100, 50)

with tab2:
    mt.write("Raw data goes here.")
    mt.json({"status": "ok", "data": [1, 2, 3]})

mt.header("Expander")
with mt.expander("Show more details"):
    mt.write("These are the hidden details inside the expander.")
    
mt.header("Horizontal Container")
with mt.container(horizontal=True):
    mt.button("Button A")
    mt.button("Button B")
    mt.button("Button C")
