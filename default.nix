{ lib,
  setuptools,
  construct,
  buildPythonPackage
}:
buildPythonPackage {
  pname = "gmosh";
  version = "v2.2.1";
  format = "pyproject";

  src = lib.cleanSourceWith rec {
      src = ./.;
      name = "gmosh-src";
      filter = let
        whitelist = [
          "src(/gmosh(/.*\.py)?)?"
          "ui(/.*\.ui)?"
          "pyproject\.toml"
          "LICENSE\.txt"
        ];
        in path: type:
          let
          relativePath = lib.removePrefix (toString src + "/") path;
          in builtins.any (r: builtins.match r relativePath != null) whitelist;
  };
  doCheck = false;

  nativeBuildInputs = [
    setuptools
  ];

  propagatedBuildInputs = [
    construct
  ];

  meta = with lib; {
    homepage = "https://github.com/FPtje/gmosh";
    description = "Garry's mod workshop CLI tool and small UI";
    license = licenses.mit;
  };
}
