from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
import math
from kivy.config import Config
import threading
from pynput.keyboard import Listener, Controller, Key

keyboard = Controller()

run = True


# Thread decorator
def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper


# Set the window's dimensions
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '550')


# Main Layout
class MainLayout(BoxLayout):
    display_text = StringProperty("0")
    text = StringProperty("0")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Start the keylog function in another thread
        self.keylog()

    # Button click event handler for 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, ), . buttons
    def on_button_click(self, widget):
        if self.display_text == "0" or self.display_text == "ERROR" or self.text[-1] == "=":
            self.display_text = widget
            self.text = widget if self.text == "0" or self.display_text == "ERROR" or self.text[-1] == "=" else self.text
        elif len(self.display_text) < self.width/36 and len(self.text) < 33:
            self.display_text += widget
            self.text += widget if not any([i in self.text for i in ("+", "-", "/", "x", "^", "*")]) else ""

    # Button click event handler for + , -, x, /, ^ buttons
    def mathematical_operation(self, widget):
        if self.display_text == "ERROR":
            self.text = "0"
            self.display_text = "0"
        if self.display_text == "0" or self.display_text == "ERROR" or self.text[-1] == "=":
            self.text = self.display_text + widget if any([i in self.text for i in ("+", "-", "/", "x", "^", "*")]) else "0" + widget
        else:
            self.text += self.display_text + widget if any([i in self.text for i in ("+", "-", "/", "x", "^", "*")]) else widget
        self.display_text = "0"

    # Evaluate the mathematical expression when '=' button is pressed
    def compute(self):
        try:
            if (self.display_text == "0" and self.text == "0") or self.display_text == "ERROR" or self.text[-1] == "=":
                self.text = self.display_text if self.text[-1] == "=" else "0" + self.display_text if any([i in self.text for i in ("+", "-", "/", "x", "^")]) else "0"
            else:
                self.text += self.display_text if any([i in self.text for i in ("+", "-", "/", "x", "^", "*")]) else ""

            exec(f'exp = {self.text.replace("x", "*").replace("^", "**")}', globals())
            x = self.width//36 - len(str(exp).split(".")[0]) - 2

            res = int(exp) if exp == int(exp) else exp

            if len(str(res)) >= self.width/36:
                self.display_text = f"{res:e}"
            else:
                self.display_text = str(round(res, x))

        except ZeroDivisionError:
            self.display_text = "ERROR"
        self.text += "="

    # Backspace
    def backspace(self):
        if self.display_text != "0" and self.display_text != "ERROR":
            self.display_text = self.display_text[:-1] if len(self.display_text) != 1 else "0"
            if not any([i in self.text for i in ("+", "-", "/", "x", "^", "*")]):
                self.text = self.text[:-1] if len(self.text) != 1 else "0"

    # Clear the main display
    def clear(self):
        self.display_text = "0"
        if not any([i in self.text for i in ("+", "-", "/", "x", "^", "*")]):
            self.text = "0"

    # Clear Everything
    def clear_all(self):
        self.display_text = "0"
        self.text = "0"

    # Event handler for +/- button
    def add_sign(self):
        if self.display_text != "0":
            if self.display_text[0] != "-":
                self.display_text = "-" + self.display_text
            else:
                self.display_text = self.display_text[1:]

    # Mathematical constant pi
    def add_pi(self):
        if self.display_text == "0":
            self.display_text = str(math.pi)[:8]
        else:
            if self.display_text == "0" or self.display_text == "ERROR" or self.text[-1] == "=":
                self.text = self.display_text + "x" if any([i in self.text for i in ("+", "-", "/", "x", "^", "*")]) else "0" + "x"
            else:
                self.text += self.display_text + "x" if any([i in self.text for i in ("+", "-", "/", "x", "^", "*")]) else "x"
            self.display_text = str(math.pi)[:8]

    # Opening parenthesis
    def parenthesis(self):
        if self.display_text != "0":
            if self.display_text == "0" or self.display_text == "ERROR" or self.text[-1] == "=":
                self.text = self.display_text + "x" if any([i in self.text for i in ("+", "-", "/", "x", "^", "*")]) else "0" + "x"
            else:
                self.text += self.display_text + "x" if any([i in self.text for i in ("+", "-", "/", "x", "^", "*")]) else "x"
            self.display_text = "0"
            self.text += "("
        else:
            self.display_text = "("
            self.text = "("

    # New thread to handle key presses
    @threaded
    def keylog(self):

        def on_press(key):

            try:
                key = key.char

                if key in "0123456789.)":
                    self.on_button_click(key)
                elif key in "+-*x/^":
                    self.mathematical_operation(key)
                elif key == "(":
                    self.parenthesis()
                elif key == "=":
                    self.compute()
                else:
                    pass

            except AttributeError:
                if key == Key.backspace:
                    self.backspace()
                elif key == Key.enter:
                    self.compute()
                else:
                    pass

        def on_release(key):
            global run
            return run

        with Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()


# App
class CalculatorApp(App):
    pass


# Start the app
CalculatorApp().run()

# Stop the second thread when window is closed
run = False
keyboard.tap('q')
