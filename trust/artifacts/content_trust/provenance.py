from models import Scale


def provenance(authors, trusted_authors, scale):
    """
    Calculate provenance trust by reading the authors for the current resource and comparing them to the set of
    trusted authors. The returned topic trust value expresses the congruency of both sets, normalized to the
    given scale.

    :param authors: A list of original authors of the resource.
    :type authors: list
    :param trusted_authors: A list of authors that are trusted by the agent that is evaluating the resource.
    :type trusted_authors: list
    :param scale: The Scale object to be used by the agent.
    :type scale: Scale
    :return: The provenance trust value
    :rtype: float or int
    """

    if len(authors) == 0:
        return None

    count_congruent = len(set(authors) & set(trusted_authors))
    score = count_congruent / len(authors)
    return scale.normalize_value_to_scale(score, 0, 1)
