from functools import reduce
from ledger import at, one

kind = {}

def units_of(e):
    if e.is_Number: return one
    if e.is_Symbol: return kind[e]
    if e.is_Mul:    return reduce(at, map(units_of, e.args))
    if e.is_Pow:    return tuple(n * e.exp for n in units_of(e.base))
    if e.is_Add:
        found = {units_of(t) for t in e.args}
        assert len(found) == 1, found      # this is the check, not a guard
        return found.pop()
