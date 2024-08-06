# Configuration

Add a `.semver` file in the top-level directory of your repo. This file should be in YAML syntax and can override various settings for semantic release. If you do not specify part of the config, the default values will be used.

Contents:

- [Changelog Path](#changelog-path)
- [Changelog Writer](#changelog-writer)
- [Prefixes](#prefixes)
- [Replace Files](#replace-files)
- [Tag Format](#tag-format)


## Changelog Path

You can change the path to the Changelog file by simply specifying a new `changelog_path` in the config.

```yaml
changelog_path: docs/CHANGELOG.md
```

Any directories along the way will be created for you. For example, if the `docs/` directory does not exist when using the above config, it will be created when you run `pagekey-semver`.


## Changelog Writer

The default changelog writer is quite simple - for each version, it adds a level-2 header for the version and below it, each commit as a bullet.

```md
## v1.0.0

- fix: Do something (f7ae92385abc9a0f84ed1e7624ec7205e01472a6)
- feat: Add some feature (1933db71316abfea44b6e12d20399827eb03322e)
```

If you don't like this format, override the default changelog writer with your own class. You can do this by adding a `changelog_writer.py` and populate it with the following:

```python
from pagekey_semver.changelog import ChangelogWriter

class CustomChangelogWriter(ChangelogWriter):
    def write_changelog(self, changelog_file, version, commits):
        changelog_file.write("Hello " + version.name + "\n")
        for commit in commits:
            changelog_file.write("> " + commit.message + "\n")
```

Then specify your writer in the `.semver` config file:

```yaml
changelog_writer: changelog_writer:CustomChangelogWriter
```

Now, when you run `pagekey-semver`, the changelog will look like this:

```md
Hello v1.0.0
> fix: Do something
> feat: Add some feature
```


## Prefixes

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


## Replace Files

You can specify "replace files," which PageKey Semver will process and replace the text you specify with the new version. There are four types of Replace Files: JSON, YAML, SED, and TOML.

You can provide a list of any number of files you need to replace in the config. By default, none are specified:

```yaml
replace_files: []
```

Documentation and examples are available for each type of replace file:

- [JSON Replace File](./replace_files/json.md)
- [SED Replace File](./replace_files/sed.md)
- [TOML Replace File](./replace_files/toml.md)
- [YAML Replace File](./replace_files/yaml.md)


## Tag Format

You can specify a custom tag format for your versioning. This affects which existing tags are detected and, in turn, the new tag that is created. You can use `%M` to represent the major version, `%m` to represent minor, and `%p` to represent patch. The default format is:

```yaml
format: "v%M.%m.%p"
```

If you want to remove the `v`, then you just need to configure the following:

```yaml
format: "%M.%m.%p
```

If you prefer dahses over dots, you can write:

```yaml
format: "v%M-%m-%p
```