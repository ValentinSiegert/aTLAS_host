import importlib
import importlib.util
import sys
from serializer import Interface
from abc import ABC, abstractmethod
from os import listdir
from os.path import isfile
from pathlib import Path


class UpdatableInterface(Interface):
    """
    Makes Interface objects updatable by updating the self.kwargs at start of serialization.
    """
    def serialize(self):
        for key in self.kwargs.keys():
            value = getattr(self, key)
            self.kwargs[key] = value if type(value) is not type else value.__name__
        return super().serialize()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Observation(UpdatableInterface):
    """
    Representing one observation within a scenario.
    """
    observation_id = int
    before = list
    sender = str
    receiver = str
    authors = list
    topic = str
    message = str
    details = dict

    def __init__(self, observation_id, before, sender, receiver, authors, message, details):
        """
        :type observation_id: int
        :type before: list
        :type sender: str
        :type receiver: str
        :type authors: list
        :type message: str
        :type details: dict
        """

        self.observation_id = observation_id
        self.before = before
        self.sender = sender
        self.receiver = receiver
        self.authors = authors
        self.message = message
        self.details = details

        super().__init__(observation_id=observation_id, before=before, sender=sender, receiver=receiver, authors=authors,
                         message=message, details=details)

    def __eq__(self, other):
        return self.observation_id == other.observation_id and self.before == other.before and \
               self.sender == other.sender and self.receiver == other.receiver and self.authors == other.authors \
               and self.message == other.message and self.details == other.details


class Scale(ABC):
    """
    Base class for all trust scales in aTLAS.
    """
    @abstractmethod
    def minimum_to_trust_others(self):
        """
        :return: trust minimum another party has to have to be declared as trusted or to be cooperated with
        :rtype: float or int
        """
        pass

    @abstractmethod
    def default_value(self):
        """
        :return: represents the default value for any new or unknown party
        :rtype: float or int
        """
        pass

    @abstractmethod
    def maximum_value(self):
        """
        :return: represents the maximum value within this scale
        :rtype: float or int
        """
        pass

    @abstractmethod
    def minimum_value(self):
        """
        :return: represents the minimum value within this scale
        :rtype: float or int
        """
        pass

    @abstractmethod
    def cooperation_threshold(self):
        """
        :return: represents the cooperation threshold for the current scale
        :rtype: float or int
        """
        pass

    @abstractmethod
    def set_cooperation_threshold(self, new_cooperation_threshold):
        """
        Changes the cooperation threshold for the current scale to the received value
        """
        pass

    @abstractmethod
    def normalize_value_to_scale(self, value, data_min, data_max):
        """
        Calculates a value that is normalized for the scale interval

        :param value: The value that should be normalized
        :param data_min: Smallest possible value for the given data
        :param data_max: Largest possible value for the given data
        :return: The normalized value
        """
        pass

    def __init__(self):
        if hasattr(self, 'maximum') and hasattr(self, 'minimum'):
            if type(self.maximum) is float and type(self.minimum) is float:
                self.number_type = float
            elif type(self.maximum) is int and type(self.minimum) is int:
                self.number_type = int
            else:
                raise TypeError("Scale is defined with mixed minimum and maximum variable types. "
                                "Requires to be int and int, or float and float.")
        else:
            raise AttributeError("Scale requires minimum and maximum variable.")


class Scenario(UpdatableInterface):
    """
    The Scenario class for the usage of the scenarios with its DSL files.
    """
    name = str
    agents = list
    observations = list
    description = str
    history = dict
    scales_per_agent = dict
    metrics_per_agent = dict

    def agent_uses_metric(self, agent, metric_name):
        """
        :param agent: the agent's descriptor
        :param metric_name: the metric's name
        :type agent: str
        :type metric_name: str
        :return: whether metric name is used by agent
        :rtype: bool
        """
        return metric_name in self.metrics_per_agent[agent].keys()

    def any_agents_use_metric(self, metric_name):
        """
        :param metric_name: the metric's name
        :type metric_name: str
        :return: whether metric_name is used by any agent in the scenario
        :rtype: bool
        """
        return any(metric_name in metrics.keys() for agent, metrics in self.metrics_per_agent.items())

    def agents_with_metric(self, metric_name):
        """
        :param metric_name: the metric's name
        :type metric_name: str
        :return: all agents with their metric if they use metric_name as well
        :rtype: dict
        """
        agent_dict = {}
        if metric_name == 'content_trust.topic' or metric_name == 'content_trust.authority':
            agent_dict = {agent: metrics[metric_name] for agent, metrics in self.metrics_per_agent.items()
                          if metric_name in metrics.keys()}
        return agent_dict

    def check_consistency(self):
        """
        Checks the consistency of the initiated Scenario and raises Errors if something went wrong.

        :rtype: None
        :raises ValueError: any checked attribute has not a semantic reliable value.
        :raises TypeError: any object (e.g. Observation, Scale) cannot be initialized properly.
        :raises ModuleNotFoundError: Any scale's package was not found on local storage.
        :raises SyntaxError: Any scale implementation is not subclass of Scale and UpdatableInterface.
        """
        if len(self.name) == 0:
            raise ValueError("Scenario names must be not empty.")
        if len(self.agents) <= 1:
            raise ValueError("Scenario agents must describe at least 2 agents.")
        if len(self.observations) == 0:
            raise ValueError("Scenario schedule must be not empty.")
        for observation in self.observations:
            if type(observation) != dict:
                raise ValueError("Each Observation requires to be dict.")
            Observation(**observation)  # check if observation is instantiable, else TypeError will be raised.
        for scale_dict in self.scales_per_agent.values():
            init_scale_object(scale_dict)
        # TODO: check for correct scales_per_agent setup in context of float and int numbers
        # TODO: check for correct metrics_per_agent setup
        for metrics in self.metrics_per_agent.values():
            if '__final__' not in metrics.keys() or 'name' not in metrics['__final__'].keys():
                raise ValueError("Each agent requires a final trust metric under "
                                 "metrics_per_agent[agent]['__final__']['name'].")

    @staticmethod
    def format_number_type_of_value(value, target_type):
        """
        Formats the given value to target type if value is of type int or float
        and target type is float or int respectively.

        :param value: The value to potentially change its number type.
        :type value: Any
        :param target_type: The numbers target type.
        :type target_type: type
        :return: The value in correct number type or original type if not float or int.
        :rtype: Any
        """
        if type(value) is float or type(value) is int:
            if target_type is float:
                return float(value)
            elif target_type is int:
                return int(value)
        return value

    @staticmethod
    def format_number_type_in_dictionary(dictionary, target_type):
        """
        Formats the numbers in the given dictionary by iterating over it to given target type.

        :param dictionary: The dictionary to iterate over.
        :type dictionary: dict
        :param target_type: The numbers target type.
        :type target_type: type
        """
        for key, value in dictionary.items():
            dictionary[key] = Scenario.format_number_type_of_value(value, target_type)
            if type(value) is dict:
                Scenario.format_number_type_in_dictionary(value, target_type)
            if type(value) is list:
                Scenario.format_number_type_in_listing(value, target_type)

    @staticmethod
    def format_number_type_in_listing(listing, target_type):
        """
        Formats the numbers in the given list by iterating over it to given target type.

        :param listing: The list to iterate over.
        :type listing: list
        :param target_type: The numbers target type.
        :type target_type: type
        """
        for count, value in enumerate(listing):
            listing[count] = Scenario.format_number_type_of_value(value, target_type)
            if type(value) is dict:
                Scenario.format_number_type_in_dictionary(value, target_type)
            if type(value) is list:
                Scenario.format_number_type_in_listing(value, target_type)

    @staticmethod
    def correct_number_types(obj_desc):
        """
        Corrects number types in object description of Scenario by using `load_scale_spec`
        and `change_number_type_in_dictionary` to format scale, history and metric descriptions.

        :param obj_desc: object description of Scenario
        :type obj_desc: dict
        :return: object description of Scenario with correct number formats
        :rtype: dict
        :raises ModuleNotFoundError: Scale's package was not found on local storage.
        :raises SyntaxError: Scale implementation is not subclass of Scale and UpdatableInterface.
        """
        for agent in obj_desc['agents']:
            scale_dict = obj_desc['scales_per_agent'][agent]
            cls = load_scale_spec(scale_dict)
            number_type = cls.maximum
            if type(obj_desc['scales_per_agent'][agent]) is dict:
                Scenario.format_number_type_in_dictionary(obj_desc['scales_per_agent'][agent], number_type)
            else:
                Scenario.format_number_type_in_listing(obj_desc['scales_per_agent'][agent], number_type)
            if type(obj_desc['history'][agent]) is dict:
                Scenario.format_number_type_in_dictionary(obj_desc['history'][agent], number_type)
            else:
                Scenario.format_number_type_in_listing(obj_desc['history'][agent], number_type)
            if type(obj_desc['metrics_per_agent'][agent]) is dict:
                Scenario.format_number_type_in_dictionary(obj_desc['metrics_per_agent'][agent], number_type)
            else:
                Scenario.format_number_type_in_listing(obj_desc['metrics_per_agent'][agent], number_type)

    def scenario_args(self, name, agents, observations, history, scales_per_agent, metrics_per_agent,
                      description="No one described this scenario so far."):
        """
        This method only exists to give out the real arg list to the Scenario Factory, while init is only requesting
        those mandatory arguments for the small constructor which is required for the large scenario files.

        :type name: str
        :type agents: list
        :type observations: list
        :type history: dict
        :type scales_per_agent: dict
        :type metrics_per_agent: dict
        :type description: str
        """
        pass

    def __init__(self, name, agents=None, observations=None, history=None, scales_per_agent=None, metrics_per_agent=None,
                 description="No one described this scenario so far."):
        """
        :type name: str
        :type agents: list
        :type observations: list
        :type history: dict
        :type scales_per_agent: dict
        :type metrics_per_agent: dict
        :type description: str
        """
        if history is None or len(history.keys()) == 0:
            # TODO history should be able to be None at default and then set to 0 for all agents
            #  -> maybe even not completely set and filled up with 0
            pass
        self.name = name
        self.agents = agents if agents else []
        self.observations = observations if observations else []
        self.history = history if history else {}
        self.scales_per_agent = scales_per_agent if scales_per_agent else {}
        self.metrics_per_agent = metrics_per_agent if metrics_per_agent else {}
        self.description = description
        # only check consistency if scenario is not on small load
        if agents and observations and history and scales_per_agent and metrics_per_agent:
            self.check_consistency()
        super().__init__(name=name, agents=self.agents, observations=self.observations, history=self.history,
                         scales_per_agent=self.scales_per_agent, metrics_per_agent=self.metrics_per_agent,
                         description=description)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return '%s' % self.name

    def __eq__(self, other):
        return self.name == other.name and self.agents == other.agents and self.observations == other.observations and \
               self.history == other.history and self.scales_per_agent == other.scales_per_agent and \
               self.metrics_per_agent == other.metrics_per_agent and self.description == other.description


def load_scale_spec(scale_dict):
    """
    Loads a scale object spec of the given scale attributes by dynamically importing the correct class.
    scale_dict['package'] requires to be a .py file name in scale packages,
    which Class name is the same without '_' in CamelCase.

    :param scale_dict: scale object definition
    :type scale_dict: dict
    :return: the scale object spec
    :raises ModuleNotFoundError: Scale's package was not found on local storage.
    :raises SyntaxError: Scale implementation is not subclass of Scale and UpdatableInterface.
    """
    scales_path = Path(Path(__file__).parent.absolute()) / "scales"
    module_name = vars(sys.modules[__name__])['__package__']
    cls = None
    scale_file_names = [file for file in listdir(scales_path) if isfile(scales_path / file)
                        and file.endswith("_scale.py")]
    for file_name in scale_file_names:
        file_package = file_name.split(".")[0]
        # python module path
        if module_name != '':
            import_module = f".scales.{file_package}"
        else:
            import_module = f"scales.{file_package}"
        # ensure package is accessible
        implementation_spec = importlib.util.find_spec(import_module, module_name)
        if file_package == scale_dict['package'] and implementation_spec is not None:
            # check if module was imported during runtime to decide if reload is required
            scale_spec = importlib.util.find_spec(import_module, module_name)
            # import scale config to variable
            scale_module = importlib.import_module(import_module, module_name)
            # only reload module after importing if spec was found before
            if scale_spec is not None:
                scale_module = importlib.reload(scale_module)
            # class name requires to be file name in CamelCase
            class_name = ''.join([name_part.capitalize() for name_part in file_package.split("_")])
            if hasattr(scale_module, class_name):
                cls = getattr(scale_module, class_name)
                if not issubclass(cls, Scale) or not issubclass(cls, UpdatableInterface):
                    raise SyntaxError("Scale implementation is not subclass of Scale and UpdatableInterface.")
    if cls is None:
        raise ModuleNotFoundError(f"Scale with package '{scale_dict['package']}' was not found.")
    return cls


def init_scale_object(scale_dict):
    """
    Creates a scale object of the given scale attributes by using `load_scale_spec(scale_dict)`.

    :param scale_dict: scale object definition
    :type scale_dict: dict
    :return: the initiated scale object
    :rtype: Scale or None
    :raises ModuleNotFoundError: Scale's package was not found on local storage.
    :raises SyntaxError: Scale implementation is not subclass of Scale and UpdatableInterface.
    :raises TypeError: Scale object cannot get initialized correctly with scale_dict values.
    """
    cls = load_scale_spec(scale_dict)
    scale_kwargs = {key: value for key, value in scale_dict.items() if key != 'package'}
    scale_object = cls(**scale_kwargs)  # might raises TypeError by class specification
    return scale_object
