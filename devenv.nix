{ pkgs, lib, config, inputs, ... }:

{
  packages = with pkgs; [
    # Python configured below
  ];

  languages.python = {
    enable = true;
    version = "3.12.4";
    venv.enable = true;
    venv.requirements = requirements/py-requirements.txt;
   };

  services.postgres = {
    enable = true;
    package = pkgs.postgresql_16;
    initialDatabases = [
      { name = "beanserver"; }
    ];
  };

  pre-commit.default_stages = [
    "pre-commit" "pre-push"
  ];
  pre-commit.excludes = [
    "docs/"
    "/migrations/"
    "devcontainer.json"
  ];
  pre-commit.hooks = {
    trim-trailing-whitespace.enable = true;
    end-of-file-fixer.enable = true;
    check-json.enable = true;
    check-toml.enable = true;
    check-xml.enable = true;
    check-yaml.enable = true;
    python-debug-statements.enable = true;
    check-builtin-literals.enable = true;
    check-case-conflicts.enable = true;
    check-docstring-first.enable = true;
    detect-private-keys.enable = true;
    commitizen.enable = true;
  };
  pre-commit.hooks.django-upgrade = {
    # https://github.com/adamchainz/django-upgrade
    enable = true;
    name = "django-upgrade";
    description = "Automatically upgrade your Django project code";
    entry = "django-upgrade --target-version 5.0";
    language = "python";
    types = ["python"];
  };

  pre-commit.hooks.ruff-lint = {
    # https://github.com/astral-sh/ruff-pre-commit
    enable = true;
    name = "ruff-lint";
    description = "Ruff Linter (for python code)";
    entry = "ruff check --force-exclude --fix --exit-non-zero-on-fix";
    language = "python";
    types_or = ["python" "pyi" "jupyter"];
    require_serial = true;
  };

  pre-commit.hooks.ruff-format = {
    # https://github.com/astral-sh/ruff-pre-commit
    enable = true;
    name = "ruff-format";
    description = "Ruff Formatter (for python code)";
    entry = "ruff format --force-exclude";
    language = "python";
    types_or = ["python" "pyi" "jupyter"];
    require_serial = true;
  };

  pre-commit.hooks.djlint-reformat-django = {
    # https://github.com/djlint/djLint
    enable = true;
    name = "djlint-reformat-django";
    description = "djLint formatting for Django";
    entry = "djlint --reformat --profile=django";
    language = "python";
    types_or = ["html"];
  };

  pre-commit.hooks.djlint-django = {
    # https://github.com/djlint/djLint
    enable = true;
    name = "djlint-django";
    description = "djLint linting for Django";
    entry = "djlint --profile=django";
    language = "python";
    types_or = ["html"];
  };

}
