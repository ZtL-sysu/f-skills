# GPT Overall Framework Figure Prompt Template

Create Figure 1: a clean publication-ready overall framework/architecture diagram in the user's provided reference-template style and in the style of a modern ML paper pipeline figure. This figure is generated directly with GPT image generation (`image2` in the user's wording), not with Nature figure skills.

Style requirements:
- Wide landscape scientific diagram, white background.
- Left-to-right pipeline with bold uppercase column headers.
- Rounded rectangles with thin black outlines.
- Pastel module colors: gray inputs, pale blue encoders, pale orange fusion, pale teal backbone, stronger orange outputs, dashed red diagnostics.
- Straight black connector arrows with explicit branch/merge points.
- Small technical icons inside boxes, such as grids, node graphs, waveforms, feature tiles, bar traces, or heatmaps where appropriate.
- Include concise mathematical/tensor labels on arrows where useful.
- Include a bottom legend explaining color categories and dashed diagnostic boxes.
- Keep labels legible and professional. No photorealism, no 3D, no marketing poster style.

Paper-specific content:
- Paper title/topic: [FILL]
- Core method name: [FILL]
- Inputs: [FILL]
- Encoder modules: [FILL]
- Fusion modules: [FILL]
- Main backbone/core algorithm: [FILL]
- Output heads/decoders: [FILL]
- Diagnostics/auxiliary outputs: [FILL]
- Key symbols to show on arrows: [FILL]
- Final outputs: [FILL]

Composition:
- Column 1 header: [FILL]
- Column 2 header: [FILL]
- Column 3 header: [FILL]
- Column 4 header: [FILL]
- Optional column 5 header: [FILL]

Important:
- The diagram must match the actual paper and not invent modules.
- Use short labels, not paragraph text.
- The result should look like a framework figure for a NeurIPS/ICML/Nature Machine Intelligence paper.
- This is the whole-paper overall figure, not a data result plot.
