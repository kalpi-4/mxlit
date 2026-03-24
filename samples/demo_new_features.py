import mxlit as mt

mt.title("Mxlit New Features Demo")
mt.write("This app demonstrates the newly added components in the mxlit library.")

mt.header("1. Text Components")
mt.subheader("LaTeX")
mt.latex(r"E = mc^2")
mt.latex(r"\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}")

mt.subheader("Badge")
mt.badge("New!")
mt.badge("Experimental")

mt.header("2. Media Components")
mt.logo("https://streamlit.io/images/brand/streamlit-mark-color.png")
mt.write("Logo displayed above")

mt.subheader("Audio & Video")
mt.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
mt.video("https://www.w3schools.com/html/mov_bbb.mp4")

mt.header("3. Input Widgets")
col1, col2 = mt.columns(2)

with col1:
    num = mt.number_input("Select a number", min_value=0, max_value=100, value=42)
    mt.write(f"Number selected: {num}")
    
    color = mt.color_picker("Pick a color", value="#ff4b4b")
    mt.write(f"Color selected: {color}")
    
    date = mt.date_input("Select a date", value="2024-01-01")
    mt.write(f"Date selected: {date}")
    
    is_toggled = mt.toggle("Enable advanced settings", value=True)
    mt.write(f"Toggled: {is_toggled}")

with col2:
    text_area_val = mt.text_area("Tell us about yourself", value="I love coding in Python!")
    mt.write(f"Text length: {len(text_area_val)} characters")
    
    radio_val = mt.radio("Choose your favorite framework", options=["Streamlit", "Mxlit", "FastAPI"], index=1)
    mt.write(f"Radio selected: {radio_val}")
    
    select_val = mt.selectbox("Choose a programming language", options=["Python", "JavaScript", "Rust", "Go"], index=0)
    mt.write(f"Dropdown selected: {select_val}")

mt.header("4. Status Messages")
mt.success("Operation completed successfully!")
mt.info("This is an informational message.")
mt.warning("Be careful with this action.")
mt.error("Something went wrong.")

try:
    1 / 0
except Exception as e:
    mt.exception(e)

mt.header("5. Charts")
mt.write("Note: These are stub implementations preparing the component tree.")
mt.line_chart([1, 5, 2, 6, 3])
mt.bar_chart({"A": 10, "B": 20, "C": 15})
mt.area_chart([10, 20, 10, 30])
mt.scatter_chart({"x": [1, 2, 3], "y": [4, 5, 6]})
