from datetime import datetime, timedelta

import numpy as np
import pulp as pl

import enduseroptimizer
from enduseroptimizer import (
    Consumer,
    Grid,
    HeatNode,
    Producer,
    Storage,
    config,
)


class EndUser:
    def __init__(self, name: str = "EndUser"):
        """Base class for the enduseroptimizer. Represents a closed
        system/building/community, where electricity is transported
        without losses.

        Editable attributes:
            name (str): Name of the instanciated object, for logging
            producers (list[Producer]): usable electricity producers
            storages (list[Storage]): available electricity storages
            consumers (list[Consumer]): available electricity consumers
            heatnodes (list[HeatNode]): independent heatnodes in the system
            grid (Grid): describes the Grid the enduser is connected to
            loss (float): value of the loss, updated after optimization
            include_results (bool): when true, the optimization results
                are included in the exported files
            start_time (datetime): date of the start of the simulation
            flexibility (bool): enable flexible assets in the enduser
            status (str): status of the optimization, updated after optimization
        """
        self.name = name

        self.producers: list[Producer] = []
        self.storages: list[Storage] = []
        self.consumers: list[Consumer] = []
        self.heatnodes: list[HeatNode] = []
        self.grid: Grid = Grid()
        self.loss: float = 0.0
        self.include_results: bool = False
        self.start_time: datetime = datetime(year=2021, month=6, day=1)
        self.flexibility: bool = True
        self.status: str = "Not Solved"

    def get_timestamps(self) -> list[datetime]:
        """Returns the timestamps of the optimization horizon"""
        return [
            self.start_time + timedelta(hours=i*config.delta_t) for i in range(config.horizon)
        ]

    def to_dict(self) -> dict:
        data = {}

        data["horizon_i"] = config.horizon
        data["delta_t_i"] = config.delta_t
        data["include_results_i"] = self.include_results
        data["start_time_i"] = self.start_time.timestamp()

        data["flexibility_i"] = self.flexibility

        data["producers_d"] = {}
        for i, producer in enumerate(self.producers):
            data["producers_d"][i] = producer.to_dict(self.include_results)

        data["storages_d"] = {}
        for i, storage in enumerate(self.storages):
            data["storages_d"][i] = storage.to_dict(self.include_results)

        data["consumers_d"] = {}
        for i, consumer in enumerate(self.consumers):
            data["consumers_d"][i] = consumer.to_dict(self.include_results)

        data["heatnodes_dd"] = {}
        for i, heatnode in enumerate(self.heatnodes):
            data["heatnodes_dd"][i] = heatnode.to_dict(self.include_results)

        data["grid_d"] = {}
        data["grid_d"]["0"] = self.grid.to_dict(self.include_results)

        if self.include_results:
            data["loss_i"] = self.loss

        return data

    def from_dict(self, data: dict) -> None:
        enduseroptimizer.config.horizon = data["horizon_i"]
        enduseroptimizer.config.delta_t = data["delta_t_i"]
        self.include_results = data["include_results_i"]
        self.start_time = datetime.fromtimestamp(data["start_time_i"])
        self.flexibility = data["flexibility_i"]

        for key in data["producers_d"].keys():
            inst = Producer()
            inst.from_dict(data["producers_d"][key], self.include_results)
            self.producers.append(inst)

        for key in data["storages_d"].keys():
            inst = Storage()
            inst.from_dict(data["storages_d"][key], self.include_results)
            self.storages.append(inst)

        for key in data["consumers_d"].keys():
            inst = Consumer()
            inst.from_dict(data["consumers_d"][key], self.include_results)
            self.consumers.append(inst)

        for key in data["heatnodes_dd"].keys():
            inst = HeatNode()
            inst.from_dict(data["heatnodes_dd"][key], self.include_results)
            self.heatnodes.append(inst)

        self.grid = Grid()
        self.grid.from_dict(data["grid_d"]["0"], self.include_results)

        if self.include_results:
            self.loss = data["loss_i"]

    def optimize(self) -> None:
        """Optimize the electricity import/export values of the enduser,
        w.r.t. the loss function given by the grid, using the previously
        defined flexible assets
        """
        m = pl.LpProblem("MPC", pl.LpMinimize)
        constraints = {}

        # Consumers
        for i, consumer in enumerate(self.consumers):
            consumer.energy_deficit_k = [
                pl.LpVariable(
                    cat="Continuous",
                    lowBound=0,
                    upBound=consumer.energy_deficit_max_k[k] * self.flexibility,
                    name=f"energy_deficit_k[{i}]{k}",
                )
                for k in range(config.horizon)
            ]

            consumer.power_actual_k = [
                pl.LpVariable(
                    cat="Continuous",
                    lowBound=consumer.power_min,
                    upBound=consumer.available_k[k] * consumer.power_max,
                    name=f"power_actual_k[{i}]{k}",
                )
                for k in range(config.horizon)
            ]

            constraints.update(
                {
                    f"energy_deficit_k[{i}]0": pl.LpConstraint(
                        e=(
                            consumer.energy_deficit_k[0]
                            - (consumer.power_desired_k[0] - consumer.power_actual_k[0])
                            * config.delta_t
                        ),
                        sense=pl.LpConstraintEQ,
                        rhs=0,
                    )
                }
            )

            constraints.update(
                {
                    f"energy_deficit_k[{i}]{k}": pl.LpConstraint(
                        e=(
                            consumer.energy_deficit_k[k]
                            - consumer.energy_deficit_k[k - 1]
                            - (consumer.power_desired_k[k] - consumer.power_actual_k[k])
                            * config.delta_t
                        ),
                        sense=pl.LpConstraintEQ,
                        rhs=0,
                    )
                    for k in range(config.horizon)
                }
            )

        # Storages
        for i, storage in enumerate(self.storages):
            storage.event_connect_k[0] = storage.available_k[0]  # start of window
            for k in range(1, config.horizon):
                storage.event_connect_k[k] = (
                    storage.available_k[k] - storage.available_k[k - 1]
                ) == 1
                storage.event_disconnect_k[k] = (
                    storage.available_k[k] - storage.available_k[k - 1]
                ) == -1

            storage.energy_k = [
                pl.LpVariable(
                    cat="Continuous",
                    lowBound=storage.available_k[k]
                    * storage.energy_capacity
                    * storage.state_of_charge_min,
                    upBound=storage.available_k[k]
                    * storage.energy_capacity
                    * storage.state_of_charge_max,
                    name=f"storage_energy_k[{i}]{k}",
                )
                for k in range(config.horizon)
            ]

            storage.power_charging_k = [
                pl.LpVariable(
                    cat="Continuous",
                    lowBound=0,
                    upBound=storage.available_k[k]
                    * storage.power_charge_max
                    * self.flexibility,
                    name=f"storage_power_charging_k[{i}]{k}",
                )
                for k in range(config.horizon)
            ]

            storage.power_discharging_k = [
                pl.LpVariable(
                    cat="Continuous",
                    lowBound=0,
                    upBound=storage.available_k[k]
                    * storage.power_discharge_max
                    * self.flexibility,
                    name=f"storage_power_discharging_k[{i}]{k}",
                )
                for k in range(config.horizon)
            ]

            for k in range(config.horizon):
                if storage.available_k[k]:
                    if storage.event_connect_k[
                        k
                    ]:  # storage just got connected (or start of window), use state_of_charge_initial
                        constraints.update(
                            {
                                f"energy storage[{i}]{k} initial": pl.LpConstraint(
                                    e=(
                                        -storage.energy_k[k]
                                        + storage.energy_capacity
                                        * storage.state_of_charge_initial_k[k]
                                        + (
                                            storage.efficiency_charging
                                            * storage.power_charging_k[k]
                                            - 1.0
                                            / storage.efficiency_discharging
                                            * storage.power_discharging_k[k]
                                        )
                                        * config.delta_t
                                    ),
                                    sense=pl.LpConstraintEQ,
                                    rhs=0,
                                )
                            }
                        )
                    else:  # storage was already connected, use last energy
                        constraints.update(
                            {
                                f"energy storage[{i}]{k}": pl.LpConstraint(
                                    e=(
                                        -storage.energy_k[k]
                                        + storage.energy_k[k - 1]
                                        + (
                                            storage.efficiency_charging
                                            * storage.power_charging_k[k]
                                            - 1.0
                                            / storage.efficiency_discharging
                                            * storage.power_discharging_k[k]
                                        )
                                        * config.delta_t
                                    ),
                                    sense=pl.LpConstraintEQ,
                                    rhs=0,
                                )
                            }
                        )
                    if (
                        storage.event_disconnect_k[k] or k == config.horizon - 1
                    ):  # final SoC constraint
                        constraints.update(
                            {
                                f"energy storage[{i}]{k} final": pl.LpConstraint(
                                    e=(
                                        -storage.energy_k[k]
                                        + storage.energy_capacity
                                        * storage.state_of_charge_final_k[k]
                                    ),
                                    sense=pl.LpConstraintEQ,
                                    rhs=0,
                                )
                            }
                        )

        for i, producer in enumerate(self.producers):
            producer.power_curtailment_factor_k = [
                pl.LpVariable(
                    cat="Continuous",
                    lowBound=0,
                    upBound=producer.power_curtailment_factor_max,
                    name=f"producer_curtailment_factor_k[{i}]{k}",
                )
                for k in range(config.horizon)
            ]

        for i, heatnode in enumerate(self.heatnodes):
            for j, heatproducer in enumerate(heatnode.heatproducers):
                heatproducer.power_k = [
                    pl.LpVariable(
                        cat="Continuous",
                        lowBound=0,
                        name=f"power_k-heatnode[{i}]-producer[{j}]{k}",
                    )
                    for k in range(config.horizon)
                ]

                heatproducer.running_k = [
                    pl.LpVariable(
                        cat="Binary",
                        name=f"running_k-heatnode[{i}]-producer[{j}]{k}",
                    )
                    for k in range(config.horizon)
                ]

                heatproducer.starting_k = [
                    pl.LpVariable(
                        cat="Binary",
                        name=f"starting_k-heatnode[{i}]-producer[{j}]{k}",
                    )
                    for k in range(config.horizon)
                ]

                constraints.update(
                    {
                        f"power_max-heatnode[{i}]-producer[{j}]{k}": pl.LpConstraint(
                            e=(
                                -heatproducer.power_k[k]
                                + (
                                    heatproducer.running_k[k]
                                    + heatproducer.starting_k[k]
                                    * heatproducer.power_loss_startup
                                )
                                * heatproducer.power_max
                            ),
                            sense=pl.LpConstraintGE,
                            rhs=0,
                        )
                        for k in range(config.horizon)
                    }
                )

                constraints.update(
                    {
                        f"power_min-heatnode[{i}]-producer[{j}]{k}": pl.LpConstraint(
                            e=(
                                -heatproducer.power_k[k]
                                + heatproducer.running_k[k]
                                * heatproducer.minimum_power_factor
                                * heatproducer.power_max
                            ),
                            sense=pl.LpConstraintLE,
                            rhs=0,
                        )
                        for k in range(config.horizon)
                    }
                )

                constraints.update(
                    {
                        f"power_start-heatnode[{i}]-producer[{j}]{k}": pl.LpConstraint(
                            e=(
                                -heatproducer.power_k[k]
                                + heatproducer.starting_k[k]
                                * heatproducer.power_loss_startup
                                * heatproducer.power_max
                            ),
                            sense=pl.LpConstraintLE,
                            rhs=0,
                        )
                        for k in range(config.horizon)
                    }
                )

                constraints.update(
                    {
                        f"starting-heatnode[{i}]-producer[{j}]0": pl.LpConstraint(
                            e=(-heatproducer.starting_k[0] + heatproducer.running_k[0]),
                            sense=pl.LpConstraintEQ,
                            rhs=0,
                        )
                    }
                )

                constraints.update(
                    {
                        f"starting1-heatnode[{i}]-producer[{j}]{k}": pl.LpConstraint(
                            e=(-heatproducer.starting_k[k] + heatproducer.running_k[k]),
                            sense=pl.LpConstraintGE,
                            rhs=0,
                        )
                        for k in range(1, config.horizon)
                    }
                )

                constraints.update(
                    {
                        f"starting2-heatnode[{i}]-producer[{j}]{k}": pl.LpConstraint(
                            e=(
                                heatproducer.starting_k[k]
                                + heatproducer.running_k[k - 1]
                            ),
                            sense=pl.LpConstraintLE,
                            rhs=1,
                        )
                        for k in range(1, config.horizon)
                    }
                )

                constraints.update(
                    {
                        f"starting3-heatnode[{i}]-producer[{j}]{k}": pl.LpConstraint(
                            e=(
                                -heatproducer.starting_k[k]
                                + heatproducer.running_k[k]
                                - heatproducer.running_k[k - 1]
                            ),
                            sense=pl.LpConstraintLE,
                            rhs=0,
                        )
                        for k in range(1, config.horizon)
                    }
                )

            for j, heatstorage in enumerate(heatnode.heatstorages):
                heatstorage.temperature_k = [
                    pl.LpVariable(
                        cat="Continuous",
                        lowBound=heatstorage.temperature_min,
                        upBound=heatstorage.temperature_max,
                        name=f"temperature_k-heatnode[{i}]-storage[{j}]{k}",
                    )
                    for k in range(config.horizon)
                ]

                heatstorage.energy_in_k = [
                    pl.LpVariable(
                        cat="Continuous",
                        name=f"energy_in_k-heatnode[{i}]-storage[{j}]{k}",
                    )
                    for k in range(config.horizon)
                ]

                heatstorage.energy_out_k = [
                    pl.LpVariable(
                        cat="Continuous",
                        name=f"energy_out_k-heatnode[{i}]-storage[{j}]{k}",
                    )
                    for k in range(config.horizon)
                ]

                constraints.update(
                    {
                        f"temperature_final-heatnode[{i}]-storage[{j}]": pl.LpConstraint(
                            e=(
                                -heatstorage.temperature_k[config.horizon - 1]
                                + heatstorage.temperature_final
                            ),
                            sense=pl.LpConstraintEQ,
                            rhs=0,
                        )
                    }
                )

                constraints.update(
                    {
                        f"energy_in_k-heatnode[{i}]-storage[{j}]{k}": pl.LpConstraint(
                            e=(
                                -pl.lpSum(
                                    (
                                        heatproducer.power_k[k]
                                        - heatproducer.starting_k[k]
                                        * heatproducer.power_loss_startup
                                        * heatproducer.power_max
                                    )
                                    * heatproducer.efficiency
                                    * config.delta_t
                                    for heatproducer in heatnode.heatproducers
                                )
                                + pl.lpSum(
                                    heatstorage.energy_in_k[k]
                                    for heatstorage in heatnode.heatstorages
                                )
                            ),
                            sense=pl.LpConstraintEQ,
                            rhs=0,
                        )
                        for k in range(config.horizon)
                    }
                )

                constraints.update(
                    {
                        f"Heat storage-heatnode[{i}]-storage[{j}]initial": pl.LpConstraint(
                            e=(
                                -heatstorage.volume
                                * self.flexibility
                                * (
                                    heatstorage.temperature_k[0]
                                    - heatstorage.temperature_init
                                )
                                * (heatstorage.density * heatstorage.specific_heat)
                                + heatstorage.energy_in_k[0]
                                - heatstorage.energy_out_k[0]
                                - heatstorage.loss_factor * heatstorage.temperature_k[0]
                            ),
                            sense=pl.LpConstraintEQ,
                            rhs=0,
                        )
                    }
                )

                constraints.update(
                    {
                        f"Heat storage-heatnode[{i}]-storage[{j}]{k}": pl.LpConstraint(
                            e=(
                                -heatstorage.volume
                                * self.flexibility
                                * (
                                    heatstorage.temperature_k[k]
                                    - heatstorage.temperature_k[k - 1]
                                )
                                * (heatstorage.density * heatstorage.specific_heat)
                                + heatstorage.energy_in_k[k]
                                - heatstorage.energy_out_k[k]
                                - heatstorage.loss_factor * heatstorage.temperature_k[k]
                            ),
                            sense=pl.LpConstraintEQ,
                            rhs=0,
                        )
                        for k in range(1, config.horizon)
                    }
                )

            constraints.update(
                {
                    f"energy_out_k-heatnode[{i}]{k}": pl.LpConstraint(
                        e=(
                            -pl.lpSum(
                                heatconsumer.power_actual_k[k] * config.delta_t
                                for heatconsumer in heatnode.heatconsumers
                            )
                            + pl.lpSum(
                                heatstorage.energy_out_k[k]
                                for heatstorage in heatnode.heatstorages
                            )
                        ),
                        sense=pl.LpConstraintEQ,
                        rhs=0,
                    )
                    for k in range(config.horizon)
                }
            )

        # Grid
        self.grid.power_import_k = [
            pl.LpVariable(
                cat="Continuous",
                lowBound=0,
                upBound=self.grid.power_import_max_k[k],
                name=f"grid_import_max{k}",
            )
            for k in range(config.horizon)
        ]

        self.grid.power_export_k = [
            pl.LpVariable(
                cat="Continuous",
                lowBound=0,
                upBound=self.grid.power_export_max_k[k],
                name=f"grid_export_max{k}",
            )
            for k in range(config.horizon)
        ]

        # Overall constraints
        constraints.update(
            {
                f"power_balance[{j}]": pl.LpConstraint(
                    e=(
                        -self.grid.power_import_k[j]
                        + self.grid.power_export_k[j]
                        + pl.lpSum(
                            consumer.power_actual_k[j] for consumer in self.consumers
                        )
                        + pl.lpSum(
                            heatproducer.power_k[j]
                            for heatnode in self.heatnodes
                            for heatproducer in heatnode.heatproducers
                        )
                        + pl.lpSum(
                            storage.power_charging_k[j] - storage.power_discharging_k[j]
                            for storage in self.storages
                        )
                        - pl.lpSum(
                            producer.power_actual_k[j]
                            * (1 - producer.power_curtailment_factor_k[j])
                            for producer in self.producers
                        )
                    ),
                    sense=pl.LpConstraintEQ,
                    rhs=0,
                )
                for j in range(config.horizon)
            }
        )

        self.grid.exporting_to_grid_k = [
            pl.LpVariable(
                cat="Binary",
                name=f"exporting_to_grid_k{k}",
            )
            for k in range(config.horizon)
        ]

        constraints.update(
            {
                f"Export indicator 1-{k}": pl.LpConstraint(
                    e=(
                        -self.grid.power_export_k[k]
                        + self.grid.exporting_to_grid_k[k]
                        * self.grid.power_export_max_k[k]
                    ),
                    sense=pl.LpConstraintGE,
                    rhs=0,
                )
                for k in range(config.horizon)
            }
        )

        constraints.update(
            {
                f"Mutually exclusive import/export-{k}": pl.LpConstraint(
                    e=(
                        self.grid.power_import_k[k]
                        - (1 - self.grid.exporting_to_grid_k[k])
                        * self.grid.power_import_max_k[k]
                    ),
                    sense=pl.LpConstraintLE,
                    rhs=0,
                )
                for k in range(config.horizon)
            }
        )

        if (
            not self.grid.discharge_to_grid
        ):  # ensure export and discharge are exclusive events
            constraints.update(
                {
                    f"Exclusive export and storage discharge-M1{k}": pl.LpConstraint(
                        e=(
                            pl.lpSum(
                                storage.power_discharging_k[k]
                                for storage in self.storages
                            )
                            - (1 - self.grid.exporting_to_grid_k[k])
                            * pl.lpSum(
                                storage.power_discharge_max for storage in self.storages
                            )
                        ),
                        sense=pl.LpConstraintLE,
                        rhs=0,
                    )
                    for k in range(config.horizon)
                }
            )

        objective = pl.lpSum(
            self.grid.losses[self.grid.loss_f](self.grid, k)
            for k in range(config.horizon)
        )

        m.constraints = constraints
        m.objective = objective

        m.solve(pl.PULP_CBC_CMD(msg=0))

        print("Status: " + pl.LpStatus[m.status])
        self.status = pl.LpStatus[m.status]
        if pl.value(m.objective) is None:
            print("Cost function cannot be evaluated, probably None")
        else:
            print(
                f"Total value of the Cost function = {round(pl.value(m.objective), 2)}"
            )

        for i, consumer in enumerate(self.consumers):
            consumer.energy_deficit_k = np.array(
                [consumer.energy_deficit_k[k].varValue for k in range(config.horizon)],
                dtype=float,
            )
            consumer.power_actual_k = np.array(
                [consumer.power_actual_k[k].varValue for k in range(config.horizon)],
                dtype=float,
            )

        for i, storage in enumerate(self.storages):
            storage.energy_k = np.array(
                [storage.energy_k[k].varValue for k in range(config.horizon)],
                dtype=float,
            )
            storage.power_charging_k = np.array(
                [storage.power_charging_k[k].varValue for k in range(config.horizon)],
                dtype=float,
            )
            storage.power_discharging_k = np.array(
                [
                    storage.power_discharging_k[k].varValue
                    for k in range(config.horizon)
                ],
                dtype=float,
            )

        for i, producer in enumerate(self.producers):
            producer.power_curtailment_factor_k = np.array(
                [
                    producer.power_curtailment_factor_k[k].varValue
                    for k in range(config.horizon)
                ],
                dtype=float,
            )

        for i, heatnode in enumerate(self.heatnodes):
            for j, heatproducer in enumerate(heatnode.heatproducers):
                heatproducer.starting_k = np.array(
                    [
                        heatproducer.starting_k[k].varValue
                        for k in range(config.horizon)
                    ],
                    dtype=int,
                )
                heatproducer.running_k = np.array(
                    [heatproducer.running_k[k].varValue for k in range(config.horizon)],
                    dtype=int,
                )
                heatproducer.power_k = np.array(
                    [heatproducer.power_k[k].varValue for k in range(config.horizon)],
                    dtype=float,
                )

            for j, heatstorage in enumerate(heatnode.heatstorages):
                heatstorage.temperature_k = np.array(
                    [
                        heatstorage.temperature_k[k].varValue
                        for k in range(config.horizon)
                    ],
                    dtype=float,
                )
                heatstorage.energy_in_k = np.array(
                    [
                        heatstorage.energy_in_k[k].varValue
                        for k in range(config.horizon)
                    ],
                    dtype=float,
                )
                heatstorage.energy_out_k = np.array(
                    [
                        heatstorage.energy_out_k[k].varValue
                        for k in range(config.horizon)
                    ],
                    dtype=float,
                )

        self.grid.power_import_k = np.array(
            [self.grid.power_import_k[k].varValue for k in range(config.horizon)],
            dtype=float,
        )
        self.grid.power_export_k = np.array(
            [self.grid.power_export_k[k].varValue for k in range(config.horizon)],
            dtype=float,
        )

        self.loss = pl.value(m.objective)
        self.include_results = True
