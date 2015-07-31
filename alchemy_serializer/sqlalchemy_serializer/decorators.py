# coding: utf-8


def sessioned(session_builder_manager):
    """
    Session decorator.
    Wraps function in a session context manager.
    Delegates session and commit args to func.

    :param session_builder_manager:
        session context_manager
    :type arg1:

    :rtype: function
    """
    def decorator(func):
        def wrapper(
            *args, **kwargs
        ):
            session = kwargs.get('session', None)
            commit = kwargs.get('commit', None)

            if session is None:
                if commit is False:
                    raise ValueError(
                        "Commit can't be False when session is None"
                    )
                with session_builder_manager() as session:
                    kwargs['session'] = session
                    result = func(
                        *args, **kwargs
                    )
            else:
                result = func(
                    *args, **kwargs
                )

            if commit:
                session.commit()

            return result
        return wrapper
    return decorator
