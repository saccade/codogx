"""Three experiments in capture, with SI defaults and selectable units. Codex."""
import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as w
from IPython.display import display, clear_output, HTML
from capture_behavior import CaptureLaw, prescribed, charge_pulse, driven
from display_units import UnitPicker, QuantitySlider, words

BLUE, RED, BROWN = '#24489c', '#a85147', '#80603f'
MODES = [('Constant capture','constant'),('Rippling capture','ripple'),('Bare ring','ring')]


def axes_grid(title):
    fig, ax = plt.subplots(2,2,figsize=(11,6.5),constrained_layout=True)
    fig.suptitle(title,color=BROWN,fontsize=16)
    for a in ax.flat:
        a.grid(alpha=.18)
    return fig,ax.flat


def plot_prescribed(law, picker=None, omega0=1., alpha=.2):
    u = picker or UnitPicker([])
    d = prescribed(law,omega0=omega0,alpha=alpha)
    fig,(a,b,c,e) = axes_grid('Turn the shaft: what changes when capture changes?')
    angle = u.value(d['theta'],'angle'); time = u.value(d['t'],'time')
    a.plot(angle,u.value(d['linkage'],'flux'),color=RED,label='actual linkage')
    a.plot(angle,u.value(d['frozen_linkage'],'flux'),'--',color=BLUE,label='freeze capture at the start')
    a.set(xlabel=u.label('shaft angle','angle'),ylabel=u.label('linkage','flux'));a.legend(fontsize=8)
    b.plot(angle,u.value(d['kappa'],'capture'),color=RED)
    b.set(xlabel=u.label('shaft angle','angle'),ylabel=u.label('capture','capture'))
    c.plot(time,u.value(d['voltage'],'voltage'),color=RED)
    c.set(xlabel=u.label('time','time'),ylabel=u.label('voltage drop','voltage'))
    e.plot(time,u.value(d['climb'],'climb'),color=RED,label='whole climb')
    e.plot(time,u.value(d['shortcut'],'climb'),'--',color=BLUE,label='capture of pickup alone')
    e.plot(time,u.value(d['extra'],'climb'),':',color=BROWN,label='changing-capture term')
    e.set(xlabel=u.label('time','time'),ylabel=u.label('voltage climb','climb'));e.legend(fontsize=8)
    display(fig);plt.close(fig)
    display(HTML('<p><b>Same power map throughout:</b> torque = κi; voltage drop = κω. '
                 'The climb is κ·pickup + (dκ/dθ)·sweep². Changing capture adds the second term.</p>'))
    return d


def plot_pulses(law,picker=None,charge=.2,inertia=.1,omega0=1.):
    u=picker or UnitPicker([])
    early=charge_pulse(law,charge=charge,center=.5,inertia=inertia,omega0=omega0)
    late=charge_pulse(law,charge=charge,center=2.5,inertia=inertia,omega0=omega0)
    fig,(a,b,c,d)=axes_grid('Same charge, delivered early or late to a free shaft')
    for data,color,name in [(early,BLUE,'early pulse'),(late,RED,'late pulse')]:
        t=u.value(data['t'],'time')
        a.plot(t,u.value(data['current'],'current'),color=color,label=name)
        b.plot(t,u.value(data['kappa'],'capture'),color=color,label=name)
        c.plot(u.value(data['q'],'charge'),u.value(data['added_spin'],'spin'),color=color,label=name)
        d.plot(t,u.value(data['added_spin'],'spin'),color=color,label=name)
    c.plot(u.value(early['q'],'charge'),u.value(early['frozen_spin'],'spin'),'--',color=BROWN,
           label='starting capture × charge')
    a.set(xlabel=u.label('time','time'),ylabel=u.label('current','current'));a.legend(fontsize=8)
    b.set(xlabel=u.label('time','time'),ylabel=u.label('capture','capture'))
    c.set(xlabel=u.label('charge passed','charge'),ylabel=u.label('spin added','spin'));c.legend(fontsize=8)
    d.set(xlabel=u.label('time','time'),ylabel=u.label('spin added','spin'))
    display(fig);plt.close(fig)
    residual=max(np.max(np.abs(x['energy_error'])) for x in [early,late])
    display(HTML(f'<p>Early: <b>{words(early["added_spin"][-1],"spin",u.units,7)}</b>; '
                 f'late: <b>{words(late["added_spin"][-1],"spin",u.units,7)}</b>. '
                 f'Each passes {words(charge,"charge",u.units)}. '
                 f'Maximum kinetic-energy/work residual: {words(residual,"energy",u.units,3)}.</p>'))
    return early,late


def plot_driven(law=None,picker=None,drive=1.2,duration=180.):
    u=picker or UnitPicker([])
    law=law or CaptureLaw('ring',1.)
    chosen=driven(law,drive=drive,duration=duration)
    constant=driven(CaptureLaw('constant',law.base),drive=drive,duration=duration)
    fig,(a,b,c,d)=axes_grid('Let the shaft answer: damping and a separate periodic torque drive')
    t=u.value(chosen['t'],'time')
    a.plot(t,u.value(chosen['omega'],'sweep'),color=RED,label=law.mode)
    a.plot(t,u.value(constant['omega'],'sweep'),color=BLUE,alpha=.7,label='constant capture')
    a.set(xlabel=u.label('time','time'),ylabel=u.label('sweep','sweep'));a.legend(fontsize=8)
    tail=chosen['t']>40
    wrapped=np.angle(np.exp(1j*chosen['theta']))
    b.scatter(u.value(wrapped[tail],'angle'),u.value(chosen['omega'][tail],'sweep'),s=.4,color=RED)
    b.set(xlabel=u.label('angle, wrapped','angle'),ylabel=u.label('sweep','sweep'),title='Motion after the start')
    p=chosen['poincare'];pw=np.angle(np.exp(1j*p[0]))
    c.scatter(u.value(pw,'angle'),u.value(p[1],'sweep'),s=16,color=RED)
    c.set(xlabel=u.label('angle, wrapped','angle'),ylabel=u.label('sweep','sweep'),title='Once per drive cycle')
    d.semilogy(t,np.maximum(chosen['separation'],1e-16),color=RED,label='nearby starts: '+law.mode)
    d.semilogy(t,np.maximum(constant['separation'],1e-16),color=BLUE,label='nearby starts: constant')
    d.set(xlabel=u.label('time','time'),ylabel='state separation (dimensionless)');d.legend(fontsize=8)
    display(fig);plt.close(fig)
    rate=chosen['lyapunov']
    display(HTML(f'<p>Finite-time tangent growth after the start: <b>{rate:.3f} per second</b> '
                 f'(constant-capture comparison: {constant["lyapunov"]:.3f}). '
                 f'Energy-ledger residual: {words(max(abs(chosen["energy_error"])),"energy",u.units,3)}. '
                 'The saved driven-ring example has positive growth, consistent with chaos. '
                 'For Bare ring, set the drive to zero to see it settle regularly.</p>'))
    return chosen,constant


def make_panel(kind,units=None):
    kinds=['angle','sweep','time','capture']
    kinds += {'prescribed':['flux','voltage','climb','pickup'],
              'pulses':['current','charge','spin','energy','inertia'],
              'driven':['torque','energy']}[kind]
    picker=UnitPicker(kinds,units)
    mode=w.Dropdown(options=MODES,value='ring' if kind=='driven' else 'constant',description='capture')
    out=w.Output(); controls=[mode]; quantities={}
    def add(name,unit,value,lo,hi,step):
        q=QuantitySlider(picker,unit,name,value,lo,hi,step)
        quantities[name]=q;controls.append(q.slider);return q
    base=add('capture scale','capture',1. if kind=='driven' else .5,.1,2.,.1)
    ripple=w.FloatSlider(value=.8,min=0,max=1,step=.1,description='ripple fraction',continuous_update=False)
    controls.append(ripple)
    if kind=='prescribed':
        speed=add('initial sweep','sweep',1.,.1,2.,.1)
        pickup=add('pickup','pickup',.2,0,1,.1)
    elif kind=='pulses':
        charge=add('charge per pulse','charge',.2,.02,.4,.02)
        inertia=add('shaft inertia','inertia',.1,.05,.5,.05)
        speed=add('initial sweep','sweep',1.,0,2.,.1)
    else:
        drive=add('drive torque','torque',1.2,0,1.5,.1)
        duration=add('duration','time',180.,60.,300.,30.)
    def render(change=None):
        law=CaptureLaw(mode.value,base.si,ripple.value)
        with out:
            clear_output(wait=True)
            if kind=='prescribed':plot_prescribed(law,picker,speed.si,pickup.si)
            elif kind=='pulses':plot_pulses(law,picker,charge.si,inertia.si,speed.si)
            else:plot_driven(law,picker,drive.si,duration.si)
    for q in quantities.values():q.observe(render)
    mode.observe(render,names='value');ripple.observe(render,names='value')
    picker.on_change(lambda *args:render())
    render()
    panel=w.VBox([picker.widget,w.GridBox(controls,layout=w.Layout(
        grid_template_columns='repeat(2, 440px)',grid_gap='4px')),out])
    panel.controls={'mode':mode,'ripple':ripple,**{k:v.slider for k,v in quantities.items()},'units':picker.selectors}
    panel.quantities=quantities;panel.unit_picker=picker;panel.refresh=render
    return panel


def explore_behavior(units=None):
    panels=[make_panel(name,units) for name in ['prescribed','pulses','driven']]
    tabs=w.Tab(children=panels)
    for i,title in enumerate(['1 · Turn it','2 · Pass charge','3 · Let it move']):tabs.set_title(i,title)
    tabs.panels=panels
    return tabs
