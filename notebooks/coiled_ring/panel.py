"""Shared controls for both accounts; SI defaults and selectable units. Codex."""
import io
from dataclasses import replace
import ipywidgets as w
import numpy as np
from comparison import comparison_at
from ring import state_at
from display_units import UnitPicker, QuantitySlider, words

def explore(case, view, units=None):
    current = case
    picker = UnitPicker(['angle','length','current','sweep','force','torque','flux'], units)
    image = w.Image(format='png', layout=w.Layout(width='100%', max_width='1100px'))
    table, readout = w.HTML(), w.HTML()
    angle = QuantitySlider(picker,'angle','angle',np.arccos(4/5),0,2*np.pi,.02)
    heading = QuantitySlider(picker,'angle','heading',case.values['heading'],0,2*np.pi,.1)
    tube = QuantitySlider(picker,'length','tube',case.values['tube'],0,.4,.05)
    amperes = QuantitySlider(picker,'current','current',case.values['current'],-3,3,.5)
    speed = QuantitySlider(picker,'sweep','sweep',case.values['sweep'],.1,3,.1)
    windings = w.Dropdown(options=[2,5,12,25,36],value=case.windings,description='windings')
    arrows = w.Checkbox(value=True,description='Show local forces')
    play = w.Play(min=0,max=round(1000*2*np.pi/speed.si),step=80,interval=100)
    buttons = {name:w.Button(description=label) for name,label in
               [('triangle','3–4–5'),('aligned','Aligned'),('edge','Edge on')]}
    def show(change=None):
        view.display_units = picker.units
        time = angle.si/current.values['sweep']
        state = state_at(current,time)
        data = io.BytesIO()
        view.still(current,time,forces=arrows.value).save(data,'PNG')
        image.value = data.getvalue()
        table.value = comparison_at(current,time,units=picker.units)
        readout.value = (f'<b>{words(angle.si,"angle",picker.units)}</b> · '
             f'{state.time:.3f} s at {words(current.values["sweep"],"sweep",picker.units)}')
    def change_case(change=None):
        nonlocal current
        play.playing = False
        current = replace(case,heading=(heading.si,'rad'),windings=windings.value,
            tube=(tube.si,'meter'),current=(amperes.si,'ampere'),sweep=(speed.si,'rad/second'))
        play.max = round(1000*2*np.pi/speed.si)
        show()
    def choose(value):
        play.playing = False
        angle.set_si(value)
        show()
    play.observe(lambda change:angle.set_si(min(2*np.pi,speed.si*change['new']/1000)),names='value')
    for key,value in [('triangle',np.arccos(4/5)),('aligned',0),('edge',np.pi/2)]:
        buttons[key].on_click(lambda button,value=value:choose(value))
    angle.observe(show)
    arrows.observe(show,names='value')
    windings.observe(change_case,names='value')
    for control in (heading,tube,amperes,speed):control.observe(change_case)
    picker.on_change(lambda *args:show())
    show()
    panel = w.VBox([picker.widget,image,w.HBox([play,angle.slider,*buttons.values()]),
        w.HBox([windings,tube.slider]),w.HBox([heading.slider,amperes.slider]),
        w.HBox([speed.slider,arrows]),readout,table])
    panel.controls = dict(angle=angle.slider,play=play,heading=heading.slider,
        windings=windings,tube=tube.slider,current=amperes.slider,sweep=speed.slider,
        arrows=arrows,**buttons,units=picker.selectors)
    panel.comparison,panel.unit_picker,panel.time_link = table,picker,None
    return panel

