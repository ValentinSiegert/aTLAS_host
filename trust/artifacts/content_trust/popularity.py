from trust.artifacts.content_trust.direct_experience import direct_experience
from trust.artifacts.content_trust.recommendation import ask_for_recommendations
from exec.ask_others import ask_other_agent
from datetime import datetime
from loggers.basic_logger import BasicLogger
from models import Scale


def popularity(agent, other_agent, resource_id, peers, discovery, scale, recency_limit):
    """
    Asking other agent for its popularity value and weighting it with other agent's direct XP.

    :param agent: The agent which calculates the trust. (start of relationship)
    :type agent: str
    :param other_agent: The other agent for which the trust relationship is calculated. (end of relationship)
    :type other_agent: str
    :param resource_id: The URI of the evaluated resource.
    :type resource_id: str
    :param peers: The peer group of the evaluating agent
    :type peers: list
    :param discovery: Addresses of all agents within the scenario.
    :type discovery: dict
    :param scale: The Scale object to be used by the agent.
    :type scale: Scale
    :param recency_limit: A datetime object which is used for "forgetting" old history entries
    :type recency_limit: datetime
    :return: The popularity trust value weighted by other agent's direct XP.
    :rtype: float or int
    """
    message = f"popularity_{resource_id}_{recency_limit.strftime(BasicLogger.get_time_format_string())}"
    known = 0

    agents_to_ask = [third_agent for third_agent in peers if third_agent != agent and third_agent != other_agent]
    for peer in agents_to_ask:
        remote_ip, remote_port = discovery[peer].split(':')
        received = ask_other_agent(remote_ip, int(remote_port), message)
        if bool(received):
            known += 1

    percentage = known / len(peers)
    # normalize needed in case the scale uses integers
    # cheating ensures that the format of the number is correct but (under the assumption that the parts for
    # trust and distrust are equally sized), missing popularity does not result in distrust
    return scale.normalize_value_to_scale(percentage, -1, 1)


def popularity_response(agent, resource_id, recency_limit, scale, logger):
    """
    The popularity is calculated by averaging the recommendations on agent of third agents.

    :param agent: The agent which calculates the popularity.
    :type agent: str
    :param resource_id: The URI of the evaluated resource.
    :type resource_id: str
    :param recency_limit: A datetime object which is used for "forgetting" old history entries (sent by requester)
    :type recency_limit: datetime
    :param scale: The Scale object to be used by the agent.
    :type scale: Scale
    :param logger: The logger object to be used by the agent.
    :type logger: BasicLogger
    :return: The popularity trust value of agent itself.
    :rtype: bool
    """
    history_lines = logger.read_lines_from_agent_history(agent)
    history = [1 for entry in history_lines if entry['resource_id'] == resource_id and
               datetime.strptime(entry['date_time'], BasicLogger.get_time_format_string()) > recency_limit and
               entry['trust_value'] != 'None' and float(entry['trust_value']) >= scale.minimum_to_trust_others()]

    return len(history) > 0
