{ pkgs, lib, config, inputs, ... }:

{
  packages = with pkgs; [
    git # Source code versioning
    zellij # A better tmux (terminal multiplexer)
    atuin # Command history, to use it with fish, follow this: https://docs.atuin.sh/guide/installation/#installing-the-shell-plugin
    helix # A modal editor, similar to vim but different
    fish # A better shell than bash
    toybox # Unix command line utilities like which, clear
    less # file pager
    curl # Transferring files
    ripgrep # A better grep
    postgresql_16 # Database system
    # python configured below
  ];

  languages.python = {
    enable = true;
    version = "3.12.4";
    venv.enable = true;
  };

  services.postgres = {
    enable = true;
    initialDatabases = [
      { name = "beanserver"; }
    ];
  };


  enterShell = ''
  pip install -r requirements/local.txt
  pre-commit install
  '';
}
