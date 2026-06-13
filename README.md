<a name="top"></a>
<div align="center">

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:6b46c1,100:2b6cb0&height=120&section=header&text=PARTNERMAP&fontSize=48&fontColor=ffffff&fontAlignY=58" width="100%" alt="PARTNERMAP"/>

# PARTNERMAP

### Track partnership/channel agreements as YAML records and compute account overlap, co-sell coverage gaps, and renewal/expiry alerts.

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=18&duration=3500&pause=1000&color=6B46C1&center=true&vCenter=true&width=720&lines=Track+partnershipchannel+agreements+as+YAML+records+and+comp;Self-hostable+%C2%B7+MCP-native+%C2%B7+CI-ready+%C2%B7+polyglot" width="720"/>

[![PyPI](https://img.shields.io/pypi/v/cognis-partnermap.svg?color=6b46c1)](https://pypi.org/project/cognis-partnermap/) [![CI](https://github.com/cognis-digital/partnermap/actions/workflows/ci.yml/badge.svg)](https://github.com/cognis-digital/partnermap/actions) [![License: COCL 1.0](https://img.shields.io/badge/License-COCL%201.0-2b6cb0.svg)](LICENSE) [![Suite](https://img.shields.io/badge/Cognis-Neural%20Suite-6b46c1.svg)](https://github.com/cognis-digital)

*Part of the Cognis Neural Suite.*

</div>

```bash
pip install "git+https://github.com/cognis-digital/partnermap.git"
partnermap scan .            # → prioritized findings in seconds
```

<!-- cognis:layman:start -->
## What is this?

partnermap is a command-line tool that helps businesses track their partner and reseller agreements in simple text files. It reads those files and automatically finds which customers appear in more than one partner's account list — so you can spot conflicts or co-sell opportunities without sharing raw customer names with anyone. It also watches renewal and expiry dates and warns you when a contract is coming due or has already lapsed. It is aimed at sales operations, partnerships, and business development teams who want a lightweight, self-hosted alternative to expensive account-mapping platforms.
<!-- cognis:layman:end -->

## Contents

- [Why partnermap?](#why) · [Features](#features) · [Quick start](#quick-start) · [Example](#example) · [Architecture](#architecture) · [AI stack](#ai-stack) · [How it compares](#how-it-compares) · [Integrations](#integrations) · [Install anywhere](#install-anywhere) · [Related](#related) · [Contributing](#contributing)

<a name="why"></a>
## Why partnermap?

Account mapping without uploading your customer list to a third party — find partner overlap on your own infra and get CI-driven renewal-expiry warnings.

`partnermap` is single-purpose, scriptable, and self-hostable: point it at a target, get prioritized results in the format your workflow already speaks (table · JSON · SARIF), gate CI on it, and let agents drive it over MCP.

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="features"></a>
## Features

- ✅ Parse Yaml
- ✅ Account Token
- ✅ Load Partner File
- ✅ Load Partners
- ✅ Compute Overlaps
- ✅ Renewal Alerts
- ✅ Analyze
- ✅ Runs on Linux/macOS/Windows · Docker · devcontainer
- ✅ Ports in Python, JavaScript, Go, and Rust (`ports/`)

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="quick-start"></a>
<!-- cognis:domains:start -->
## Domains

**Primary domain:** Revenue & Business  ·  **JTF MERIDIAN division:** FOUNDRY · MASON

**Topics:** `cognis` `business` `saas` `revenue-ops`

Part of the **Cognis Neural Suite** — 300+ source-available tools organized across 12 domains under the JTF MERIDIAN command structure. See the [suite on GitHub](https://github.com/cognis-digital) and [jtf-meridian](https://github.com/cognis-digital/jtf-meridian) for how the pieces fit together.
<!-- cognis:domains:end -->

<!-- cognis:install:start -->
## Install

`partnermap` is source-available (not published to PyPI) — every method below installs
straight from GitHub. Pick whichever you prefer; the one-line scripts auto-detect
the best tool available on your machine.

**One-liner (Linux / macOS):**
```sh
curl -fsSL https://raw.githubusercontent.com/cognis-digital/partnermap/HEAD/install.sh | sh
```

**One-liner (Windows PowerShell):**
```powershell
irm https://raw.githubusercontent.com/cognis-digital/partnermap/HEAD/install.ps1 | iex
```

**Or install manually — any one of:**
```sh
pipx install "git+https://github.com/cognis-digital/partnermap.git"     # isolated (recommended)
uv tool install "git+https://github.com/cognis-digital/partnermap.git"  # uv
pip install "git+https://github.com/cognis-digital/partnermap.git"      # pip
```

**From source:**
```sh
git clone https://github.com/cognis-digital/partnermap.git
cd partnermap && pip install .
```

Then run:
```sh
partnermap --help
```
<!-- cognis:install:end -->

## Quick start

```bash
pip install "git+https://github.com/cognis-digital/partnermap.git"
partnermap --version
partnermap scan .                       # scan current project
partnermap scan . --format json         # machine-readable
partnermap scan . --fail-on high        # CI gate (non-zero exit)
```

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="example"></a>
## Example

```text
$ partnermap scan .
  [HIGH    ] PAR-001  example finding             (./src/app.py)
  [MEDIUM  ] PAR-002  another signal              (./config.yaml)

  2 findings · risk score 5 · 38ms
```

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="architecture"></a>
## Architecture

```mermaid
flowchart LR
  A[Input: file / dir / API] --> B[Collectors]
  B --> C[Rules / Analyzers]
  C --> D[Scorer]
  D --> E{Reporters}
  E --> F[Table]
  E --> G[JSON / SARIF]
  E --> H[MCP tool -. drives .-> AI agents]
```

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="ai-stack"></a>
## Use it from any AI stack

`partnermap` is interoperable with every popular way of using AI:

- **MCP server** — `partnermap mcp` (Claude Desktop, Cursor, Cognis.Studio, [uncensored-fleet](https://github.com/cognis-digital/uncensored-fleet))
- **OpenAI-compatible / JSON** — pipe `partnermap scan . --format json` into any agent or LLM
- **LangChain · CrewAI · AutoGen · LlamaIndex** — wrap the CLI/JSON as a tool in one line
- **CI / scripts** — exit codes + SARIF for non-AI pipelines

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="how-it-compares"></a>
## How it compares

| | **Cognis partnermap** | Crossbeam |
|---|:---:|:---:|
| Self-hostable, no account | ✅ | varies |
| Single command, zero config | ✅ | ⚠️ |
| JSON + SARIF for CI | ✅ | varies |
| MCP-native (AI agents) | ✅ | ❌ |
| Polyglot ports (JS/Go/Rust) | ✅ | ❌ |
| Open license | ✅ COCL | varies |

*Built in the spirit of **Crossbeam/Reveal account mapping, as a local CLI**, re-framed the Cognis way. Missing a credit? Open a PR.*

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="integrations"></a>
## Integrations

Pipes into your stack: **SARIF** for code-scanning, **JSON** for anything, an **MCP server** (`partnermap mcp`) for AI agents, and a webhook forwarder for SIEM/Slack/Jira. See [`docs/INTEGRATIONS.md`](docs/INTEGRATIONS.md).

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="install-anywhere"></a>
## Install — every way, every platform

```bash
pip install "git+https://github.com/cognis-digital/partnermap.git"    # pip (works today)
pipx install "git+https://github.com/cognis-digital/partnermap.git"   # isolated CLI
uv tool install "git+https://github.com/cognis-digital/partnermap.git" # uv
pip install cognis-partnermap                                          # PyPI (when published)
docker run --rm ghcr.io/cognis-digital/partnermap:latest --help        # Docker
brew install cognis-digital/tap/partnermap                             # Homebrew tap
curl -fsSL https://raw.githubusercontent.com/cognis-digital/partnermap/main/install.sh | sh
```

| Linux | macOS | Windows | Docker | Cloud |
|---|---|---|---|---|
| `scripts/setup-linux.sh` | `scripts/setup-macos.sh` | `scripts/setup-windows.ps1` | `docker run ghcr.io/cognis-digital/partnermap` | [DEPLOY.md](docs/DEPLOY.md) (AWS/Azure/GCP/k8s) |

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="related"></a>
## Related Cognis tools

- [`warmline`](https://github.com/cognis-digital/warmline) — Score and rank inbound/outbound leads from a YAML rulebook, emitting a ranked queue as JSON/CSV for your SDRs and CI gates.
- [`coldforge`](https://github.com/cognis-digital/coldforge) — Render personalized cold-outreach sequences from Markdown templates + a contacts CSV, with spam-score linting and per-send dry-run preview.
- [`pactgen`](https://github.com/cognis-digital/pactgen) — Generate branded sales proposals and SOWs from a YAML scope file + pricing table into PDF/HTML, with a deterministic line-item math check.
- [`crmsync`](https://github.com/cognis-digital/crmsync) — Bidirectional, idempotent sync of contacts/deals between a local SQLite source-of-truth and CRM APIs (HubSpot/Pipedrive/Salesforce) via one config.
- [`dripcheck`](https://github.com/cognis-digital/dripcheck) — Lint email sequences and drip campaigns for deliverability: SPF/DKIM/DMARC, link health, unsubscribe presence, and CAN-SPAM/GDPR compliance.
- [`dealflow`](https://github.com/cognis-digital/dealflow) — Model your sales pipeline as a YAML state machine and compute conversion rates, stage velocity, and weighted forecast straight from CRM exports.

**Explore the suite →** [🗂️ all 170+ tools](https://github.com/cognis-digital/cognis-neural-suite) · [⭐ awesome-cognis](https://github.com/cognis-digital/awesome-cognis) · [🔗 cognis-sources](https://github.com/cognis-digital/cognis-sources) · [🤖 uncensored-fleet](https://github.com/cognis-digital/uncensored-fleet) · [🧠 engram](https://github.com/cognis-digital/engram)

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="contributing"></a>
## Contributing

PRs, new rules, and demo scenarios are welcome under the collaboration-pull model — see [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

> ### ⭐ If `partnermap` saved you time, **star it** — it genuinely helps others find it.

## License

Source-available under the **Cognis Open Collaboration License (COCL) v1.0** — free for personal, internal-evaluation, research, and educational use; **commercial / production use requires a license** (licensing@cognis.digital). See [LICENSE](LICENSE).

---

<div align="center"><sub><b><a href="https://cognis.digital">Cognis Digital</a></b> · one of 170+ tools in the <a href="https://github.com/cognis-digital/cognis-neural-suite">Cognis Neural Suite</a> · <i>Making Tomorrow Better Today</i></sub></div>
