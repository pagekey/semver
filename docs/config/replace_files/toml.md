# TOML Replace File

If you specify a TOML Replace File, it will parse the TOML file specified and replace the key with the new version. Nested keys are supported using `.`.

## Example 1: Cargo.toml

If you specify the following in your `.semver` config file:

```yaml
replace_files:
  - type: toml
    name: Cargo.toml
    key: version
```

Given the following contents for `Cargo.toml`:

```toml
name = "my package"
version = "v0.0.0"
```

When creating `v1.0.0`, the PageKey Semver will replace the `Cargo.toml` with the following:

```toml
name = "my package"
version = "v1.0.0"
```

Note that the value will always be replaced with the `format` you specified in the config, regardless of the previous value.

## Example 2: Nested Keys

If you specify the following in your `.semver` config file:

```yaml
replace_files:
  - type: toml
    name: Cargo.toml
    key: project.metadata.version
```

Given the following contents for `Cargo.toml`:

```toml
name = "my package"

[project.metadata]
version = "v0.0.0"
```

When creating `v1.0.0`, the PageKey Semver will replace the `package.json` with the following:

```toml
name = "my package"

[project.metadata]
version = "v1.0.0"
```

Note that the value will always be replaced with the `format` you specified in the config, regardless of the previous value.
