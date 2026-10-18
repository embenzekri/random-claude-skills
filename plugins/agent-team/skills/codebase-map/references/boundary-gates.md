# Boundary check: dependency rules as a CI gate

Source of the rule: `team-lead` rule 8, "Rules become gates". `docs/architecture/dependency-rules.md`
is the human statement; one of these configs is its machine form. Both live in the repo and are
changed together. Write the config, run it on current main, record existing violations in an
allowlist (one ticket each), and make CI fail only on NEW violations.

## TypeScript / JavaScript: dependency-cruiser

Install in the target repo: `npm i -D dependency-cruiser`. Create `.dependency-cruiser.cjs`:

```js
module.exports = {
  forbidden: [
    { name: "no-ui-to-db", severity: "error",
      from: { path: "^packages/ui" }, to: { path: "^packages/db" } },
    { name: "no-cross-area-internals", severity: "error",
      from: { path: "^packages/([^/]+)/" },
      to: { path: "^packages/(?!\\1)[^/]+/src/(?!index)" } },   // only another area's public index
    { name: "no-circular", severity: "error", from: {}, to: { circular: true } },
  ],
  options: { doNotFollow: { path: "node_modules" }, tsConfig: { fileName: "tsconfig.json" } },
};
```

Run: `cd /ABS/REPO && npx depcruise packages --config /ABS/REPO/.dependency-cruiser.cjs`
Baseline of known violations: `npx depcruise packages --config /ABS/REPO/.dependency-cruiser.cjs --output-type baseline > /ABS/REPO/.dependency-cruiser-known-violations.json`
then add `--ignore-known /ABS/REPO/.dependency-cruiser-known-violations.json` to the CI command.

## Python: import-linter

Install: `pip install import-linter`. Create `.importlinter` at the repo root:

```ini
[importlinter]
root_packages =
    app_billing
    app_orders
    app_shared

[importlinter:contract:layers]
name = areas depend only downwards
type = layers
layers =
    app_orders
    app_billing
    app_shared

[importlinter:contract:no-internals]
name = billing internals are private
type = forbidden
source_modules = app_orders
forbidden_modules = app_billing.internal
```

Run: `cd /ABS/REPO && lint-imports`. Known violations: `ignore_imports` in the contract, each with
a comment naming its ticket.

## Other stacks

Go: `go list -deps` plus `depguard` (golangci-lint). Java/Kotlin: ArchUnit tests. Rust: workspace
crate graph via `cargo deny`/`cargo-modules`. Anything: a 20-line script that greps import paths
per area against the forbidden list in `dependency-rules.md` is acceptable if no tool fits.

## CI wiring

Add one job step: run the checker plus `sh /ABS/REPO/scripts/check-context-caps.sh`. Mutation-check
the gate once: add a forbidden import, confirm CI goes red, remove it (same discipline as
`verify-against-reality`). If the gate cannot be added now, put it in the retro as a ticket;
the rules file alone is not a gate.
