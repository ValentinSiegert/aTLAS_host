if len(__name__.split('.')) > 2:
    from ..models import Scale, UpdatableInterface
else:
    from models import Scale, UpdatableInterface


class MarshBriggsScale(Scale, UpdatableInterface):
    """
    Implements the trust scale from Marsh and Briggs (2009).
    https://link.springer.com/chapter/10.1007/978-1-84800-356-9_2
    https://www.researchgate.net/publication/227021342_Examining_Trust_Forgiveness_and_Regret_as_Computational_Concepts
    """
    name = str
    maximum = float
    minimum = float
    default = float
    cooperation = float
    forgivability = float

    def minimum_to_trust_others(self):
        return self.cooperation

    def default_value(self):
        return self.default

    def maximum_value(self):
        return self.maximum

    def minimum_value(self):
        return self.minimum

    def __init__(self, minimum, maximum, default=0.0, cooperation=0.5, forgivability=-0.5,
                 name="Trust Scale by Marsh and Briggs (2009)"):
        """
        :type minimum: float
        :type maximum: float
        :type default: float
        :type cooperation: float
        :type forgivability: float
        :type name: str
        """
        self.name = name
        self.maximum = maximum
        self.minimum = minimum
        self.default = default
        self.cooperation = cooperation
        self.forgivability = forgivability
        Scale.__init__(self)
        UpdatableInterface.__init__(self, maximum=maximum, minimum=minimum, default=default, name=name,
                                    forgivability=forgivability, cooperation=cooperation)
