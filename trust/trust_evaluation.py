from trust.artifacts.content_trust.recommendation import recommendation as content_trust_recommendation
from trust.artifacts.content_trust.direct_experience import direct_experience as content_trust_direct_experience
from trust.artifacts.content_trust.popularity import popularity as content_trust_popularity
from trust.artifacts.content_trust.authority import authority as content_trust_authority
from trust.artifacts.content_trust.topic import topic as content_trust_topic
from trust.artifacts.content_trust.provenance import provenance as content_trust_provenance
from trust.artifacts.content_trust.age import age_check as content_trust_age
from trust.artifacts.content_trust.related_recources import related as content_trust_related_resources
from trust.artifacts.content_trust.user_expertise import user_expertise as content_trust_user_expertise
from trust.artifacts.final_trust import weighted_avg_final_trust
from models import Scale, Observation
from datetime import datetime
from loggers.basic_logger import BasicLogger


def eval_trust(agent, other_agent, observation, agent_behavior, scale, logger, discovery):
    """
    Calculate trust metrics and then finalize all values to one final trust value.

    :param agent: The agent which calculates the trust. (start of relationship)
    :type agent: str
    :param other_agent: The other agent for which the trust relationship is calculated. (end of relationship)
    :type other_agent: str
    :param observation: Content and metadata of message received and on which the trust is calculated.
    :type observation: Observation
    :param agent_behavior: Metrics to be used the agent.
    :type agent_behavior: dict
    :param scale: The Scale object to be used by the agent.
    :type scale: Scale
    :param logger: The logger object to be used by the agent.
    :type logger: BasicLogger
    :param discovery: Addresses of all agents within the scenario.
    :type discovery: dict
    :return: The final trust value for one specific interaction between agent and the other agent.
    :rtype: float or int
    """
    trust_values = {}
    resource_id = observation.details['uri']

    # retrieve Recency age limit from agent trust preferences
    if 'content_trust.recency_age_limit' in agent_behavior:
        recency_limit = datetime.fromtimestamp(agent_behavior['content_trust.recency_age_limit'])
    else:
        recency_limit = datetime.fromtimestamp(0)

    if 'content_trust.context_level' in observation.details and 'content_trust.context_values' in agent_behavior:
        scale.set_cooperation_threshold(
            agent_behavior['content_trust.context_values'][observation.details['content_trust.context_level']])

    if 'content_trust.bias' in observation.details:
        bias_value = observation.details['content_trust.bias']
        logger.write_to_agent_trust_log(agent, 'content_trust.bias', other_agent, bias_value, resource_id)
        trust_values['content_trust.bias'] = bias_value

    if 'content_trust.specificity' in observation.details:
        specificity_value = observation.details['content_trust.specificity']
        logger.write_to_agent_trust_log(agent, 'content_trust.specificity', other_agent, specificity_value, resource_id)
        trust_values['content_trust.specificity'] = specificity_value

    if 'content_trust.likelihood' in observation.details:
        likelihood_value = observation.details['content_trust.likelihood']
        logger.write_to_agent_trust_log(agent, 'content_trust.likelihood', other_agent, likelihood_value, resource_id)
        trust_values['content_trust.likelihood'] = likelihood_value

    if 'content_trust.incentive' in observation.details:
        incentive_value = observation.details['content_trust.incentive']
        logger.write_to_agent_trust_log(agent, 'content_trust.incentive', other_agent, incentive_value, resource_id)
        trust_values['content_trust.incentive'] = incentive_value

    if 'content_trust.deception' in observation.details and 'content_trust.deception' in agent_behavior:
        deception_value = observation.details['content_trust.deception']
        # deceptive
        if deception_value < agent_behavior['content_trust.deception']:
            return scale.minimum_value()
        logger.write_to_agent_trust_log(agent, 'content_trust.deception', other_agent, deception_value, resource_id)
        trust_values['content_trust.deception'] = deception_value

    if 'content_trust.max_lifetime_seconds' in agent_behavior:
        age_punishment_value = content_trust_age(agent_behavior, observation, scale)
        logger.write_to_agent_trust_log(agent, 'content_trust.age', other_agent, age_punishment_value, resource_id)
        if 'content_trust.enforce_lifetime' in agent_behavior and agent_behavior['content_trust.enforce_lifetime']:
            if age_punishment_value < scale.maximum_value():
                return scale.minimum_value()
        else:
            trust_values['content_trust.age'] = age_punishment_value

    if 'content_trust.authority' in agent_behavior:
        authority_value = content_trust_authority(agent_behavior['content_trust.authority'], other_agent, scale)
        logger.write_to_agent_trust_log(agent, 'content_trust.authority', other_agent, authority_value, resource_id)
        trust_values['content_trust.authority'] = authority_value

    if 'content_trust.topic' in agent_behavior:
        topic_value = content_trust_topic(agent, other_agent, agent_behavior['content_trust.topic'],
                                          observation.details['content_trust.topics'], recency_limit, logger, scale)
        logger.write_to_agent_trust_log(agent, 'content_trust.topic', other_agent, topic_value, resource_id)
        trust_values['content_trust.topic'] = topic_value

    if 'content_trust.provenance' in agent_behavior:
        provenance_value = content_trust_provenance(observation.authors,
                                                    agent_behavior['content_trust.provenance'], scale)
        logger.write_to_agent_trust_log(agent, 'content_trust.provenance', other_agent, provenance_value, resource_id)
        trust_values['content_trust.provenance'] = provenance_value

    if 'content_trust.direct_experience' in agent_behavior:
        direct_experience_value = content_trust_direct_experience(agent, resource_id, recency_limit, scale, logger)
        logger.write_to_agent_trust_log(agent, 'content_trust.direct_experience', other_agent, direct_experience_value,
                                        resource_id)
        trust_values['content_trust.direct_experience'] = direct_experience_value

    if 'content_trust.recommendation' in agent_behavior:
        recommendation_value = content_trust_recommendation(agent, other_agent, resource_id, scale, logger, discovery,
                                                            recency_limit)
        logger.write_to_agent_trust_log(agent, 'content_trust.recommendation', other_agent, recommendation_value,
                                        resource_id)
        trust_values['content_trust.recommendation'] = recommendation_value

    if 'content_trust.related_resources' in agent_behavior:
        related_resources_value = content_trust_related_resources(
            agent, observation.details['content_trust.related_resources'], recency_limit, scale, logger)
        logger.write_to_agent_trust_log(agent, 'content_trust.related_resources', other_agent, related_resources_value,
                                        resource_id)
        trust_values['content_trust.related_resources'] = related_resources_value

    if 'content_trust.user_expertise' in agent_behavior:
        user_expertise_value = content_trust_user_expertise(
            agent, other_agent, resource_id, observation.details['content_trust.topics'],
            discovery, scale, logger, recency_limit)
        logger.write_to_agent_trust_log(agent, 'content_trust.user_expertise', other_agent, user_expertise_value,
                                        resource_id)
        trust_values['content_trust.user_expertise'] = user_expertise_value

    if 'content_trust.popularity' in agent_behavior:
        if 'content_trust.popularity' in agent_behavior and 'peers' in agent_behavior['content_trust.popularity']:
            peers = agent_behavior['content_trust.popularity']['peers']
        else:
            peers = discovery.keys()
        popularity_value = content_trust_popularity(agent, other_agent, resource_id,
                                                    peers, discovery,
                                                    scale, recency_limit)
        logger.write_to_agent_trust_log(agent, 'content_trust.popularity', other_agent, popularity_value, resource_id)
        trust_values['content_trust.popularity'] = popularity_value

    """
    final Trust calculations
    """
    # delete all metrics from final trust calculation, which results are set to None
    trust_values = {metric: value for metric, value in trust_values.items() if value is not None}
    final_trust_value = None
    if agent_behavior['__final__']:
        if agent_behavior['__final__']['name'] == 'weighted_average':
            final_trust_value = weighted_avg_final_trust(trust_values, agent_behavior['__final__']['weights'], None)

    for topic in observation.details['content_trust.topics']:
        logger.write_to_agent_topic_trust(agent, other_agent, topic, final_trust_value, resource_id)

    return final_trust_value
