# Migration Guide: ABSESpy 0.7.x to 0.8.x

## Overview

ABSESpy 0.8.0 introduces several improvements while maintaining backward compatibility with 0.7.x projects. This guide explains the changes and how your existing projects will continue to work.

## Key Changes

### 1. Automatic Raster Application (Fixed in 0.8.x)

**What changed:**
- In 0.7.x, when creating a module with `raster_file` and `attr_name`, the raster data was automatically applied to cells as the specified attribute
- Early 0.8.x versions required explicit `apply_raster=True` parameter

**Fixed:**
✅ This backward compatibility issue has been fixed! Your existing code will now work without any changes.

**Example:**
```python
# This works in both 0.7.x and 0.8.x (after fix)
self.dem = self.create_module(
    raster_file=self.ds.dem,
    cell_cls=CompetingCell,
    attr_name="elevation",  # Automatically applies raster as 'elevation' attribute
    major_layer=True,
)

# You can still explicitly control the behavior if needed
self.dem = self.create_module(
    raster_file=self.ds.dem,
    cell_cls=CompetingCell,
    attr_name="elevation",
    apply_raster=False,  # Explicitly disable auto-application
    major_layer=True,
)
```

**Technical details:**
When you provide `attr_name` parameter along with `raster_file`, `vector_file`, or `xda` parameters, the framework now automatically sets `apply_raster=True` to maintain backward compatibility with 0.7.x behavior.

### 2. Configuration Struct Mode Handling

**What changed:**
- In 0.7.x, configurations were more flexible about accepting new keys dynamically
- In 0.8.x, we've improved the configuration system while maintaining this flexibility

**Good news:**
✅ Your existing projects will continue to work without any changes! We've implemented automatic struct mode handling to ensure backward compatibility.

**Technical details:**
The framework now automatically disables OmegaConf's struct mode when merging configurations, allowing dynamic key addition just like in 0.7.x.

### 3. Configuration Interpolation Syntax

**What changed:**
- The default configuration now uses safer interpolation syntax
- Changed from `${exp.name:ABSESpy}` to `${oc.select:exp.name,ABSESpy}`

**Why this matters:**
The new syntax handles missing configuration keys more gracefully, preventing errors when migrating projects from older versions.

**Good news:**
✅ Your existing project configurations don't need to be updated! The framework handles both old and new syntax.

## Backward Compatibility Features

### Extra Parameters in Model Initialization

Your existing code that passes extra parameters to the model will continue to work:

```python
# This works in both 0.7.x and 0.8.x
model = MainModel(
    parameters=config,
    nature_cls=CustomNature,  # Extra parameter
    human_cls=CustomHuman,    # Extra parameter
    custom_param="value"      # Extra parameter
)
```

### Missing Configuration Sections

Projects that don't have an `exp` section in their configuration will work correctly:

```yaml
# Old config without 'exp' section - still works!
model:
  name: MyModel
time:
  end: 100
```

The framework will use default values automatically.

### Partial Configuration Sections

If your configuration has only some of the expected fields, the framework will fill in the defaults:

```yaml
# Config with only 'exp.name' - still works!
exp:
  name: MyProject
  # outdir is missing - framework uses default 'out'
```

## Testing Your Migration

To verify your project works with 0.8.x:

1. **Update ABSESpy:**
   ```bash
   pip install --upgrade abses
   # or
   uv pip install --upgrade abses
   ```

2. **Run your existing code:**
   Your project should work without any changes. If you encounter issues, please report them.

3. **Check for warnings:**
   While your code will work, you might see deprecation warnings for certain patterns (e.g., using lowercase actor parameter keys). These are informational and won't break your code.

## New Features You Can Adopt (Optional)

While not required, you can adopt these new patterns in 0.8.x:

### 1. Use PascalCase for Actor Parameters

**0.7.x style (still works):**
```yaml
farmer:
  initial_capital: 1000
```

**0.8.x style (recommended):**
```yaml
Farmer:
  initial_capital: 1000
```

### 2. Use Safer Configuration Interpolation

**Old style (still works):**
```yaml
output_dir: ${exp.outdir:out}
```

**New style (recommended):**
```yaml
output_dir: ${oc.select:exp.outdir,out}
```

## Troubleshooting

### Issue: "Key 'X' is not in struct"

**Solution:**
This should be automatically fixed in 0.8.x. If you still encounter this error:
1. Make sure you're using ABSESpy 0.8.0 or later
2. Check that you haven't manually enabled struct mode in your code
3. Report the issue if it persists

### Issue: "Unsupported interpolation type"

**Solution:**
This should be automatically fixed in 0.8.x with the improved default configuration. If you still encounter this:
1. Check your configuration file for custom interpolations
2. Consider using the `oc.select` syntax for safer interpolations
3. Report the issue if it persists

### Issue: "Could not interpret value `tick` for `x`" when plotting experiment data

**Problem:**
When trying to plot dynamic/time series data from experiments, you get an error like:
```python
ValueError: Could not interpret value `tick` for `x`. An entry with this name does not appear in `data`.
```

**Cause:**
By default, `Experiment.batch_run()` only saves **final state data** (from `final_reporters`), not the time series data collected at each step (from `model_reporters`).

**Solution:**
Use a **hook function** to save time series data after each run:

```python
import logging
from pathlib import Path
from abses import MainModel
from abses.core.experiment import Experiment

# 获取 ABSESpy 的 logger
logger = logging.getLogger("abses")

def save_model_data_hook(model, job_id=None, repeat_id=None):
    """Hook to save time series data after each model run."""
    logger.info(f"Saving model data (job_id={job_id}, repeat_id={repeat_id})")

    # Get time series data from model reporters
    model_data = model.datacollector.get_model_vars_dataframe()

    if not model_data.empty:
        # Add metadata columns
        model_data.insert(0, "tick", range(len(model_data)))
        model_data.insert(0, "repeat_id", repeat_id)
        model_data.insert(0, "job_id", job_id)

        # Save to CSV
        filename = model.outpath / f"model_data_job{job_id}_repeat{repeat_id}.csv"
        model_data.to_csv(filename, index=False)
        logger.info(f"Data saved to: {filename}")

# Use the hook in your experiment
exp = Experiment(MyModel, cfg=cfg)
exp.add_hooks(save_model_data_hook)
exp.batch_run(repeats=10)

# Load and plot the data
import pandas as pd
import seaborn as sns

# Load all CSV files
csv_files = list(exp.outpath.glob("model_data_*.csv"))
all_data = pd.concat([pd.read_csv(f) for f in csv_files])

# Now you can plot
sns.lineplot(data=all_data, x="tick", y="population", hue="job_id")
```

**Important notes:**
- Make sure you define `model_reporters` in your configuration to collect time series data:

```yaml
reports:
  model:
    population: "num_agents"  # Collect at each step
    wealth: "total_wealth"
  final:
    final_population: "num_agents"  # Collect only at end
```

- The `exp.summary()` method only returns final state data
- For time series plots, you need to save and load the data using hooks
- See [Logging Guide](../wiki/logging-guide.md) for details on using logger in hooks

## Getting Help

If you encounter any migration issues:

1. Check the [GitHub Issues](https://github.com/ABSESpy/ABSESpy/issues)
2. Ask questions in our [Discussions](https://github.com/ABSESpy/ABSESpy/discussions)
3. Read the [full documentation](https://absespy.github.io/ABSESpy/)

## Summary

✅ **No changes required** - Your 0.7.x projects should work with 0.8.x out of the box

✅ **Backward compatible** - We've implemented automatic handling of common migration issues

✅ **Optional improvements** - You can adopt new patterns gradually at your own pace

The ABSESpy team is committed to maintaining backward compatibility and making upgrades smooth. Thank you for using ABSESpy!

