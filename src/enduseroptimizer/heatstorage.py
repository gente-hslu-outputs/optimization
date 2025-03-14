import numpy as np


class HeatStorage:  # TODO - enforce heatproducer/heatstorage mapping (e.g max 1 storage per heatnode)
    def __init__(self, name: str = "HeatStorage") -> None:
        """Class defining a heat storage

        Editable attributes:
            name (str): Name of the instanciated object, for logging
            temperature_max (float): maximum temperature the storage can reach in degC
            temperature_min (float): minimum temperature the storage can reach in degC
            loss_factor (float): heat loss factor of the storage in kWh/K
            volume (float): volume of the storage in l
            density (float): density of the storage in kg/l
            specific_heat (float): specific heat of the storage in kWh/kg/K
            temperature_input (float): temperature of the input flow in degC
            temperature_init (float): initial temperature of the storage in degC
            temperature_final (float): final temperature of the storage in degC
            flow_max (float): maximum flow the storage can provide in l/h

        Optimized attributes:
            energy_in_k (array[float]): energy entering the storage at each timestep in kWh
            energy_out_k (array[float]): energy leaving the storage at each timestep in kWh
            flow_k (array[float]): flow provided by the storage at each timestep in l/s
            temperature_k (array[float]): temperature of the storage at each timestep in degC
        """
        self.name: str = name

        self.temperature_max: float = 80  # degC
        self.temperature_min: float = 40  # degC
        self.loss_factor: float = 1e-4  # kWh/K
        self.volume: float = 200  # l
        self.density: float = 1  # kg/l
        self.specific_heat: float = 1.11e-3  # kWh/kg/K
        self.temperature_input: float = 10  # degC
        self.temperature_init: float = 60  # degC
        self.temperature_final: float = 60  # degC
        self.flow_max: float = 5 * 3600  # l/h

        self.energy_in_k = np.array([])  # kWh
        self.energy_out_k = np.array([])  # kWh

        self.flow_k = np.array([])  # l/s
        self.temperature_k = np.array([])  # degC

    def to_dict(self, include_results: bool = False) -> dict:
        data = {}
        data["temperature_max_i"] = self.temperature_max
        data["temperature_min_i"] = self.temperature_min
        data["loss_factor_i"] = self.loss_factor
        data["volume_i"] = self.volume
        data["density_i"] = self.density
        data["specific_heat_i"] = self.specific_heat
        data["temperature_input_i"] = self.temperature_input
        data["temperature_init_i"] = self.temperature_init
        data["temperature_final_i"] = self.temperature_final
        data["flow_max_i"] = self.flow_max

        if include_results:
            data["flow_k"] = self.flow_k.tolist()
            data["temperature_k"] = self.temperature_k.tolist()

        return data

    def from_dict(self, data: dict, include_results: bool) -> None:
        self.temperature_max = data["temperature_max_i"]
        self.temperature_min = data["temperature_min_i"]
        self.loss_factor = data["loss_factor_i"]
        self.volume = data["volume_i"]
        self.density = data["density_i"]
        self.specific_heat = data["specific_heat_i"]
        self.temperature_input = data["temperature_input_i"]
        self.temperature_init = data["temperature_init_i"]
        self.temperature_final = data["temperature_final_i"]
        self.flow_max = data["flow_max_i"]

        if include_results:
            self.flow_k = np.asarray(data["flow_k"], dtype=float)
            self.temperature_k = np.asarray(data["temperature_k"], dtype=float)
