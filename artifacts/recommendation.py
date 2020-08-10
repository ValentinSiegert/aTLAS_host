###############################################
# Recommendations
import socket
from artifacts.direct_experience import direct_experience
from exec.ask_others import ask_other_agent


def recommendation(current_agent, other_agent, discovery, cooperation_threshold, logger):
    agents_to_ask = [third_agent for third_agent in discovery if third_agent != current_agent and third_agent != other_agent and direct_experience(current_agent, third_agent, logger) >= cooperation_threshold]
    recommendations = ask_for_recommendations(current_agent, other_agent, agents_to_ask, discovery, logger)
    recommendation_value = sum(recommendations)/len(recommendations) if len(recommendations) > 0 else 0.00
    return recommendation_value


def ask_for_recommendations(current_agent, other_agent, agents_to_ask, discovery, logger):
    recommendations = []
    message = f"recommendation_{other_agent}"
    for third_agent in agents_to_ask:
        remote_ip, remote_port = discovery[third_agent].split(":")
        received_value = ask_other_agent(remote_ip, int(remote_port), message)
        recommendations.append(direct_experience(current_agent, third_agent, logger) * received_value)
    return recommendations



def recommendation_response(agent, recommendation_agent, logger):
    return direct_experience(agent, recommendation_agent, logger)

