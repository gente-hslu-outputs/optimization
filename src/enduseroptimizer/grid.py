import numpy as np
import numpy.typing as npt

from enduseroptimizer import config


class Grid:
    def loss_cost(self, k: int) -> float:
        return (
            self.import_tariff_k[k] * self.power_import_k[k]
            - self.export_tariff_k[k] * self.power_export_k[k]
        )

    def loss_grid_supply(self, k: int) -> float:
        return self.power_import_k[k]

    losses = {
        "minimize_cost": loss_cost,
        "minimize_grid_supply": loss_grid_supply,
    }

    def __init__(self, name: str = "Grid") -> None:
        """Class to define an external electricity grid

        Editable attributes:
            name (str): Name of the instanciated object, for logging
            discharge_to_grid (bool): allow simultaneous discharging of storages and
                export to grid. Defaults to True
            power_import_max_k (array[float]): maximum power importable from the grid,
                defined for each timestep
            power_export_max_k (array[float]): maximum power exportable to the grid,
                defined for each timestep
            import_tariff_k (array[float]): price per kWh of imported energy,
                defined for each timestep
            export_tariff_k (array[float]): price per kWh of exported energy,
                defined for each timestep
            loss_f (Grid.losses.keys()): loss function to use for optimization

        Optimized attributes:
            power_import_k (array[float]): actual power imported from the grid for
                each timestep, returned by the optimizer
            power_export_k (array[float]): actual power exported to the grid for
                each timestep, returned by the optimizer
            exporting_to_grid_k (array[float]): True for the timesteps for which
                the Enduser is exporting energy to the grid
        """
        self.name = name

        self.discharge_to_grid: bool = True

        self.power_import_max_k: npt.NDArray[np.float_] = 100.0 * np.ones(
            config.horizon
        )  # kW
        self.power_export_max_k: npt.NDArray[np.float_] = 100.0 * np.ones(
            config.horizon
        )  # kW
        self.import_tariff_k: npt.NDArray[np.float_] = np.zeros(config.horizon)  # $/kWh
        self.export_tariff_k: npt.NDArray[np.float_] = np.zeros(config.horizon)  # $/kWh

        self.power_import_k = np.array([])  # kW
        self.power_export_k = np.array([])  # kW
        self.exporting_to_grid_k = np.array([])  # 0/1 (helper)

        self.loss_f = "minimize_cost"

    def to_dict(self, include_results: bool = False) -> dict:
        data = {}

        data["discharge_to_grid_b"] = self.discharge_to_grid
        data["power_import_max_k"] = self.power_import_max_k.tolist()
        data["power_export_max_k"] = self.power_export_max_k.tolist()
        data["import_tariff_k"] = self.import_tariff_k.tolist()
        data["export_tariff_k"] = self.export_tariff_k.tolist()
        data["loss_f_s"] = self.loss_f

        if include_results:
            data["power_import_k"] = self.power_import_k.tolist()
            data["power_export_k"] = self.power_export_k.tolist()
            # data['loss_k'] = [self.losses[self.loss_f](self, k) for k in range(len(self.power_import_k))]

        return data

    def from_dict(self, data: dict, include_results: bool) -> None:
        self.discharge_to_grid = data["discharge_to_grid_b"]
        self.power_import_max_k = np.asarray(data["power_import_max_k"], dtype=float)
        self.power_export_max_k = np.asarray(data["power_export_max_k"], dtype=float)
        self.import_tariff_k = np.asarray(data["import_tariff_k"], dtype=float)
        self.export_tariff_k = np.asarray(data["export_tariff_k"], dtype=float)
        self.loss_f = data["loss_f_s"]

        if include_results:
            self.power_import_k = np.asarray(data["power_import_k"], dtype=float)
            self.power_export_k = np.asarray(data["power_export_k"], dtype=float)
            # self.loss_k = np.asarray(data['loss_k'], dtype=float)
