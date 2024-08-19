# pagekey-semver

Simple automated version tagging for any Git-based software project.

Check out the [docs](./docs/index.md) to learn more.


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


## Requirements / Assumptions

This tool requires that the following software is installed on the system running it:

- Python 3
- [`bash`](https://linux.die.net/man/1/bash)
- [`sed`](https://linux.die.net/man/1/sed), if using the [`sed` file replacer](./docs/config/file_replacers/sed.md).
- [`which`](https://linux.die.net/man/1/which), to check if `sed` is installed and raise a human-friendly error if not.


## Usage

To use this package, you'll need to start prefixing commits with `major:`, `minor:`, and `patch:`. If you don't like these prefixes, you can customize them in the [config file](./docs/config/index.md). Here's a brief description of what each one means:

- `major`: If you put this prefix on a commit, it means that if people update to this version of your code, they will need to change their code or else things will break. In other words, you've made a breaking change to your API / software interface. This increments the first number of the version: `v1.0.0` would go to `v2.0.0`.
- `minor`: This means you've added something new, such as a feature (`feat` is another common prefix for this type). If people auto-update to this version, your old code will still work, but new features will be available, too. It's backwards compatible. This increments the second number of the version: `v1.0.0` would go to `v1.1.0`.
- `patch`: Similarly, this does not break anything. Instead of adding a feature, you're just fixing a bug or doing something small that doesn't affect the user's experience much. This increments the third number of the version: `v1.0.0` would go to `v1.0.1`.

You can run this package locally as shown in "Getting Started" above, but most people will want to run this in CI/CD so that everything is automated and you don't have to thing about versioning anymore - just use properly prefixed commits, and you'll be good to go.

As you'll see below, it's highly recommended to set the `SEMVER_TOKEN` variable to your push credential, as well as `SEMVER_USER` if applicable for your Git hosting platform. For GitHub, use `GITHUB_TOKEN` or any other PAT secret you've created. For GitLab, you must create your own secret - `GITLAB_TOKEN` is a common name for it.


### GitHub Actions

The simplest way to get started is to paste the following workflow into a file such as `.github/workflows/ci.yml`.

```yaml
name: Run semantic version process.

on: [push]

jobs:
  version:
    uses: pagekey/semver/.github/workflows/semver.yml@main
```

If you want to specify which user is used to push, you can use the following snippet. You must create the `SEMVER_USER` and `SEMVER_TOKEN` secrets. You can use a [GitHub Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) set as a repo or organization [secret](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions). If you'd rather not use your personal account for the PAT, you can use a bot account.

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

Beware that GitHub does **not** trigger a pipeline on tags pushed from Actions (or at least, I couldn't figure out how to get it to do that.)

If you want to trigger another workflow only when a tag has been created, you can use the following, combining `needs` and `if` to check:

```yaml
jobs:
  # ...
  # omitting "version" job shown above
  # ...

  publish:
    needs: version
    if: ${{ needs.version.outputs.semver_release_occurred == 'true' }}
    steps:
      # Do anything that should only occur on new tags, such as publishing/deploying your code.
      - name: Checkout code
        uses: actions/checkout@v4
```

To create a GitLab release, check out the docs for the [GitHub Create Release integration](./docs/config/create_release.md#github).


### GitLab CI/CD

GitLab CI/CD is a bit more straightforward than GitHub Actions for this package. There is no restriction on running pipelines that have been created automatically, so a tag pipeline will run when the package pushes. Use the following snippet in your `.gitlab-ci.yml` file to get started. Be sure to set `SEMVER_USER` and `SEMVER_TOKEN`. For user, you can use `oauth2`, `gitlab-ci-token`, or your username. For the token, use a personal or group access token.

Note that `only` and `except` are deprecated, but are included here for simplicity. You can migrate to `rules` if you would like.

```yaml
stages:
  - version


semver-dry-run:
  stage: version
  image: python:3.10
  except: [main, tags]
  script:
    - pip install pagekey-semver
    - pagekey-semver plan

semver:
  stage: version
  image: python:3.10
  only: [main]
  script:
    - pip install pagekey-semver
    - pagekey-semver apply
```

To create a GitLab release, check out the docs for the [GitLab Create Release integration](./docs/config/create_release.md#gitlab).


## Philosophy

This is an opinionated version of Semantic Release that loosely follows the guidelines at [semver.org](https://semver.org/). It puts practicality above all theory. This differs in a few ways from more popular semantic release packages:

- If there are no tags matching the specified format yet, then `v0.1.0` is used as the first version.
- There is no special treatment of "pre-releases", versions prior to `v1.0.0`. Everything behaves the same: patch prefixes increment the third number, minor patches increment the middle number, and major prefixes increment the first number. If there are multiple prefixes, the prefix with the greatest precedence is applied. If you don't like the default settings, you can override them using the configuration format below.
- There is currently no support for scoped commits (`fix(release): do something`) unless you add each scope to the `.semver` file as its own prefix.


## Configuration

See [here](./docs/config/index.md) for more information on how to configure the tool.
