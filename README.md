<div align="center">
  <img src="sharepointfrappe/public/images/logo_bockhoff.png" alt="Bockhoff Technologies" width="160" />

  <h1>SharepointFrappe</h1>

  <b>Sync your Frappe file attachments to SharePoint — and keep them in Frappe.</b>

  <br /><br />

  <a href="#features">Features</a> ·
  <a href="#how-it-works">How it works</a> ·
  <a href="#installation">Installation</a> ·
  <a href="#setup--configuration">Setup</a> ·
  <a href="#usage">Usage</a> ·
  <a href="#guide">Guide</a>
</div>

---

## Overview

SharepointFrappe extends Frappe's built-in file handling so that whenever a file is attached to a
record, it can be transparently uploaded to **SharePoint** in addition to — or instead of —
Frappe's local storage. You decide, per DocType, *where* files live and *how* their cloud folder
structure is named.

It works by overriding Frappe's core `File` document class, so it applies to **every** attachment
field across your site without touching your other apps.

## Features

| | |
| --- | --- |
| 🔌 **SharePoint integration** | Connect SharePoint via an Azure AD app. |
| 📂 **Per-DocType rules** | Choose `Frappe only`, `Cloud only`, or `Both` for each DocType. |
| 🧭 **Templated folder paths** | Build cloud folders from static text, field values, the record name, or the DocType name — with a live path preview in the form. |
| 🏷️ **Flexible file naming** | Keep original filenames or apply a template like `{name}-{field}`. |
| ⚔️ **Conflict handling** | Rename, replace, or fail on duplicate filenames. |
| 🔐 **Cached credentials** | Tokens are cached with expiry so connections stay fast. |
| 🧭 **SharepointFrappe workspace** | Installed on the desk home with shortcuts to every doctype and the guide; visible to **System Manager** by default. |
| 🎨 **Modern, branded forms** | Every SharepointFrappe form ships with a clean, on-brand UI and inline guidance. |

## How it works

```
 Attach a file ──▶ Frappe File (overridden) ──▶ SF Upload Rule for the DocType?
                                                  │
                          ┌───────────────────────┼───────────────────────┐
                          ▼                        ▼                       ▼
                    Frappe only               Cloud only                 Both
                  (stock behaviour)      (push to cloud, file_url    (disk write +
                                          points at the cloud)        cloud mirror)
```

The cloud destination and folder path come from the **SF Upload Rule** matched to the attachment's
target DocType, resolved against the linked **SF Cloud Connection**.

## Installation

Install with the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH

# get the app
bench get-app sharepointfrappe $URL_OF_THIS_REPO --branch main/develop

# install onto a site
bench --site $SITE_NAME install-app sharepointfrappe

# build the bundled assets (logo, branded form styles)
bench build --app sharepointfrappe
bench --site $SITE_NAME clear-cache
```

Then reload your browser. A **SharepointFrappe** workspace is added to the desk home (visible to System
Managers) with shortcuts to all DocTypes and the setup guide.

### Roles & access

- **System Manager** can create and manage SF Cloud Connections and SF Upload Rules (folder
  structure) — this is the default role for all SharepointFrappe DocTypes.
- **Any user** can attach files: connection lookup, rule matching and folder creation run
  server-side in the background, so no extra permissions (or exposure of credentials) are needed.

**Requirements**

- Frappe v16+
- Python 3.10+

## Setup & configuration

### 1. Create a SF Cloud Connection

Go to **SF Cloud Connection → New**.

1. Register an app in Azure AD and grant it `Sites.ReadWrite.All`.
2. Enter the **Tenant ID**, **Client ID**, and **Client Secret**.
3. From your SharePoint URL `https://<tenant>.sharepoint.com/sites/<site>`, enter the
   **Tenant Name** (`<tenant>`, before `.sharepoint.com`) and the **Site Name** (`<site>`,
   after `/sites/`). The `sites/` prefix is added for you.
4. Enter the **Drive Name** (the document library, e.g. `Documents` / `Dokumente`).

Click **Connect** — a green *Connected* pill confirms the credentials work.

### 2. Create an SF Upload Rule

Go to **SF Upload Rule → New**.

| Field | What it does |
| --- | --- |
| **Target Doctype** | Which DocType's attachments this rule governs |
| **Storage Mode** | `Frappe only` / `Cloud only` / `Both` |
| **SF Cloud Connection** | The connection to upload through |
| **Naming Strategy** | `Original` filename or a `Templated` name (`{name}`, `{field}`) |
| **Conflict Behavior** | `Rename`, `Replace`, or `Fail` on duplicates |
| **Folder Segments** | One row per folder level — watch the live path preview update |

### 3. Test it

Use the bundled **SF Test Upload** DocType (or any DocType you wrote a rule for), attach a file, and
confirm it appears in the target SharePoint folder.

## Usage

Once a rule is in place, **no further action is needed** — staff attach files the normal Frappe
way and SharepointFrappe routes them according to your rules. Cloud-only files have their `file_url`
pointed at the cloud copy, so links keep working from inside Frappe.

## Guide

A full, illustrated setup-and-usage guide is bundled with the app and served at:

```
https://your-site/sharepointfrappe-guide
```

## Technical Notes

**SharepointFrappe overrides the core `File` DocType class (`override_doctype_class`) — intentionally and minimally.** Cloud-only storage must send the upload to SharePoint *instead of* writing it to local disk, and Frappe performs that disk write inside `File.save_file()` during `before_insert`, where it can't be intercepted via `doc_events` or post-save hooks. SharepointFrappe therefore overrides only `save_file()` to apply the matched SF Upload Rule, and delegates to `super().save_file()` for `Frappe only` storage and every other File operation.

## Contributing

This app uses `pre-commit` for code formatting and linting. Please
[install pre-commit](https://pre-commit.com/#installation) and enable it:

```bash
cd apps/sharepointfrappe
pre-commit install
```

Configured tools: `ruff`, `eslint`, `prettier`, `pyupgrade`.

## License

[AGPLv3](license.txt) — this project was originally forked from a MIT-licensed codebase; the
original notice is preserved in [license-original-mit.txt](license-original-mit.txt).
