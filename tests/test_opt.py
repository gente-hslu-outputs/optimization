import numpy as np
import pytest

from enduseroptimizer import config


def test_unsolvable(example_enduser):
    example_enduser.grid.power_import_max_k = 1.0 * np.ones(config.horizon)
    example_enduser.optimize()
    assert example_enduser.status != "Optimal"


def test_unflexible(example_enduser):
    example_enduser.flexibility = False
    example_enduser.optimize()
    assert example_enduser.status == "Optimal"
    for consumer in example_enduser.consumers:
        assert np.all(consumer.energy_deficit_k == 0)
    for storage in example_enduser.storages:
        assert np.all(storage.power_charging_k == 0)
        assert np.all(storage.power_discharging_k == 0)
    for heatnode in example_enduser.heatnodes:
        for heatstorage in heatnode.heatstorages:
            assert np.allclose(
                (
                    heatstorage.energy_in_k
                    - heatstorage.energy_out_k
                    - (heatstorage.loss_factor * heatstorage.temperature_k)
                ),
                np.zeros(config.horizon),
                atol=1e-6,
            )


def test_flex_relax(example_enduser):
    example_enduser.optimize()
    assert example_enduser.status == "Optimal"
    flex_loss = example_enduser.loss

    example_enduser.flexibility = False
    example_enduser.optimize()
    assert example_enduser.status == "Optimal"
    unflex_loss = example_enduser.loss

    assert unflex_loss > flex_loss


def test_mutualimportexport(example_enduser):
    example_enduser.grid.import_tariff_k = np.zeros(config.horizon)
    example_enduser.grid.export_tariff_k = 100 * np.ones(config.horizon)
    example_enduser.optimize()
    assert example_enduser.status == "Optimal"
    assert (
        example_enduser.grid.power_import_k @ example_enduser.grid.power_export_k
    ) == 0

@pytest.mark.parametrize("loss", ["minimize_cost", "minimize_grid_supply"])
@pytest.mark.parametrize("factor", [0.01, 0.1, 1, 10, 100, 1000])
@pytest.mark.parametrize(
    "import_tariff, export_tariff",
    [
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
    ],
)
def test_constant_pricing(example_enduser, import_tariff, export_tariff, factor, loss):
    example_enduser.grid.import_tariff_k = (
        factor * import_tariff * np.ones(config.horizon)
    )
    example_enduser.grid.export_tariff_k = (
        factor * export_tariff * np.ones(config.horizon)
    )
    example_enduser.grid.loss_f = loss
    example_enduser.optimize()
    assert example_enduser.status == "Optimal"
