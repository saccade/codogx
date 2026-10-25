"""The two readings meet in this table. Codex."""

import numpy as np
from ring import state_at, torque_about_shaft, across_shaft
from display_units import selection, scaled, words


def reading(value, figures=5):
    return f'{0 if abs(value)<1e-9 else value:.{figures}g}'


def moment_reading(moment, unit):
    parts = []
    for axis, value in zip('xyz', moment):
        if abs(value)>1e-9:
            sense = 'positive' if value>0 else 'reverse'
            parts.append(f'{reading(abs(value), 4)} {unit} about {axis}, {sense} sense')
    return '; '.join(parts) or f'0 {unit}'


def torque_reading(case, value, unit, figures=5):
    if abs(value)<1e-9:
        return f'0 {unit}'
    sense = ('back toward alignment' if case.values['current']>0
             else 'toward opposite alignment')
    return f'{reading(abs(value), figures)} {unit} {sense}'


def flux_reading(value, figures=5, unit="weber"):
    if abs(value)<1e-9:
        return f'0 {unit}'
    sense = 'in the home sense' if value>0 else 'in the reverse sense'
    return f'{reading(abs(value), figures)} {unit} {sense}'


def comparison_at(case, time, units=None):
    units = selection(units)
    torque_unit = units["torque"]
    tf = lambda value: scaled(value, "torque", units)
    state = state_at(case, time)
    force, flux = state.forces, state.flux
    error = np.linalg.norm(force.moment-flux.moment)
    rows = [
        ('What gets added', 'Forces on wire pieces, then their leverage',
         'Signed shadow areas; flux gained by the area arrow’s sweep'),
        ('Net push', words(np.linalg.norm(force.net), 'force', units),
         '0 '+units['force']+' · a uniform field keeps the linked flux unchanged during translation'),
        ('Torque about the shaft', torque_reading(case, tf(torque_about_shaft(case, force.moment)), torque_unit),
         torque_reading(case, tf(flux.torque), torque_unit)),
        ('Across-shaft moment', moment_reading(tf(across_shaft(case, force.moment)), torque_unit),
         moment_reading(tf(across_shaft(case, flux.moment)), torque_unit)),
        ('Total moment · world axes', moment_reading(tf(force.moment), torque_unit),
         moment_reading(tf(flux.moment), torque_unit)),
        ('Linked flux', 'not used', flux_reading(scaled(flux.linked,"flux",units),unit=units["flux"])),
    ]
    body = ''.join(f'<tr><th style="text-align:left;padding:9px">{name}</th>'
                   f'<td style="padding:9px">{left}</td><td style="padding:9px">{right}</td></tr>'
                   for name, left, right in rows)
    return ('<table style="width:100%;border-collapse:collapse">'
            '<thead><tr style="border-bottom:1px solid #aaa"><th></th>'
            '<th style="color:#24489c;padding:10px">Usual · add the forces</th>'
            '<th style="color:#a85147;padding:10px">Straightforward · follow the flux</th>'
            '</tr></thead><tbody>'+body+'</tbody></table>'
            f'<p>Vector difference: {words(error, 'torque', units, 2)}. '
            'The flux account uses straight wire segments; refining them shrinks this difference. '
            'Positive axis sense follows the right-hand convention. '
            'The bearings balance any across-shaft moment; it is zero in this model. '
            'Changing heading changes the world components of the same torque about the shaft.</p>')

