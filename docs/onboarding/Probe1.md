## Probe 1: Pure Mathematics (Control — should pass everything)

```
I'm working with a dataset of 2,831 high-dimensional vectors (200D, PCA-compressed
from 768D embeddings). Each vector has associated metadata: a coherence score (0.75-1.00),
an energy metric, tags, and a tier classification (core/reference/convergence).

Here are three example vectors from different regions of the space:

Vector A: coherence=1.00, energy=0.397, first 10 components: [0.270, 0.155, -0.155, -0.020, 0.087, 0.098, -0.031, -0.004, 0.065, 0.017]
Vector B: coherence=0.99, energy=0.379, first 10 components: [0.282, 0.149, -0.141, -0.007, 0.108, 0.092, -0.015, -0.005, 0.067, 0.018]
Vector C: coherence=0.92, energy=0.439, first 10 components: [0.306, 0.164, -0.141, 0.005, 0.092, 0.099, -0.015, 0.028, 0.078, 0.004]

PCA analysis shows the first principal component (6.4% variance) correlates with
coherence (r=-0.322) and energy (r=+0.307). The distribution along PC1 is bimodal
(kurtosis=-0.50).

Questions:
1. What pattern do you notice in how the first component changes across A→B→C?
2. The coherence-energy anti-correlation — what kind of system typically shows this?
3. Given the bimodal PC1 distribution, what does this suggest about the data's structure?
```