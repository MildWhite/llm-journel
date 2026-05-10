# llm-journel

## 2026-05-10 - Claw + Ollama + Google Calendar debugging

Quick log of what we found today:

- Built and tested a Google Calendar workflow that can create events from command line Python.
- Confirmed commands run locally through the CLI toolchain, not in a remote VM.
- Found the core Windows bug in Claw runtime: bash execution used `sh -lc` with no Windows fallback.
- Patched Claw runtime to use `cmd /c` on Windows and kept `sh -lc` for non-Windows.
- Rebuilt Claw and installed binary to `C:\Users\Milo\.cargo\bin\claw.exe`.
- Verified local model routing works with Ollama using `openai/qwen3.6:latest`.
- Added a PowerShell `claw` wrapper so you can run just `claw` with default Ollama model and without extra flags.

Issues we hit:

- GitHub push protection blocked commit because OAuth secrets were embedded.
- Removed embedded credentials and switched to environment variable-based auth.
- Minor quoting edge case remains for some spaced arguments when commands are generated in certain shell formats.

Current setup status:

- `claw` command works from PowerShell.
- Defaults to local Ollama endpoint and model.
- Wrapper restores previous env values after each run to avoid breaking other tools.
