{ src ? ./cli }:
{ pkgs, fastlint }:
let
  pythonPkgs = pkgs.python311Packages;

  # pyfastlint inputs pulled from pipfile
  pydepsFromPipfile = setupPy: pipfile: type:
    let
      pipfileLockInputs'' = with builtins;
        (attrNames ((fromJSON (readFile (pipfile))).${type}));
      # remove fastlint from the lockfile inputs
      pipfileLockInputs' = pkgs.lib.lists.remove "fastlint" pipfileLockInputs'';

      setupPyFile = (builtins.readFile setupPy);
      # check if the package is in the setup.py before adding it to the list
      isInSetupPy = name: (builtins.match ".*${name}.*" setupPyFile) != null;
      pipfileLockInputs = builtins.filter isInSetupPy pipfileLockInputs';
      # replace . with -
    in builtins.map (name: builtins.replaceStrings [ "." ] [ "-" ] name)
    pipfileLockInputs;

  pipfile = src + "/Pipfile.lock";
  setupPy = src + "/setup.py";
  pythonInputs = builtins.map (name: pythonPkgs.${name})
    (pydepsFromPipfile setupPy pipfile "default");

  # TODO get working
  # devPythonInputs = builtins.map (name: pythonPkgs.${name})
  #  ((pydepsFromPipfile pipfile "develop"));

  devPkgs = [ pkgs.pipenv ];

  pyfastlint = pythonPkgs.buildPythonApplication {
    # thanks to @06kellyjac
    pname = "pyfastlint";
    inherit (fastlint) version;
    inherit src;

    propagatedBuildInputs = pythonInputs ++ [ fastlint ];
    # Stops weird long step when entering shell
    dontUseSetuptoolsShellHook = true;
  };
in {
  pkg = pyfastlint;
  devEnv = { };
  inherit devPkgs;
}
