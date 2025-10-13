"""Module containing all the exceptions used in pytac."""


class FieldException(Exception):  # noqa: N818
    """Exception associated with invalid field requests."""

    pass


class HandleException(Exception):  # noqa: N818
    """Exception associated with requests with invalid handles."""

    pass


class DataSourceException(Exception):  # noqa: N818
    """Exception associated with Device misconfiguration or invalid requests to
    a data source.
    """

    pass


class UnitsException(Exception):  # noqa: N818
    """Conversion not understood."""

    pass


class ControlSystemException(Exception):  # noqa: N818
    """Exception associated with control system misconfiguration."""

    pass
