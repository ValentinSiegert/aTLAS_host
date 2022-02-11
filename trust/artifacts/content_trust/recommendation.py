from dis import disco
from exec.ask_others import ask_other_agent
from trust.artifacts.content_trust.direct_experience import get_combined_direct_experience_for_agent, direct_experience
from datetime import datetime
from loggers.basic_logger import BasicLogger
from models import Scale
import statistics


def recommendation(agent, other_agent, resource_id, scale, logger, discovery, recency_limit):
    """
    Get recommendations on other agent of third agents and average them to one recommendation value.

    :param agent: The agent which calculates the popularity.
    :type agent: str
    :param other_agent: The other agent for which the popularity value is calculated.
    :type other_agent: str
    :param resource_id: The URI of the evaluated resource.
    :type resource_id: str
    :param scale: The Scale object to be used by the agent.
    :type scale: Scale
    :param logger: The logger object to be used by the agent.
    :type logger: BasicLogger
    :param discovery: Addresses of all agents within the scenario.
    :type discovery: dict
    :param recency_limit: A datetime object which is used for "forgetting" old history entries
    :type recency_limit: datetime
    :return: The Recommendation trust value.
    :rtype: float or int
    """

    agents_to_ask = []
    for third_agent in discovery:
        if third_agent != agent and third_agent != other_agent:
            combined = get_combined_direct_experience_for_agent(
                agent, third_agent, logger, recency_limit, scale)
            if combined != None and combined >= scale.minimum_to_trust_others():
                agents_to_ask.append(third_agent)

    recommendations = ask_for_recommendations(
        agent, resource_id, agents_to_ask, scale, logger, discovery, recency_limit)
    return statistics.median(recommendations) if len(recommendations) > 0 else None


def ask_for_recommendations(agent, resource_id, agents_to_ask, scale, logger, discovery, recency_limit):
    """
    Asking all agents to ask about their recommendation on other agent and listing them.

    :param agent: The agent which calculates the popularity.
    :type agent: str
    :param resource_id: The URI of the evaluated resource.
    :type resource_id: str
    :param agents_to_ask: The third agents to ask for recommendation.
    :type agents_to_ask: list
    :param scale: The Scale object to be used by the agent.
    :type scale: Scale
    :param logger: The logger object to be used by the agent.
    :type logger: BasicLogger
    :param discovery: Addresses of all agents within the scenario.
    :type discovery: dict
    :param recency_limit: A datetime object which is used for "forgetting" old history entries
    :type recency_limit: datetime
    :return: The recommendation trust values of third agents on other_agent.
    :rtype: list
    """
    recommendations = []
    message = f"recommendation_{resource_id}_{datetime.strftime(recency_limit, BasicLogger.get_time_format_string())}"
    for third_agent in agents_to_ask:
        remote_ip, remote_port = discovery[third_agent].split(":")
        response = ask_other_agent(remote_ip, int(remote_port), message)
        if response != 'None':
            received_value = float(response)
            combined = get_combined_direct_experience_for_agent(
                agent, third_agent, logger, recency_limit, scale)
            if combined != None:
                recommendations.append(combined * received_value)

    return recommendations


def recommendation_response(agent, resource_id, recency_limit, scale, logger):
    """
    Giving back the direct XP as the recommendation on other agent in the point of view from agent.

    :param agent: The agent which calculates the popularity.
    :type agent: str
    :param resource_id: The URI of the evaluated resource.
    :type resource_id: str
    :param recency_limit: A datetime object which is used for "forgetting" old history entries
    :type recency_limit: datetime
    :param scale: The Scale object to be used by the agent.
    :type scale: Scale
    :param logger: The logger object to be used by the agent.
    :type logger: BasicLogger
    :return: The recommendation trust values of third agents on other_agent.
    :rtype: list
    """
    return direct_experience(agent, resource_id, recency_limit, scale, logger)
