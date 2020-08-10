from artifacts.recommendation import recommendation
from artifacts.direct_experience import direct_experience
from artifacts.popularity import popularity
from artifacts.authority import authority
from artifacts.agreement import agreement
from artifacts.age import age_check
from artifacts.recency import recency
from artifacts.relatedRecources import related
from artifacts.specificity import specificity
from artifacts.provenance import provenance
from artifacts.topic import topic

############################################################################
# ---The trust_initialization function starts with the imported behavior models
# ---and checks them for behavior-keywords. Those keywords trigger the specific
# ---function call to calculate the corresponding value from the artifacts.
# ---This is needed to calculate the final trust value


def calc_trust_metrics(agent, other_agent, current_topic, agent_behavior, weights, trust_thresholds,
                       authorities, logger, discovery):
    if 'direct experience' in agent_behavior:
        direct_experience_value = format(weights["direct experience"] * direct_experience(agent, other_agent, logger), '.2f')
        logger.write_to_agent_trust_log(agent, "direct experience", other_agent, direct_experience_value)
    if 'authority' in agent_behavior and other_agent in authorities[agent]:
        authority_value = format(weights["authority"] * authority(), '.2f')
        logger.write_to_agent_trust_log(agent, "authority", other_agent, authority_value)
    if 'popularity' in agent_behavior:
        popularity_value = format(float(weights["popularity"]) * float(popularity(agent, other_agent, discovery, logger)), '.2f')
        logger.write_to_agent_trust_log(agent, "popularity", other_agent, popularity_value)
    if 'recommendation' in agent_behavior:
        recommendation_value = format(weights["recommendation"] * recommendation(agent, other_agent, discovery, trust_thresholds['cooperation'], logger), '.2f')
        logger.write_to_agent_trust_log(agent, "recommendation", other_agent, recommendation_value)
    if 'topic' in agent_behavior:
        topic_value = format(weights["topic"] * topic(agent, other_agent, current_topic, logger), '.2f')
        logger.write_to_agent_trust_log(agent, "topic", other_agent, topic_value)

    # if 'age' in agent_behavior:
    #     credibility_value = str(format(
    #         float(weights["age"]) * age_check(current_agent, other_agent, current_message[24:26]),
    #         '.2f'))
    #     fo = open(log_path.absolute(), "ab+")
    #     fo.write(
    #         bytes(get_current_time() + ', age trustvalue from: ', 'UTF-8') + bytes(other_agent, 'UTF-8') +
    #         bytes(' ' + credibility_value, 'UTF-8') +
    #         bytes("\n", 'UTF-8'))
    #     fo.close()
    #
    # if 'agreement' in agent_behavior:
    #     credibility_value = str(format(float(weights["agreement"]) * float(
    #         agreement(current_agent, other_agent, current_message[24:26])), '.2f'))
    #     fo = open(log_path.absolute(), "ab+")
    #     fo.write(
    #         bytes(get_current_time() + ', agreement trustvalue from: ', 'UTF-8') + bytes(other_agent, 'UTF-8') +
    #         bytes(' ' + credibility_value, 'UTF-8') +
    #         bytes("\n", 'UTF-8'))
    #     fo.close()
    #
    # if 'provenance' in agent_behavior:
    #     credibility_value = str(
    #         format(float(weights["provenance"]) * float(provenance(current_agent, current_message[16:18])), '.2f'))
    #     fo = open(log_path.absolute(), "ab+")
    #     fo.write(
    #         bytes(get_current_time() + ', provenance trustvalue from: ', 'UTF-8') + bytes(other_agent, 'UTF-8') +
    #         bytes(' ' + credibility_value, 'UTF-8') +
    #         bytes("\n", 'UTF-8'))
    #     fo.close()
    #
    # if 'recency' in agent_behavior:
    #     credibility_value = str(
    #         format(float(weights["recency"]) * float(recency(current_agent, current_message[24:26])), '.2f'))
    #     fo = open(log_path.absolute(), "ab+")
    #     fo.write(
    #         bytes(get_current_time() + ', recency trustvalue from: ', 'UTF-8') + bytes(other_agent, 'UTF-8') +
    #         bytes(' ' + credibility_value, 'UTF-8') +
    #         bytes("\n", 'UTF-8'))
    #     fo.close()
    #
    # if 'related resource' in agent_behavior:
    #     credibility_value = str(
    #         format(float(weights["related resource"]) * float(related(current_agent, current_message[24:26])), '.2f'))
    #     fo = open(log_path.absolute(), "ab+")
    #     fo.write(
    #         bytes(get_current_time() + ', related resource trustvalue from: ', 'UTF-8') + bytes(other_agent, 'UTF-8') +
    #         bytes(' ' + credibility_value, 'UTF-8') +
    #         bytes("\n", 'UTF-8'))
    #     fo.close()
    #
    # if 'specificity' in agent_behavior:
    #     credibility_value = str(format(float(weights["specificity"]) * float(
    #         specificity(current_agent, other_agent, current_message[24:26])), '.2f'))
    #     fo = open(log_path.absolute(), "ab+")
    #     fo.write(
    #         bytes(get_current_time() + ', specificity trustvalue from: ', 'UTF-8') + bytes(other_agent, 'UTF-8') +
    #         bytes(' ' + credibility_value, 'UTF-8') +
    #         bytes("\n", 'UTF-8'))
    #     fo.close()




