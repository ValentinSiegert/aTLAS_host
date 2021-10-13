from trust.artifacts.content_trust.direct_experience import direct_experience
from trust.artifacts.content_trust.recommendation import ask_for_recommendations
from exec.ask_others import ask_other_agent


def popularity(agent, other_agent, discovery, scale, logger):
    """
    Asking other agent for its popularity value and weighting it with other agent's direct XP.

    :param agent: The agent which calculates the trust. (start of relationship)
    :type agent: str
    :param other_agent: The other agent for which the trust relationship is calculated. (end of relationship)
    :type other_agent: str
    :param scale: The Scale object to be used by the agent.
    :type scale: Scale
    :param logger: The logger object to be used by the agent.
    :type logger: BasicLogger
    :param discovery: Addresses of all agents within the scenario.
    :type discovery: dict
    :return: The popularity trust value weighted by other agent's direct XP.
    :rtype: float or int
    """
    remote_ip, remote_port = discovery[other_agent].split(":")
    message = f"popularity_{agent}"
    received_value = ask_other_agent(remote_ip, int(remote_port), message)
    # popularity value of other agent has to be weighted with direct experience to other_agent
    popularity_value = direct_experience(agent, other_agent, scale, logger) * received_value
    return popularity_value


def popularity_response(agent, other_agent, scale, logger, discovery):
    """
    The popularity is calculated by averaging the recommendations on agent of third agents.

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
    :return: The popularity trust value of agent itself.
    :rtype: float or int
    """
    # other_agent has to get all recommendations about itself
    agents_to_ask = [third_agent for third_agent in discovery if third_agent != agent and third_agent != other_agent and
                     direct_experience(agent, third_agent, scale, logger) >= scale.minimum_to_trust_others()]
    recommendations = ask_for_recommendations(agent, agent, agents_to_ask, scale, logger, discovery)
    # all recommendations are weighted with direct experience and averaged
    default = scale.default_value()
    popularity_value = sum(recommendations) / len(recommendations) if len(recommendations) > 0 else default
    return popularity_value


