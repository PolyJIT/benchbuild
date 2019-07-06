# Dictionary-like configuration objects.

We provide a simple reusable configuration mechanism for benchbuild that supports
default values, override through environment variables, and configuration files.

## The class `Configuration`

At the heart of benchbuild's configuration system you can find the class 'Configuration'.

### Basic Usage

You can store settings for your project inside the class `Configuration`.
Upon construction you need to provide a namespace to house all configuration variables
in, such as "BB" for BenchBuild.

```python
CFG = Configuration("bb")
```


You can extend the configuration by inner nodes and leaf nodes, forming a tree-like data structure.
Inner nodes are simple dictionaries and can span arbitrary nesting structures.
Leaf nodes are dictionaries that contain the following keys:
    - default: Stores the default value for the configuration option.
    - desc: A description for this configuration option.
The current value a leaf node holds will be stored in the 'value' key of a leaf node.

```python
CFG['my_config'] = {
    'option_1' : {
        'default': True,
        'desc': 'Toggle option 1'
    },
    'option_2' : {
        'default': True,
        'desc': 'Toggle option 2'
    },
}
```

You can access the current values inside your application code using the `value()` method
on a leaf node, after the configuration is set for the first time.
This will return the stored value in its current representation/type.
You can access the string representation using an explicit conversion by applying the `str` method on a leaf node.
The initial value can either be set manually with an assignment to the leaf node (see example below), or with default initialization through `setup_config` and `update_env`.

```python
> CFG['my_config']['option_1'] = True
> type(CFG['my_config']['option_1'].value())
bool
> CFG['my_config']['option_1'].value()
True
> str(CFG['my_config']['option_1'])
'True'
```

### Automatic Generation of Environment Variables.

The configuration is able to provide a neat serialized representation that can be used in shell scripts.
Any configuration node can be represented as a document of environment variables.

```python
> CFG['my_config']['option_2'] = False
> CFG['my_config']['option_1']
BB_MY_CONFIG_OPTION_1=true
> CFG['my_config']
BB_MY_CONFIG_OPTION_1=true
BB_MY_CONFIG_OPTION_2=false
```

The environment variable names can be used to control the setting of a configuration 
option via the environment of benchbuild.
The values stored in the environment variable are YAML representations of the objects stored in the `value` property of the leaf node.

### Automatic Initialization

The configuration can be initialized using the functions `setup_config` and `update_env`.
Both are meant to be called from the user code during program setup/module load of the user-specific configuration.

```python
import benchbuild.utils.settings as s
CFG = s.Configuration('bb')
CFG['my_config'] = {
    'option_1' : {
        'default': True,
        'desc': 'Toggle option 1'
    }
}
s.setup_config(CFG)
s.update_env(CFG)
```

#### Setup Config

The function `setup_config` triggers configuration initialization from default values and
config file. It follows the ruleset:
    1. Check for a filepath in environment variable: `BB_CONFIG_FILE`, or
    2. Recursively lookup the default config file, starting from the current working 
       directory upwards to the root of the filesystem.
    3. Load configuration from file, if found in (1) or (2), and
    4. Initialize all configuration options from the environment.

#### Update Environment

The function `update_env` is benchbuild-specific and updates the environment of the 
running process. We update the variables:
    - `PATH` from `*_ENV_PATH`
    - `LD_LIBRARY_PATH` from `*_ENV_LD_LIBRARY_PATH`
This updates the plumbum local-machine environment as well and enables program lookup in user-defined paths.

## API reference

```eval_rst
.. automodule:: benchbuild.settings
    :members:
    :undoc-members:
    :show-inheritance:
```
