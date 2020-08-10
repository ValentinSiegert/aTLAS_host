###############################################
# Popularity check
# The popularity is calculated by averaging the recommendation

from artifacts.direct_experience import direct_experience
from artifacts.recommendation import ask_for_recommendations
from exec.ask_others import ask_other_agent


def popularity(agent, other_agent, discovery, logger):
    remote_ip, remote_port = discovery[other_agent].split(":")
    message = f"popularity"
    received_value = ask_other_agent(remote_ip, int(remote_port), message)
    # popularity value of other agent has to be weighted with direct experience to other_agent
    popularity_value = direct_experience(agent, other_agent, logger) * received_value
    return popularity_value


def popularity_response(agent, discovery, cooperation_threshold, logger):
    # other_agent has to get all recommendations about itself
    agents_to_ask = [third_agent for third_agent in discovery if
                     direct_experience(agent, third_agent, logger) >= cooperation_threshold]
    recommendations = ask_for_recommendations(agent, agent, agents_to_ask, discovery, logger)
    # all recommendations are weighted with direct experience and averaged
    popularity_value = sum(recommendations) / len(recommendations) if len(recommendations) > 0 else 0.00
    return popularity_value


