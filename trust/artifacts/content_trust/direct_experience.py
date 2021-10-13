

def direct_experience(agent, other_agent, scale, logger):
    """
    The values in the history from agent about other agent are combined via median to the direct XP.

    :param agent: The agent which calculates the trust. (start of relationship)
    :type agent: str
    :param other_agent: The other agent for which the trust relationship is calculated. (end of relationship)
    :type other_agent: str
    :param scale: The Scale object to be used by the agent.
    :type scale: Scale
    :param logger: The logger object to be used by the agent.
    :type logger: BasicLogger
    :return: Direct experience value from agent about other agent.
    :rtype: float or int
    """
    history_lines = logger.read_lines_from_agent_history(agent)
    # getting all history values of the agent respective to the other agent
    history = [float(entry.split(" ")[-1]) for entry in history_lines if
               logger.line_about_other_agent(entry, other_agent)]
    # calculate direct experience
    direct_xp = sum(history) / len(history) if len(history) > 0 else scale.default_value()
    return direct_xp
