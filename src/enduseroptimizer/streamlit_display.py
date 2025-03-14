import pandas as pd
import plotly.graph_objs as go
import streamlit as st

from enduseroptimizer import config, EndUser


# TODO: do recursively
def plot_enduser(mdl: EndUser) -> None:
    st.set_page_config(
        page_title="AISOP end-user model",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    time_arr = pd.date_range(
        start=mdl.start_time, periods=config.horizon, freq="{}H".format(config.delta_t)
    )

    data = mdl.to_dict()

    for asset_dict in data.keys():
        if str(asset_dict).endswith("_d"):
            for asset_inst in data[asset_dict].keys():
                with st.expander(
                    "{}".format(str(asset_dict).replace("s_d", "_" + str(asset_inst)))
                ):
                    fig = go.Figure()
                    for asset_value in data[asset_dict][asset_inst].keys():
                        if str(asset_value).endswith("_k"):
                            fig.add_trace(
                                go.Scatter(
                                    x=time_arr,
                                    y=data[asset_dict][asset_inst][asset_value],
                                    name=asset_value,
                                )
                            )
                    st.plotly_chart(fig, use_container_width=True)
        elif str(asset_dict).endswith("_dd"):
            for asset_subdict in data[asset_dict].keys():
                for asset_subdict_inst in data[asset_dict][asset_subdict].keys():
                    for asset_inst in data[asset_dict][asset_subdict][
                        asset_subdict_inst
                    ].keys():
                        with st.expander(
                            "{} {}".format(
                                str(asset_dict).replace(
                                    "s_dd", "_" + str(asset_subdict)
                                ),
                                str(asset_subdict_inst).replace(
                                    "s_d", "_" + str(asset_inst)
                                ),
                            )
                        ):
                            fig = go.Figure()
                            for asset_value in data[asset_dict][asset_subdict][
                                asset_subdict_inst
                            ][asset_inst].keys():
                                if str(asset_value).endswith("_k"):
                                    fig.add_trace(
                                        go.Scatter(
                                            x=time_arr,
                                            y=data[asset_dict][asset_subdict][
                                                asset_subdict_inst
                                            ][asset_inst][asset_value],
                                            name=asset_value,
                                        )
                                    )
                            st.plotly_chart(fig, use_container_width=True)
