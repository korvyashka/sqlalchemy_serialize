# coding: utf-8
from sqlalchemy_utils.functions import (
    get_columns, get_hybrid_properties
)
from .fields import SerializeField, SerializeCustomModelField


class SQLAlchemySerializator(object):
    fields = None
    hybrid_fields = None

    def __init__(
        self, extra_fields=None,
        extra_hybrid_fields=None,
    ):
        self.query_fields = []
        self.serialize_fields = []
        self.custom_serialize_fields = []

        self._init_query_fields(
            extra_fields=extra_fields,
            extra_hybrid_fields=extra_hybrid_fields,
        )
        self._init_serialize_fields()
        self._init_custom_serialize_fields()

    def _init_query_fields(
        self, extra_fields=None,
        extra_hybrid_fields=None,
    ):
        class_fields = self.__class__.fields or []
        extra_fields = extra_fields or []
        simple_fields = class_fields + extra_fields
        class_hybrid_fields = self.__class__.hybrid_fields or []
        extra_hybrid_fields = extra_hybrid_fields or []

        hybrid_fields = class_hybrid_fields + extra_hybrid_fields

        query_fields = simple_fields + hybrid_fields

        self.simple_fields = simple_fields
        self.hybrid_fields = hybrid_fields
        self.query_fields = query_fields

    def _init_serialize_fields(self):
        serialize_fields = []
        for field in self.query_fields:
            key = field.key or field.anon_label
            serialize_field = getattr(self, key, None)
            serialize_func = getattr(
                self, "serialize_{}".format(key), None
            )

            if serialize_field is None:
                serialize_field = SerializeField(
                    key,
                    func=serialize_func
                )
            else:
                if serialize_func is not None:
                    serialize_field.func = serialize_func

            serialize_fields.append(serialize_field)

        self.serialize_fields = serialize_fields

    def _init_custom_serialize_fields(self):
        self.custom_serialize_fields = filter(
            lambda x: isinstance(x, SerializeCustomModelField),
            self.__class__.__dict__.values()
        )

    def get_query_fields(self):
        return self.query_fields

    # deprecated
    def get_fields(self):
        return self.get_query_fields()

    def to_dict(self, raw, *custom_args, **custom_kwargs):
        result = {}
        for i, field in enumerate(self.serialize_fields):
            result[field.key] = field.serialize(raw[i])
        for field in self.custom_serialize_fields:
            result[field.key] = field.serialize(
                result, *custom_args, **custom_kwargs
            )
        return result


class SQLAlchemyModelSerializator(SQLAlchemySerializator):
    """
    Base serialize class.
    Can be used with dynamic fields.
    Class vars of type sqlalchemy.Column will be used
    as serializator fields if exists.

    # provide fields as *fields or model to introspect fields
    # or both
    >>> serializator = SqlAlchemySerializator(Guild.name)
    ...
    >>> data = serializator.to_dict(query_first_result)

    >>> serializator = SqlAlchemySerializator(model=Guild)

    :param fields: fields to serialize
    :type fields: list[sqlalchemy.Column]
    """
    fields = None
    hybrid_fields = None
    to_inspect_fields = True
    to_inspect_hybrid_fields = True
    model = None

    def __init__(
        self, extra_fields=None,
        extra_hybrid_fields=None,
        to_inspect_fields=None,
        to_inspect_hybrid_fields=None,
    ):
        self.model = self.__class__.model
        if not self.model:
            raise ValueError("set model class attribute")
        self.to_inspect_fields = False
        self.to_inspect_hybrid_fields = False

        super(SQLAlchemyModelSerializator, self).__init__(
            extra_fields=extra_fields,
            extra_hybrid_fields=extra_hybrid_fields,
        )

    def to_dict(self, raw, *custom_args, **custom_kwargs):
        """
        Return dict from sqlalchemy raw result.

        >>> serializator.to_dict(raw)
        >>> map(serializator.to_dict, query_filter_result)

        :param raw: iterable from sqlalchemy query
        :type raw: tuple|list

        :rtype: dict
        :return: serialized dict
        """
        result = {}
        if isinstance(raw, tuple):
            result = super(SQLAlchemyModelSerializator, self).to_dict(raw)
        else:
            for field in self.serialize_fields:
                result[field.key] = field.serialize(
                    getattr(raw, field.key)
                )
            for field in self.custom_serialize_fields:
                result[field.key] = field.serialize(
                    result, *custom_args, **custom_kwargs
                )
        return result

    def _init_query_fields(
        self, extra_fields=None,
        extra_hybrid_fields=None,
        to_inspect_fields=None,
        to_inspect_hybrid_fields=None,
    ):
        super(SQLAlchemyModelSerializator, self)._init_query_fields(
            extra_fields=extra_fields,
            extra_hybrid_fields=extra_hybrid_fields,
        )
        model = self.model
        if not self.simple_fields:
            class_to_inspect_fields = self.__class__.to_inspect_fields
            to_inspect_fields = (
                to_inspect_fields
                if to_inspect_fields is not None
                else class_to_inspect_fields
            )
            if to_inspect_fields:
                fields = get_columns(model).values()
                self.simple_fields.extend(fields)

        if not self.hybrid_fields:
            class_to_inspect_hybrid_fields = self.__class__.to_inspect_hybrid_fields
            to_inspect_hybrid_fields = (
                to_inspect_hybrid_fields
                if to_inspect_hybrid_fields is not None
                else class_to_inspect_hybrid_fields
            )
            if to_inspect_hybrid_fields:
                hybrid_properties = get_hybrid_properties(model)
                for key in hybrid_properties.keys():
                    field = getattr(model, key)

                    field.key = key
                    self.hybrid_fields.append(field)

        self.query_fields = self.simple_fields + self.hybrid_fields


class Sequence(object):
    # Not implemented
    pass
