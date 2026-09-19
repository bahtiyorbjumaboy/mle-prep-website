# ML Interview OS

A static, source-driven workspace for a machine learning interview curriculum. It turns canonical Markdown into a dashboard, knowledge and coding browsers, durable answer and coding-solution libraries, a searchable source library, and a browser-local completion tracker.

The project uses Astro, Starlight, TypeScript, and static generation. It requires no backend, database, authentication, or hosted content service.

## Screenshots

Add current desktop and mobile screenshots here after deploying your curriculum.

## Quick start

Requirements: Node.js 22+ and npm.

```bash
npm install
npm run dev
```

Useful commands:

```bash
npm run index      # regenerate generated/curriculum-index.json
npm run validate   # validate curriculum relationships
npm run test       # parser, identity, and progress tests
npm run build      # production static build
npm run check      # type-check, test, validate, and build
```

The empty repository is a supported state. It renders instructions instead of demo curriculum data.

## Repository structure

```text
curriculum/
  2026/{sources,interview-answers,coding-solutions}/
  2027/{sources,interview-answers,coding-solutions}/
generated/curriculum-index.json
scripts/                       # indexing and validation
src/{components,layouts,lib,pages,styles}/
templates/interview-answer.md
.github/workflows/deploy-pages.yml
```

Files under `curriculum/**/sources/` are canonical and are never changed by a build. The generated JSON file is derived and may be regenerated at any time.

## Study artifact contract

| Artifact | Purpose | Relationship | May contain live progress? |
| --- | --- | --- | --- |
| Source | Authoritative question bank, coding set, roadmap, or instruction document | Defines canonical items | No |
| Interview answer | Durable reusable answer to one knowledge question | Exactly one knowledge item; at most one per item | No |
| Coding solution | Complete source-code solution | Filename identifies exactly one coding item; at most one per item | No |

Current completion, mastery, attempts, and short personal notes live in the browser progress store. Durable interview answers and coding solutions must not contain live-progress state.

## Adding curriculum files

Copy files without renaming their internal wording:

```text
curriculum/2026/sources/01_2026_Generalist_MLE_Coding_Set_FINAL.md
curriculum/2026/sources/Bank_01_Linear_Algebra_FINAL.md
curriculum/2027/sources/03_2027_Search_Recs_STAFF_Roadmap_FINAL.md
```

Then run:

```bash
npm run validate
npm run build
```

The indexer recognizes question/problem headings, coding ID families, bank filenames, and roadmap `Week N` headings. It retains unparsed source content and reports useful warnings instead of inventing missing fields.

## Canonical IDs

Knowledge IDs such as `A3` are not globally unique. Their keys include curriculum and bank:

- `2026:bank01:A3`
- `2026:bank02:A3`
- `2027:ranking-recommendation:R08`

Coding keys use a coding namespace, for example `2027:coding:REC-05`. Progress and artifact links use these stable keys, not mutable question wording. Ambiguous roadmap references are not guessed.

Artifact frontmatter may use the concise unambiguous 2027 forms `2027:R01` and `2027:REC-05`; the index resolves them to internal bank/coding-qualified keys. A 2026 knowledge reference must always include its bank, such as `2026:bank01:A3`, because `A3` may also exist in another bank.

## Adding interview answers

Use `curriculum/2026/interview-answers/bankXX/<ID>.md` or one of the domain-qualified 2027 locations:

```text
curriculum/2027/interview-answers/search/S01.md
curriculum/2027/interview-answers/recommendation/R01.md
```

```yaml
---
type: interview-answer
item: "2027:R01"
title: "Two-stage and multi-stage recommender architecture"
created: "2026-09-17"
updated: "2026-09-17"
tags: [recommendation, ranking]
---
```

Begin body headings at H2. One answer maps to exactly one knowledge item. Put reusable concept teaching in a `## Learn the Concept` section in the same file. See `templates/interview-answer.md`.

## Adding coding solutions

Add the complete source file using its canonical problem ID as the filename:

```text
curriculum/2026/coding-solutions/DSA-01.py
curriculum/2027/coding-solutions/search/SRCH-11.py
curriculum/2027/coding-solutions/recommendation/REC-05.py
```

The filename is the identity: use the exact coding ID and do not identify a solution by display wording. The indexer resolves concise IDs such as `REC-05` to their internal canonical key and rejects unknown, misplaced, or duplicate solutions. Supported text source files include Python, JavaScript/TypeScript, SQL, Java, C/C++, Go, Rust, Scala, Kotlin, shell, and R. The complete file is rendered verbatim on the website.

Interview-answer Markdown supports headings, tables, task lists, fenced code, inline and display LaTeX math, and Mermaid fenced blocks. Math is processed through Astro's Unified pipeline with `remark-math` and `rehype-katex`; source LaTeX is passed through unchanged before rendering. Use `$...$` for inline math and `$$...$$` for display math. The KaTeX stylesheet is included globally.

## Progress persistence and portability

Interactive progress is stored in browser `localStorage` under a versioned key. Each record can contain completion, curriculum-specific mastery wording, attempt count, last-attempt date, and a short personal note. This data is private to that browser and is not committed.

Use **Export progress** to download readable JSON, **Import** to validate and replace local data, and **Reset** to clear it. Import preserves valid records, reports malformed ones, and safely retains unknown canonical keys for future curricula. Import overwrite and reset both require confirmation.

Rendered Markdown and coding-solution pages include text-size controls. The selected reading size is stored locally in the browser and reused across content pages.

## Validation

`npm run validate` detects duplicate canonical keys, unknown artifact references, duplicate interview answers/solutions, misplaced solution files, malformed or unquoted dates, H1 artifact headings, forbidden live-progress fields, malformed frontmatter, and invalid progress fixtures. Non-fatal source ambiguity is printed with context. Tests cover parsing, identity, artifact relationships, contract violations, progress import, and real KaTeX output. The mandatory math fixture is `tests/fixtures/math-rendering.md`.

## GitHub Pages deployment

1. Push the repository to GitHub with the default branch named `main`.
2. In **Settings → Pages**, choose **GitHub Actions** as the source.
3. Push a commit or run the workflow manually.

`.github/workflows/deploy-pages.yml` installs locked dependencies, validates curriculum data, runs tests, builds static output, and deploys `dist/` using standard Pages permissions. No secrets are needed.

The Astro config derives the project-page base from `GITHUB_REPOSITORY`, so `https://USERNAME.github.io/REPOSITORY/` works without hard-coded usernames. For unusual hosting, set `SITE_URL` and/or `BASE_PATH` at build time.

## Updating the site

Add or edit any source or study-artifact Markdown; run `npm run check`; commit; and push. Pages rebuilds automatically. Navigation, browse pages, relationships, and detail routes come from the generated index, so no manual menu edit is needed.

## Troubleshooting base paths

- Do not hand-prefix Markdown assets with the repository name. Use relative paths where practical.
- Local development intentionally runs at `/`; the Actions build supplies `/<repository>` automatically.
- Reproduce a project-page build locally with `BASE_PATH=/your-repository npm run build`.
- If Pages shows a 404, confirm the Pages source is **GitHub Actions** and the repository's default branch matches the workflow trigger.

## Why Markdown stays the source of truth

Markdown is portable, Git-friendly, diffable, easy to author, and independent of this UI. The build reads it into a normalized model and renders richer navigable pages without rewriting the original documents. That separation keeps curriculum review honest: source wording and schedules remain authoritative while the application adds search, linking, progress, and presentation.

## Intentionally deferred

Cloud/GitHub progress sync, automatic spaced-repetition scheduling, analytics, mock-interview history, and charts are extension points rather than first-version features. The local progress adapter and normalized index keep those additions possible without changing the Markdown authoring model.
