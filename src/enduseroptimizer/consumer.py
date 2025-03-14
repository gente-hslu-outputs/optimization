import numpy as np
import numpy.typing as npt

from enduseroptimizer import config


class Consumer:
    def __init__(self, name: str = "Consumer") -> None:
        """Class defining an electrical energy consumer

        Editable attributes:
            name (str): Name of the instanciated object, for logging
            power_max (float): Maximal power accepted by the consumer
            available_k (array[int]): timesteps for which the consumer is available
            energy_deficit_max_k (array[float]): maximal energy deficit (compared to
                desired power) per timestep
            power_desired_k (array[float]): power desired (or planned) by the consumer
                at each timestep

        Optimized attributes:
            power_actual_k (array[float]): actual power delivered to the consumer at
                each timestep, written by the optimizer
            energy_deficit_k (array[float]): actual consumer energy deficit at
                each timestep, written by the optimizer
        """

        self.name: str = name

        self.power_max: float = 100.0  # kW
        self.power_min: float = 0.0  # kW

        self.available_k: npt.NDArray[np.int_] = np.ones(config.horizon)  # 0/1
        self.energy_deficit_max_k: npt.NDArray[np.float_] = np.zeros(
            config.horizon
        )  # kWh
        self.power_desired_k: npt.NDArray[np.float_] = np.zeros(config.horizon)  # kW

        self.power_actual_k = np.array([])  # kW
        self.energy_deficit_k = np.array([])  # kWh

    def to_dict(self, include_results: bool = False) -> dict:
        data = {}
        data["power_max_i"] = self.power_max
        data["power_min_i"] = self.power_min

        data["available_k"] = self.available_k.tolist()
        data["energy_deficit_max_k"] = self.energy_deficit_max_k.tolist()
        data["power_desired_k"] = self.power_desired_k.tolist()

        if include_results:
            data["power_actual_k"] = self.power_actual_k.tolist()
            data["energy_deficit_k"] = self.energy_deficit_k.tolist()

        return data

    def from_dict(self, data: dict, include_results: bool) -> None:
        self.power_max = data["power_max_i"]
        self.power_min = data["power_min_i"]

        self.available_k = np.asarray(data["available_k"], dtype=int)
        self.energy_deficit_max_k = np.asarray(
            data["energy_deficit_max_k"], dtype=float
        )
        self.power_desired_k = np.asarray(data["power_desired_k"], dtype=float)

        if include_results:
            self.power_actual_k = np.asarray(data["power_actual_k"], dtype=float)
            self.energy_deficit_k = np.asarray(data["energy_deficit_k"], dtype=float)
