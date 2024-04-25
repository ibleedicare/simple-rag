{
    description = "A php environment";
    inputs = {
        nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11";
        flake-utils.url = "github:numtide/flake-utils";
    };

    outputs = { self, nixpkgs, flake-utils, ... }:
        flake-utils.lib.eachDefaultSystem (system:
            let
                pkgs = import nixpkgs {
                    inherit system;
                };
            in
            {
                devShell = pkgs.mkShell {
                    buildInputs = with pkgs;[
                        python3
                        poetry
                    ];
                    LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";
                };
            }
        );

}

