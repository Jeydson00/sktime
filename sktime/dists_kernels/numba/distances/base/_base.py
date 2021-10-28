# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod

import numpy as np

from sktime.dists_kernels.numba.distances.base._types import DistanceCallable


class NumbaDistance(ABC):
    """Abstract class to define a numba compatible distance metric."""

    @staticmethod
    def distance(x: np.ndarray, y: np.ndarray, **kwargs: dict) -> float:
        """Compute the distance between two timeseries.

        Parameters
        ----------
        x: np.ndarray (2d array)
            First timeseries.
        y: np.ndarray (2d array)
            Second timeseries.
        kwargs: dict
            kwargs for the distance computation.

        Returns
        -------
        float
            Distance between x and y.
        """
        dist_callable = NumbaDistance.distance_factory(x, y, **kwargs)
        return dist_callable(x, y)

    def distance_factory(
        self, x: np.ndarray, y: np.ndarray, **kwargs: dict
    ) -> DistanceCallable:
        """Create a no_python distance.

        This method will validate the kwargs and ensure x and y are in the correct
        format and then return a no_python compiled distance that uses the kwargs.

        The no_python compiled distance will be in the form:
        Callable[[np.ndarray, np.ndarray], float]. #

        This can then be used to to calculate distances efficiently or can be used
        inside other no_python functions.

        Parameters
        ----------
        x: np.ndarray (2d array)
            First timeseries
        y: np.ndarray (2d array)
            Second timeseries
        kwargs: kwargs
            kwargs for the given distance metric

        Returns
        -------
        Callable[[np.ndarray, np.ndarray], float]
            Callable where two, numpy 2d arrays are taken as parameters (x and y),
            a float is then returned that represents the distance between x and y.
            This callable will be no_python compiled.

        Raises
        ------
        ValueError
            If x or y is not a numpy array.
            If x or y has less than or greater than 2 dimensions.
        RuntimeError
            If the distance metric could not be compiled to no_python.
        """
        NumbaDistance._validate_factory_timeseries(x)
        NumbaDistance._validate_factory_timeseries(y)

        no_python_callable = self._distance_factory(x, y, **kwargs)

        if not hasattr(no_python_callable, "signatures"):
            raise RuntimeError(
                "The distance metric specified could not be no_python"
                "compiled. Try again and if the problem persists raise"
                "an issue."
            )

        return no_python_callable

    @staticmethod
    def _validate_factory_timeseries(x: np.ndarray) -> None:
        """Ensure the timeseries are correct format.

        Parameters
        ----------
        x: np.ndarray (2d array)
            A timeseries to check.

        Raises
        ------
        ValueError
            If x is not a numpy array.
            If x has less than or greater than 2 dimensions.
        """
        if not isinstance(x, np.ndarray):
            raise ValueError(
                f"The array {x} is not a numpy array. Please ensure it"
                f"is a 2d numpy and try again."
            )

        if x.ndim != 2:
            raise ValueError(
                f"The array {x} has the incorrect number of dimensions."
                f"Ensure the array has exactly 2 dimensions and try "
                f"again."
            )

    @abstractmethod
    def _distance_factory(
        self, x: np.ndarray, y: np.ndarray, **kwargs: dict
    ) -> DistanceCallable:
        """Abstract method to create a no_python compiled distance.

        _distance_factory should validate kwargs and then compile a no_python callable
        that takes (x, y) as parameters and returns a float that represents the distance
        between the two timeseries.

        Parameters
        ----------
        x: np.ndarray (2d array)
            First timeseries
        y: np.ndarray (2d array)
            Second timeseries
        kwargs: kwargs
            kwargs for the given distance metric

        Returns
        -------
        Callable[[np.ndarray, np.ndarray], float]
            Callable where two, numpy 2d arrays are taken as parameters (x and y),
            a float is then returned that represents the distance between x and y.
            This callable will be no_python compiled.
        """
        ...

    @staticmethod
    @abstractmethod
    def _numba_distance(x, y) -> float:
        """Abstract method to define a no_python distance between two timeseries.

        Parameters
        ----------
        x: np.ndarray (2d array)
            First timeseries.
        y: np.ndarray (2d array)
            Second timeseries.

        Returns
        -------
        float
            Distance between x and y.
        """
        ...
