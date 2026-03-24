import mxlit as mt

mt.title("Testing New Components")

mt.header("Text")
mt.latex("E = mc^2")
mt.badge("New Feature!")

mt.header("Media")
mt.logo("https://example.com/logo.png")
mt.audio("https://example.com/audio.mp3")
mt.video("https://example.com/video.mp4")

mt.header("Widgets")
num = mt.number_input("Enter a number", min_value=0, max_value=10, value=5)
mt.write("Number is:", num)

text = mt.text_area("Enter text", value="Hello")
mt.write("Text is:", text)

rad = mt.radio("Choose", ["A", "B"], index=0)
mt.write("Radio is:", rad)

sel = mt.selectbox("Select", ["X", "Y"], index=0)
mt.write("Select is:", sel)

tog = mt.toggle("Enable something", value=True)
mt.write("Toggle is:", tog)

mt.header("Charts")
mt.line_chart([1, 2, 3])
mt.bar_chart([1, 2, 3])
mt.area_chart([1, 2, 3])
mt.scatter_chart([1, 2, 3])

mt.header("Status")
mt.error("This is an error")
mt.warning("This is a warning")
mt.info("This is an info")
mt.success("This is a success")
try:
    1 / 0
except Exception as e:
    mt.exception(e)

mt.header("More Widgets")
mt.color_picker("Pick a color", "#ff0000")
mt.date_input("Pick a date", "2024-01-01")
