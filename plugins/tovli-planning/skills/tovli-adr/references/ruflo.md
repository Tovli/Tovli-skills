# Ruflo and Claude Flow integration

## Check availability and choose a backend

First discover connected Ruflo or Claude Flow MCP memory tools. Clients may expose them as `mcp__ruflo__…`, `mcp__claude-flow__…`, or `mcp__plugin_ruflo-core_ruflo__…`. Match the operation by its advertised schema. Some clients render hyphens as underscores. An MCP connection configured for the target project's memory is sufficient by itself.

If you need a CLI fallback, run [the preflight script](../scripts/ruflo_preflight.py) from the target repository root with Python 3.10 or later. Use the absolute path to the installed skill's script:

```sh
python "/path/to/tovli-adr/scripts/ruflo_preflight.py"
```

The script returns JSON with the resolved project root and the available CLI launchers, ordered with project-local executables first. An empty `candidates` list means the script found neither CLI in the project's `node_modules/.bin` or on `PATH`. The probe only inspects the filesystem and never runs Ruflo or fetches packages. Check any additional installed launcher documented by the target project. If Python is unavailable, check with `Get-Command -Name ruflo,claude-flow -ErrorAction SilentlyContinue` in PowerShell or `command -v` for both names in a POSIX shell, and inspect `node_modules/.bin`.

Reuse the last completed CLI probe, including an empty result, for later activations in the same conversation, project root, and shell environment. Run a fresh probe when the previous result is missing from context, setup or `PATH` changes, the user asks to recheck, or a cached launcher fails to start. Check MCP availability against the current tool list and verify the selected store independently of the CLI probe.

If neither route is found, use the skill's warning. If a connection is found but its project cannot be verified, report the configuration issue and continue locally unless a CLI can reach the project store.

Use the selected launcher in place of `ruflo` in the examples below. Inspect `mcp tools` and `mcp exec --help` when capabilities differ. Confirm the CLI resolves to the project's store. If it defaults to a user-wide store, select the project's database with a process-local `CLAUDE_FLOW_DB_PATH` override, or pass `--path` to supported `memory` commands. The unqualified ADR IDs assume project-local storage.

The CLI can call the same MCP operations by their unprefixed names. Pass the parameters as a single serialized JSON argument. For example, in a POSIX shell:

```sh
ruflo mcp exec --tool memory_search --params '{"namespace":"adr-patterns","query":"PostgreSQL for persistence","limit":10}' --format json
```

For PowerShell 7.3 or later, build the argument with `ConvertTo-Json`:

```powershell
$adrParams = @{ namespace = 'adr-patterns'; query = 'PostgreSQL for persistence'; limit = 10 } | ConvertTo-Json -Compress
ruflo mcp exec --tool memory_search --params $adrParams --format json
```

Inspect the returned tool result, including the nested `result` in CLI JSON. An exit code of zero can accompany a tool-level failure. A write marked `durable: false` remains pending. Verify writes through the same route when native CLI memory commands and MCP use different database files.

## Search and register

Use the actual ADR ID in place of `ADR-NNN`. Use project-relative paths with forward slashes in the metadata.

| Stage | Tool | Parameters |
| --- | --- | --- |
| Find candidates before indexing | `memory_search` | `namespace: "adr-patterns"`, `query`: decision title and a short context summary, `limit: 10` |
| Register the saved ADR | `agentdb_hierarchical-store` | `key: "mem:ADR-NNN"`, `tier: "semantic"`, `value`: a JSON-encoded **string** with `id`, `title`, `status`, `date`, and `file` |
| Record each verified dependency | `agentdb_causal-edge` | `sourceId: "mem:ADR-NNN"`, `targetId: "mem:ADR-RELATED"` using the older ADR's actual ID, `relation: "depends-on"` |
| Index for future searches | `memory_store` | `namespace: "adr-patterns"`, `key: "ADR-NNN"`, `value`: title and a concise context summary drawn from the saved ADR, `upsert: false` when supported |

For hierarchical storage, the outer parameters are an object and the embedded metadata is a string:

```json
{
  "key": "mem:ADR-003",
  "tier": "semantic",
  "value": "{\"id\":\"ADR-003\",\"title\":\"Use PostgreSQL for persistence\",\"status\":\"proposed\",\"date\":\"2026-11-25\",\"file\":\"docs/adr/ADR-003-use-postgresql-for-persistence.md\"}"
}
```

Use the metadata key even if the store returns an internal record ID. Store the hierarchy record before creating outgoing edges. Check for an occupied key if the ADR ID is being reused or the local and stored records disagree. Report a conflicting key and preserve its existing value. For the search index, send a short summary of the decision context.

If only the CLI memory commands are available, use `ruflo memory search --namespace adr-patterns --query <query>` and `ruflo memory store --namespace adr-patterns --key <ADR-ID> --value <summary>` with `--no-upsert` when supported. Check their help for the installed version's syntax and pass each argument as data. Report hierarchical registration as pending when its tool is unavailable.

If a graph write fails or the backend cannot confirm the edge after a CLI call, persist the verified relationship with `memory_store` or `memory store` in the `adr-edges` namespace. Use a stable key such as `depends-on:ADR-003:ADR-001` and a JSON string such as `{"from":"ADR-003","to":"ADR-001","relation":"depends-on"}`. Use the actual ADR IDs without the graph's `mem:` prefix. Check that the indexed edge can be retrieved by namespace and key, and report the graph registration as pending until verified.

## Resume a partial registration

Read the existing Markdown and work from its ID. Check the exact key and value in the semantic tier using `agentdb_hierarchical-list` when available, or inspect exact-key matches returned by the server's recall tool. Use `memory_retrieve` with namespace `adr-patterns` and the ADR ID to check the search entry. Use `agentdb_graph-query` if it can verify the source, target, and relation on the active backend. An untyped neighbor alone cannot confirm a dependency. Resume confirmed missing work and leave ambiguous writes pending if they cannot be reconciled.
