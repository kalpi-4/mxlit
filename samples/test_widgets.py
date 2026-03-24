import mxlit as mt

mt.title("Mxlit Interactive Widgets Test")

# Test Text Input
name = mt.text_input("What is your name?", value="Alice")
mt.write("Hello,", name)

# Test Checkbox
show_details = mt.checkbox("Show details", value=False)
if show_details:
    mt.write("Here are some secret details.")

# Test Slider
age = mt.slider("How old are you?", 0, 120, 25)
mt.write("You are", age, "years old.")

# Test Button
if mt.button("Click me!"):
    mt.write("Button was clicked!")
else:
    mt.write("Button is not clicked.")

# Counter using session state
if "counter" not in mt.session_state:
    mt.session_state["counter"] = 0

if mt.button("Increment Counter"):
    mt.session_state["counter"] += 1

mt.metric("Counter", mt.session_state["counter"])
