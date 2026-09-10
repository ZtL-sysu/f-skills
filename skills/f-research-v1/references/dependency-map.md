# Dependency Map

This skill is a dispatcher. Prefer installed skills by name. If they are unavailable, use available copies in `bundled-skills/` as reference material and continue when they provide the required capability. Report the fallback. Request a missing dependency only when no available equivalent can satisfy the actual gate; do not infer that a reference copy supplies an executable CLI.

## Names and Aliases

| User wording | Preferred skill/tool | Vendored folder |
|---|---|---|
| `autoresearchclaw`, `AutoResearchClaw`, `researchclaw` | `autoresearch` plus local AutoResearchClaw CLI | `bundled-skills/0-autoresearch-skill` |
| `nature skills`, Nature-style plots | `nature-figure` | `bundled-skills/nature-figure` |
| `image2`, GPT draw, overall/framework figure | GPT's own image-generation capability, invoked directly after the complete paper is understood; do not use Nature skills for the overall Figure 1 | none; not a skill dependency |
| `paper skills`, paragraph expansion | `paper-refine`, `paper-polish-workflow`, `ml-paper-writing` | matching folders |
| TeX compile, PDF build, LaTeX errors | `paper-compile` | `bundled-skills/paper-compile` |
| `humanizer` | `humanizer` | `bundled-skills/humanizer` |
| `20-ml`, ML paper polish | `ml-paper-writing` | `bundled-skills/ml-paper-writing` |
| citation verification, duplicate references | `nature-citation`, `citation-audit`, `ml-paper-writing` plus `reference-dedup-audit.md` | matching folders |

## Install Advice for Recipients

If a recipient copies this folder as a single skill, the main `f-research-v1` skill will load, but nested dependencies may not auto-trigger. For full behavior, copy the folders under `bundled-skills/` into the recipient's normal skills directory as top-level skills, or install equivalent skills with the same names.

## Priority

Use installed current skills first because they may be newer. Use vendored copies only when installed versions are missing, renamed, or unavailable.
