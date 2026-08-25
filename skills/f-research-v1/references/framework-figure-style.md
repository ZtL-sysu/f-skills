# Framework Figure Style

Use this style for the GPT-generated framework/architecture figure. It is based on the user's provided reference image: a clean, paper-ready technical pipeline diagram with labeled modules, arrows, pastel blocks, mathematical annotations, and a legend.

## Visual Layout

- Wide landscape aspect ratio, about 16:9 or wider.
- White background with no decorative gradients, bokeh, or 3D effects.
- Left-to-right pipeline with 4-5 titled columns, such as `INPUTS`, `ENCODERS`, `FUSION + BACKBONE`, `HEADS`, `OUTPUTS`.
- Bold uppercase column headers above the modules.
- Rounded rectangles with thin black strokes.
- Straight black connector arrows; branch and merge points should be explicit.
- Small technical icons inside modules where useful: grids, graphs, nodes, waveforms, bars, heatmaps, feature patches.
- A bottom legend explaining color families and line styles.

## Color Language

Use restrained pastel families:

- light gray/white for inputs;
- pale blue for graph or text/image encoders;
- pale teal/cyan for temporal, spiking, or sequence backbone;
- pale purple for local/context features;
- pale orange for fusion modules;
- stronger orange for output or decision heads;
- dashed red outline for diagnostics, auxiliary losses, or analysis outputs.

Keep the palette soft and publication-like. Avoid neon colors, glossy buttons, shadows that look like UI cards, or infographic clutter.

## Technical Labeling

Include:

- short module names with one-line parenthetical explanations;
- tensor/graph symbols near arrows when helpful, such as `G`, `h`, `z`, `f_fused`, `(N x D)`;
- clear output labels;
- diagnostic or auxiliary boxes only if the paper discusses them.

Do not include unsupported equations or metrics. The figure must reflect the final manuscript.

## GPT Image Prompt Pattern

Use `assets/framework-figure-prompt-template.md` and fill it from the completed paper. The prompt should explicitly ask for an editable-looking scientific architecture diagram, not a poster or marketing illustration.

After generation, inspect the image:

- Are all main modules present?
- Does the left-to-right flow match the method?
- Are labels legible?
- Are arrows coherent?
- Is the bottom legend present?
- Does it match the reference style without copying its domain-specific content?

Regenerate if any answer is no.
