# JSON Replace File

If you specify a JSON Replace File, it will parse the JSON file specified and replace the key with the new version. Nested keys are supported using `.`.

## Example 1: package.json

Given the following file:

```json
{
  "name": "my package",
  "version": "v0.0.0"
}
```

If you specify the following:

```yaml
replace_files:
  - type: json
    name: package.json
    key: version
```

When creating `v1.0.0`, the package will replace the file with the following:

```json
{
  "name": "my_package",
  "version": "v1.0.0"
}
```

Note that the value will always be replaced with the `format` you specified in the config, regardless of the previous value.

## Example 2: Nested Keys

TODO
