from enduseroptimizer import HeatConsumer, HeatProducer, HeatStorage


class HeatNode:
    def __init__(self, name: str = "HeatNode") -> None:
        """Class defining a heat node, containing heat producers, heat storages and
            heat consumers, that are can exchange heat with each other

        Editable attributes:
            name (str): Name of the instanciated object, for logging
            heatproducers (list[HeatProducer]): list of heat producers
            heatstorages (list[HeatStorage]): list of heat storages
            heatconsumers (list[HeatConsumer]): list of heat consumers
        """
        self.name: str = name

        self.heatproducers: list[HeatProducer] = []
        self.heatstorages: list[HeatStorage] = []
        self.heatconsumers: list[HeatConsumer] = []

    def to_dict(self, include_results: bool = False) -> dict:
        data = {}
        data["heatproducers_d"] = {}
        for i, heatproducer in enumerate(self.heatproducers):
            data["heatproducers_d"][i] = heatproducer.to_dict(include_results)

        data["heatstorages_d"] = {}
        for i, heatstorage in enumerate(self.heatstorages):
            data["heatstorages_d"][i] = heatstorage.to_dict(include_results)

        data["heatconsumers_d"] = {}
        for i, heatconsumer in enumerate(self.heatconsumers):
            data["heatconsumers_d"][i] = heatconsumer.to_dict(include_results)

        return data

    def from_dict(self, data: dict, include_results: bool) -> None:
        for key in data["heatproducers_d"].keys():
            inst = HeatProducer()
            inst.from_dict(data["heatproducers_d"][key], include_results)
            self.heatproducers.append(inst)

        for key in data["heatstorages_d"].keys():
            inst = HeatStorage()
            inst.from_dict(data["heatstorages_d"][key], include_results)
            self.heatstorages.append(inst)

        for key in data["heatconsumers_d"].keys():
            inst = HeatConsumer()
            inst.from_dict(data["heatconsumers_d"][key], include_results)
            self.heatconsumers.append(inst)
