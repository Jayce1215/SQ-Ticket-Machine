import gradio as gr
from gradio_calendar import Calendar
import datetime
def input(name, number, address, city, state, zip_code, symtop, image):
    # salutation = "Good morning" if is_morning else "Good evening"
    greeting = f"{name}'s symptoms are {symtop} and the address is {address}, {city}, {state}, {zip_code}"
    return greeting

def is_weekday(date: datetime.datetime):
    return date.weekday() < 5 

demo = gr.Interface(
    fn=input,
    inputs=["text", "text", "text", "text", "text", "text", "text", "image"],
    outputs=["text"],
)
demo.launch()
