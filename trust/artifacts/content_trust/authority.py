

def authority(agent_authorities, other_agent, scale):
    """
    All authorities of the agent get the scale's maximum, while all others get the minimum to trust value.

    :param agent_authorities: The list of agents to be seen as authority by the current agent.
    :type agent_authorities: list
    :param other_agent: The other agent for which the trust relationship is calculated. (end of relationship)
    :type other_agent: str
    :param scale: The Scale object to be used by the agent.
    :type scale: Scale
    :return: Returns authority trust value.
    :rtype: float or int
    """
    if other_agent in agent_authorities:
        return scale.maximum_value()
    else:
        return scale.minimum_to_trust_others()
