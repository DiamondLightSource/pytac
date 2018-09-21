import logging
from types import NoneType
from pytac.cs import ControlSystem
from caproto.threading.client import Context, Batch


class CaprotoControlSystem(ControlSystem):
    def __init__(self):
        self._results = []
        logging.disable(logging.WARNING)

    def _append_result(self, response):
        """Append a result to the current list of results.

        Args:
            response (caproto class): The response from epics containing the
                                       result data.
        """
        self._results.append(response.data[0])

    def get_single(self, pv):
        """Get the value of a given PV.

        Args:
            pv (string): The process variable given as a string. It can be a
                         readback or a setpoint PV.

        Returns:
            float: Represents the current value of the given PV.
        """
        pv_object = Context().get_pvs(pv)[0]
        return pv_object.read().data[0]

    def get_multiple(self, pvs):
        """Get the value for given PVs.

        Args:
            pvs (list): A list of process variables, given as a strings. They
                         can be a readback or setpoint PVs.

        Returns:
            list: of floats, representing the current values of the PVs.

        Raises:
            ValueError: if the PVs are not passed in as a list.
        """
        if not isinstance(pvs, list):
            raise ValueError('Please enter PVs as a list.')
        self._results = []
        pv_objects = Context().get_pvs(*pvs)
        with Batch() as b:
            for pv_object in pv_objects:
                while isinstance(pv_object.channel, NoneType):
                    pass  # Wait until pv object is fully initialised.
                b.read(pv_object, self._append_result)
        while len(self._results) is not len(pvs):
            pass  # Wait for results to be returned.
        return self._results

    def set_single(self, pv, value):
        """Set the value of a given PV.

        Args:
            pv (string): The PV to set the value of. It must be a setpoint PV.
            value (Number): The value to set the PV to.
        """
        pv_object = Context().get_pvs(pv)[0]
        pv_object.write(value, wait=False)

    def set_multiple(self, pvs, values):
        """Set the values for given PVs.

        Args:
            pvs (list): A list of PVs to set the values of. It must be a
                         setpoint PV.
            values (list): A list of the numbers to set no the PVs.

        Raises:
            ValueError: if the PVs or values are not passed in as a list, or if
                         the lists of values and PVs are diffent lengths.
        """
        if not isinstance(pvs, list) or not isinstance(values, list):
            raise ValueError('Please enter PVs and values as a list.')
        elif len(pvs) != len(values):
            raise ValueError('Please enter the same number of values as PVs.')
        pv_objects = Context().get_pvs(*pvs)
        with Batch() as b:
            for pv_object, value in zip(pv_objects, values):
                while isinstance(pv_object.channel, NoneType):
                    pass  # Wait until pv object is fully initialised.
            b.write(pv_object, value)
