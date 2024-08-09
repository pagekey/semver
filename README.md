# pagekey-semver

This is a simple, opinionated semantic versioning tool.

Check out the docs site (coming soon) or the [docs site source](./docs/index.md) to learn more.

## Getting Started

1. Install the package

```bash
pip install pagekey-semver
```

2. Run the dry run to see what will happen.

```bash
pagekey-semver plan
```

3. Run it for real to tag and push!

```bash
pagekey-semver apply
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

See [here](./docs/config/index.md) for more information on how to configure the tool.
