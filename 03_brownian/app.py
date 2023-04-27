import math
from pathlib import Path

from brownian_motion import brownian_data, brownian_widget
from mediapipe import hand_to_camera_eye, info_smoother
from shiny import App, reactive, render, req, ui
import shiny.experimental as x
from shinywidgets import output_widget, register_widget

from shinymediapipe import input_hand
from smoother import reactive_smooth

# Check that JS prerequisites are installed
if not (Path(__file__).parent / "shinymediapipe" / "node_modules").is_dir():
    raise RuntimeError(
        "Mediapipe dependencies are not installed. "
        "Please run `npm install` in the 'shinymediapipe' subdirectory."
    )

# Set to True to see underlying XYZ values and canvas
debug = True

app_ui = x.ui.page_fillable(
    ui.h2("Brownian motion"),
    x.ui.layout_sidebar(
        x.ui.sidebar(
            ui.input_action_button("data_btn", "New Data"),
            ui.p(ui.input_switch("use_smoothing", "Smooth tracking", True)),
            (
                ui.div(ui.tags.strong("x:"), ui.output_text("x_debug", inline=True)),
                ui.div(ui.tags.strong("y:"), ui.output_text("y_debug", inline=True)),
                ui.div(ui.tags.strong("z:"), ui.output_text("z_debug", inline=True)),
            )
            if debug
            else None,
        ),
        output_widget("plot").add_class("html-fill-item"),
        fillable=True,
    ),
    input_hand("hand", debug=debug, throttle_delay_secs=0.05),
)


def server(input, output, session):
    # BROWNIAN MOTION ====

    @reactive.Calc
    def random_walk():
        """Generates brownian data whenever 'New Data' is clicked"""
        input.data_btn()
        return brownian_data(n=200)

    # Create Plotly 3D widget and bind it to output_widget("plot")
    widget = brownian_widget(600, 600)
    register_widget("plot", widget)

    @reactive.Effect
    def resize_widget():
        """Manually size the plotly widget to fill its container"""
        width = input[".clientdata_output_plot_width"]()
        height = input[".clientdata_output_plot_height"]()
        widget.update_layout(width=int(width), height=int(height))

    @reactive.Effect
    def update_plotly_data():
        walk = random_walk()
        layer = widget.data[0]
        layer.x = walk["x"]
        layer.y = walk["y"]
        layer.z = walk["z"]
        layer.marker.color = walk["z"]

    # HAND TRACKING ====

    @reactive.Calc
    def camera_info():
        """The eye position, as reflected by the hand input"""
        hand_val = input.hand()
        req(hand_val)

        res = hand_to_camera_eye(hand_val, detect_ok=True)
        req(res)
        return res

    # The raw data is a little jittery. Smooth it out by averaging a few samples
    @reactive_smooth(n_samples=5, smoother=info_smoother)
    @reactive.Calc
    def smooth_camera_info():
        return camera_info()

    @reactive.Effect
    def update_plotly_camera():
        """Update Plotly camera using the hand tracking"""
        info = smooth_camera_info() if input.use_smoothing() else camera_info()
        widget.layout.scene.camera.eye = info["eye"] if info is not None else None
        widget.layout.scene.camera.up = info["up"] if info is not None else None

    # DEBUGGING ====

    @output
    @render.text
    def x_debug():
        return camera_info()["eye"]["x"]

    @output
    @render.text
    def y_debug():
        return camera_info()["eye"]["y"]

    @output
    @render.text
    def z_debug():
        return camera_info()["eye"]["z"]


app = App(app_ui, server)
