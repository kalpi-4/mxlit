import mxlit as mt
import pandas as pd
import time
import uuid

# Basic state setup
if "clicks" not in mt.session_state:
    mt.session_state["clicks"] = 0

if "form_submitted" not in mt.session_state:
    mt.session_state["form_submitted"] = False

# Sidebar Configuration
with mt.sidebar:
    mt.image("https://www.python.org/static/community_logos/python-logo-master-v3-TM.png", width=200)
    mt.title("Settings")
    
    theme = mt.text_input("Theme Name", value="Light")
    show_data = mt.checkbox("Show raw data", value=True)
    num_rows = mt.slider("Rows to show", 1, 10, 5)
    
    mt.markdown("---")
    if mt.button("Reset Settings"):
        mt.session_state["clicks"] = 0
        mt.session_state["form_submitted"] = False
        mt.rerun()

# Main Area
mt.title("Altlit Advanced Demo 🚀")
mt.write("Welcome to the comprehensive demo of **Altlit** featuring dashboards, NER, and streaming.")

# Layout: Columns with Metrics
mt.header("Dashboard Overview")
col1, col2, col3 = mt.columns(3)
with col1:
    mt.metric("Total Views", 1024 + mt.session_state["clicks"] * 10, "+12%")
with col2:
    mt.metric("Active Users", 256 + mt.session_state["clicks"], "-2%")
with col3:
    mt.metric("Server Load", f"{45 + mt.session_state['clicks'] % 10}%", "Stable")

# Layout: Tabs
mt.header("Interactive Analysis")
tab1, tab2, tab3 = mt.tabs(["AI & NLP", "Data Editor", "Streaming"])

with tab1:
    mt.subheader("Named Entity Recognition (NER)")
    mt.write("Highlighting recognized entities in a text snippet.")
    
    sample_text = "Apple is looking at buying U.K. startup for $1 billion. Tim Cook announced this in San Francisco."
    entities = [
        {"start": 0, "end": 5, "label": "ORG"},
        {"start": 27, "end": 31, "label": "GPE"},
        {"start": 44, "end": 54, "label": "MONEY"},
        {"start": 56, "end": 64, "label": "PERSON"},
        {"start": 83, "end": 96, "label": "GPE"}
    ]
    mt.ner_text(sample_text, entities)
    
    with mt.expander("Show raw code for NER"):
        mt.code("""sample_text = "Apple is looking at buying U.K. startup for $1 billion."
entities = [{"start": 0, "end": 5, "label": "ORG"}, ...]
mt.ner_text(sample_text, entities)""")

with tab2:
    mt.subheader("Data Interaction")
    if mt.button("Increment Counter"):
        mt.session_state["clicks"] += 1
        
    mt.write("Current Counter Value:", mt.session_state["clicks"])

    if show_data:
        # Generate some mock data using the slider value from the sidebar
        df = pd.DataFrame({
            "User": [f"User {i}" for i in range(num_rows)],
            "Score": [100 - i * 5 for i in range(num_rows)],
            "Status": ["Active" if i % 2 == 0 else "Inactive" for i in range(num_rows)]
        })
        mt.dataframe(df)
    else:
        mt.write("Raw data display is disabled in the sidebar settings.")

with tab3:
    mt.subheader("Text Streaming Component")
    mt.write("Click the button below to simulate streaming text.")
    
    if "stream_started" not in mt.session_state:
        mt.session_state["stream_started"] = False

    if mt.button("Start Streaming"):
        mt.session_state["stream_started"] = True
        mt.session_state["stream_key"] = str(uuid.uuid4())
        
    if mt.session_state.get("stream_started"):
        def my_generator():
            words = "This is a demonstration of the streaming text component in Altlit. It mimics server-sent events perfectly!".split(" ")
            for word in words:
                yield word + " "
        
        mt.write_stream(my_generator())
        mt.session_state["stream_started"] = False


mt.markdown("---")
mt.subheader("Contact Form")
# Simple form simulation
name = mt.text_input("Name", "")
if mt.button("Submit"):
    mt.session_state["form_submitted"] = True
    
if mt.session_state["form_submitted"]:
    if name:
        mt.html(f"<div style='padding:1rem;background-color:#d4edda;border-radius:0.5rem;'>Thank you, {name}! Your form was submitted.</div>")
    else:
        mt.html("<div style='padding:1rem;background-color:#f8d7da;border-radius:0.5rem;'>Please enter your name before submitting.</div>")

