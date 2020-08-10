from serializer import Interface


class Observation(Interface):
    observation_id = int
    before = list
    sender = str
    receiver = str
    author = str
    topic = str
    message = str

    def __init__(self, observation_id, before, sender, receiver, author, topic, message):
        self.observation_id = observation_id
        self.before = before
        self.sender = sender
        self.receiver = receiver
        self.author = author
        self.topic = topic
        self.message = message
        super().__init__(observation_id=observation_id, before=before, sender=sender, receiver=receiver, author=author,
                         topic=topic, message=message)

    def __eq__(self, other):
        return self.observation_id == other.observation_id and self.before == other.before and \
               self.sender == other.sender and self.receiver == other.receiver and self.author == other.author \
               and self.topic == other.topic and self.message == other.message


class Scenario(Interface):
    name = str
    agents = list
    observations = list
    description = str
    history = dict
    trust_thresholds = dict
    weights = dict
    metrics_per_agent = dict
    authorities = dict
    topics = dict

    @staticmethod
    def check_consistency(name, agents, observations):
        if len(name) == 0:
            raise ValueError("Scenario names must be not empty.")
        if len(agents) <= 1:
            raise ValueError("Scenario agents must describe at least 2 agents.")
        if len(observations) == 0:
            raise ValueError("Scenario schedule must be not empty.")
        for observation in observations:
            if type(observation) != dict or not "observation_id" in observation.keys() or not \
                    "sender" in observation.keys() or not "receiver" in observation.keys() or not \
                    "author" in observation.keys() or not "topic" in observation.keys() or not \
                    "message" in observation.keys() or not "before" in observation.keys():
                raise ValueError("Each Observation requires to be dict with all its attributes.")

    def __init__(self, name, agents, observations, history, trust_thresholds, weights,
                 metrics_per_agent, authorities, topics, description="No one described this scenario so far."):
        if history is None or len(history.keys()) == 0:
            # TODO history should be able to be None at default and then set to 0 for all agents
            #  -> maybe even not completely set and filled up with 0
            pass
        self.check_consistency(name, agents, observations)
        self.name = name
        self.agents = agents
        self.observations = observations
        self.history = history
        self.trust_thresholds = trust_thresholds
        self.weights = weights
        self.metrics_per_agent = metrics_per_agent
        self.authorities = authorities
        self.topics = topics
        self.description = description
        super().__init__(name=name, agents=agents, observations=observations, history=history,
                         trust_thresholds=trust_thresholds, weights=weights, metrics_per_agent=metrics_per_agent,
                         authorities=authorities, topics=topics, description=description)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return '%s' % self.name

    def __eq__(self, other):
        return self.name == other.name and self.agents == other.agents and self.observations == other.observations and \
               self.description == other.description



