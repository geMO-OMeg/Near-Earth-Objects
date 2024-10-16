"""Provide filters for querying close approaches and limit the generated results.

The `create_filters` function produces a collection of objects that is used by
the `query` method to generate a stream of `CloseApproach` objects that match
all of the desired criteria. The arguments to `create_filters` are provided by
the main module and originate from the user's command-line options.

This function can be thought to return a collection of instances of subclasses
of `AttributeFilter` - a 1-argument callable (on a `CloseApproach`) constructed
from a comparator (from the `operator` module), a reference value, and a class
method `get` that subclasses can override to fetch an attribute of interest from
the supplied `CloseApproach`.

The `limit` function simply limits the maximum number of values produced by an
iterator.
"""
from operator import eq, ge, le
import itertools

class UnsupportedCriterionError(NotImplementedError):
    """A filter criterion is unsupported."""


class AttributeFilter:
    """A general superclass for filters on comparable attributes.

    An `AttributeFilter` represents the search criteria pattern comparing some
    attribute of a close approach (or its attached NEO) to a reference value. It
    essentially functions as a callable predicate for whether a `CloseApproach`
    object satisfies the encoded criterion.

    It is constructed with a comparator operator and a reference value, and
    calling the filter (with __call__) executes `get(approach) OP value` (in
    infix notation).

    Concrete subclasses can override the `get` classmethod to provide custom
    behavior to fetch a desired attribute from the given `CloseApproach`.

    """

    def __init__(self, op, value):
        """Construct a new `AttributeFilter` from an binary predicate and a reference value.

        The reference value will be supplied as the second (right-hand side)
        argument to the operator function. For example, an `AttributeFilter`
        with `op=operator.le` and `value=10` will, when called on an approach,
        evaluate `some_attribute <= 10`.

        :param op: A 2-argument predicate comparator (such as `operator.le`).
        :param value: The reference value to compare against.
        """
        self.op = op
        self.value = value

    def __call__(self, approach):
        """Invoke `self(approach)`."""
        return self.op(self.get(approach), self.value)

    @classmethod
    def get(cls, approach):
        """Get an attribute of interest from a close approach.

        Concrete subclasses must override this method to get an attribute of
        interest from the supplied `CloseApproach`.

        :param approach: A `CloseApproach` on which to evaluate this filter.
        :return: The value of an attribute of interest, comparable to `self.value` via `self.op`.
        """
        raise UnsupportedCriterionError

    def __repr__(self):
        """Compare filter attribute."""
        return f"{self.__class__.__name__}(op=operator.{self.op.__name__}, value={self.value})"


"""
Subclasses of AttributeFilter which override its get() method to get an attribute of
interest from the supplied `CloseApproach`

Args: approach: a CloseApproach object
returns: an attribute of interest (date(datetime), distance(float), velocity(float), diameter(float) or hazard(bool))
"""
class DateFilter(AttributeFilter):
    """
    Filter to retrieve the date attribute from an approach.

    This class inherits from the AttributeFilter base class and 
    provides a method to extract the date from an approach's 
    time attribute.
    """

    @classmethod
    def get(cls, approach):
        """
        Get the date from the provided approach.

        Args:
            approach: An object that has a time attribute.

        Returns:
            The date component of the approach's time.
        """
        return approach.time.date()

class DistFilter(AttributeFilter):
    """
    Filter to retrieve the distance attribute from an approach.

    This class inherits from the AttributeFilter base class and 
    provides a method to extract the distance from an approach.

    """

    @classmethod
    def get(cls, approach):
        """
        Get the distance from the provided approach.

        Args:
            approach: An object that has a distance attribute.

        Returns:
            The distance of the approach.
        """
        return approach.distance

class VeloFilter(AttributeFilter):
    """
    Filter to retrieve the velocity attribute from an approach.

    This class inherits from the AttributeFilter base class and 
    provides a method to extract the velocity from an approach.

    """

    @classmethod
    def get(cls, approach):
        """
        Get the velocity from the provided approach.

        Args:
            approach: An object that has a velocity attribute.

        Returns:
            The velocity of the approach.
        """
        return approach.velocity 

class DiamFilter(AttributeFilter):
    """
    Filter to retrieve the diameter attribute from a near-Earth object (NEO).

    This class inherits from the AttributeFilter base class and 
    provides a method to extract the diameter from an approach's 
    neo attribute.

    """

    @classmethod
    def get(cls, approach):
        """
        Get the diameter from the provided approach's NEO.

        Args:
            approach: An object that has a neo attribute with a diameter.

        Returns:
            The diameter of the NEO associated with the approach.
        """
        return approach.neo.diameter

class HazFilter(AttributeFilter):
    """
    Filter to check if a near-Earth object (NEO) is hazardous.

    This class inherits from the AttributeFilter base class and 
    provides a method to determine if the NEO associated with 
    an approach is hazardous.

    """

    @classmethod
    def get(cls, approach):
        """
        Determine if the NEO associated with the approach is hazardous.

        Args:
            approach: An object that has a neo attribute with a hazardous flag.

        Returns:
            A boolean indicating whether the NEO is hazardous.
        """
        return approach.neo.hazardous


def create_filters(date=None, start_date=None, end_date=None,
                   distance_min=None, distance_max=None,
                   velocity_min=None, velocity_max=None,
                   diameter_min=None, diameter_max=None,
                   hazardous=None):
    """Create a collection of filters from user-specified criteria.
    
    Each of these arguments is provided by the main module with a value from the
    user's options at the command line. Each one corresponds to a different type
    of filter. For example, the `--date` option corresponds to the `date`
    argument, and represents a filter that selects close approaches that occured
    on exactly that given date. Similarly, the `--min-distance` option
    corresponds to the `distance_min` argument, and represents a filter that
    selects close approaches whose nominal approach distance is at least that
    far away from Earth. Each option is `None` if not specified at the command
    line (in particular, this means that the `--not-hazardous` flag results in
    `hazardous=False`, not to be confused with `hazardous=None`).

    The return value must be compatible with the `query` method of `NEODatabase`
    because the main module directly passes this result to that method. For now,
    this can be thought of as a collection of `AttributeFilter`s.

    :param date: A `date` on which a matching `CloseApproach` occurs.
    :param start_date: A `date` on or after which a matching `CloseApproach` occurs.
    :param end_date: A `date` on or before which a matching `CloseApproach` occurs.
    :param distance_min: A minimum nominal approach distance for a matching `CloseApproach`.
    :param distance_max: A maximum nominal approach distance for a matching `CloseApproach`.
    :param velocity_min: A minimum relative approach velocity for a matching `CloseApproach`.
    :param velocity_max: A maximum relative approach velocity for a matching `CloseApproach`.
    :param diameter_min: A minimum diameter of the NEO of a matching `CloseApproach`.
    :param diameter_max: A maximum diameter of the NEO of a matching `CloseApproach`.
    :param hazardous: Whether the NEO of a matching `CloseApproach` is potentially hazardous.
    :return: A collection of filters for use with `query`.
    """
    """
    filter_mappings: Maps each filter type to its corresponding filter class and operator.
    filter_values: Stores the values for each filter type.
    The loop iterates over filter_mappings, retrieves the filter value from filter_values, and checks if it's not None.
    If the value exists, it creates an instance of the corresponding filter class with the appropriate operator and value.
    """
    # Define mappings for each filter type
    filter_mappings = {
        'date': (DateFilter, eq),
        'start_date': (DateFilter, ge),
        'end_date': (DateFilter, le),
        'distance_min': (DistFilter, ge),
        'distance_max': (DistFilter, le),
        'velocity_min': (VeloFilter, ge),
        'velocity_max': (VeloFilter, le),
        'diameter_min': (DiamFilter, ge),
        'diameter_max': (DiamFilter, le),
        'hazardous': (HazFilter, eq)
    }

    # Define a dictionary of filter values
    filter_values = {
        'date': date,
        'start_date': start_date,
        'end_date': end_date,
        'distance_min': distance_min,
        'distance_max': distance_max,
        'velocity_min': velocity_min,
        'velocity_max': velocity_max,
        'diameter_min': diameter_min,
        'diameter_max': diameter_max,
        'hazardous': hazardous
    }

    filters = []

    # Iterate over filter mappings and add filters as needed
    for key, (filter_class, op) in filter_mappings.items():
        value = filter_values.get(key)
        if value is not None:
            filters.append(filter_class(op, value))

    return filters



def limit(iterator, n=None):
    """
    Produce a limited stream of values from an iterator.
    
    If `n` is 0 or None, don't limit the iterator at all.

    :param iterator: An iterator of values.
    :param n: The maximum number of values to produce.
    :yield: The first (at most) `n` values from the iterator.
    """
    if n is None or n == 0:
        yield from iterator
    else:
        # Iterate through the iterator and yield up to n values
        count = 0
        for item in iterator:
            if count >= n:
                break
            yield item
            count += 1
