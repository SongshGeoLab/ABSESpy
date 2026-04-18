# Changelog

## [0.11.6](https://github.com/SongshGeoLab/ABSESpy/compare/v0.11.5...v0.11.6) (2026-04-18)


### Bug Fixes

* **agents:** :bug: Swap ActorsList base order to fix mesa 3.5 MRO error ([2c17215](https://github.com/SongshGeoLab/ABSESpy/commit/2c17215975f8cc68ebe2c5f5f2abf1e5b5015ee2))
* **compatibility:** :bug: Introduce mesa-geo compatibility handling and regression tests ([c92eefd](https://github.com/SongshGeoLab/ABSESpy/commit/c92eefd887df29ebf2e013df48758612fe6c92c7))

## [0.11.5](https://github.com/SongshGeoLab/ABSESpy/compare/v0.11.4...v0.11.5) (2026-01-17)


### Bug Fixes

* **tracker:** :bug: Rename 'distribution' to 'samples' in AimTracker for API compatibility ([a387f1e](https://github.com/SongshGeoLab/ABSESpy/commit/a387f1ee21bc6f748c617b386573889515861b11))

## [0.11.4](https://github.com/SongshGeoLab/ABSESpy/compare/v0.11.3...v0.11.4) (2026-01-07)


### Bug Fixes

* **analysis:** :bug: Improve data handling in ResultAnalyzer for missing CSV files ([e0b5d5f](https://github.com/SongshGeoLab/ABSESpy/commit/e0b5d5f2a5c8e8182cd26b1d2a7c6d6a3fce1f8d))
* **tracker:** :bug: Resolved the issue where configurations could only be recorded as strings. ([1745558](https://github.com/SongshGeoLab/ABSESpy/commit/1745558440abcb6ed043265a1fb099ab96121499))

## [0.11.3](https://github.com/SongshGeoLab/ABSESpy/compare/v0.11.2...v0.11.3) (2026-01-07)


### Bug Fixes

* **experiment:** :bug: Update repeat_id to run_id for consistency in experiment logging ([93cf775](https://github.com/SongshGeoLab/ABSESpy/commit/93cf7759906a23823a18a5a5cc274db61c6e43a0))

## [0.11.2](https://github.com/SongshGeoLab/ABSESpy/compare/v0.11.1...v0.11.2) (2026-01-07)


### Bug Fixes

* **logging:** :memo: Clarify logging configuration in absespy.yaml ([892f098](https://github.com/SongshGeoLab/ABSESpy/commit/892f098a7dfcfc2b215d4a7b6fed6cc5a40b65f0))

## [0.11.1](https://github.com/SongshGeoLab/ABSESpy/compare/v0.11.0...v0.11.1) (2026-01-06)


### Bug Fixes

* **analysis:** :bug: Improve error handling for uninitialized data in ResultAnalyzer ([ef99a6d](https://github.com/SongshGeoLab/ABSESpy/commit/ef99a6d8ca740b6497efcf6c4bb6153bd596288f))
* **logging:** :bug: Enhance logging setup for experiments and user modules ([63cf80d](https://github.com/SongshGeoLab/ABSESpy/commit/63cf80dcad54805809d7c040d24c9a59116046cd))
* **logging:** :bug: Update logging configuration to prevent empty log files and improve experiment log naming ([82e9e44](https://github.com/SongshGeoLab/ABSESpy/commit/82e9e44e3efb392a711f9cf7acc83b7a554ec433))

## [0.11.0](https://github.com/SongshGeoLab/ABSESpy/compare/v0.10.0...v0.11.0) (2026-01-06)


### Features

* **analysis:** :sparkles: Add analysis utilities and documentation for experiment results ([d6267d8](https://github.com/SongshGeoLab/ABSESpy/commit/d6267d87295291c64f724f9aeef7c636a353b6cd))


### Bug Fixes

* **project:** :construction_worker: Update pre-commit configuration and tox settings ([8e115f6](https://github.com/SongshGeoLab/ABSESpy/commit/8e115f642d80423ec47e298fdf4fc93fe71c48a2))

## [0.10.0](https://github.com/SongshGeoLab/ABSESpy/compare/v0.9.4...v0.10.0) (2026-01-01)


### Features

* **tracking:** :sparkles: Integrate Aim and MLflow tracking backends with configuration updates ([27a7606](https://github.com/SongshGeoLab/ABSESpy/commit/27a7606342dd7fe19926c85fde0b9376ff4c59d2))


### Bug Fixes

* **config:** :bug: Improve error handling in tracker configuration validation ([1bb75b0](https://github.com/SongshGeoLab/ABSESpy/commit/1bb75b0d7ed0583a2186280ffba5d4bffabcf101))
* **dependencies:** :bug: Update Aim version constraint and improve compatibility with Mesa 3.4.0 ([5b10768](https://github.com/SongshGeoLab/ABSESpy/commit/5b10768a56e632c9680c8592d2e4f65c5f6fa74b))
* **dependencies:** :bug: Update MLflow version constraint and improve configuration handling ([7259e53](https://github.com/SongshGeoLab/ABSESpy/commit/7259e53d250207a27673e82ffd81a8b63d8d93d4))

## [0.9.4](https://github.com/SongshGeoLab/ABSESpy/compare/v0.9.3...v0.9.4) (2025-12-12)


### Bug Fixes

* **dependencies:** :bug: update numpy version constraint in pyproject.toml and uv.lock ([157af45](https://github.com/SongshGeoLab/ABSESpy/commit/157af45f9ca3c6fbbb13b8ce6dff3ffd06d2e263))

## [0.9.3](https://github.com/SongshGeoLab/ABSESpy/compare/v0.9.2...v0.9.3) (2025-11-10)


### Bug Fixes

* **model:** :bug: Enhance steps calculation in MainModel class ([9d688e4](https://github.com/SongshGeoLab/ABSESpy/commit/9d688e4a9662823baaff4cb1a1f2d684d0588be0))

## [0.9.2](https://github.com/SongshGeoLab/ABSESpy/compare/v0.9.1...v0.9.2) (2025-11-09)


### Bug Fixes

* **core:** :bug: Update type annotations and docstrings for Experiment and TimeDriver classes ([cf1ffec](https://github.com/SongshGeoLab/ABSESpy/commit/cf1ffec6778d02eea8d1aeaa5b02f3361dd0823f))
* **model:** :bug: Improve type checking in MainModel class ([ae46993](https://github.com/SongshGeoLab/ABSESpy/commit/ae469938e70c5c2bccb21cf58a884cc21de3a3dd))
* **model:** :bug: Remove unnecessary time.go() call in MainModel class. ([b4cbbe6](https://github.com/SongshGeoLab/ABSESpy/commit/b4cbbe6868294edfe42938f322ef21ff4471e3cd))
* **nature:** :bug: Prevent duplicate layers from being added in BaseNature class ([0d85c4e](https://github.com/SongshGeoLab/ABSESpy/commit/0d85c4e7f9f6f1b4c0894ee541346f606068e98c))

## [0.9.1](https://github.com/SongshGeoLab/ABSESpy/compare/v0.9.0...v0.9.1) (2025-10-29)


### Bug Fixes

* **ci:** :wrench: update GitHub Actions workflows to install documentation dependencies ([c9b99fe](https://github.com/SongshGeoLab/ABSESpy/commit/c9b99fe96effdfc373d9c7a960ee32f47915b62e))
* **dependencies:** :bug: reorganize documentation dependencies in pyproject.toml so that mkdocs-jupyter is not required anymore ([6e1dd9e](https://github.com/SongshGeoLab/ABSESpy/commit/6e1dd9e813e40700ce7a823bd0f8d08276eb1630))

## [0.9.0](https://github.com/SongshGeoLab/ABSESpy/compare/v0.8.5...v0.9.0) (2025-10-29)


### Features

* **actor, patch:** :sparkles: Add move_to method in Actor and count_agents method in PatchModule ([11e63b2](https://github.com/SongshGeoLab/ABSESpy/commit/11e63b2a95fc72232a5ab96d840bf9ad66743b30))
* **actor:** :sparkles: Add evaluate method to Actor for scoring candidates with rollback functionality ([bad83ac](https://github.com/SongshGeoLab/ABSESpy/commit/bad83ac22e769cafa092584414a83a603dda3c9b))
* **agents, space:** :sparkles: Enhance agent and cell functionality with new properties and methods ([cacf3d0](https://github.com/SongshGeoLab/ABSESpy/commit/cacf3d04957ddf54d949277c86e3bc80af415dad))
* **core:** Protocol-based architecture refactoring ([12534d8](https://github.com/SongshGeoLab/ABSESpy/commit/12534d8c93517336c57f0d86a57aaab366fb6af7))
* **examples:** :sparkles: Remove outdated agent and analysis files, add configuration and quick start notebook ([d1fed62](https://github.com/SongshGeoLab/ABSESpy/commit/d1fed623172cdeb8cddcfe3a560f0be94c340c68))
* **examples:** :white_check_mark: Introduce configuration file and enhance model dynamics ([1fa3e0c](https://github.com/SongshGeoLab/ABSESpy/commit/1fa3e0cc879c4c7e01f19b4040160e410006105e))
* **patch:** :sparkles: Implement __getitem__ method for PatchModule with numpy-style indexing ([1c66edb](https://github.com/SongshGeoLab/ABSESpy/commit/1c66edb3e833d145295e0ae139e54d89340e2c18))


### Bug Fixes

* **sequences:** Fix attribute access in better() method ([2f1089f](https://github.com/SongshGeoLab/ABSESpy/commit/2f1089f40267cb2b7b5967f2d7519fec6fff3a15))


### Documentation

* **docs:** :memo: Enhance UML documentation and integrate Mermaid diagrams ([62a9cdd](https://github.com/SongshGeoLab/ABSESpy/commit/62a9cdd62715c6c72439def968a1a8a896b16aae))
* **tutorials, docs:** :memo: Expand tutorial content and enhance documentation structure ([316c972](https://github.com/SongshGeoLab/ABSESpy/commit/316c97203b21c94c0a797bb9199d2a8ca4818c60))

## [0.7.5](https://github.com/SongshGeoLab/ABSESpy/compare/v0.7.4...v0.7.5) (2025-02-16)


### Bug Fixes

* **api:** :bug: Fix agent select by time incorrectly in Container ([fabaa35](https://github.com/SongshGeoLab/ABSESpy/commit/fabaa35e1d06b9b383c1e950d956ee96abfad003))
* **api:** :bug: fix draw actors methods ([fff471b](https://github.com/SongshGeoLab/ABSESpy/commit/fff471b90a4423c5d0365efb7ae4d82118d3a3be))
* **docs:** :bug: Fix all the outdated notebook docs ([a3667ab](https://github.com/SongshGeoLab/ABSESpy/commit/a3667aba54bd5c18380bcfd2bac00366051c2953))
* **docs:** :memo: Remove docs for decision, deprecated feature ([a87bf6a](https://github.com/SongshGeoLab/ABSESpy/commit/a87bf6a316f56dbf0ba5dc42db45d60c3d837ac0))

## [0.7.4](https://github.com/SongshGeoLab/ABSESpy/compare/v0.7.3...v0.7.4) (2025-02-06)


### Bug Fixes

* :green_heart: Fix python version update in release please ([365df5c](https://github.com/SongshGeoLab/ABSESpy/commit/365df5c9f70089b5da7c48aec810fbef727aa7cd))

## [0.7.3](https://github.com/SongshGeoLab/ABSESpy/compare/v0.7.2...v0.7.3) (2025-02-06)


### Bug Fixes

* :green_heart: Fix python version update in release please ([68c2dae](https://github.com/SongshGeoLab/ABSESpy/commit/68c2dae336d6f70c4453c4b3d6be26a94f3b0e57))

## [0.7.2](https://github.com/SongshGeoLab/ABSESpy/compare/v0.7.1...v0.7.2) (2025-02-06)


### Bug Fixes

* **src:** :bug: Fix bug in visualizing empty agent sets ([96abff1](https://github.com/SongshGeoLab/ABSESpy/commit/96abff1244412d149f89ddce25cf988dc5f94019))
* **src:** :bug: Parse parameters in correct order now ([cd648c7](https://github.com/SongshGeoLab/ABSESpy/commit/cd648c7ac6ded2bbd23268577cfa0345d7d89df8))

## [0.7.1](https://github.com/SongshGeoLab/ABSESpy/compare/0.7.0...v0.7.1) (2025-02-03)


### Bug Fixes

* :green_heart: Only generate joss draft on main, using poetry instead of pip ([fb8dafc](https://github.com/SongshGeoLab/ABSESpy/commit/fb8dafc2126754545432e88130b03d13e5b54c5c))
* **docs:** :memo: Moved contributing guideness to main repo and fixed it's docs style ([6601f3c](https://github.com/SongshGeoLab/ABSESpy/commit/6601f3c39c44480141e5014fa944b108a659e370))
* **project:** :green_heart: remove griffle plugin from mkdocs-material ([9805663](https://github.com/SongshGeoLab/ABSESpy/commit/9805663a42a9d0ddf45871a1297275c198248f42))

<a id='changelog-0.7.0'></a>
## 0.7.0 — 2024-11-17

## Refactoring

- [x] #refactor♻️ API compatible with Mesa 3.x version.
- [x] #refactor♻️ Better experiment class

## New Features

- [x] #feat✨ Improve compatibility for visualisation with Mesa 3.x version
- [x] #feat✨ Add Solara function for Mesa 3.x visualisation

<a id='changelog-0.7.0.alpha'></a>
## 0.7.0.alpha — 2024-11-08

## Refactoring

- [x] #refactor♻️ API compatible with Mesa 3.x version.

## New Features

- [x] #feat✨ Improve compatibility for visualisation with Mesa 3.x version

<a id='changelog-0.6.10'></a>
## 0.6.10 — 2024-07-12

## Documentation changes

- [x] #docs📄 Update geodata document with excluded mkdocs config

## New Features

- [x] #feat✨ Specific current datetime for TimeDriver

## Refactoring

- [x] #refactor♻️ when single run in exp, no progress bar anymore

<a id='changelog-0.6.9'></a>
## 0.6.9 — 2024-06-08

## Refactoring

- [x] #refactor♻️ Improved code structure.

## New Features

- [x] #feat✨ `TimeDrive` included a new `expected_ticks` property

<a id='changelog-0.6.8'></a>
## 0.6.8 — 2024-06-04

## Refactoring

- [x] #refactor♻️ Use a new `datacollector` instead of mesa's `datacollector`

## New Features

- [x] #feat✨ Separate different agents when collecting data on agents
- [x] #feat✨ Setup subsystem class when init an experiment
- [x] #feat✨ now can set-up logging configs in yaml
- [x] #feat✨ Reproject a `DataArray` by patch
- [x] #feat✨ Random assign a value to `ActorsList`

<a id='changelog-0.6.7'></a>
## 0.6.7 — 2024-05-29

## New Features

- [x] #feat✨ Access datasets configurations by `.ds` or `.datasets` globally

## Fixed bugs

- [x] #bug🐛 Aligned behaves of `random.new` and `random.choice`
- [x] #bug🐛  fixed future warning when check `unique_id`
- [x] #bug🐛  now `Path` object is acceptable when using vector data to create `patch`
- [x] #bug🐛  The arg `agent_cls` passed to `_new_one` method now

<a id='changelog-0.6.6'></a>
## 0.6.6 — 2024-05-19

## Fixed bugs

- [x] #bug🐛 Fixed `Actor`'s indices transforming bug.
- [x] #bug🐛 Fixed `flipud` raster when loading data with different `y` coords.

## Refactoring

- [x] #refactor♻️ Improved the coding structure of `AgentsContainer`
- [x] #refactor♻️ Improved the generator of `unique_id` for new Actors
- [x] #refactor♻️ Improved coding structure of visualizations.

## Documentation changes

- [x] #docs📄 A new tutorial for creating actors by importing network
- [x] #docs📄 Improved the tutorials of `geodata.ipynb` and `model_viz.ipynb`

## New Features

- [x] #feat✨ `PatchCell` also has the accessibility of `TimeDriver` now.
- [x] #feat✨ Actors can be created by passing a sequence of `unique_id`  now.
- [x] #feat✨  Normal `Actor` now has a geometry of point according to the pos
- [x] #feat✨ A new property of `geo_type` for `Actor` and `Cell`.
- [x] #feat✨ New `.summary`  method to check attributes of `Actor` and `ActorsList`
- [x] #feat✨ Plotting `network` and `shapefile`

<a id='changelog-0.6.5'></a>
## 0.6.5 — 2024-05-17

## Fixed bugs

- [x] #bug🐛 solving situation when entities with prob are not enough for expected size in random choose
- [x] #bug🐛  Fixed shape `(1, x)` natural patch squeezed bug

<a id='changelog-0.6.4'></a>
## 0.6.4 — 2024-05-16

## Fixed bugs

- [x] #bug🐛 Fixed `module_class` type incompatibility when arg `how` is assigned
- [x] #bug🐛 Fixed `VizNodeList` with `savefig` arg

## Documentation changes

- [x] #docs📄 Improved logs

## New Features

- [x] #feat✨ Adding logs for model and experiment.
- [x] #feat✨ counting the ages of the actors

<a id='changelog-0.6.3'></a>
## 0.6.3 — 2024-05-12

## New Features

- [x] #feat✨ now experiment can record model's vars

<a id='changelog-0.6.2'></a>
## 0.6.2 — 2024-05-12

## Refactoring

- [x] #refactor♻️ update dependencies.

<a id='changelog-0.6.1'></a>
## 0.6.1 — 2024-05-12

## New Features

- [x] #feat✨ added applying mask option when apply a raster

## Fixed bugs

- [x] #bug🐛 include `__init__.py` for default config

<a id='changelog-0.6.0'></a>
## 0.6.0 — 2024-05-11

## Fixed bugs

- [x] #bug🐛 Fixed hotelling model's multiple preferences bug.
- [x] #bug🐛 Fixed dataset unavailable in the tests

## Performance improvements

- [x] #zap⚡️ Improved speed by removing some dead codes.

## Refactoring

- [x] #refactor♻️ Refactored structure of `BaseNature` for better performance.

## New Features

- [x] #feat✨ Added an `Experiment` class for advanced model batch running.
- [x] #feat✨ Now `BaseNature` module can manipulate the major layer directly.
- [x] #feat✨ Added the basic model visualization methods.

## Documentation changes

- [x] #docs📄 Added a completed tutorial of forest fire to demonstrate multiple runs.

<a id='changelog-0.5.8'></a>
## 0.5.8 — 2024-04-18

## Performance improvements

- [x] #zap⚡️ Improved nature raster operation performance by vectorizing

## Refactoring

- [x] #refactor♻️ Refactor nature for more convenience and consistency

## Fixed bugs

- [x] #bug🐛 fixed the same seed for all `ActorsList` bugs.

## Documentation changes

- [x] #docs📄 update notebooks with cleaner descriptions on Nature

<a id='changelog-0.5.7'></a>
## 0.5.7 — 2024-04-10

## Fixed bugs

- [x] #bug🐛 Fixing default getter setter for `ActorsList`, `Actor`, and `PatchCell`
- [x] #bug🐛  AttributeError when getting value with wrong key

## Documentation changes

- [x] #docs📄 adding authors' ORCID of the paper
- [x] #docs📄 correcting installation from source tutorial
- [x] #docs📄  fixing Mantilla Ibarra name and capitalizing refers

<a id='changelog-0.5.6'></a>
## 0.5.6 — 2024-04-06

## Refactoring

- [x] #refactor♻️ improve code formats

## Documentation changes

- [x] #docs📄 updated fundings in paper
- [x] #docs📄 updated README contributors

<a id='changelog-0.5.5'></a>
## 0.5.5 — 2024-04-06

## Refactoring

- [x] #refactor♻️ Improved code formats

## Documentation changes

- [x] **LINE 30**: Missing space between "...tools (Schlüter et al., 2023)" and "to implement...". Should appear as "...tools (Schlüter et al., 2023) to implement..."
- [x] **LINE 42**: The figure reference "(Figure 1)" should not be bold but instead use formatting that enables linking to the actual figure. You can see how this is done in other JOSS publications such as [https://joss.theoj.org/papers/10.21105/joss.06294](https://joss.theoj.org/papers/10.21105/joss.06294)[](https://www.sci-hub.ee/10.21105/joss.06294). I'll only mention this for This figure, but note that this should be done for all figure references in your paper.
- [x] **LINE 48**: The statement "...but somehow enhanced." should be changed here. Perhaps use "...but with enhanced functionality." or the something similar.
- [x] **LINE 49**: Since YAML is a data serialization language, it should be referenced by its name here instead of the extension which sometimes varies. So instead of "...through .yaml files." you could use "...through the use of YAML configuration files." or something similar. You can read more about YAML [here](https://yaml.org/) if you like. Note that there are several of these usages throughout the paper that you may need to correct.
- [x] **LINE 53**: Wording is off here. Instead of "...(2) enhancing reality and manageability of ABMs." something like the following would be more clear "...(2) enhancing the reality and manageability of ABMs." This is phrased several times like this throughout the paper, so please let me know if it should be written as stated. I'll not mention the other occurrences, but address those if needed.
- [x] **LINE 56**: "...and can be..." should be "...which can be..."
- [x] **LINE 63**: "(Schlüter et al., 2017), (Beckage et al., 2022)" should appear as "(Schlüter et al., 2017; Beckage et al., 2022)"
- [x] **LINE 87-88**: You use the formatting `{"start: '2022-12-31', "end": 2024-01-01, year: 1}` please add in what I believe should be the correct, consistent formatting as following: `{"start: "2022-12-31", "end": "2024-01-01", "year": 1}`. Please correct me if I am wrong. I am also assuming "year" requires an integer as you have written.
- [x] **LINE 88**: "...to the 'time' module..." should be formatted as "...to the `time` module..." where backticks are used.
- [x] **LINE 102**: You use "input/output" though earlier in the paper you use "Input/Ouput" please choose one method to be consistent.
- [x] **LINE 131**: Your reference for the Janssen et al. paper is not formatted correctly. See [https://www.jasss.org/11/2/6/citation.html](https://www.jasss.org/11/2/6/citation.html)
- [x] **LINE 135**: Should have a colon after "In". See [https://link.springer.com/chapter/10.1007/978-3-030-61255-9_30#citeas](https://link.springer.com/chapter/10.1007/978-3-030-61255-9_30#citeas)[](https://www.sci-hub.ee/10.1007/978-3-030-61255-9_30)
- [x] **LINE 159**: Missing colon after "In" see [https://link.springer.com/chapter/10.1007/978-3-319-67217-5_2#citeas](https://link.springer.com/chapter/10.1007/978-3-319-67217-5_2#citeas)[](https://www.sci-hub.ee/10.1007/978-3-319-67217-5_2)

<a id='changelog-0.5.4'></a>
## 0.5.4 — 2024-03-28

## Documentation changes

- [x] #docs📄 Line 24: 'research' not 'researches'
- [x] #docs📄 Line 44: rather than 'et al.' maybe use actual words (e.g. 'and others') so as not to confuse against the file suffixes which are similar abbreviations
- [x] #docs📄  Line 55: What do you mean by 'practicing' here? This doesn't seem right. Please edit to clarify
- [x] #docs📄  Lines 57-65: I'm surprised these three points (Perceptions, Decision-making, Response) don't match the words used in Fig 2 (Options, Evaluate, Behaviour). Or are the latter three (in the Fig) all part of the 'decision-making' step? Aligning the steps in the list with the figure would be useful, I think
- [x] #docs📄  Line 76: I think 'vary' should be 'varying'
- [x] #docs📄  Line 93: 'more accurate' - this is a relative statement, so please clarify 'more accurate' than what?
- [x] #docs📄  Line 99: ( wang2022h? )) is not included in the reference list
- [x] #docs📄  Line 100: it's good that you recognise the similarity here to `AgentPy` but you don't then clearly explain how `absespy` is beneficial for SES researchers - maybe you could highlight the explicit functionality for representing the 'nature' side of CHANS (`AgentPy` really focuses on the 'human' side).
- [x] #docs📄  Line 108: 'merely heuristic' - I think this is a little over-critical of NetLogo, which can incorporate 'real-world' (I think you mean 'empirical'?) data although not at the scale `absespy` could. I suggest you edit here to focus on the value of `absespy` for working with large-scale, empirical data so that models can run more efficiently than would be possible for the same data in NetLogo. You might also highlight your `TimeDriver` module which is a benefit over NetLogo's more simple 'ticks'

- [x] #docs📄  L105 & L151: netlogo and Netlogo should be NetLogo
- [x] #docs📄  L42, L98, L101 & L153 : mesa-geo and Mesa-geo should be Mesa-Geo
- [x] #docs📄  L95, L97, L98, L102, L129 & L153 : mesa should be Mesa
- [x] #docs📄  L96: abce should be ABCE
- [x] #docs📄  L128, L148 & L154: python should be Python

- [x] #docs📄 Update project readme
- [x] #docs📄 Improve JOSS paper overall.

<a id='changelog-0.5.3'></a>
## 0.5.3 — 2024-03-26

## Fixed bugs

- [x] #bug🐛 Only alive actors can apply default methods by decorator `alive_required` now.
- [x] #bug🐛 now moving has a return to control continue to move or not.
- [x] #bug🐛 now update the position attribute correctly after moving
- [x] #bug🐛 fixing release drafter to the latest version

<a id='changelog-0.5.2'></a>
## 0.5.2 — 2024-03-26

## Performance improvements

- [x] #zap⚡️ improve getting performance from container

## New Features

- [x] #feat✨ now getting link name can be with a default empty return
- [x] #feat✨ getting an attr value from a `ActorsList`
- [x] #feat✨ before moving, `Actor` may do something
- [x] #feat✨ possible to control max length when customize `PatchCell`
- [x] #feat✨  getting an item or None from `ActorsList` or container

<a id='changelog-0.5.1'></a>
## 0.5.1 — 2024-03-20

## Documentation changes

- [x] #docs📄 Update all tutorials
- [x] #docs📄 Update readme

## Refactoring

- [x] #refactor♻️ Refactoring some tests
- [x] #refactor♻️ Remove some died codes.

<a id='changelog-0.5.0'></a>
## 0.5.0 — 2024-03-12

## Performance improvements

- [x] #zap⚡️ improve code formats
- [x] #build🏗 upgrade dependencies and using typing-extension

## New Features

- [x] #feat✨ Agents now can use `move.to` a random `pos` on a layer
- [x] #feat✨ Random choose now can select from an empty list
- [x] #feat✨ actors' movement by new proxy class

## Documentation changes

- [x] #docs📄 updating docs notebooks for beginners
- [x] #docs📄 refactoring the structure of api docs
- [x] #docs📄 improve docs format

## Fixed bugs

- [x] #bug🐛 use typing_extensions to make abses compatible to python 3.9
- [x] #bug🐛 alter nature now behaves correctly
- [x] #bug🐛 fixing `Main Nature` `total_bounds` check ambigious
- [x] #bug🐛 fixing `random.replace` arg doesn't work problem

## Refactoring

- [x] #refactor♻️ separate `_CellAgentsContainer` and `AgentsContainer`
- [x] #refactor♻️ using default schedule and data collector, but compatible to attrs config
- [x] #refactor♻️ AgentsContainer private and not singleton anymore
- [x] refactoring `nature`, `Actor` `links` and its tests
- [x] store agents by container in PatchCell
- [x] use `get`, `set` methods to control the actor's behaviors

<a id='changelog-0.4.2'></a>
## 0.4.2 — 2024-01-11

## Refactoring

- [x] #refactor♻️ Refactoring data collector tests to `tests/conftest.py`

## Fixed bugs

- [x] #bug🐛 Data collector strings are collected now.

<a id='changelog-0.4.1'></a>
## 0.4.1 — 2024-01-11

## Documentation changes

- [x] #docs📄 Update project README

## Fixed bugs

- [x] #bug🐛 Fix `mkdocs` CI bug

<a id='changelog-0.4.0'></a>
## 0.4.0 — 2024-01-11

## New Features

- [x] #feat✨ `run_model`  function can set steps now.
- [x] #feat✨ Better logging by loguru

## Documentation changes

- [x] #docs📄 Re-structuring documentations
- [x] #docs📄 Update get-started
- [x] #docs📄 Actors' movement

<a id='changelog-0.3.5rc'></a>
## 0.3.5rc — 2023-12-05

## Fixed bugs

- [x] #bug🐛 fix `AttributeError: 'super' object has no attribute 'random'`

<a id='changelog-0.3.5'></a>
## 0.3.5 — 2023-12-05

## New Features

- [x] #feat✨ `random.choice` in random module
- [x] #feat✨ `data-collector` module for collecting data

## Documentation

- [x] #docs📄 Update API documentation of `random`
- [x] #docs📄 Add a citation of `wang2022h`

<a id='changelog-0.3.4'></a>
## 0.3.4 — 2023-12-01

## Fixed bugs

- [x] #bug🐛 (modules): :bug: fixed the geometry links behave not stably.

<a id='changelog-0.3.3'></a>
## 0.3.3 — 2023-11-29

## Fixed bugs

- [x] #bug🐛 fixing `random.choice` triggered error : `'super' object has no attribute 'random'`

<a id='changelog-0.3.2'></a>
## 0.3.2 — 2023-11-29

## New Features

- [ ] #feat✨ Generate random links between actors with the possibility

<a id='changelog-0.3.1'></a>
## 0.3.1 — 2023-11-28

## Performance improvements

- [x] #build🏗 Un-pin the dependencies and upgrade

<a id='changelog-0.3.0'></a>
## 0.3.0 — 2023-11-11

## Documentation changes

- [x] #docs📄 Refine the api documentation
- [x] #docs📄 Add a simple paper to introduce the package
- [x] #docs📄 Update readme to highlight some features.
- [x] #docs📄 Add an example of Hotelling model.

## New Features

- [x] #feat✨ Introduce, test, documentation an example of decisions framework

## Refactoring

- [x] #refactor♻️ Some small refactoring when polishing api documents

<a id='changelog-0.2.1.alpha'></a>
## 0.2.1.alpha — 2023-11-07

## Documentation changes

- [x] #docs📄 introduce the new feature: real-world time control
- [x] #docs📄 Architectural Elegance for Modular Socio-Ecological Systems Modeling

## Refactoring

- [x] #refactor♻️ using `loguru` for logs
- [x] #refactor♻️ using `pendulum` for solving `TimeDriver`
- [x] #refactor♻️ [使用logrue来控制日志](https://github.com/Delgan/loguru)

## Fixed bugs

- [x] #bug🐛 fixing twice logging bug
- [x] #bug🐛 hot-fix infinitely model runing
- [x] #bug🐛 Twice logging.

## v-0.1.0 🎉

## New Features

- [x] #feat✨  #agent🤖️  Create, remove, add `Actor` in `Container`
- [x] #feat✨  #agent🤖️  Select `Actor` in `ActorsList` by adding selection syntax
- [x] #feat✨  #agent🤖️  read attributes from current `PatchCell`.
- [x] #feat✨  #Nature🌍 Automatically reads spatial data as raster variables
- [x] #feat✨  #Nature🌍 Adding, removing `Actors` into nature spaces.

## Documentation changes

- [x] #docs📄  #project🎉 Logging.
- [x] #docs📄 #project🎉 Basic introduction of `ABSESpy`

## v-0.1.1 🎉

## Documentation changes

- [x] #docs📄 update README document

## v-0.1.2 🎉

## Fixed bugs

- [x] #bug🐛 fixed log setup twice

## v-0.2.0.alpha 🎉

- [x] #refactor♻️ Remove `variable` class and replace it with `DynamicVariable`.
- [x] #refactor♻️ Remove `TimeDriverManager` and adding type hint to `TimeDriver`
- [x] #build🏗 #project🎉 Removed dependence of `AgentPy`.
