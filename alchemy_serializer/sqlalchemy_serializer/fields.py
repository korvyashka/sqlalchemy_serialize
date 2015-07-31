class SerializeField(object):
    """
    Basic field for serialization.

    :param str name: override field.key
    :param function func: will be evaluated on result value
        - if None: will not change value
    """
    def __init__(
        self, key,
        func=None
    ):
        self.key = key
        self.func = func or self._zero_serialize

    def _zero_serialize(self, value):
        return value

    def serialize(self, value):
        """
        Serialize value with self.func

        :param object value:

        :rtype: object
        :return: serialized value
        """
        return self.func(value)


class SerializeCustomModelField(object):
    def __init__(
        self, func,
        key
    ):
        self.func = func
        self.key = key

    def serialize(self, instance, *args, **kwargs):
        """
        Serialize value with self.func

        :param object value:

        :rtype: object
        :return: serialized value
        """
        return self.func(instance, *args, **kwargs)
