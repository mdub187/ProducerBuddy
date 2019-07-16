import yaml
import os

def load_yaml(filename = 'settings.yml'):
    return yaml.safe_load(open(filename))

def autoscroll(sbar, first, last):
    """Hide and show scrollbar as needed."""
    first, last = float(first), float(last)
    if first <= 0 and last >= 1:
        sbar.grid_remove()
    else:
        sbar.grid()
        sbar.set(first, last)
