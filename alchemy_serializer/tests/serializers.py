from sqlalchemy_serializer.serializers import (
    SQLAlchemySerializator,
    SQLAlchemyModelSerializator
)
from sqlalchemy_serializer.fields import SerializeCustomModelField

from .models import Guild


class GuildSimpleSerializer(SQLAlchemySerializator):
    fields = [
        Guild.name,
        Guild.gold,
        Guild.level,
        Guild.max_members,
        Guild.created_on,
    ]

    def serialize_created_on(self, value):
        return value.isoformat()


class GuildHybridSerializer(GuildSimpleSerializer):
    hybrid_fields = [
        Guild.is_rich.label('is_rich')
    ]


def gold_and_level(result):
    return "{gold}: {level}".format(
        gold=result['gold'],
        level=result['level']
    )


class GuildCustomSerializer(GuildSimpleSerializer):
    gold_and_level = SerializeCustomModelField(gold_and_level, 'gold_and_level')


class GuildModelSerializer(SQLAlchemyModelSerializator):
    pass


class GuildModelSerializerOff(SQLAlchemyModelSerializator):
    to_inspect_hybrid_fields = False