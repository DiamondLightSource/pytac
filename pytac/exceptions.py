"""Module containing all the exceptions used in pytac."""


class FieldException(Exception):
    """Exception associated with invalid field requests.
    """
    pass


class HandleException(Exception):
    """Exception associated with requests with invalid handles.
    """
    pass


class DataSourceException(Exception):
    """Exception associated with Device misconfiguration or invalid requests to
        a data source.
    """
    pass


class UnitsException(Exception):
    """Conversion not understood.
    """
    pass


class ControlSystemException(Exception):
    """Exception associated with control system misconfiguration.
    """
    pass
