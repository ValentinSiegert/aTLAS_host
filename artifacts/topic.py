import re
###############################################
# Topic check


def topic(agent, other_agent, current_topic, logger):
    topic_lines = logger.readlines_from_agent_topic_trust(agent)
    regex = re.compile('(?<=\\\')(.*?)(?=\\\')')  # regex to find everything between two apostrophes
    # getting all topic values of the agent respective to the other agent and the current topic
    topic_values = [float(entry.split(" ")[-1]) for entry in topic_lines if regex.findall(entry)[0] == other_agent and regex.findall(entry)[2] == current_topic]
    # calculate topic trust
    topic_value = sum(topic_values) / len(topic_values) if len(topic_values) > 0 else 0.00
    return topic_value


