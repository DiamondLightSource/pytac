from pytac.cs import ControlSystem
from pytac.exceptions import ControlSystemException
from cothread.catools import caget, caput, ca_nothing


class CothreadControlSystem(ControlSystem):
    """A control system using cothread to communicate with EPICS. N.B. this is
        the default control system.

    It is used to communicate over channel access with the hardware
    in the ring.

    **Methods:**
    """
    def __init__(self):
        pass

    def get_single(self, pv, throw=True):
        """Get the value of a given PV.

        Args:
            pv (string): The process variable given as a string. It can be a
                         readback or a setpoint PV.

        Returns:
            scalar: Represents the current value of the given PV.

        Raises:
            ControlSystemException: if it cannot connect to the specified PV.
        """
        try:
            return caget(pv, timeout=1.0, throw=True)
        except ca_nothing:
            if throw:
                raise ControlSystemException('cannot connect to {}'.format(pv))
            else:
                print('cannot connect to {}'.format(pv))
                return None

    def get_multiple(self, pvs, throw=True):
        """Get the value for given PVs.

        Args:
            pvs (list): A list of process variables, given as a strings. They
                         can be a readback or setpoint PVs.

        Returns:
            list: of scalars, representing the current values of the PVs.

        Raises:
            ControlSystemException: if it cannot connect to one or more PVs.
        """
        results = caget(pvs, timeout=1.0, throw=False)
        for result in results:
            if isinstance(result, ca_nothing):
                if throw:
                    raise ControlSystemException('cannot connect to {}'.format(result.name))
                else:
                    print('cannot connect to {}'.format(result.name))
                    result = None
        return results

    def set_single(self, pv, value, throw=True):
        """Set the value of a given PV.

        Args:
            pv (string): The PV to set the value of. It must be a setpoint PV.
            value (Number): The value to set the PV to.

        Raises:
            ControlSystemException: if it cannot connect to the specified PV.
        """
        try:
            caput(pv, value, timeout=1.0, throw=True)
        except ca_nothing:
            if throw:
                raise ControlSystemException('cannot connect to {}'.format(pv))
            else:
                print('cannot connect to {}'.format(pv))

    def set_multiple(self, pvs, values, throw=True):
        """Set the values for given PVs.

        Args:
            pvs (list): A list of PVs to set the values of. It must be a
                         setpoint PV.
            values (sequence): A list of the numbers to set no the PVs.

        Raises:
            ValueError: if the lists of values and PVs are diffent lengths.
            ControlSystemException: if it cannot connect to one or more PVs.
        """
        if len(pvs) != len(values):
            raise ValueError('Please enter the same number of values as PVs.')
        status = caput(pvs, values, timeout=1.0, throw=False)
        for stat in status:
            if not stat.ok:
                if throw:
                    raise ControlSystemException('cannot connect to {}'.format(stat.name))
                else:
                    print('cannot connect to {}'.format(stat.name))
