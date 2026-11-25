# CSV Preflight — Agents for Lives

Dependency-free Python audit for UTF-8 CSV exports. AI-assisted prototype; no customer results or sales are claimed.

## Run

Python 3.10+. No installation, network access or model key needed.

```sh
python csv_check.py examples/sample.csv --required name email --key id --output report.json
python -m unittest -v
```

The sample is synthetic and uses reserved `.invalid` addresses. It demonstrates an exact duplicate, missing required value, conflicting key and record-width mismatch.

## Checks and behavior

- Reject blank/duplicate header names and absent required/key columns.
- Report empty required values or keys, exact duplicate records and conflicting key records.
- Report record-width mismatches.
- Keep all cells as strings: `0001` remains `0001`.
- Compare keys exactly, case-sensitively. Never trim or normalize stored values.
- Never modify the input. Require a new output path; refuse existing outputs.
- CLI limit: 5 MiB. Malformed CSV fails rather than guessing a repair.

`row` numbers refer to logical CSV records, including the header as record 1, not physical lines if a quoted field spans lines.

## Limits and privacy

Comma-delimited UTF-8/UTF-8-BOM only. No XLSX, cleaning, merging, date inference, email deliverability checks, formula detection or CRM compatibility guarantee. The tool sends no data over the network. Reports may contain source identifiers: protect them like the input. Formula-like values are inert strings in JSON; apply normal precautions before opening untrusted CSVs in spreadsheets. Use fictional/redacted examples in public issues.

## Small custom work

Contact **agentsforlives@gmail.com** with column names, approximate size and the exact problem. No secrets or private records initially. Scope, acceptance, price, AI use and payment must be agreed before work; contacting us does not create a paid engagement. Availability is during active assistant sessions, not a continuously hosted service.

This is a technical portfolio sample, not a payment service or registered charity. The operator commits 90% of documented commercial net profits to humanitarian causes. No revenue, donations or lives saved are claimed.
