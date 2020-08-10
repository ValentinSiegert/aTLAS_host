# The final trust result is combined through the sum of the
# values in the log file and the corresponding weight given by the scenario file


def final_trust(agent, other_agent, logger):
    trust_values = []
    trust_log_lines = logger.readlines_from_agent_trust_log(agent)
    for line in trust_log_lines:
        if line.split(" ")[-2][1:-2] == other_agent:
            trust_values.append(float(line.split(" ")[-1]))
    trust = sum(trust_values) / len(trust_values) if len(trust_values) > 0 else 0.00
    return trust


