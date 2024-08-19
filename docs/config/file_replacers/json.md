# JSON Replace File

If you specify a JSON Replace File, it will parse the JSON file specified and replace the key with the new version. Nested keys are supported using `.`.

## Example 1: package.json

If you specify the following in your `.semver` config file:

```yaml
replace_files:
  - type: json
    name: package.json
    key: version
    format: "v%M.%m.%p"
```

Given the following contents for `package.json`:

```json
{
  "name": "my package",
  "version": "v0.0.0"
}
```

When creating `v1.0.0`, the PageKey Semver will replace the `package.json` with the following:

```json
{
  "name": "my_package",
  "version": "v1.0.0"
}
```

Note that the value will always be replaced with the `format` you specified in the config, regardless of the previous value.

## Example 2: Nested Keys

If you specify the following in your `.semver` config file:

```yaml
replace_files:
  - type: json
    name: package.json
    key: project.metadata.version
    format: "v%M.%m.%p"
```

Given the following contents for `package.json`:

```json
{
  "name": "my package",
  "project": {
    "metadata": {
        "version": "v0.0.0"
    }
  }
}
```

When creating `v1.0.0`, the PageKey Semver will replace the `package.json` with the following:

```json
{
  "name": "my package",
  "project": {
    "metadata": {
        "version": "v1.0.0"
    }
  }
}
```

Note that the value will always be replaced with the `format` you specified in the config, regardless of the previous value.
