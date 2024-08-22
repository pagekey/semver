### SED File Replacer

The SED File Replacer is unlike the others in that it executes the `sed` program to perform a very flexible replace on any file. This is helpful when you have references to versions buried somewhere that is not easily parsed and changed by the other tools.

#### Example 1: README Replacement

If you specify the following in your `.semver` config file:

```yaml
file_replacers:
  - type: sed
    name: README.md
    script: s/^This/This is version %M.%m.%p of the project./g
```

Given the following contents for `README.md`:

```md
# Some Project

This is version 0.0.0 of the project.
```

When creating `v1.0.0`, the PageKey Semver will replace the `package.json` with the following:

```md
# Some Project

This is version 1.0.0 of the project.
```
