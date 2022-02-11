from models import Scale
from loggers.basic_logger import BasicLogger
from datetime import datetime


def topic(agent, other_agent, trusted_topics, current_topics, recency_limit, logger, scale):
    """
    Calculate topic trust by calculating the average trust for each topic given in current_topics based on the topic
    trust log

    :param agent: The agent which calculates the popularity.
    :type agent: str
    :param other_agent: The other agent for which the popularity value is calculated.
    :type other_agent: str
    :param trusted_topics: A dictionary of dictionaries of predefined topic trust values for other agents; the format has to be similar to this: {'agent_a': {'topic_1': 0.5, 'topic_2': -0.7}} and the values have to be valid for the given scale
    :type trusted_topics: dict
    :param current_topics: The topics of the message received and on which the trust is calculated.
    :type current_topics: list
    :param recency_limit: A datetime object which is used for "forgetting" old history entries
    :type recency_limit: datetime
    :param logger: The logger object to be used by the agent.
    :type logger: BasicLogger
    :param scale: The Scale object to be used by the agent.
    :type scale: Scale
    :return: The topic trust value.
    :rtype: float or int
    """

    if len(current_topics) == 0:
        return None

    topic_values = []

    topic_history_lines = logger.read_lines_from_agent_topic_trust(agent)
    topic_history = {}
    for entry in topic_history_lines:
        if datetime.strptime(entry['date_time'], BasicLogger.get_time_format_string()) > recency_limit:
            if entry['other_agent'] == other_agent:
                if entry['topic'] not in topic_history or topic_history[entry['topic']] is None:
                    topic_history[entry['topic']] = []
                topic_history[entry['topic']].append(float(entry['trust_value']))

    for topic in current_topics:
        # get trust value from trust preferences
        history_values = []
        if trusted_topics is not None and other_agent in trusted_topics and topic in trusted_topics[other_agent]:
            history_values.append(trusted_topics[other_agent][topic])

        if topic in topic_history:
            history_values += topic_history[topic]

        if len(history_values) > 0:
            topic_mean = sum(history_values) / len(history_values)
            topic_values.append(topic_mean)

    if len(topic_values) > 0:
        return sum(topic_values) / len(topic_values)
    else:
        return None
