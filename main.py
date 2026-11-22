
import ast
import operator

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Line


Window.clearcolor = get_color_from_hex("#09091D")

PURPLE = "#853BEB"
LIGHT_PURPLE = "#BD83FF"
DARK = "#17152F"
WHITE = "#F8F3FF"


# Safe mathematical evaluator
def safe_calculate(expression):
    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant):
            if type(node.value) in (int, float):
                return node.value
            raise ValueError("Invalid number")

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)

            if op_type not in allowed_operators:
                raise ValueError("Invalid operation")

            left = evaluate(node.left)
            right = evaluate(node.right)

            if op_type is ast.Pow and abs(right) > 10:
                raise ValueError("Number too large")

            return allowed_operators[op_type](left, right)

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)

            if op_type not in allowed_operators:
                raise ValueError("Invalid operation")

            return allowed_operators[op_type](evaluate(node.operand))

        raise ValueError("Invalid expression")

    tree = ast.parse(expression, mode="eval")
    result = evaluate(tree)

    if not isinstance(result, (int, float)):
        raise ValueError("Invalid result")

    if abs(result) > 1e100:
        raise ValueError("Result too large")

    return result


class NeonButton(Button):

    def __init__(self, fill=DARK, **kwargs):
        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)

        self.color = get_color_from_hex(WHITE)
        self.font_size = dp(23)

        self.fill = get_color_from_hex(fill)

        self.bind(pos=self.draw, size=self.draw)
        self.draw()

    def draw(self, *args):
        self.canvas.before.clear()

        with self.canvas.before:
            Color(*self.fill)

            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(18)]
            )

            Color(*get_color_from_hex("#A76BFF"))

            Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    dp(18)
                ),
                width=1
            )


class PremiumCalculator(App):

    title = "Clyra"

    def build(self):

        self.expression = ""

        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(3)
        )

        root = BoxLayout(
            orientation="vertical",
            padding=dp(14),
            spacing=dp(12),
            size_hint_y=None
        )

        root.bind(minimum_height=root.setter("height"))

        # HEADER

        header = Label(
            text="[b]♛ PREMIUM[/b]\n[color=#BD83FF]CALCULATOR[/color]",
            markup=True,
            font_size=dp(25),
            size_hint_y=None,
            height=dp(85)
        )

        root.add_widget(header)

        # DISPLAY

        self.display = TextInput(
            text="0",
            readonly=True,
            multiline=False,
            halign="right",
            font_size=dp(38),
            size_hint_y=None,
            height=dp(90),
            background_normal="",
            background_active="",
            background_color=get_color_from_hex(DARK),
            foreground_color=get_color_from_hex(WHITE),
            padding=[dp(15), dp(20)]
        )

        root.add_widget(self.display)

        # CALCULATOR BUTTONS

        keys = [
            ["C", "(", ")", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "−"],
            ["1", "2", "3", "+"],
            ["0", ".", "%", "="]
        ]

        keypad = GridLayout(
            cols=4,
            spacing=dp(9),
            size_hint_y=None,
            height=dp(310)
        )

        for row in keys:
            for key in row:

                color = (
                    PURPLE
                    if key in ["÷", "×", "−", "+", "="]
                    else DARK
                )

                if key == "C":
                    color = "#71345F"

                button = NeonButton(
                    text=key,
                    fill=color
                )

                button.bind(on_press=self.press)

                keypad.add_widget(button)

        root.add_widget(keypad)

        # TVA SECTION

        heading = Label(
            text="[b]✦ TVA CALCULATOR ✦[/b]",
            markup=True,
            color=get_color_from_hex(LIGHT_PURPLE),
            font_size=dp(21),
            size_hint_y=None,
            height=dp(48)
        )

        root.add_widget(heading)

        fields = BoxLayout(
            spacing=dp(10),
            size_hint_y=None,
            height=dp(65)
        )

        self.ht_input = TextInput(
            hint_text="Montant HT",
            multiline=False,
            input_filter="float",
            font_size=dp(18),
            background_normal="",
            background_active="",
            background_color=get_color_from_hex(DARK),
            foreground_color=get_color_from_hex(WHITE),
            hint_text_color=get_color_from_hex(LIGHT_PURPLE),
            padding=[dp(12), dp(18)]
        )

        self.rate_input = TextInput(
            text="20",
            hint_text="TVA %",
            multiline=False,
            input_filter="float",
            font_size=dp(18),
            background_normal="",
            background_active="",
            background_color=get_color_from_hex(DARK),
            foreground_color=get_color_from_hex(WHITE),
            hint_text_color=get_color_from_hex(LIGHT_PURPLE),
            padding=[dp(12), dp(18)]
        )

        fields.add_widget(self.ht_input)
        fields.add_widget(self.rate_input)

        root.add_widget(fields)

        # TVA BUTTON

        calculate = NeonButton(
            text="✦  CALCULER TVA  ✦",
            fill=PURPLE,
            size_hint_y=None,
            height=dp(58)
        )

        calculate.font_size = dp(20)
        calculate.bind(on_press=self.calculate_tva)

        root.add_widget(calculate)

        # TVA RESULT

        self.result = Label(
            text="TVA : 0.00       |       TTC : 0.00",
            color=get_color_from_hex(WHITE),
            font_size=dp(16),
            size_hint_y=None,
            height=dp(48)
        )

        root.add_widget(self.result)

        scroll.add_widget(root)

        return scroll

    # CALCULATOR LOGIC

    def press(self, instance):

        key = instance.text

        if key == "C":
            self.expression = ""
            self.display.text = "0"
            return

        if key == "=":

            try:
                if not self.expression:
                    return

                expression = (
                    self.expression
                    .replace("÷", "/")
                    .replace("×", "*")
                    .replace("−", "-")
                    .replace("%", "/100")
                )

                result = safe_calculate(expression)

                if isinstance(result, float) and result.is_integer():
                    result = int(result)

                self.expression = str(result)
                self.display.text = self.expression

            except (ValueError, SyntaxError, ZeroDivisionError, OverflowError):
                self.expression = ""
                self.display.text = "Error"

            return

        if self.display.text == "Error":
            self.expression = ""

        self.expression += key
        self.display.text = self.expression

    # TVA CALCULATOR

    def calculate_tva(self, instance):

        try:
            ht = float(self.ht_input.text)
            rate = float(self.rate_input.text)

            if ht < 0 or rate < 0:
                raise ValueError

            tva = ht * rate / 100
            ttc = ht + tva

            self.result.text = (
                f"TVA : {tva:.2f}    |    TTC : {ttc:.2f}"
            )

        except ValueError:
            self.result.text = "Enter valid amounts"


if __name__ == "__main__":
    PremiumCalculator().run()
