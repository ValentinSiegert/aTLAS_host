from .trust_evaluation import eval_trust


def eval_trust_with_init(agent, other_agent, current_topic, agent_behavior, scale, logger, discovery):
    if agent_behavior['__init__']['name'] == 'random':
        pass
    eval_trust(agent, other_agent, current_topic, agent_behavior, scale, logger, discovery)
