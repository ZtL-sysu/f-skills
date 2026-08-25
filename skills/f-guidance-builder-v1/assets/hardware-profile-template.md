# Hardware Profile

## Local Experiment Machine

- Role: run experiments, training, evaluation, preprocessing, writing, and artifact preparation by default
- OS:
- CPU:
- RAM:
- GPU:
- GPU memory:
- Disk free:
- CUDA:
- Apple MPS available:
- Conda/Python:
- Selected Conda environment:
- Key probes: run `scripts/hardware_probe.py` inside the intended Conda environment, supplemented by OS-native checks when needed

## Optional Remote Compute

- Enabled only when: explicitly requested in the guidance or authorized after local feasibility fails
- Role:
- OS:
- Endpoint reference: record a non-secret alias only; never embed credentials
- CPU:
- RAM:
- GPU:
- GPU memory:
- Disk free:
- CUDA:
- Conda/Python:
- Artifact synchronization plan:

## Experiment Budget

- Maximum runtime per run:
- Maximum total runtime:
- Maximum number of runs:
- Maximum dataset size:
- Maximum model size:

## Feasibility Notes

- Expected bottleneck:
- Scaling strategy:
- Risks:
- Assumptions:
