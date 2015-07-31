import datetime

from sqlalchemy import (
    Column, DateTime, ForeignKey, Integer, String,
    Boolean, Text, update
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from sqlalchemy_serializer import Base
from sqlalchemy_serializer.decorators import sessioned


class Guild(Base):
    """
    Guild model
    """
    __tablename__ = 'guild'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    gold = Column(
        Integer, nullable=False,
        default=0
    )
    level = Column(
        Integer, nullable=False,
        default=1
    )
    max_members = Column(Integer, nullable=False)

    created_on = Column(
        DateTime, nullable=False,
        default=datetime.datetime.now
    )

    @sessioned
    def add_member(
        self,
        name='test',
        gold=0,
        session=None,
        commit=True
    ):
        member = GuildMember(
            guild=self,
            name=name,
            gold=gold,
        )
        session.add(member)
        session.commit()

        return member

    @hybrid_property
    def is_rich(self):
        """
        :rtype: bool
        :return:
        """
        return self.gold > 100500

    def to_dict(self):
        return {
            'name': self.name,
            'gold': self.gold,
            'level': self.level,
            'max_members': self.max_members,
            'created_on': self.created_on.isoformat(),
        }

    def to_dict_with_hybrid(self):
        return {
            'name': self.name,
            'gold': self.gold,
            'level': self.level,
            'max_members': self.max_members,
            'created_on': self.created_on.isoformat(),
            'is_rich': self.is_rich,
        }


class GuildMember(Base):
    """
    Guild member model
    """
    __tablename__ = 'guildmember'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    gold = Column(
        Integer, nullable=False,
        default=0
    )

    guild_id = Column(ForeignKey(u'guild.id'), nullable=False, index=True)

    created_on = Column(
        DateTime, nullable=False,
        default=datetime.datetime.now
    )
    guild = relationship(u'Guild', primaryjoin='GuildMember.guild_id == Guild.id')
