# Create Release Integration

This config option allows you to create a release in your Git hosting platform on tag.

## GitHub

To create a GitHub release on tags, define the following in your `.semver` file:

```yaml
integrations:
  github:
    create_release:
      project: "pagekey/semver"
      token_variable: "SEMVER_TOKEN"
      title_format: "v%M.%m.%p"
      body: "Auto-generated release."
```

Variables:

- Replace `project` with the path to your project repo.
- Make sure that `token_variable` contains the name of the environment variable that will be used to push (this should be a personal access token with write permission on the target repository).
- Fill out `title_format` with the desired format. Note that `%M` will be replaced with the major version number, `%m` with the minor, and `%p` with the patch.
- Fill out a body for the release. Templates are not yet supported for this field.


## GitLab

To create a GitLab release on tags, define the following in your `.semver` file:

```yaml
integrations:
  gitlab:
    create_release:
      project: "60867298"
      token_variable: "GITLAB_TOKEN"
      title_format: "v%M.%m.%p"
      body: "Auto-generated release."
```


Variables:

- Replace the value for `project` with your project ID. You can find this in GitLab by going to the web url for your repo, click the three dots on the right, and hitting "Copy Project ID."
  - Note: In the future, it may make sense to use `$CI_PROJECT_ID` for this so that you don't have to fill it in automatically. If you're interested in this feature, let me know by writing an issue or finding the relevant issue and commenting on it.
- Make sure that `token_variable` contains the name of the environment variable that will be used to push (this should be a personal access token with write permission on the target repository).
- Fill out `title_format` with the desired format. Note that `%M` will be replaced with the major version number, `%m` with the minor, and `%p` with the patch.
- Fill out a body for the release. Templates are not yet supported for this field.

An alternative to using this integration is to simply create the release on tags, because GitLab does not prevent you from running pipelines based on bot pushes. To do so, add the following to your `.gitlab-ci.yml`:

```yaml
release_job:
  stage: version
  image: registry.gitlab.com/gitlab-org/release-cli:latest
  rules:
    - if: $CI_COMMIT_TAG                 # Run this job when a tag is created
  script:
    - echo "running release_job"
  release:                               # See https://docs.gitlab.com/ee/ci/yaml/#release for available properties
    tag_name: '$CI_COMMIT_TAG'
    description: '$CI_COMMIT_TAG'
```

The above snippet is from the [GitLab docs](https://docs.gitlab.com/ee/user/project/releases/release_cicd_examples.html#create-a-release-when-a-git-tag-is-created).
