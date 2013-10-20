"""

one kind of switch which switches when you stand on it
    * like a pressure plate


another kind of switch that you have to stand next to and activate
    * moving into the switch activates it


switch effects
    * make tile disappear when pressure plate is activated and
      reappear when it is deactivated
    * and vice-versa
     
    * also force fields can appear and disappear

A pressure plate is marked by a P on the map and may only be at z=0.

    "presure_plate_effect": [
        # Plate         Effect         And
        # Location      Location       State
        [[Px, Py, 0], [[E1x, E1y, E1z, OnOff], ...],
        ...
    ]

Effect locations must be treated as objects rather than as
static terrain tiles.

When a map is read in, the effect locations will be removed
from the .data1d array and put into the .objects dictionary.


"""

