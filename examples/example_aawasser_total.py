from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
from databaseaccessor import DfReader, DfWriter
from enduseroptimizer import (
    Consumer,
    EndUser,
    Grid,
    HeatNode,
    HeatProducer,
    HeatStorage,
    Producer,
    Storage,
    config,
    plot_enduser,
)
import pandas as pd

import logging

if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    def get_array(sorted_time_list, measurement_name, field_columns, delta_t=15/60):
        ret = reader.read(
            int(datetime.timestamp(sorted_time_list[0])),
            int(datetime.timestamp(sorted_time_list[-1]) + delta_t * 60 * 60 / 2), # add half a step to the end time to get the last value
            measurement_name,
            field_columns,
        )[field_columns[0]]
        if len(ret) != len(sorted_time_list):
            print(
                f"Warning: Different data points available for {measurement_name} {field_columns}, interpolating."
            )
            ret = ret.reindex(pd.DatetimeIndex(sorted_time_list)).interpolate(
                method="linear"
            )
        return ret.values

    config_path = ((Path(__file__).parent / "../../config/config.ini").resolve(),)
    reader = DfReader(
        "hist",
        config_path=config_path,
    )

    writer = DfWriter(bucket="opt", config_path=config_path, debug_msg=True)
    writer.delete(bucket="opt", measurement="power_kW")
    writer.delete(bucket="opt", measurement="energy_kWh")

    horizon = int(1 * 24 * 60 / 15)  # number of discrete steps
    delta_t = 15 / 60  # length of steps [h]
    config.horizon = horizon  # number of discrete steps
    config.delta_t = delta_t  # length of steps [h]
    config.plotting = False  # plotting of results

    start_times = [
        datetime(year=2023, month=1, day=1, tzinfo=timezone.utc) + timedelta(days=i)
        for i in range(300)
    ]
    comp_start = datetime.now()
    for i, start_time in enumerate(start_times):
        print(f"Step {i+1} of {len(start_times)}")
        print(f"Start time: {start_time}")
        stop_time = start_time + timedelta(hours=horizon * delta_t)

        mdl = EndUser()
        mdl.start_time = start_time
        ts_list = [pd.Timestamp(i) for i in mdl.get_timestamps()]

        grid = Grid()
        grid.import_tariff_k = 0.5 * np.ones(horizon)
        grid.export_tariff_k = 0.2 * np.ones(horizon)
        grid.loss_f = "minimize_cost"
        grid.power_import_max_k = 200 * np.ones(horizon)
        grid.power_export_max_k = 200 * np.ones(horizon)
        grid.discharge_to_grid = False
        mdl.grid = grid

        pv_anlage = Producer()
        pv_anlage.power_curtailment_factor_max = 0.0
        pv_anlage.power_actual_k = get_array(ts_list, "power_kW", ["PV"], delta_t)
        mdl.producers.append(pv_anlage)

        hydro_anlage = Producer()
        hydro_anlage.power_curtailment_factor_max = 0.0
        hydro_anlage.power_actual_k = get_array(ts_list, "power_kW", ["Hydro"], delta_t)
        mdl.producers.append(hydro_anlage)

        batterie1 = Storage()
        batterie1.power_charge_max = 25
        batterie1.power_discharge_max = 25
        batterie1.energy_capacity = 65
        batterie1.state_of_charge_max = 1
        batterie1.state_of_charge_min = 0
        mdl.storages.append(batterie1)

        batterie2 = Storage()
        batterie2.power_charge_max = 25
        batterie2.power_discharge_max = 25
        batterie2.energy_capacity = 65
        batterie2.state_of_charge_max = 1
        batterie2.state_of_charge_min = 0
        mdl.storages.append(batterie2)

        batterie3 = Storage()
        batterie3.power_charge_max = 25
        batterie3.power_discharge_max = 25
        batterie3.energy_capacity = 65
        batterie3.state_of_charge_max = 1
        batterie3.state_of_charge_min = 0
        mdl.storages.append(batterie3)

        # heatnode1 = HeatNode()
        # heatproducer1 = HeatProducer()
        # heatproducer2 = HeatProducer()
        # heatstorage1 = HeatStorage()
        # heatstorage1.volume = 10.5 * 1e3
        # heatstorage1.flow_max = 1e3 * 3600
        # heatnode1.heatproducers.append(heatproducer1)
        # heatnode1.heatproducers.append(heatproducer2)
        # heatnode1.heatstorages.append(heatstorage1)
        # # TODO add consumers
        # mdl.heatnodes.append(heatnode1)

        house34 = Consumer()
        house34.energy_deficit_k = 0 * np.ones(horizon)
        house34.power_min = 0.0
        house34.power_max = 100
        house34.power_desired_k = get_array(ts_list, "power_kW", ["House_34"], delta_t)
        mdl.consumers.append(house34)

        house36 = Consumer()
        house36.energy_deficit_k = 0 * np.ones(horizon)
        house36.power_min = 0.0
        house36.power_max = 100
        house36.power_desired_k = get_array(ts_list, "power_kW", ["House_36"], delta_t)
        mdl.consumers.append(house36)

        house38 = Consumer()
        house38.energy_deficit_k = 0 * np.ones(horizon)
        house38.power_min = 0.0
        house38.power_max = 100
        house38.power_desired_k = get_array(ts_list, "power_kW", ["House_38"], delta_t)
        mdl.consumers.append(house38)

        ladestation = Consumer()
        ladestation.energy_deficit_k = 0 * np.ones(horizon)
        ladestation.power_min = 0.0
        ladestation.power_max = 100
        ladestation.power_desired_k = get_array(
            ts_list, "power_kW", ["Ladestation_Total"], delta_t
        )
        mdl.consumers.append(ladestation)

        mdl.optimize()

        power = {
            "Grid": mdl.grid.power_import_k - mdl.grid.power_export_k,
            "PV": pv_anlage.power_actual_k * (1 - pv_anlage.power_curtailment_factor_k),
            "Hydro": hydro_anlage.power_actual_k
            * (1 - hydro_anlage.power_curtailment_factor_k),
            "Batterie_1": batterie1.power_charging_k - batterie1.power_discharging_k,
            "Batterie_2": batterie2.power_charging_k - batterie2.power_discharging_k,
            "Batterie_3": batterie3.power_charging_k - batterie3.power_discharging_k,
            "House_34": house34.power_actual_k,
            "House_36": house36.power_actual_k,
            "House_38": house38.power_actual_k,
            "Ladestation_Total": ladestation.power_actual_k,
        }
        df = pd.DataFrame(power, index=ts_list)
        writer.write(df, "power_kW")

        energy = {
            "Batterie1_level": batterie1.energy_k * batterie1.energy_capacity,
            "Batterie2_level": batterie2.energy_k * batterie2.energy_capacity,
            "Batterie3_level": batterie3.energy_k * batterie3.energy_capacity,
            "House34_deficit": house34.energy_deficit_k,
            "House36_deficit": house36.energy_deficit_k,
            "House38_deficit": house38.energy_deficit_k,
            "Ladestation_deficit": ladestation.energy_deficit_k,
        }
        df = pd.DataFrame(energy, index=ts_list)
        writer.write(df, "energy_kWh")
    comp_end = datetime.now()
    print(f"Computation took {comp_end - comp_start}")
    print("Data written to database")
