# The Dog Math doc's own sentences, as checks.  Each says:
# this times that is a unit of the other.
from ledger import units as u, at, on, lever, stroke, lump, meter

def said(a, b, is_):
    return at(a, b) == is_

def test_saying_products():          # section 4
    assert said(lever, u['sweep'], u['cat'])        # 1 hand sweeping at 50
    assert said(lump, u['cat'], u['oompf'])         # 7 lump moving at 7 cat
    assert said(u['oompf'], lever, u['roll'])       # 2 oompf levered at 5 hand
    assert said(u['wheel'], u['sweep'], u['roll'])  # 0.5 wheel sweeping at 2
    assert said(u['crank'], u['sweep'], u['pow'])   # 1.5 crank sweeping at 2
    assert said(lump, lever, u['ponder'])           # 2 lump at 5 hand
    assert said(u['zing'], u['wheel'], u['thump'])  # 18 zing of half a wheel: hook
    assert said(lump, u['card'], u['wheel'])        # 2 lump across 2 card
    assert said(u['push'], meter, u['thump'])       # 4 push through 3 meter

def test_heft_takes_a_height_not_a_lever():
    # 0.1 ponder under 10 zoom: heft, 1 thump.  With a lever it cranks.
    assert said(u['ponder'], u['zoom'], u['crank'])
    assert said(at(lump, meter), u['zoom'], u['thump'])

def test_handy_facts():
    assert said(u['crank'], stroke, u['grunt'])
    assert u['grunt'] == u['thump']
    assert u['crank'] != u['thump']
    assert u['card'] != u['sheet']                   # same shape, different job
    assert on(u['crank'], u['wheel']) == u['pickup']
    assert on(u['roll'], u['wheel']) == u['sweep']
    assert u['shift'] == u['transit']

def test_ghosts():                    # section 6
    assert on(u['wheel'], lump) == u['card']         # profile
    assert said(u['card'], u['zing'], u['zump'])
    assert on(u['thump'], lump) == u['zip']
