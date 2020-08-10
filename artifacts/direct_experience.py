###############################################
# Direct Experience
# The tag values in the logfiles are combined to the Direct XP via the median


def direct_experience(agent, other_agent, logger):
    history_lines = logger.readlines_from_agent_history(agent)
    # getting all history values of the agent respective to the other agent
    history = [float(entry.split(" ")[-1]) for entry in history_lines if entry.split(" ")[-2][1:-2] == other_agent]
    # calculate direct experience
    direct_xp = sum(history) / len(history) if len(history) > 0 else 0.00
    return direct_xp

