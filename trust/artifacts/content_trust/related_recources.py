from trust.artifacts.content_trust.direct_experience import direct_experience
from models import Scale
from loggers.basic_logger import BasicLogger
from datetime import datetime


def related(agent, related_resources, recency_limit, scale, logger):
    """
    Evaluates the resources referenced by the resource that is currently evaluated by retrieving their past
    direct experience values and calculating its average.

    :param agent: The agent evaluating the resource.
    :type agent: str
    :param related_resources: A list of URIs of the resources that are related to or referenced by the evaluated resource.
    :type related_resources: list
    :param recency_limit: A datetime object which is used for "forgetting" old history entries
    :type recency_limit: datetime
    :param scale: The Scale object to be used by the agent.
    :type scale: Scale
    :param logger: The logger object to be used by the agent.
    :type logger: BasicLogger
    :return: The Related Resources trust value
    :rtype float or int
    """

    experiences = []
    
    for resource_id in related_resources:
        direct_xp = direct_experience(agent, resource_id, recency_limit, scale, logger)
        if direct_xp != None:
            experiences.append(direct_xp)
    
    if len(experiences) > 0:
        return sum(experiences) / len(experiences)
    else:
        return None
