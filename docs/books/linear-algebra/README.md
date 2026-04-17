# Introduction to Linear Algebra — For Data Scientists

A compact, diagram-rich textbook on linear algebra written by **M. Aammar Amjad**,
aimed at aspiring data scientists and ML engineers.

## Contents

* **`index.html`** — the full book (12 chapters + preface, index, end matter).
  Rendered client-side with [KaTeX](https://katex.org/) for math and inline SVG
  for all diagrams. Open in any modern browser.
* **`styles.css`** — black / white / red typographic theme.
* **`Linear-Algebra-for-Data-Scientists.pdf`** — print-ready PDF rendered from
  the HTML.
* **`build_pdf.py`** — regenerates the PDF from the HTML using headless
  Chromium via Playwright.

## Chapters

1. Vectors & Vector Spaces
2. Matrices & Matrix Operations
3. Systems of Linear Equations
4. Determinants & Invertibility
5. Basis, Dimension & Rank
6. Linear Transformations
7. Orthogonality, Projections & Least Squares
8. Eigenvalues & Eigenvectors
9. Singular Value Decomposition & PCA
10. Matrix Factorisations (LU / QR / Cholesky)
11. Numerical Linear Algebra
12. Applications in Data Science

End matter: answer key, NumPy cheatsheet, glossary, references.

Each chapter follows the same rhythm: overview → topics → worked example →
diagram → **one MCQ** → **one or two problems** → NumPy snippet → recap card.

## Rebuilding the PDF

```bash
pip install playwright
python -m playwright install chromium
python build_pdf.py
```

## License

© 2026 M. Aammar Amjad. All rights reserved.
