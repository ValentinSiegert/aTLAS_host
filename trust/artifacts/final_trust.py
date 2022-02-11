# The final trust result is combined through the sum of the
# values in the log file and the corresponding weight given by the scenario file


def weighted_avg_final_trust(trust_values, weights, scale_middle):
    weighted_trust_values = []
    for metric, value in trust_values.items():
        weight = weights[metric] if metric in weights.keys() else 1.0
        weighted_trust_values.append(weight * value)
    trust = sum(weighted_trust_values) / len(weighted_trust_values) if len(weighted_trust_values) > 0 else scale_middle
    return trust
