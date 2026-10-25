"""A picture, its quantities, and a few knobs."""

import io
from dataclasses import replace

import ipywidgets as w

from ledger import number
from panels import panels
from pendulum import state_at


def explore(case, view):
    current = case
    image = w.Image(format='png', width=440)
    readout = w.HTML()
    system = w.Dropdown(options=list(panels), value='dog', description='units')
    zoom = w.FloatSlider(value=view.scale, min=3, max=7, step=0.25,
                         description='zoom', continuous_update=False)
    time = w.IntSlider(min=0, max=round(number(case.duration, 'second') * 100),
                       description='1/100 second')
    clock = w.Play(min=0, max=time.max, step=4, interval=40, description='Play')
    link = w.jslink((clock, 'value'), (time, 'value'))
    controls = dict(system=system, zoom=zoom, time=time, clock=clock)
    knobs = w.HBox()

    def show(change=None):
        t = time.value / 100
        state = state_at(current, t)
        data = io.BytesIO()
        view.draw(current, state).save(data, 'PNG')
        image.value = data.getvalue()
        chosen = panels[system.value]

        def say(value, source, target):
            return f'{float(number((value, source), target)):.3f} {target}'

        readout.value = (
            f'<b>{t:.2f} second</b><br><br>'
            f"heft: {say(state.heft, 'thump', chosen['energy'])}<br>"
            f"hook: {say(state.hook, 'thump', chosen['energy'])}<br>"
            f"total: {say(state.heft + state.hook, 'thump', chosen['energy'])}<br><br>"
            f"speed: {say(state.speed, 'cat', chosen['speed'])}<br>"
            f'angle: {state.angle:.3f} stroke<br>'
            f'sweep: {state.sweep:.3f} sweep'
        )

    def release_again(change):
        nonlocal current
        clock.playing = False
        chosen = panels[system.value]
        current = replace(case,
            length=(controls['length'].value, chosen['length']),
            mass=(controls['mass'].value, chosen['mass']),
            gravity=(controls['gravity'].value, chosen['gravity']),
            release=(controls['release'].value, 'stroke'))
        time.value = 0
        show()

    def choose_units(change=None):
        chosen = panels[system.value]
        limits = dict(length=(0.1, 1.2, 0.05, 'meter'),
                      mass=(0.1, 5, 0.1, 'lump'),
                      gravity=(1, 20, 1, 'zoom'),
                      release=(0, 2.6, 0.1, 'stroke'))
        for field, (low, high, step, source) in limits.items():
            unit = chosen.get(field, 'stroke')
            knob = w.FloatSlider(
                value=float(number(getattr(current, field), unit)),
                min=float(number((low, source), unit)),
                max=float(number((high, source), unit)),
                step=float(number((step, source), unit)),
                description=f'{field} · {unit}',
                style=dict(description_width='150px'),
                continuous_update=False)
            knob.observe(release_again, names='value')
            controls[field] = knob
        knobs.children = (
            w.VBox([controls['length'], controls['mass']]),
            w.VBox([controls['release'], controls['gravity']]),
        )
        show()

    def zoom_picture(change):
        view.scale = zoom.value
        show()

    time.observe(show, names='value')
    zoom.observe(zoom_picture, names='value')
    system.observe(choose_units, names='value')
    choose_units()
    panel = w.VBox([
        w.HBox([image, readout]), w.HBox([clock, time]),
        w.HBox([system, zoom]), knobs,
        w.HTML('A physical knob sets up a fresh release. Units and zoom keep the current instant.'),
    ])
    panel.controls = controls
    panel.readout = readout
    panel.time_link = link
    return panel
