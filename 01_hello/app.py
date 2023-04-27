from shiny import App, render, ui
import shiny.experimental as x
import numpy as np
import matplotlib.pyplot as plt

app_ui = x.ui.page_fillable(
    ui.input_slider("n", "N", min=0, max=100, value=20),
    x.ui.output_plot("plot"),
)


def server(input, output, session):
    @output
    @render.plot(alt="A histogram")
    def plot():
        x = 20 * np.random.randn(input.n())
        plt.hist(x, bins=7, density=True)
        plt.xlim((-75, 75))


app = App(app_ui, server)
