from datetime import datetime
from loggers.basic_logger import BasicLogger
from models import Scale


def direct_experience(agent, resource_id, recency_limit, scale, logger):
    """
    The values in the history from agent about other agent are combined via median to the direct XP.

    :param agent: The agent which calculates the trust. (start of relationship)
    :type agent: str
    :param resource_id: The URI of the resource which is evaluated.
    :type resource_id: str
    :param recency_limit: A datetime object which is used for "forgetting" old history entries
    :type recency_limit: datetime
    :param scale: The Scale object to be used by the agent.
    :type scale: Scale
    :param logger: The logger object to be used by the agent.
    :type logger: BasicLogger
    :return: Direct experience value from agent about other agent.
    :rtype: float or int
    """

    history_lines = logger.read_lines_from_agent_history(agent)
    # getting all history values of the agent respective to the evaluated resource and filters them based on their age
    # and the recency limit set in the trust preferences of the agent
    history = [float(entry['trust_value']) for entry in history_lines if entry['resource_id'] == resource_id and
               datetime.strptime(entry['date_time'], BasicLogger.get_time_format_string()) > recency_limit and
               entry['trust_value'] != 'None']
    # calculate direct experience
    direct_xp = sum(history) / len(history) if len(history) > 0 else None
    return direct_xp


def get_combined_direct_experience_for_agent(agent, third_agent, logger, recency_limit, scale):
    """
    Calculates the average of recent direct experience trust values for resources provided by the respective agent.
    :param agent: The agent that is evaluating the resource.
    :type agent: str
    :param third_agent: An agent that isn't the evaluating or evaluated agent.
    :type third_agent: str
    :param logger: The current logger object.
    :type logger: BasicLogger
    :param recency_limit: A datetime object which is used for "forgetting" old history entries
    :type recency_limit: datetime
    :param scale: The Scale object to be used by the agent.
    :type scale: Scale
    :return: Direct Experience average value for the third_agent
    :rtype: float or int
    """

    history_lines = logger.read_lines_from_agent_history(agent)
    history = [float(entry['trust_value']) for entry in history_lines if entry['other_agent'] == third_agent and
               datetime.strptime(entry['date_time'], BasicLogger.get_time_format_string()) > recency_limit and
               entry['trust_value'] != 'None']
    # calculate direct experience
    direct_xp = sum(history) / len(history) if len(history) > 0 else None
    return direct_xp
