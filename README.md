# pagekey-semver

This is a simple, opinionated semantic versioning tool.


## Getting Started

1. Install the package

```bash
pip install pagekey-semver
```

2. Run the dry run to see what will happen.

```bash
pagekey-semver --dry-run
```

3. Run it for real to tag and push!

```bash
pagekey-semver
```

## Usage


### GitHub Actions

Coming soon.


### GitLab CI/CD

Coming soon.


## Philosophy

This is an opinionated version of Semantic Release that loosely follows the guidelines at [semver.org](https://semver.org/). It puts practicality above all theory. There is no special treatment of "pre-releases", versions prior to `v1.0.0`. Everything behaves the same: patch prefixes increment the third number, minor patches increment the middle number, and major prefixes increment the first number. If there are multiple prefixes, the prefix with the greatest precedence is applied. If you don't like the default settings, you can override them using the configuration format below.

This package is intended to run on a Linux system with the `bash` shell installed.


## Configuration

Add a `.semver` file in the top-level directory of your repo. This file should be in YAML syntax and can override various settings for semantic release. If you do not specify part of the config, the default values will be used.


### Changelog Path

You can change the path to the Changelog file by simply specifying a new `changelog_path` in the config.

```yaml
changelog_path: docs/CHANGELOG.md
```

Any directories along the way will be created for you. For example, if the `docs/` directory does not exist when using the above config, it will be created when you run `pagekey-semver`.


### Prefixes

To override which prefixes create a new release, you can use the following `.semver` file. Be sure to provide values for major, minor, and patch releases.

```yaml
prefixes:
  - label: huge
    type: major
  - label: mini
    type: minor
  - label: micro
    type: patch
```

With the above config and a project with a latest tag of `v0.1.0`, adding the commit `micro: Fix a bug` would create `v0.1.1`, adding `mini: Add feature` would create `v0.2.0`, and adding `huge: Break everything` would create `v1.0.0`.

### Tag Format

You can specify a custom tag format for your versioning. This affects which existing tags are detected and, in turn, the new tag that is created. You can use `%M` to represent the major version, `%m` to represent minor, and `%p` to represent patch. The default format is:

```yaml
foramt: "v%M.%m.%p"
```

If you want to remove the `v`, then you just need to configure the following:

```yaml
format: "%M.%m.%p
```

If you prefer dahses over dots, you can write:

```yaml
format: "v%M-%m-%p
```
