from enduseroptimizer.config import Config

config = Config()

# config instanciated first, so that it can be used in other modules
from enduseroptimizer.consumer import Consumer
from enduseroptimizer.grid import Grid
from enduseroptimizer.heatconsumer import HeatConsumer
from enduseroptimizer.heatproducer import HeatProducer
from enduseroptimizer.heatstorage import HeatStorage
from enduseroptimizer.heatnode import HeatNode
from enduseroptimizer.producer import Producer
from enduseroptimizer.storage import Storage
from enduseroptimizer.enduser import EndUser

# for plotting only
try:
    import plotly
    import streamlit
    from enduseroptimizer.streamlit_display import plot_enduser

    config.plotting = True
except ImportError:
    pass
