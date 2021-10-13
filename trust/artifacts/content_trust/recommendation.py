from trust.artifacts.content_trust.direct_experience import direct_experience
from exec.ask_others import ask_other_agent


def recommendation(agent, other_agent, scale, logger, discovery):
    """
    Get recommendations on other agent of third agents and average them to one recommendation value.

    :param agent: The agent which calculates the popularity.
    :type agent: str
    :param other_agent: The other agent for which the popularity value is calculated.
    :type other_agent: str
    :param scale: The Scale object to be used by the agent.
    :type scale: Scale
    :param logger: The logger object to be used by the agent.
    :type logger: BasicLogger
    :param discovery: Addresses of all agents within the scenario.
    :type discovery: dict
    :return: The recommendation trust value.
    :rtype: float or int
    """
    agents_to_ask = [third_agent for third_agent in discovery if third_agent != agent and third_agent != other_agent and
                     direct_experience(agent, third_agent, scale, logger) >= scale.minimum_to_trust_others()]
    recommendations = ask_for_recommendations(agent, other_agent, agents_to_ask, scale, logger, discovery)
    default = scale.default_value()
    recommendation_value = sum(recommendations)/len(recommendations) if len(recommendations) > 0 else default
    return recommendation_value


def ask_for_recommendations(agent, other_agent, agents_to_ask, scale, logger, discovery):
    """
    Asking all agents to ask about their recommendation on other agent and listing them.

    :param agent: The agent which calculates the popularity.
    :type agent: str
    :param other_agent: The other agent for which the popularity value is calculated.
    :type other_agent: str
    :param agents_to_ask: The third agents to ask for recommendation.
    :type agents_to_ask: list
    :param scale: The Scale object to be used by the agent.
    :type scale: Scale
    :param logger: The logger object to be used by the agent.
    :type logger: BasicLogger
    :param discovery: Addresses of all agents within the scenario.
    :type discovery: dict
    :return: The recommendation trust values of third agents on other_agent.
    :rtype: list
    """
    recommendations = []
    message = f"recommendation_{other_agent}"
    for third_agent in agents_to_ask:
        remote_ip, remote_port = discovery[third_agent].split(":")
        received_value = ask_other_agent(remote_ip, int(remote_port), message)
        recommendations.append(direct_experience(agent, third_agent, scale, logger) * received_value)
    return recommendations


def recommendation_response(agent, other_agent, scale, logger):
    """
    Giving back the direct XP as the recommendation on other agent in the point of view from agent.

    :param agent: The agent which calculates the popularity.
    :type agent: str
    :param other_agent: The other agent for which the popularity value is calculated.
    :type other_agent: str
    :param scale: The Scale object to be used by the agent.
    :type scale: Scale
    :param logger: The logger object to be used by the agent.
    :type logger: BasicLogger
    :return: The recommendation trust values of third agents on other_agent.
    :rtype: list
    """
    return direct_experience(agent, other_agent, scale, logger)

