import mxlit as mt
import pandas as pd

mt.title("Altlit Basic Components Test")

mt.header("Text Components")
mt.write("This is `mt.write()`. It can print multiple args:", 1, "two", 3.0)
mt.subheader("Subheader")
mt.text("This is fixed-width text created with mt.text().")
mt.markdown("**This is markdown**, but currently just renders raw text.")
mt.code("def foo():\n    print('bar')")
mt.html("<p style='color: blue'>This is raw HTML rendering.</p>")

mt.header("Data Components")
df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'City': ['New York', 'Paris', 'London']
})

mt.subheader("Dataframe")
mt.dataframe(df)

mt.subheader("Table")
mt.table(df.head(2))

mt.subheader("JSON")
mt.json({"foo": "bar", "baz": [1, 2, 3]})

mt.subheader("Metrics")
mt.metric("Temperature", "70 °F", "1.2 °F")
mt.metric("Wind Speed", "8 mph", "-2 mph")

