import numpy as np
import numpy.typing as npt

from enduseroptimizer import config


class HeatConsumer:
    """Class defining a heat consumer

    Editable attributes:
        name (str): Name of the instanciated object, for logging
        power_actual_k (array[float]): heat power the consumer requires
    """

    def __init__(self, name: str = "HeatConsumer") -> None:
        self.name: str = name
        self.power_actual_k: npt.NDArray[np.float_] = np.zeros(config.horizon)  # kW

    def to_dict(self, include_results: bool = False) -> dict:
        data = {}
        data["power_actual_k"] = self.power_actual_k.tolist()

        return data

    def from_dict(self, data: dict, include_results: bool) -> None:
        self.power_actual_k = np.asarray(data["power_actual_k"], dtype=float)
