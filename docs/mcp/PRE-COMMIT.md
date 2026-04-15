# Local Checks — overseerr-mcp

This repository does not currently ship a checked-in Git hook manager config such as `.pre-commit-config.yaml` or `lefthook.yml`.

## Run checks manually

```bash
uv sync --dev
just lint
just fmt
just typecheck
just test
```

## Additional targeted checks

```bash
bash scripts/check-docker-security.sh
bash scripts/check-no-baked-env.sh
bash scripts/ensure-ignore-files.sh --check .
just validate-skills
just check-contract
```
