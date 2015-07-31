# -*- coding: utf-8 -*-
import logging
from contextlib import closing

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import settings
from .decorators import (
    sessioned as utils_sessioned
)

engine = create_engine(
    settings.CONNECTION_STRING,
    echo=True
)
Session = sessionmaker(bind=engine)


def create_session(context_manager=True):
    """
    Create sqlalchemy session.
    Wrapper on sessionmaker factory.

    >>> with create_session() as session:
    >>>     do_smth()

    :param bool context_manager:
        if True: will return closing context manager

    :rtype: sqlalchemy.orm.session.Session
    :return: new session
    """
    if context_manager:
        return closing(Session())
    else:
        return Session()


sessioned = utils_sessioned(create_session)

for name in ['sqlalchemy.engine.base.Engine']:
    logger = logging.getLogger(name)
    logger.disabled = settings.DISABLE_SQL_ALCHEMY_LOGGER
