from models import Scale
from trust.artifacts.content_trust.recommendation import ask_for_recommendations
from loggers.basic_logger import BasicLogger
from datetime import datetime
import statistics


def user_expertise(agent, other_agent, resource_id, topics, discovery, scale, logger, recency_limit):
    """
    Calculates the user expertise value by asking topic experts for their recommendation value for the evaluated
    resource.

    :param agent: The agent which calculates the popularity.
    :type agent: str
    :param other_agent: The other agent for which the popularity value is calculated.
    :type other_agent: str
    :param resource_id: The URI of the evaluated resource.
    :type resource_id: str
    :param topics: A list of the topics of the currently evaluated resource
    :type topics: str
    :param discovery: Addresses of all agents within the scenario.
    :type discovery: dict
    :param scale: The Scale object to be used by the agent.
    :type scale: Scale
    :param logger: The logger object to be used by the agent.
    :type logger: BasicLogger
    :param recency_limit: A datetime object which is used for "forgetting" old history entries
    :type recency_limit: datetime
    :return: The User Expertise trust value.
    :rtype: float or int
    :return:
    """

    agents_to_ask = []

    # Collects expert users for each topic
    for topic in topics:
        history_lines = logger.read_lines_from_agent_topic_trust(agent)
        # getting all history values of the agent respective to the evaluated resource and filters them based on
        # their age and the recency limit set in the trust preferences of the agent

        # pre-filter history_lines with the recency_limit
        for entry in [line for line in history_lines
                      if datetime.strptime(line['date_time'], BasicLogger.get_time_format_string()) > recency_limit]:
            # get entries for the current resource based on its ID and filter by topic name
            if entry['resource_id'] == resource_id and entry['topic'] == topic:
                # check whether the topic trust value is above the minimum to trust others as set by the scale and
                # test if the agents_to_ask list already contains the agent of the current entry or is the current
                # interaction partner
                if float(entry['trust_value']) >= scale.minimum_to_trust_others() \
                        and entry['other_agent'] not in agents_to_ask and entry['other_agent'] != other_agent:
                    # adds the agent to the list of expert users
                    agents_to_ask.append(entry['other_agent'])

    expertise_values = ask_for_recommendations(agent, resource_id, agents_to_ask, scale, logger, discovery, recency_limit)
    return statistics.median(expertise_values) if len(expertise_values) > 0 else None
