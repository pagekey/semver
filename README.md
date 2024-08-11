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

As you'll see below, it's highly recommended to set the `SEMVER_TOKEN` variable to your push credential, as well as `SEMVER_USER` if applicable for your Git hosting platform.

### GitHub Actions

Follow these steps to use PageKey Semver with GitHub Actions.

1. Generate a GitHub Personal Access Token. Follow [this guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) if you're not sure how.

2. Add the token to your repo or organization as the `SEMVER_TOKEN` secret. See [this guide](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions) for more info on how to do that.

3. Add a `SEMVER_USER` secret containing your username. If you'd rather not use your personal account, use a bot account.

4. Add the following workflow in your repo at `.github/workflows/ci.yml`:

```yaml
name: Run semantic version process.

on: [push]

jobs:
  version:
    uses: pagekey/semver/.github/workflows/semver.yml@main
    with:
      SEMVER_USER: ${{ secrets.SEMVER_USER }}
      SEMVER_TOKEN: ${{ secrets.SEMVER_TOKEN }}
```


### GitLab CI/CD

Coming soon.


## Philosophy

This is an opinionated version of Semantic Release that loosely follows the guidelines at [semver.org](https://semver.org/). It puts practicality above all theory. There is no special treatment of "pre-releases", versions prior to `v1.0.0`. Everything behaves the same: patch prefixes increment the third number, minor patches increment the middle number, and major prefixes increment the first number. If there are multiple prefixes, the prefix with the greatest precedence is applied. If you don't like the default settings, you can override them using the configuration format below.

This package is intended to run on a Linux system with the `bash` shell installed.


## Configuration

See [here](./docs/config/index.md) for more information on how to configure the tool.

