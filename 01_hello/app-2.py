from shiny import App, reactive, render, ui
import shiny.experimental as x
import numpy as np
import matplotlib.pyplot as plt

app_ui = x.ui.page_fillable(
    x.ui.layout_sidebar(
        x.ui.sidebar(
            ui.input_slider("n", "Observations", min=0, max=100, value=20),
            ui.input_slider("bins", "Bins", min=0, max=20, value=7),
        ),
        x.ui.output_plot("plot"),
    )
)


def server(input, output, session):
    @reactive.Calc
    def random_sample():
        return np.random.randn(input.n())

    @output
    @render.plot(alt="A histogram")
    def plot():
        plt.hist(random_sample(), bins=input.bins(), density=True)
        plt.xlim((-4, 4))


app = App(app_ui, server)
