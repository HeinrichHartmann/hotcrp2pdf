{
  description = "Pandoc + LaTeX + PDF tools for CFP book generation";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pkgs.pandoc
            pkgs.texlive.combined.scheme-medium  # Includes xelatex, pdflatex, etc.
            pkgs.poppler_utils                   # For pdfunite
            pkgs.pdftk                           # Optional: another PDF concat tool
          ];
          shellHook = ''
            echo "Pandoc, LaTeX, and PDF tools are ready!"
          '';
        };
      }
    );
}