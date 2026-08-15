# Thien-Skill-Creative-Diagram v1.0.0 — Owner Release Approval Packet

**Release candidate:** `TCD-RELEASE-1.0.0-RC1`  
**Package candidate:** `TCD-PACKAGES-1.0.0-RC1`  
**Status:** G-07 `PASS` and release authorized under D-037; execution pending GitHub CLI authentication

## Exact artifacts submitted for approval

| Target | Artifact | SHA-256 |
|---|---|---|
| Claude plugin | `dist/thien-skill-creative-diagram-1.0.0-claude-plugin.zip` | `bba5b464322d8d50ec2f9b76e18581df3e5614004078ba40708f2c8cd1104fa9` |
| OpenAI plugin | `dist/thien-skill-creative-diagram-1.0.0-openai-plugin.zip` | `7d7a33dbdecdd87e9f5237c3ab39b1416ba11c3b736424ba3eb0151c9d73893c` |
| Universal raw skill | `dist/thien-skill-creative-diagram-1.0.0-universal-raw-skill.zip` | `4fcccc656008dd1caba8c1605b0523b0c041afaf216f739aba7373b5d5ac748f` |

Checksum manifest SHA-256: `af491f8f0dc9f3dd86ca9158a5456fb36e34acc14aa70030c4e46f6d5ed17596`.

## Gate reconciliation

- G-00 through G-06 are `PASS` in `PLAN.md`.
- Exact G-06 legal candidate remains `TCD-LEGAL-1.0.0-RC2`, aggregate SHA-256 `8f16380761cd6026166daa12ee36227d96e0e3b92ce605f4d9057624de8292c6`.
- Approved benchmark/goldens and brand selection match the hashes bound in `release-candidate-freeze.json`.
- P-13 verification remains 23/23 pass; the complete regression suite remains 127/127 pass.
- The release does not claim any conditional surface as supported.

## Owner decisions recorded under D-035

1. All three exact ZIP files and overall release candidate `TCD-RELEASE-1.0.0-RC1` are approved.
2. Medium residual risks `P14-R01` and `P14-R02` are accepted.
3. Option A — full private audit repository — is selected, excluding `.DS_Store`, cache and transient files.
4. The owner confirms target URL `https://github.com/thiendeptrainhat/Thien-Skill-Creative-Diagram`.

## Repository publication-scope options

| Option | Content | Tradeoff |
|---|---|---|
| A — Full private audit repository | All governed project files, canonical source, `dist/` and complete evidence including QA-only images/goldens; exclude `.DS_Store`, caches and transient files. | Strongest audit trail; largest repository and retains QA-only material privately. |
| B — Curated private release-source repository | Governance, canonical source, legal/provenance, deterministic build/verifiers, `dist/` and release/gate records; exclude bulky QA-only images/contact sheets and development evidence. | Smaller, but the pushed repository no longer contains the complete local audit corpus. |
| C — Artifact-only private repository | Versioned ZIP files, checksums and minimum release/legal records. | Smallest, but does not publish the canonical source/audit trail and is least aligned with a source-available project repository. |

Option A was selected under D-035 and A1 was selected under D-036. The refined scan distinguished five files containing actual owner-machine paths from two files containing only generic absolute-path security regex/fixtures. The deterministic publication mirror replaces only the five actual-path files with stable placeholders, records repo-relative before/after hashes without reproducing sensitive values, retains the two security-test files unchanged, and excludes `.DS_Store`, cache and transient classes. Local source bytes remain unchanged.

The exact GitHub target was subsequently verified by read-only inspection in an authenticated owner session: the URL resolves to `thiendeptrainhat/Thien-Skill-Creative-Diagram`, displays `Private`, and shows the empty-repository quick-setup surface. No browser mutation was performed.

## Owner release authorization under D-037

The owner approved G-07 `PASS` and authorized init of the sanitized mirror, commit to `main`, creation and push of tag `v1.0.0`, push of `main`, and GitHub Release `v1.0.0` with the three frozen ZIPs and `SHA256SUMS.txt`. The pushed repository must include a detailed installation README and license information; root `README.md` satisfies that requirement.

Execution is paused because `gh auth status` reports the active `thiendeptrainhat` token as invalid. Authentication must be restored before any authorized Git or release mutation.
