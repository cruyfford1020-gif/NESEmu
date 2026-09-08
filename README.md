# PS1 BIN Builder for iPhone / Codespaces

This repository is prepared to rebuild PlayStation 1 disc images using `mkpsxiso` inside GitHub Codespaces.

## Workflow

1. Open this repository in GitHub Codespaces from Safari on iPhone.
2. Upload your original PS1 BIN/CUE or extracted game files into the `input/` folder.
3. Run:

```bash
./setup.sh
```

For an original BIN/CUE, first dump it while preserving layout/LBA:

```bash
./dump-original.sh input/game.cue
```

This creates extracted files and an XML layout under `work/`.

After replacing your modified files, rebuild with:

```bash
./build-bin.sh work/layout.xml output/game.bin
```

The resulting BIN/CUE will be in `output/`.

> Keep the original XML layout when rebuilding a modified game so file order and sector placement are preserved as closely as possible.
