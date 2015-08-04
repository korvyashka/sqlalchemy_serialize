# coding: utf-8
from sqlalchemy_utils.functions import (
    get_columns, get_hybrid_properties
)
from .fields import SerializeField, SerializeCustomModelField


class SQLAlchemySerializator(object):
    """
    Base serialize class.
    Class is intended to work only with group of fields.

    Fields are of 2 types:
        1. Common fields: any fields, that are understood
         by session query context.
         Provide label for each non-model field or hybrid field.

        .. code:: python

            SQLAlchemySerializator(
                (Model.some_int_field > 1).label('some_label')
            )

        3. Custom fields, that are evaluated on result raw as custom functions.

    To serialize field with custom function:
        define serialize_label(self, value) function.

    Example usecase:

    .. code:: python

        class User(Base):
            # ...
            name = Column(String(255), nullable=False, unique=True)
            age = Column(Integer)

            @hybrid_property
            def is_old(self):
                return self.age > 200

        class UserSerializator(SQLAlchemySerializator):
            fields = [
                User.name,
                User.is_old.label('old'),
            ]

            def serialize_name(self, value):
                return value.upper()

        serializator = UserSerializator()

        u = User(name='George', age=130)
        data = serializator.to_dict(u)
        # {'name': 'GEORGE', 'old': False}

        users = session.query(
            **serializator.get_query_fields
        ).all()
        data = map(serializator.to_dict, users)
    """
    fields = None

    def __init__(
        self, *extra_fields
    ):
        """
        Build serializer, based on class fields and extra_fields.

        .. code:: python

            serializator = SQLAlchemySerializator(
                (Account.unpaid < 1000).label('trusty'),
                (User.name == 'George').label('is_George')
            )

        :param tuple extra_fields:
            extra fields to extend class serializer fields
        """
        self.query_fields = []
        self.serialize_fields = []
        self.custom_serialize_fields = []

        self._init_query_fields(
            extra_fields=extra_fields,
        )
        self._init_serialize_fields()
        self._init_custom_serialize_fields()

    def _init_query_fields(
        self, extra_fields=None,
    ):
        class_fields = self.__class__.fields or []
        extra_fields = extra_fields or []
        query_fields = class_fields + list(extra_fields)

        self.query_fields = query_fields

    def _init_serialize_fields(self):
        serialize_fields = []
        for field in self.query_fields:
            key = field.key
            if not key:
                raise ValueError('provide label for all non-Model fields')
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
        """
        Return fields needed for query session.

        .. code:: python

            session.query(
                *serializator.get_query_fields()
            )

        :rtype: list
        :return: query fields
        """
        return self.query_fields

    # deprecated
    def get_fields(self):
        return self.get_query_fields()

    def to_dict(self, raw, *custom_args, **custom_kwargs):
        """
        Return dict from sqlalchemy raw result.

        .. code:: python

            serializator.to_dict(raw)
            map(serializator.to_dict, query_filter_result)

        :param raw: iterated query result
        :type raw: tuple|list

        :param custom_args:
            will be dispatched to custom_field functions
        :type custom_kwargs:
            will be dispatched to custom_field functions

        :rtype: dict
        :return: dict with keys associated to labels.
        """
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
    Extended class for SQLAlchemy models.

    Extended functionality:
    1. Can inspect fields and hybrid fields of provided models
    2. Can serialize not only tuples,
        but model instance too.

    .. code:: python

        serializer = SqlAlchemySerializator(
            model=User
        )
        user = session.query(User).first()
        data = serializer.to_dict(user)
    """
    fields = None
    to_inspect_fields = True
    to_inspect_hybrid_fields = True
    model = None

    def __init__(
        self, *extra_fields,
        **kwargs
    ):
        """
        Build model serializer.

        :param tuple extra_fields:
            extra fields to extend class serializer fields

        :param kwargs:
            class args: model, to_inspect_fields, to_inspect_hybrid_fields

        """
        self.model = self.__class__.model or kwargs.get('model', None)
        if not self.model:
            raise ValueError("set model class attribute")

        class_to_inspect_fields = self.__class__.to_inspect_fields
        instance_to_inspect_fields = kwargs.get('to_inspect_fields', None)

        to_inspect_fields = (
            instance_to_inspect_fields
            if instance_to_inspect_fields is not None
            else class_to_inspect_fields
        )
        self.to_inspect_fields = to_inspect_fields

        class_to_inspect_hybrid_fields = self.__class__.to_inspect_hybrid_fields
        instance_to_inspect_hybrid_fields = kwargs.get('to_inspect_hybrid_fields', None)

        to_inspect_hybrid_fields = (
            instance_to_inspect_hybrid_fields
            if instance_to_inspect_hybrid_fields is not None
            else class_to_inspect_hybrid_fields
        )
        self.to_inspect_hybrid_fields = to_inspect_hybrid_fields

        super(SQLAlchemyModelSerializator, self).__init__(
            *extra_fields
        )

    def to_dict(self, raw, *custom_args, **custom_kwargs):
        """
        Return dict from sqlalchemy raw result.

        .. code:: python

            serializator.to_dict(raw)
            map(serializator.to_dict, query_filter_result)

        :param raw: iterated query result(model or tuple)
        :type raw: tuple|list|Model

        :param custom_args:
            will be dispatched to custom_field functions
        :type custom_kwargs:
            will be dispatched to custom_field functions


        :rtype: dict
        :return: dict with keys associated to labels.
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
    ):
        super(SQLAlchemyModelSerializator, self)._init_query_fields(
            extra_fields=extra_fields,
        )
        model = self.model
        if not self.query_fields:
            if self.to_inspect_fields:
                fields = get_columns(model).values()
                self.query_fields.extend(fields)
            if self.to_inspect_hybrid_fields:
                hybrid_properties = get_hybrid_properties(model)
                for key in hybrid_properties.keys():
                    field = getattr(model, key)

                    field.key = key
                    self.query_fields.append(field)


class Sequence(object):
    # Not implemented
    pass
