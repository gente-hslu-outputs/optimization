from datetime import datetime, timedelta
import os
from pathlib import Path

import numpy as np
import pandas as pd
from enduseroptimizer import (
    Consumer,
    EndUser,
    Grid,
    HeatConsumer,
    HeatNode,
    HeatProducer,
    HeatStorage,
    Producer,
    Storage,
    config,
)


def example_enduser() -> EndUser:
    config.horizon = int(24 * 60 / 15)  # number of discrete steps

    mdl = EndUser()
    mdl.start_time = datetime(year=2021, month=6, day=1)

    grid = Grid()
    grid.import_tariff_k = 50 * (
        np.sin(np.pi + np.linspace(-np.pi, 2 * np.pi, config.horizon)) + 2
    )
    grid.export_tariff_k = 60 * np.ones(config.horizon)
    grid.loss_f = "minimize_cost"
    grid.power_import_max_k = 500 * np.ones(config.horizon)
    grid.power_export_max_k = 100 * np.ones(config.horizon)
    grid.discharge_to_grid = True
    mdl.grid = grid

    producer1 = Producer()
    producer1.power_curtailment_factor_max = 0.2
    fake_pv = np.sin(np.linspace(-np.pi / 2, 3 / 2 * np.pi, config.horizon))
    producer1.power_actual_k = 200 * np.where(fake_pv > 0, fake_pv, 0)
    mdl.producers.append(producer1)

    consumer1 = Consumer()
    consumer1.power_desired_k = 50 + np.random.rand(config.horizon) * 10
    consumer1.energy_deficit_max_k = 20 * np.ones(config.horizon)
    consumer1.power_min = 0.0
    consumer1.power_max = 100
    mdl.consumers.append(consumer1)

    storage1 = Storage()
    for k in range(20, 60):
        storage1.available_k[k] = 0
    storage1.state_of_charge_initial_k = 0.20 * np.ones(config.horizon)
    storage1.state_of_charge_final_k = 0.20 * np.ones(config.horizon)
    mdl.storages.append(storage1)

    storage2 = Storage()
    # for k in range(10,30):
    #     storage2.available_k[k] = 0
    storage2.energy_capacity = 100
    storage2.state_of_charge_initial_k = 0.80 * np.ones(config.horizon)
    storage2.state_of_charge_final_k = 0.80 * np.ones(config.horizon)
    mdl.storages.append(storage2)

    heatnode1 = HeatNode()

    heatproducer1 = HeatProducer()
    heatnode1.heatproducers.append(heatproducer1)

    heatproducer2 = HeatProducer()
    heatproducer2.efficiency = 3.5
    heatproducer2.power_max = 1.5
    heatproducer2.minimum_power_factor = 0.2
    heatproducer2.power_loss_startup = 1
    heatnode1.heatproducers.append(heatproducer2)

    heatstorage1 = HeatStorage()
    heatnode1.heatstorages.append(heatstorage1)

    heatconsumer1 = HeatConsumer()
    heatconsumer1.power_actual_k = 3 * (
        np.sin(np.linspace(-np.pi, 2 * np.pi, config.horizon)) + 2
    )
    heatnode1.heatconsumers.append(heatconsumer1)
    mdl.heatnodes.append(heatnode1)

    mdl.optimize()
    return mdl


if __name__ == "__main__":
    mdl = example_enduser()
    if config.plotting:
        from enduseroptimizer import plot_enduser

        plot_enduser(mdl)

    dummy_time_arr = pd.date_range(start="1/1/2022", periods=96, freq="15min")

    import json

    endusers = []
    endusers.append(mdl)
    out_dict = {}
    out_dict["endusers"] = {}
    for i, enduser in enumerate(endusers):
        out_dict["endusers"][i] = enduser.to_dict()

    os.makedirs(config.default_result_path, exist_ok=True)
    with open(config.default_result_path / "opt.json", "w") as out_file:
        json.dump(out_dict, out_file, indent=4)
