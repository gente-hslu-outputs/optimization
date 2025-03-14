import numpy as np
import numpy.typing as npt

from enduseroptimizer import config


class Producer:
    def __init__(self, name: str = "Producer") -> None:
        """Class defining an electrical energy producer

        Editable attributes:
            name (str): Name of the instanciated object, for logging
            power_curtailment_factor_max (float): fraction of the produced power
                that can be curtailed, i.e not delivered to the Enduser
            power_actual_k (array[float]): electrical power the producer can provide at
                each timestep

        Optimized attributes:
            power_curtailment_factor_k (array[float]): fraction of the produced power that
                was curtailed, returned by the optimizer
        """
        self.name: str = name

        self.power_curtailment_factor_max: float = 0.0  # (0,1)

        self.power_actual_k: npt.NDArray[np.float_] = np.zeros(config.horizon)  # kW

        self.power_curtailment_factor_k = np.array([])  # (0,1)

    def to_dict(self, include_results: bool = False) -> dict:
        data = {}

        data["power_curtailment_factor_max_i"] = self.power_curtailment_factor_max
        data["power_actual_k"] = self.power_actual_k.tolist()

        if include_results:
            data["power_curtailment_factor_k"] = (
                self.power_curtailment_factor_k.tolist()
            )

        return data

    def from_dict(self, data: dict, include_results: bool) -> None:
        self.power_curtailment_factor_max = data["power_curtailment_factor_max_i"]
        self.power_actual_k = np.asarray(data["power_actual_k"], dtype=float)

        if include_results:
            self.power_curtailment_factor_k = np.asarray(
                data["power_curtailment_factor_k"], dtype=float
            )
