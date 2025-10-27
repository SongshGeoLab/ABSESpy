#!/usr/bin/env python3
"""Test colormap issue"""

from enum import IntEnum

import numpy as np


# Test Enum to int conversion
class State(IntEnum):
    EMPTY = 0
    INTACT = 1
    BURNING = 2
    SCORCHED = 3


# Test with Enum keys
cmap_dict = {
    State.EMPTY: "black",
    State.INTACT: "green",
    State.BURNING: "orange",
    State.SCORCHED: "red",
}

print("Original dict keys:", list(cmap_dict.keys()))
print("Enum to int:", [int(k) for k in cmap_dict.keys()])

# Convert to int keys
int_cmap = {int(k): v for k, v in cmap_dict.items()}
print("Int dict:", int_cmap)

# Test sorted categories
categories = list(int_cmap.keys())
color_list = [int_cmap[c] for c in sorted(categories)]
print("Sorted categories:", sorted(categories))
print("Color list:", color_list)

# Simulate data
data = np.array([[1, 1, 1], [3, 3, 3]])
print("\nData values:", np.unique(data))
print("Data should map 1->green (index 1) and 3->red (index 3)")

# The problem: ListedColormap(color_list) with 4 colors
# But data has values 1 and 3
# Value 1 would map to index 1 (green) ✓
# Value 3 would map to index 3 (red) ✓
# This should work!
