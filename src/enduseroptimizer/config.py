from pathlib import Path


class Config:
    def __init__(self) -> None:
        self._horizon = int(24 * 60 / 15)  # number of discrete steps
        self._delta_t = 15 / 60  # length of steps [h]
        self._plotting = False  # plotting of results
        self._default_result_path = Path("results")  # default path for results

    @property
    def horizon(self):
        return self._horizon

    @horizon.setter
    def horizon(self, horizon):
        self._horizon = horizon

    @property
    def delta_t(self):
        return self._delta_t

    @delta_t.setter
    def delta_t(self, delta_t):
        self._delta_t = delta_t

    @property
    def plotting(self):
        return self._plotting

    @plotting.setter
    def plotting(self, plotting):
        self._plotting = plotting

    @property
    def default_result_path(self):
        return self._default_result_path

    @default_result_path.setter
    def default_result_path(self, default_result_path):
        self._default_result_path = default_result_path
