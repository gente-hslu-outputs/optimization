# HSLU End-User Energy Optimization Tool

### Local Installation
Requires that you download the gitlab.

```cmd
pip install <path_to_root_of_this_folder>
```

in the desired environment.
For example, `cd` to into the `EndUserOptimizer` Folder and do `pip install .`

### Installation with Package Registry
Requires that you have a `.pypirc` File setup, and that you know:
- `username` (is `__token__` in the command)
- `password` (is `<your_personal_token>` in the command below)

```cmd
pip install enduseroptimzer --index-url https://__token__:<your_personal_token>@gitlab.com/api/v4/projects/45647566/packages/pypi/simple
```


## Usage

```python
# TODO: Daniel
```

>[TOC]
## Purpose
Provide a simple base for energy simulations of end-users, especially in the context of Local Energy Communities, Electrical Vehicle Fleets and Distribution Systems.

## EndUser Definition
The end-user model is based on a time horizon divided in discrete steps, during which the produced/consumed powers are assumed to be constant.

The electrical system is based on the following assets:
* `Grid`: defines electricity import/export prices and capacities (per timestep). May only allow export of instant production to grid (no shifting using storage). The model optimizes imported/exported power; 
* `Producer`: defined by a specific power output per timestamp, may have curtailment capabilities. The model optimizes curtailment;
* `Storage`: modelled by charging/discharging efficiency, maximal charge/discharge power, capacity, min/max state of charge, availability at different timestamps, as well as expected state of charge when connected/disconnected. The model optimizes charging/discharging power (while managing the state of charge);
* `Consumer`: defined by maximal power, availaility, desired power and allowed energy deficit. The model optimizes the delivered power;
* `HeatNode`: wrapper for the classes detailed below.

As the heating system can represent a big part of end-user consumption, it is also added. The system maps the end-user needs to the electrical power required to run them, while leveraging heat storage. A `HeatNode` is composed of the following (more details in technical doc):
* `HeatProducer`: defined by efficiency, maximal power, minimum running power and startup power. The model optimizes the startups/running time and delivered power;
* `HeatStorage`: defined by min/max temperatures, a linear loss factor, volume, density, specific heat, temperature at the input, initial/final temperature and maximal flow. The model optimizes the temperature and flow through the heat storage;
* `HeatConsumer`: defined by power consumption.

## File description
* `src/enduser.py` contains the the different classes used for the system definition and implements the different constraints so they can be interpreted by the PuLP optimizer invoked in the `.optimize()` method.
* `src/dataset.py` provides an abstraction layer to load the different datasets;
* `src/example_pydefine.py` calls the aforementioned files, building a mock model using data from `data/erlifeld2021.parquet`, and displays the model optimization results;
* `src/example_importexport.py` loads the `json` enduser model configuration file `data/enduser_import.py`, optimizes it and saves the results in another `json`.

## Use the optimization tool
### 1 - Preparing the environment
1. Get a Python 3.10 environment (3.11 doesn't work yet with setup.py)
2. Create a Python virtual environment in the root (`python -m venv ./.venv`)
4. Install the enduser pip package (`pip install -e ./endusermodel`)
5. (OPTIONAL) To be able to plot, install the extra package using `pip install -e ./endusermodel[plots]`

### Compatability Problems with Protobuf (Streamlit & Tensorflow)
(Re)-install Streamlit and tensorflow together with: `pip install -U streamlit tensorflow`

### 2 - Defining the EndUser(s)
There are multiple ways to define EndUsers (class defined in `enduser.py`):

1. In Python: instanciate the different classes hierarchically, starting from the EndUser class. Directly modify the instance assets to define the different parameters, as shown in `example_pydefine.py`;
2. Using a configuration file: an example is available in `enduser_import.json`, and used in `example_importexport.py`.

### 3 - Optimizing the EndUser(s)
Each EndUser can be optimized by passing an `EndUser` instance to `optimize_enduser` in `guropbi_optimizer.py`. The results are directly saved in the instance.


# Start the Optimizer from CLI
1. Go into Optimizer Folder 
2. run `streamlit run .\endusermodel\examples\example_pydefine.py` from CMD
3. ???
4. Profit


## Functionality description
