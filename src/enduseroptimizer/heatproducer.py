import numpy as np


class HeatProducer:
    def __init__(self, name: str = "HeatProducer") -> None:
        """Class defining a heat producer

        Editable attributes:
            name (str): Name of the instanciated object, for logging
            efficiency (float): efficiency of the heat producer
            power_max (float): maximal heat power the producer can provide
            minimum_power_factor (float): minimum fraction of power_max
                the producer can provide
            power_loss_startup (float): power loss when starting up the producer

        Optimized attributes:
            starting_k (array[bool]): starting event for each timestep
            running_k (array[bool]): running event for each timestep
            power_k (array[float]): electrical power consumed by the heat producer
        """
        self.name: str = name

        self.efficiency: float = 0.98  # (0,1)
        self.power_max: float = 5  # kW
        self.minimum_power_factor: float = (
            0.01  # (0, 1), minimum power needed when running, enforces running_k
        )
        self.power_loss_startup: float = 0  # kW when starting_k is True

        self.starting_k = np.array([])  # 0/1
        self.running_k = np.array([])  # 0/1
        self.power_k = np.array([])  # kW

    def to_dict(self, include_results: bool = False) -> dict:
        data = {}
        data["efficiency_i"] = self.efficiency
        data["power_max_i"] = self.power_max
        data["minimum_power_factor_i"] = self.minimum_power_factor
        data["power_loss_startup_i"] = self.power_loss_startup

        if include_results:
            data["starting_k"] = self.starting_k.tolist()
            data["running_k"] = self.running_k.tolist()
            data["power_k"] = self.power_k.tolist()

        return data

    def from_dict(self, data: dict, include_results: bool) -> None:
        self.efficiency = data["efficiency_i"]
        self.power_max = data["power_max_i"]
        self.minimum_power_factor = data["minimum_power_factor_i"]
        self.power_loss_startup = data["power_loss_startup_i"]

        if include_results:
            self.starting_k = np.asarray(data["starting_k"], dtype=int)
            self.running_k = np.asarray(data["running_k"], dtype=int)
            self.power_k = np.asarray(data["power_k"], dtype=float)
