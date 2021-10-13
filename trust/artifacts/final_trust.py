# The final trust result is combined through the sum of the
# values in the log file and the corresponding weight given by the scenario file


def weighted_avg_final_trust(trust_values, weights):
    weighted_trust_values = []
    for metric, value in trust_values.items():
        weight = weights[metric] if metric in weights.keys() else 1.0
        weighted_trust_values.append(weight * value)
    # TODO: set middle of used trust scale instead of 0.0 in following else
    trust = sum(weighted_trust_values) / len(weighted_trust_values) if len(weighted_trust_values) > 0 else 0.00
    return trust


