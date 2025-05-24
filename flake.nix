{
  description = "Convert HotCRP talk submissions to PDF document";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        
        hotcrp2pdf = pkgs.python3Packages.buildPythonApplication rec {
          pname = "hotcrp2pdf";
          version = "0.1.0";
          
          src = ./.;
          
          propagatedBuildInputs = with pkgs.python3Packages; [
            click
            jinja2
            dataclasses-json
          ];
          
          nativeCheckInputs = with pkgs; [
            pandoc
            texlive.combined.scheme-medium
          ];
          
          # Wrap the executable to include pandoc and xelatex in PATH
          postInstall = ''
            wrapProgram $out/bin/hotcrp2pdf \
              --prefix PATH : ${pkgs.lib.makeBinPath [ 
                pkgs.pandoc 
                pkgs.texlive.combined.scheme-medium 
              ]}
          '';
          
          meta = with pkgs.lib; {
            description = "Convert HotCRP talk submissions to PDF document";
            homepage = "https://github.com/your-username/hotcrp2pdf";
            license = licenses.mit;
            maintainers = [ ];
          };
        };
        
      in {
        packages.default = hotcrp2pdf;
        packages.hotcrp2pdf = hotcrp2pdf;
        
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pkgs.pandoc
            pkgs.texlive.combined.scheme-medium  # Includes xelatex, pdflatex, etc.
            pkgs.poppler_utils                   # For pdfunite
            pkgs.pdftk                           # Optional: another PDF concat tool
            pkgs.python3
            pkgs.python3Packages.pip
            pkgs.python3Packages.click
            pkgs.python3Packages.jinja2
            pkgs.python3Packages.dataclasses-json
          ];
          shellHook = ''
            echo "Pandoc, LaTeX, and PDF tools are ready!"
            echo "Run 'pip install -e .' to install hotcrp2pdf in development mode"
          '';
        };
        
        apps.default = flake-utils.lib.mkApp {
          drv = hotcrp2pdf;
          name = "hotcrp2pdf";
        };
      }
    );
}