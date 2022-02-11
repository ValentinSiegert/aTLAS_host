import datetime
from datetime import *
from models import Scale, Observation


def age_check(agent_behavior, observation, scale):
    """
    :param agent_behavior:  Metrics to be used the agent.
    :type agent_behavior: dict
    :param observation: Content and metadata of message received and on which the trust is calculated.
    :type observation: Observation
    :param scale: The trust scale used by the agent
    :type scale: Scale
    :return: An age punishment value that is equal to the scale maximum value for recent publications and falls within
    [default, max) if it exceeded the allowed lifetime.
    :rtype: float or int
    """

    now = datetime.utcnow().timestamp()
    age = observation.details['content_trust.publication_date'] + \
        agent_behavior['content_trust.max_lifetime_seconds']

    if now < age:  # within allowed lifetime
        return scale.maximum_value()
    else:  # exceeded lifetime
        if 'content_trust.age_grace_period_seconds' in agent_behavior:
            grace_value = (
                now - age) / agent_behavior['content_trust.age_grace_period_seconds']
            if grace_value < 1.0:  # within grace period
                return (1-grace_value) * scale.maximum_value()

        return scale.default_value()  # no grace period or grace period exceeded
