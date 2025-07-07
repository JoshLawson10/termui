from termui import *
import time


class ScreenOne(Screen):
    def setup(self) -> None:
        self.initialize_screen(
            name="My Custom Screen",
            cols=5,
            rows=12,
        )
        """Setup the screen with initial Divs."""
        div1 = Div(
            name="Header",
            start_col=1,
            end_col=3,
            start_row=1,
            end_row=3,
            border=True,
            title="Header",
            align_title="left",
        )
        div2 = Div(
            name="Content",
            start_col=1,
            end_col=5,
            start_row=4,
            end_row=10,
            border=True,
            title="Content",
            align_title="center",
        )
        div3 = Div(
            name="Footer",
            start_col=1,
            end_col=5,
            start_row=11,
            end_row=12,
            border=True,
            title="Footer",
            align_title="right",
        )

        self.add(div1)
        self.add(div2)
        self.add(div3)

        div1.set_content("Header Content")
        div2.set_content(
            ["Line 1 of Content", "Line 2 of Content", "Line 3 of Content"]
        )
        div3.set_content([["F", "o", "o", "t", "e", "r"], ["Footer Line 2"]])


class ScreenTwo(Screen):
    def setup(self) -> None:
        self.initialize_screen(
            name="Second Screen",
            cols=3,
            rows=6,
        )
        """Setup the second screen with initial Divs."""
        div1 = Div(
            name="Second Header",
            start_col=1,
            end_col=3,
            start_row=1,
            end_row=2,
            border=True,
            title="Second Header",
            align_title="left",
        )
        self.add(div1)
        div1.set_content("This is the second screen header.")


class Application(App):
    def setup(self) -> None:
        """Setup the application with initial screens."""
        self.register_screen(ScreenOne())
        self.register_screen(ScreenTwo())

    def update(self) -> None:
        self.show_screen(ScreenOne().name)
        time.sleep(2)
        self.show_screen(ScreenTwo().name)


if __name__ == "__main__":
    app = Application()
    app.run()
