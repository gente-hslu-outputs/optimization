import numpy as np
import numpy.typing as npt

from enduseroptimizer import config


class Storage:
    def __init__(self, name: str = "Storage") -> None:
        """Class defining an electrical energy producer

        Editable attributes:
            name (str): Name of the instanciated object, for logging
            efficiency_charging (float): in (0,1), charging efficiency
            efficiency_discharging (float): in (0,1), discharging efficiency
            power_charge_max (float): maximal charging power
            power_charge_min (float): minimal charging power (not implemented)
            power_discharge_max (float): maximal discharging power
            power_discharge_min (float): minimal discharging power (not implemented)
            energy_capacity (float): energy capacity of the storage in kWh
            state_of_charge_max (float): in (0,1), maximal state of charge
            state_of_charge_min (float): in (0,1), minimal state of charge
            available_k (array[bool]): availability of the storage for each timestep
            state_of_charge_initial_k (array[float]): given state of charge for each
                timestep, needs to be specified for timesteps the storage is connected
            state_of_charge_final_k (array[float]): desired state of charge for each
                timestep, needs to be specified for timesteps the storage is disconnected

        Optimized attributes:
            event_connect_k (array[int]): connection event for each timestep
            event_disconnect_k (array[int]): disconnection event for each timestep
            energy_k (array[float]): stored energy for each timestep
            power_charging_k (array[float]): charging power for each timestep
            power_discharging_k (array[float]): discharging power for each timestep
        """
        self.name: str = name

        self.efficiency_charging: float = 0.9  # (0,1)
        self.efficiency_discharging: float = 0.9  # (0,1)
        self.power_charge_max: float = 100.0  # kW
        self.power_charge_min: float = 100.0  # kW
        self.power_discharge_max: float = 100.0  # kW
        self.power_discharge_min: float = 100.0  # kW
        self.energy_capacity: float = 50.0  # kWh
        self.state_of_charge_max: float = 0.90  # (0,1)
        self.state_of_charge_min: float = 0.10  # (0,1)
        self.available_k: npt.NDArray[np.int_] = np.ones(
            config.horizon, dtype=int
        )  # 0/1
        self.state_of_charge_initial_k: npt.NDArray[np.float_] = np.zeros(
            config.horizon
        )  # (0,1)
        self.state_of_charge_final_k: npt.NDArray[np.float_] = np.zeros(
            config.horizon
        )  # (0,1)

        self.event_connect_k: npt.NDArray[np.int_] = np.zeros(
            config.horizon, dtype=int
        )  # 0/1
        self.event_disconnect_k: npt.NDArray[np.int_] = np.zeros(
            config.horizon, dtype=int
        )  # 0/1
        self.energy_k = np.array([])  # kWh
        self.power_charging_k = np.array([])  # kW
        self.power_discharging_k = np.array([])  # kW

    def to_dict(self, include_results: bool = False) -> dict:
        data = {}
        data["efficiency_charging_i"] = self.efficiency_charging
        data["efficiency_discharging_i"] = self.efficiency_discharging
        data["power_charge_max_i"] = self.power_charge_max
        data["power_charge_min_i"] = self.power_charge_min
        data["power_discharge_max_i"] = self.power_discharge_max
        data["power_discharge_min_i"] = self.power_discharge_min
        data["energy_capacity_i"] = self.energy_capacity
        data["state_of_charge_max_i"] = self.state_of_charge_max
        data["state_of_charge_min_i"] = self.state_of_charge_min

        data["available_k"] = self.available_k.tolist()
        data["state_of_charge_initial_k"] = self.state_of_charge_initial_k.tolist()
        data["state_of_charge_final_k"] = self.state_of_charge_final_k.tolist()

        if include_results:
            data["energy_k"] = self.energy_k.tolist()
            data["power_charging_k"] = self.power_charging_k.tolist()
            data["power_discharging_k"] = self.power_discharging_k.tolist()

        return data

    def from_dict(self, data: dict, include_results: bool) -> None:
        self.efficiency_charging = data["efficiency_charging_i"]
        self.efficiency_discharging = data["efficiency_discharging_i"]
        self.power_charge_max = data["power_charge_max_i"]
        self.power_charge_min = data["power_charge_min_i"]
        self.power_discharge_max = data["power_discharge_max_i"]
        self.power_discharge_min = data["power_discharge_min_i"]
        self.energy_capacity = data["energy_capacity_i"]
        self.state_of_charge_max = data["state_of_charge_max_i"]
        self.state_of_charge_min = data["state_of_charge_min_i"]

        self.available_k = np.asarray(data["available_k"], dtype=int)
        self.state_of_charge_initial_k = np.asarray(
            data["state_of_charge_initial_k"], dtype=float
        )
        self.state_of_charge_final_k = np.asarray(
            data["state_of_charge_final_k"], dtype=float
        )

        if include_results:
            self.energy_k = np.asarray(data["energy_k"], dtype=float)
            self.power_charging_k = np.asarray(data["power_charging_k"], dtype=float)
            self.power_discharging_k = np.asarray(
                data["power_discharging_k"], dtype=float
            )
