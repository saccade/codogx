"""Unit choices for knobs and readouts. Copy a panel to make another."""

panels = {
    'dog': dict(length='hand', mass='lump', gravity='dog/second',
                speed='cat', energy='thump',
                charge='coulomb', field='weber*stroke/sheet', force='push'),
    'SI': dict(length='meter', mass='kilogram', gravity='meter/second**2',
               speed='meter/second', energy='joule',
               charge='coulomb', field='tesla*stroke', force='newton'),
    'imperial': dict(length='foot', mass='pound', gravity='foot/second**2',
                     speed='foot/second', energy='foot*pound_force',
                     charge='coulomb', field='tesla*stroke', force='pound_force'),
}
