import re


def topic(agent, other_agent, current_topic, scale, logger):
    """
    Calculate topic trust by reading from logger all past topic trust for other agent and topic,
    and then averaging all values or giving out default_value.

    :param agent: The agent which calculates the trust. (start of relationship)
    :type agent: str
    :param other_agent: The other agent for which the trust relationship is calculated. (end of relationship)
    :type other_agent: str
    :param current_topic: The topic of the message received and on which the trust is calculated.
    :type current_topic: str
    :param scale: The Scale object to be used by the agent.
    :type scale: Scale
    :param logger: The logger object to be used by the agent.
    :type logger: BasicLogger
    :return: The topic trust value.
    :rtype: float or int
    """
    topic_lines = logger.read_lines_from_agent_topic_trust(agent)
    regex = re.compile('(?<=\\\')(.*?)(?=\\\')')  # regex to find everything between two apostrophes
    # getting all topic values of the agent respective to the other agent and the current topic
    topic_values = [float(entry.split(" ")[-1]) for entry in topic_lines
                    if regex.findall(entry)[0] == other_agent and regex.findall(entry)[2] == current_topic]
    # calculate topic trust
    topic_value = sum(topic_values) / len(topic_values) if len(topic_values) > 0 else scale.default_value()
    return topic_value
