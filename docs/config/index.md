# Configuration

Add a `.semver` file in the top-level directory of your repo. This file should be in YAML syntax and can override various settings for semantic release. If you do not specify part of the config, the default values will be used.

Contents:

- [Changelog Path](#changelog-path)
- [Changelog Writer](#changelog-writer)
- [Prefixes](#prefixes)
- [Replace Files](#replace-files)
- [Tag Format](#tag-format)
- [Integrations](#integrations)


## Changelog Path

You can change the path to the Changelog file by simply specifying a new `changelog_path` in the config.

```yaml
changelog_path: docs/CHANGELOG.md
```

Any directories along the way will be created for you. For example, if the `docs/` directory does not exist when using the above config, it will be created when you run `pagekey-semver`.


### Environment Variable Override

You can override this config item by setting the `SEMVER_changelog_path` variable.

## Changelog Writer

The default changelog writer is quite simple - for each version, it adds a level-2 header for the version and below it, each commit as a bullet.

```md
## v1.0.0

- fix: Do something (f7ae92385abc9a0f84ed1e7624ec7205e01472a6)
- feat: Add some feature (1933db71316abfea44b6e12d20399827eb03322e)
```

If you don't like this format, override the default changelog writer with your own class. You can do this by adding a `changelog_writer.py` and populate it with the following:

```python
from pagekey_semver.changelog_writer import ChangelogWriter

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

### Environment Variable Override

You can override this config item by setting the `SEMVER_changelog_writer` variable.


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

Specifying the `prefixes:` list in your config file will override all default prefixes, so be sure to include at least one option for `major`, `minor`, and `patch`.


### Environment Variable Override

You can add additional prefixes using environment variables. To do this, set the `SEMVER_prefixes_YOURLABEL` to either `major`, `minor`, or `patch`. For example, setting the `SEMVER_prefixes_custom` to `patch` will be equivalent to adding the following prefix:

```yaml
  - label: custom
    type: patch
```

When using this method, your additional prefixes are added onto the existing prefixes, which are either the default values or overridden by a config file.


## Replace Files

You can specify "replace files," which PageKey Semver will process and replace the text you specify with the new version. There are four types of Replace Files: JSON, YAML, SED, and TOML.

You can provide a list of any number of files you need to replace in the config. By default, none are specified:

```yaml
file_replacers: []
```

Documentation and examples are available for each type of replace file:

- [JSON Replace File](./file_replacers/json.md)
- [SED Replace File](./file_replacers/sed.md)
- [TOML Replace File](./file_replacers/toml.md)
- [YAML Replace File](./file_replacers/yaml.md)


### Environment Variable Override

You can use environment variables to set additional replace files. To do so, you **must** set **multiple** environment variables per replace file (`name`, `type`, and any additional fields required for that particular replacer). Setting only one or two fields will result in an error - you must set all of them.

You must create an arbitrary index for your replace file. This is used only when parsing environment variables, then it is discarded. This can be any string or even an index number. The example below uses index `0`.

If you set the following three environment variables:

- `SEMVER_file_replacers__0__name=my_file.json`
- `SEMVER_file_replacers__0__type=json`
- `SEMVER_file_replacers__0__key=version`
- `SEMVER_file_replacers__0__format=%M.%m.%p`

Setting these variables will add the following replace file to your configuration:

```yaml
  - name: my_file.json
    type: patch
    key: version
```

Refer to the docs for each specific type of replace file to ensure that you're including the required fields.


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

### Environment Variable Override

You can override this config item by setting the `SEMVER_tag_format` variable.

## Integrations

These features integrate with something outside of the Git repository. So far, the only integration supported is the [Create Release integration](./create_release.md), which sends a request to the GitHub/GitLab API to create a new release when a new tag is created.
