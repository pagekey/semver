import os

from pagekey_semver.main import cli_entrypoint


def test_add_tag_with_existing_project_works(tmp_path):
    # Arrange.
    # Create a temporary directory representing a project
    tmp_dir = tmp_path / "project"
    tmp_dir.mkdir()
    assert tmp_dir.is_dir()
    # Set up git in that project
    os.chdir(tmp_dir)
    os.system("git init")
    os.system("touch Cargo.toml")
    os.system("git add --all")
    os.system("git commit -m 'Initial commit'")
    os.system("touch package.json")
    os.system("git add package.json")
    os.system("git commit -m 'fix: Add package.json'")

    # Act.
    # Invoke semver
    cli_entrypoint()

    # Assert.
    breakpoint()
