"""
Represent models for near-Earth objects and their close approaches.

The `NearEarthObject` class represents a near-Earth object. Each has a unique
primary designation, an optional unique name, an optional diameter, and a flag
for whether the object is potentially hazardous.

The `CloseApproach` class represents a close approach to Earth by an NEO. Each
has an approach datetime, a nominal approach distance, and a relative approach
velocity.

A `NearEarthObject` maintains a collection of its close approaches, and a
`CloseApproach` maintains a reference to its NEO.

The functions that construct these objects use information extracted from the
data files from NASA, so these objects should be able to handle all of the
quirks of the data set, such as missing names and unknown diameters.
"""
from helpers import cd_to_datetime, datetime_to_str


class NearEarthObject:
    """
    A near-Earth object (NEO).

    An NEO encapsulates semantic and physical parameters about the object, such
    as its primary designation (required, unique), IAU name (optional), diameter
    in kilometers (optional - sometimes unknown), and whether it's marked as
    potentially hazardous to Earth.

    A `NearEarthObject` also maintains a collection of its close approaches -
    initialized to an empty collection, but eventually populated in the
    `NEODatabase` constructor.
    """
   
    def __init__(self, **info):
        """Create a new `NearEarthObject`.

        :param info: A dictionary of excess keyword arguments supplied to the constructor.
        """

        self.name = info.get('name')
        self.name = None if self.name in (' ', '') else self.name
        self.designation = info.get('designation')
        self.diameter = self.isDigitorNone(info.get('diameter'))
        self.hazardous = info.get('hazardous')

        # Create an empty initial collection of linked approaches.
        self.approaches = []

    def isDigitorNone(self, value):
        try:
            return float(value)
        except ValueError:
            return float('nan')
        

    @property
    def fullname(self):
        """Return a representation of the full name of this NEO."""
       
        if self.name:
            return f"{self.designation} ({self.name})"
        else:
            return self.designation

    def __str__(self):
        """Return `str(self)`."""
       
        hazardous_status = "is" if self.hazardous else "is not"
        return f"NEO {self.name} has a diameter of {self.diameter:.3f} km and {hazardous_status} potentially hazardous."

    def __repr__(self):
        """Return `repr(self)`, a computer-readable string representation of this object."""
        return (f"NearEarthObject(designation={self.designation!r}, name={self.name!r}, "
                f"diameter={self.diameter:.3f}, hazardous={self.hazardous!r})")

    def serialize(self):
        """Serialize the NEO attributes to a dictionary."""
        return {
            "designation": self.designation if self.designation else "",
            "name": self.name if self.name else "",
            "diameter_km": self.diameter if self.diameter is not None else float('nan'),
            "potentially_hazardous": self.hazardous
        }

class CloseApproach:
    """
    A close approach to Earth by an NEO.

    A `CloseApproach` encapsulates information about the NEO's close approach to
    Earth, such as the date and time (in UTC) of closest approach, the nominal
    approach distance in astronomical units, and the relative approach velocity
    in kilometers per second.

    A `CloseApproach` also maintains a reference to its `NearEarthObject` -
    initally, this information (the NEO's primary designation) is saved in a
    private attribute, but the referenced NEO is eventually replaced in the
    `NEODatabase` constructor.
    """

    def __init__(self, **info):
        """Create a new `CloseApproach`.

        :param info: A dictionary of excess keyword arguments supplied to the constructor.
        """
       
        self._designation = info.get('designation')
        self.time = cd_to_datetime(info.get('time'))
        self.distance = info.get('distance')
        if type(self.distance) is not float:
            self.distance = float(self.distance)
        self.velocity = info.get('velocity')
        self.neo = info.get('neo')

    @property
    def time_str(self):
        """
        Return a formatted representation of this `CloseApproach`'s approach time.

        The value in `self.time` should be a Python `datetime` object. While a
        `datetime` object has a string representation, the default representation
        includes seconds - significant figures that don't exist in our input
        data set.

        The `datetime_to_str` method converts a `datetime` object to a
        formatted string that can be used in human-readable representations and
        in serialization to CSV and JSON files.
        """

        if self.neo.name:
            return f"{datetime_to_str(self.time)}, {self._designation} ({self.neo.name})"
        else:
            return f"{datetime_to_str(self.time)})"

    def __str__(self):
        """Return `str(self)`."""
        return f"At {self.time_str!r}, {self._designation} ({self.neo.name})approaches Earth at a distance of {self.distance:.2f} au and a velocity of {self.velocity:.2f} km/s."
    
    def __repr__(self):
        """Return `repr(self)`, a computer-readable string representation of this object."""
        return (f"CloseApproach(time={self.time_str!r}, designation={self._designation}, distance={self.distance:.2f}, "
                f"velocity={self.velocity:.2f}, neo={self.neo!r})")

    def serialize(self):
        """Serialize the CloseApproach attributes to a dictionary."""
        return {
            "datetime_utc": datetime_to_str(self.time) if self.time else "",
            "distance_au": self.distance,
            "velocity_km_s": self.velocity
        }