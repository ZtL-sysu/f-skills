# Source Verification

Use this reference whenever the skill searches for datasets, papers, baselines, or citation candidates.

## Dataset Evidence

Prefer primary sources:

- Official benchmark or project page.
- Dataset hosting page with files and metadata.
- Hugging Face dataset card.
- Kaggle dataset page.
- OpenML, UCI, Zenodo, Figshare, PhysioNet, TCIA, MIMIC official pages, or equivalent repositories.
- GitHub release with immutable data files.

Record source URL, access date, license/terms, file size, labels, task type, and any account requirement.

Do not accept:

- "Available upon request."
- "Contact authors."
- Broken or private links.
- Pages with only descriptions and no files.
- Datasets requiring paid access, institutional approval, manual review, IRB, NDA, or long-form application.
- Ambiguous mirrors without provenance.

## Literature Evidence

Prioritize:

- Publisher or conference pages.
- arXiv plus accepted venue metadata when available.
- Semantic Scholar, OpenReview, ACL Anthology, IEEE, ACM, Springer, Elsevier, Nature, MDPI, Frontiers, PLOS, Oxford, Wiley, and official journal sites.
- Papers With Code for benchmark orientation, followed by original papers for citation.

For each high-risk novelty comparison, record:

| Paper | Year | Venue/source | Method | Task/domain | Dataset | Central claim | Overlap level | Decision |
|---|---:|---|---|---|---|---|---|---|

Overlap levels:

- `duplicate`: same method, task, dataset class, and claim.
- `high`: similar method and task, but different claim or evidence.
- `medium`: same task or method family, but clearly different contribution.
- `low`: background or adjacent work.

Reject or redirect scenarios with duplicate overlap.

## Citation Seed Rules

For the final guidance file, provide citation scope rather than a fully verified bibliography. Include likely keywords, must-cite clusters, and 36 or more candidate references when source verification is available. `f-research-v1` will later perform full citation verification.

Most references should be from the last 3-5 years unless foundational work is necessary. Keep older references for original methods, datasets, or metrics.

## Claims

Every claim in the guidance file should be tagged mentally as one of:

- `experiment`: will be tested by planned experiments.
- `citation`: supported by literature.
- `assumption`: explicitly recorded and later checked.
- `risk`: possible weakness or failure condition.

Do not turn assumptions into claims.
