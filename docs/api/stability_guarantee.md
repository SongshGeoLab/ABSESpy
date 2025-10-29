# ABSESpy API Stability Guarantee

## Overview

This document outlines ABSESpy's commitment to API stability and backward compatibility. It defines which APIs are guaranteed to remain stable across versions and provides guidelines for users and developers.

## Stability Levels

### 🔒 **Stable APIs** (Guaranteed Backward Compatibility)

These APIs are guaranteed to maintain backward compatibility across minor and patch releases:

#### Core Modeling Framework
- `MainModel` class and its core methods
- `Actor` class and its core methods
- `ActorsList` class and its core methods
- `BaseNature` class and its core methods
- `PatchCell` class and its core methods

#### Key Methods and Properties
- `model.agents` - Returns ActorsList
- `model.nature` - Returns BaseNature instance
- `model.datacollector` - Data collection interface
- `model.params` / `model.p` - Parameter access
- `model.time.tick` - Current time step
- `model.outpath` - Output path
- `model.run_id` - Run identifier

#### ActorsList Core Methods
- `select()` - Filter actors by criteria
- `array()` - Extract attributes as numpy arrays
- `shuffle_do()` - Execute methods on actors
- `random.new()` - Create new actors
- `has()` - Count actors
- `item()` - Get single actor
- `__getitem__()` - Index by breed or position

#### Spatial Operations
- `neighboring()` - Find neighboring cells
- `move.to()` - Move agent to cell
- `get_raster()` - Extract raster data
- `apply_raster()` - Apply raster data
- `create_module()` - Create spatial modules

#### Decorators
- `@alive_required` - Skip execution for dead agents
- `@raster_attribute` - Convert methods to raster properties
- `@with_axes` - Automatic matplotlib axes creation

#### Experiment Framework
- `Experiment` class and core methods
- `summary()` - Get experiment results
- `run()` - Execute experiment

### ⚠️ **Deprecated APIs** (Scheduled for Removal)

These APIs are still functional but will be removed in future major versions:

- None currently identified

### 🔄 **Experimental APIs** (May Change)

These APIs are under active development and may change:

- Advanced visualization components
- Performance optimization features
- New experimental modeling features

## Version Compatibility Policy

### Major Versions (X.0.0)
- May include breaking changes
- Deprecated APIs may be removed
- New major features may be introduced
- Migration guides will be provided

### Minor Versions (X.Y.0)
- **No breaking changes** to stable APIs
- New features may be added
- Performance improvements
- Bug fixes

### Patch Versions (X.Y.Z)
- **No breaking changes** to stable APIs
- Bug fixes only
- Security updates
- Documentation improvements

## Migration Strategy

### For Users
1. **Pin to minor versions** for production code: `abses>=0.8.0,<0.9.0`
2. **Test with new versions** in development before upgrading
3. **Follow migration guides** for major version upgrades
4. **Report compatibility issues** through GitHub issues

### For Developers
1. **Add deprecation warnings** before removing APIs
2. **Provide migration paths** for breaking changes
3. **Maintain compatibility tests** for stable APIs
4. **Document changes** in CHANGELOG.md

## Testing Strategy

### Contract Testing
- All stable APIs are covered by contract tests
- Tests verify method signatures, return types, and behavior
- Contract tests run on every PR to prevent breaking changes

### Regression Testing
- User scenarios are tested to ensure real-world compatibility
- Backward compatibility tests verify existing functionality
- Integration tests ensure components work together

### Performance Benchmarking
- Performance baselines are established for critical operations
- Performance regressions are detected and prevented
- Scalability is tested with large datasets

## API Documentation

### Method Signatures
All stable API methods maintain consistent signatures:

```python
# ActorsList methods
def select(self, filter_func=None, at_most=float('inf'), inplace=False, agent_type=None) -> ActorsList
def array(self, attr: str) -> np.ndarray
def shuffle_do(self, method_name: str) -> None

# Spatial methods
def neighboring(self, radius: int, moore: bool=True, include_center: bool=False) -> ActorsList
def move_to(self, cell: PatchCell) -> None
def get_raster(self, attr_name: str) -> np.ndarray
```

### Return Types
- `ActorsList` methods return `ActorsList` instances
- `array()` always returns `np.ndarray`
- `neighboring()` always returns `ActorsList`
- Spatial methods maintain consistent return types

### Error Handling
- Stable APIs maintain consistent error handling
- Error messages remain descriptive and helpful
- Exception types are preserved across versions

## Breaking Change Process

### Definition
A breaking change is any modification that:
- Changes method signatures
- Changes return types
- Changes behavior in a way that breaks existing code
- Removes public APIs

### Process
1. **Deprecation Period**: APIs are marked as deprecated for at least one minor version
2. **Warning Messages**: Clear deprecation warnings are shown
3. **Documentation**: Migration guides are provided
4. **Removal**: APIs are removed only in major versions

### Examples

#### ✅ Allowed Changes (Non-Breaking)
```python
# Adding optional parameters
def select(self, filter_func=None, new_param=None):  # OK

# Adding new methods
def new_method(self):  # OK

# Performance improvements
# Faster implementation of existing method  # OK
```

#### ❌ Prohibited Changes (Breaking)
```python
# Changing method signature
def select(self, new_required_param):  # BREAKING

# Changing return type
def array(self, attr): return list  # BREAKING (was np.ndarray)

# Removing methods
# def old_method(self):  # BREAKING
```

## User Guidelines

### Best Practices
1. **Use stable APIs** for production code
2. **Pin dependency versions** appropriately
3. **Test upgrades** in development environments
4. **Follow deprecation warnings** and migrate early
5. **Report issues** promptly

### Version Pinning Recommendations
```toml
# For production (stable)
abses = ">=0.8.0,<0.9.0"

# For development (latest stable)
abses = ">=0.8.0,<1.0.0"

# For experimentation (latest)
abses = ">=0.8.0"
```

### Migration Checklist
When upgrading versions:
- [ ] Review CHANGELOG.md for changes
- [ ] Run test suite to verify compatibility
- [ ] Check for deprecation warnings
- [ ] Update code if needed
- [ ] Verify functionality works as expected

## Support and Feedback

### Reporting Issues
- **GitHub Issues**: For bug reports and feature requests
- **Discussions**: For questions and community support
- **Email**: For security issues

### Getting Help
- **Documentation**: Comprehensive API documentation
- **Examples**: Working code examples
- **Tutorials**: Step-by-step guides
- **Community**: Active user community

## Changelog

### Version 0.8.0
- Initial API stability guarantee
- Established contract testing framework
- Implemented comprehensive test coverage

### Future Versions
- Continued stability for all stable APIs
- Regular performance improvements
- Enhanced documentation and examples

---

**Last Updated**: 2024-01-XX
**Next Review**: 2024-04-XX

This document is maintained by the ABSESpy development team and is updated with each release to reflect the current state of API stability guarantees.
