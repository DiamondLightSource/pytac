import pytac


class DeviceModel(object):

    def __init__(self):
        self._devices = {}
        self.units = pytac.ENG

    def add_device(self, field, device):
        self._devices[field] = device

    def get_device(self, field):
        return self._devices[field]

    def get_fields(self):
        return self._devices.keys()

    def get_pv_name(self, field, handle):
        return self._devices[field].get_pv_name(handle)

    def get_value(self, field, handle):
        print('getting value {}:{}'.format(field, handle))
        return self._devices[field].get_value(handle)

    def set_value(self, field, value):
        self._devices[field].set_value(value)
