# ClickHouse for Flow Steward

Connect ClickHouse to Flow Steward for analytical lookups, reusable Dataset queries and workflow-driven table changes. The Dataset connector tests the connection, inspects typed table schemas, checks saved SQL against selected resources, previews results, executes saved queries and infers their output schema. Use analytical results to drive later workflow steps, compare records or retrieve reporting data while keeping Dataset queries read-only.

A separate workflow action executes one INSERT, UPDATE or DELETE using named parameters and an optional parameter schema. This provides a way to store workflow results or change existing data when the ClickHouse server supports the supplied SQL syntax. Parameter values are supplied separately from the statement, allowing the same workflow to reuse SQL with different inputs.

Configure the server host, HTTP(S) port, database and user, with any required password in connection secrets. HTTPS verifies the server certificate; native TCP is not supported. Read results are limited to 100 rows and 480 KiB, and SQL support is a restricted subset. The connector does not translate unsupported mutation syntax, administer schemas or provide database triggers.

## Runtime and operation requirements

Connect **ClickHouse** datasets and run parameterized workflow writes. This repository contains one installable ClickHouse extension, version **1.3.5**, with separate Linux AMD64 and ARM64 archives. No other database can be selected or installed from this package.

## Set up a ClickHouse connection

Create a project connection using these settings:

| Setting | Meaning |
| --- | --- |
| `host` | ClickHouse host. Required. |
| `port` | ClickHouse port. Required. |
| `database` | ClickHouse database. Required. |
| `user` | ClickHouse user. Required. |
| `protocol` | HTTPS is the pinned driver default. Native TCP protocol is not supported by this prebuilt. Optional. |

Store the ClickHouse user password in the connection secrets. Resolved dataset secret environment values are forwarded to the native process; direct environment overrides retain their established precedence. Dataset advanced environment exposes only the named CLICKHOUSE_ source variables; password overrides remain in secrets. Writer connections use the explicit settings above.

Select `https` (the pinned driver default) or `http` using `protocol`. The shipped prebuilt does not expose native TCP or a `secure` switch; HTTPS verifies the server certificate. Supply the appropriate HTTP(S) port for your server.

## Read datasets and write from workflows

Datasets support connection testing, typed schema introspection, saved SQL, visual-query resource scope validation, bounded previews and execution. Read queries use the native read-only path and are capped at 100 rows and 480 KiB inline output. No trigger surface is exposed.

`execute_write` runs one INSERT, UPDATE or DELETE on the selected ClickHouse project connection. Provide `connection_ref`, SQL with named `:parameters`, a `params` object and optional JSON `param_schema`. Values stay separate from SQL and use native driver binding. The server must support the supplied SQL syntax.

The host resolves matching project configuration and secrets, account/project scope, execution context and a durable external-effect claim. Test mode suppresses writes before a driver starts. Writes execute once; uncertain dispatched failures return `retryable: false` and require checking the database before a manual retry. Workflow writes do not make dataset queries writable.

The bounded SQL subset refuses raw dollar characters and backslashes in read SQL; write SQL also refuses raw dollar characters. Put those values in bound parameters. A top-level read LIMIT accepts one integer literal with an optional integer OFFSET. The existing SQL safety guards and database-specific settings validation remain in force.

## Upgrade compatibility

The visible name is ClickHouse. The legacy extension ID `flowsteward.data-connector-mcp-toolbox-clickhouse`, project connection type `toolbox_sql_writer`, dataset connector IDs and action IDs remain unchanged so existing installations and workflows can upgrade. These are internal compatibility identifiers, not a second database selector.

## Technical implementation and packaging

Google MCP Toolbox is implementation tooling, pinned to tag `v1.16.0`, commit `06ea49d9a487a72c22419b5a8d5c22c11f0d7485`. Its fixed native build registers only this repository's ClickHouse interfaces. Installation and runtime download no drivers. Native binaries are rebuilt for this release.

To package the existing verified binaries:

```sh
python3 scripts/package_extension.py --runtime-target linux-amd64
python3 scripts/package_extension.py --runtime-target linux-arm64
```

`scripts/build_toolbox.sh` is the optional pinned implementation rebuild; it cannot select another database. `toolbox-provenance.json`, `THIRD_PARTY.yml` and root `SHA256SUMS` describe the native payloads. Each installer ZIP contains exactly one executable for its target and target/native metadata. The byte-exact Apache-2.0 license is in `LICENSE`; implementation notices are in `NOTICE`.

## Verification limits

Manifest isolation checks cover friendly names, database-specific fields, credential separation and the exact shipped SQL profiles. Contract tests cover scope/ref checks, parameter separation, test-mode suppression, output bounds and unknown write outcomes. No live ClickHouse credentials were supplied; compile and contract evidence does not establish a successful authenticated database connection.

Native payloads are rebuilt with pinned Go 1.27.4 and the reviewed module security baseline. Per-target toolchain, linked modules, size and SHA-256 are recorded in `toolbox-provenance.json`; static packaged checks reject stale native dependencies.

The native build freezes the previously approved prebuilt YAML from Toolbox v1.3.0
using `0003-approved-prebuilt-profiles.patch`; the implementation source and recorded
version remain Toolbox v1.16.0. Unused source, tool, prompt and resource registrations
are removed. Managed stdio launches use `--disable-version-check`.

The pinned Go 1.27.3 image supplies only the bootstrap operating environment.
Before any Go command, the build installs the checksum-verified official Go
1.27.4 SDK recorded in `scripts/go-toolchain-sources.json`; provenance records
the installer, selected SDK, and actual compiler embedded in each payload.
