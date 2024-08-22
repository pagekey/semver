# YAML File Replacer

If you specify a YAML File Replacer, it will parse the YAML file specified and replace the key with the new version. Nested keys are supported using `.`.

## Example 1: package.yaml

If you specify the following in your `.semver` config file:

```yaml
file_replacers:
  - type: yaml
    name: package.yaml
    key: version
    format: "v%M.%m.%p"
```

Given the following contents for `package.yaml`:

```yaml
name: "my package"
version: "v0.0.0"
```

When creating `v1.0.0`, the PageKey Semver will replace the `package.json` with the following:

```yaml
name: "my package"
version: "v1.0.0"
```

Note that the value will always be replaced with the `format` you specified in the config, regardless of the previous value.

## Example 2: Nested Keys

If you specify the following in your `.semver` config file:

```yaml
file_replacers:
  - type: json
    name: package.json
    key: project.metadata.version
    format: "v%M.%m.%p"
```

Given the following contents for `package.yaml`:

```yaml
name: "my package"
project:
  metadata:
    version: "v0.0.0"
```

When creating `v1.0.0`, the PageKey Semver will replace the `package.yaml` with the following:

```yaml
name: "my package"
project:
  metadata:
    version: "v1.0.0"
```

Note that the value will always be replaced with the `format` you specified in the config, regardless of the previous value.
