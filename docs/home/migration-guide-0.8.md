# Migration Guide: ABSESpy 0.7.x to 0.8.x

## Overview

ABSESpy 0.8.0 introduces several improvements while maintaining backward compatibility with 0.7.x projects. This guide explains the changes and how your existing projects will continue to work.

## Key Changes

### 1. Configuration Struct Mode Handling

**What changed:**
- In 0.7.x, configurations were more flexible about accepting new keys dynamically
- In 0.8.x, we've improved the configuration system while maintaining this flexibility

**Good news:**
✅ Your existing projects will continue to work without any changes! We've implemented automatic struct mode handling to ensure backward compatibility.

**Technical details:**
The framework now automatically disables OmegaConf's struct mode when merging configurations, allowing dynamic key addition just like in 0.7.x.

### 2. Configuration Interpolation Syntax

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
   poetry add abses@latest
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

