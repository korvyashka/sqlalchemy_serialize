from sqlalchemy_serializer.serializers import (
    SQLAlchemySerializator,
    SQLAlchemyModelSerializator
)
from sqlalchemy_serializer.fields import SerializeCustomModelField

from .models import Guild


class GuildSimpleSerializer(SQLAlchemySerializator):
    fields = [
        Guild.id,
        Guild.name,
        Guild.gold,
        Guild.level,
        Guild.max_members,
        Guild.created_on,
    ]

    def serialize_created_on(self, value):
        return value.isoformat()


class GuildHybridSerializer(GuildSimpleSerializer):
    fields = [
        Guild.id,
        Guild.name,
        Guild.gold,
        Guild.level,
        Guild.max_members,
        Guild.created_on,
        Guild.is_rich.label('is_rich'),
    ]


def gold_and_level(result):
    return "{gold}: {level}".format(
        gold=result['gold'],
        level=result['level']
    )


class GuildCustomSerializer(GuildSimpleSerializer):
    gold_and_level = SerializeCustomModelField(gold_and_level, 'gold_and_level')


class GuildModelSerializer(SQLAlchemyModelSerializator):
    model = Guild

    def serialize_created_on(self, value):
        return value.isoformat()


class GuildModelSerializerOffHybrid(GuildModelSerializer):
    to_inspect_hybrid_fields = False
