# clawmain

Claude Code plugin marketplace by [vishnu-77](https://github.com/vishnu-77).

```
/plugin marketplace add vishnu-77/clawmain
```

## Plugins

| Plugin | Description |
|---|---|
| [groundwork](plugins/groundwork) | Guided Claude Code setup: verified AGENTS.md, CLAUDE.md and skills, with a short "why" lesson on every choice. |

## Development

```
claude plugin validate .
python -m unittest discover -s tests
```

Local test without publishing:

```
/plugin marketplace add "D:/2025 JOB/bootclaw"
/plugin install groundwork@clawmain
```
