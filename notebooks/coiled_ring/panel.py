"""Shared controls for the two accounts. Codex."""

import io
from dataclasses import replace

import ipywidgets as w
import numpy as np
from comparison import comparison_at
from ring import state_at


def explore(case, view):
    current = case
    image = w.Image(format='png', layout=w.Layout(width='100%', max_width='1100px'))
    table = w.HTML()
    readout = w.HTML()
    angle = w.FloatSlider(min=0, max=2*np.pi, step=.02, value=np.arccos(4/5),
                          description='angle · stroke', readout_format='.3f',
                          continuous_update=False, layout=w.Layout(width='440px'),
                          style=dict(description_width='110px'))
    last_tick = round(1000*2*np.pi/case.values['sweep'])
    play = w.Play(min=0, max=last_tick, step=80, interval=100)
    link = w.link((play, 'value'), (angle, 'value'), transform=(
        lambda ms: min(2*np.pi, current.values['sweep']*ms/1000),
        lambda a: min(last_tick, round(1000*a/current.values['sweep']))))
    heading = w.FloatSlider(min=0, max=2*np.pi, step=.1, value=case.values['heading'],
                            description='heading · stroke', continuous_update=False,
                            style=dict(description_width='120px'))
    windings = w.Dropdown(options=[2, 5, 12, 25, 36], value=case.windings,
                          description='windings')
    tube = w.FloatSlider(min=0, max=4, step=.5, value=10*case.values['tube'],
                         description='tube · hand', continuous_update=False)
    current_slider = w.FloatSlider(min=-3, max=3, step=.5, value=case.values['current'],
                                   description='ampere', continuous_update=False)
    arrows = w.Checkbox(value=True, description='Show local forces')
    triangle = w.Button(description='3–4–5')
    aligned = w.Button(description='Aligned')
    edge = w.Button(description='Edge on')

    def show(change=None):
        time = angle.value/current.values['sweep']
        state = state_at(current, time)
        data = io.BytesIO()
        view.still(current, time, forces=arrows.value).save(data, 'PNG')
        image.value = data.getvalue()
        table.value = comparison_at(current, time)
        readout.value = (f'<b>{angle.value:.4f} stroke = {angle.value/(2*np.pi):.4f} turn</b>'
                         f' &nbsp; · &nbsp; {state.time:.3f} second at '
                         f'{current.values["sweep"]:g} sweep')

    def change_case(change):
        nonlocal current
        play.playing = False
        current = replace(case, heading=(heading.value, 'stroke'),
                          windings=windings.value, tube=(tube.value, 'hand'),
                          current=(current_slider.value, 'ampere'))
        show()

    def choose(value):
        play.playing = False
        angle.value = value
        show()

    triangle.on_click(lambda button: choose(np.arccos(4/5)))
    aligned.on_click(lambda button: choose(0))
    edge.on_click(lambda button: choose(np.pi/2))
    angle.observe(show, names='value')
    arrows.observe(show, names='value')
    for control in (heading, windings, tube, current_slider):
        control.observe(change_case, names='value')
    choose(np.arccos(4/5))
    panel = w.VBox([image, w.HBox([play, angle, triangle, aligned, edge]),
                    w.HBox([windings, tube]), w.HBox([heading, current_slider, arrows]),
                    readout, table])
    panel.controls = dict(angle=angle, play=play, heading=heading, windings=windings,
                          tube=tube, current=current_slider, arrows=arrows,
                          triangle=triangle, aligned=aligned, edge=edge)
    panel.comparison = table
    panel.time_link = link
    return panel
