# 🚀 <span style="color:#007bff; font-weight:bold; font-size:1.8em;">Pull Request Template</span>

<p style="font-size:1.1em; color:#555; font-style:italic; text-align:center;">Please fill out the following details to ensure a smooth and effective code review process.</p>

<p align="center">
  <img src="https://i.postimg.cc/mPJ3gZgY/bug-report-form.png" alt="Pull Request Form" style="max-width:200px; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <figcaption style="font-style:italic; font-size:0.9em; color:#666;">A comprehensive PR ensures quality.</figcaption>
</p>

---

## <span style="color:#28a745; font-weight:bold;">✅ Description</span>

Please provide a clear and concise summary of the changes introduced in this pull request.

-   **What is the purpose of this PR?** (e.g., "Fixes a bug in the API", "Adds a new feature for model training")
-   **What problem does it solve?** (Link to issue if applicable: `Closes #123` or `Fixes #456`)
-   **What changes were made?** (Briefly describe the modifications, new files, etc.)
-   **Why these changes?** (Explain the rationale behind your approach or design decisions).

---

## <span style="color:#ff8c00; font-weight:bold;">💡 Type of Change</span>

Please check the type of change that applies to your pull request.

-   [ ] **Bug fix:** Corrects an existing issue (e.g., incorrect calculation, API error).
-   [ ] **New feature:** Adds new functionality or capabilities to the project (e.g., new model, new endpoint).
-   [ ] **Breaking change:** Introduces changes that will require existing users/integrations to update their code.
-   [ ] **Documentation update:** Improves or adds to project documentation (e.g., README, Model Card, API docs).
-   [ ] **Refactoring:** Code restructuring without changing external behavior.
-   [ ] **Chore:** Maintenance tasks (e.g., dependency updates, CI/CD config).

---

## <span style="color:#6f42c1; font-weight:bold;">🧪 Testing</span>

Describe the tests you have performed to ensure your changes work correctly and don't introduce regressions. Provide instructions on how to run them.

<p align="center">
  <img src="https://i.postimg.cc/Wq1q7x4k/checklist-dashboard.png" alt="Testing Dashboard" style="max-width:200px; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <figcaption style="font-style:italic; font-size:0.9em; color:#666;">Rigorous testing ensures reliability.</figcaption>
</p>

-   [ ] **Unit tests passed:** All relevant unit tests (`pytest tests/unit/`) passed successfully.
-   [ ] **Integration tests passed:** All relevant integration tests (`pytest tests/integration/`) passed successfully.
-   [ ] **End-to-End (E2E) tests passed:** Applicable E2E tests verified the complete flow (if new features were added).
-   [ ] **Manual testing:** Details of any manual testing performed (e.g., "Tested API endpoint `/predict` with various inputs", "Verified dashboard functionality").

**Instructions to run tests (if specific):**
```bash
# Example: pytest tests/unit/test_my_module.py
```

---

## <span style="color:#17a2b8; font-weight:bold;">📸 Screenshots / Demos (Optional)</span>

If your changes involve UI updates, new visualizations, or demonstrable new features, please include screenshots or GIFs to illustrate the changes.

-   [ ] Screenshot(s) attached
-   [ ] GIF/Video demo attached

---

## <span style="color:#fd7e14; font-weight:bold;">📈 Deployment Impact (Optional)</span>

Describe any potential impact of this change on deployment, infrastructure, or performance.

-   [ ] No significant impact expected.
-   [ ] Requires new environment variables.
-   [ ] Increases resource usage (CPU/RAM/Disk).
-   [ ] Modifies existing API endpoints.
-   [ ] Changes in data storage format or schema.

---

## <span style="color:#6610f2; font-weight:bold;">📝 Checklist</span>

Please ensure the following points have been addressed before requesting a review.

<p align="center">
  <img src="https://i.postimg.cc/ctLtcPJ3/checklist-static.png" alt="Checklist Icon" style="max-width:100px; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <figcaption style="font-style:italic; font-size:0.9em; color:#666;">Confirm all items are checked.</figcaption>
</p>

-   [x] My code follows the project's style guidelines (e.g., `flake8`, `black`).
-   [x] I have performed a self-review of my own code, checking for common errors and best practices.
-   [x] I have commented my code, particularly in hard-to-understand areas, and documented functions/classes.
-   [x] I have updated the relevant documentation (e.g., README, Model Card, API docs) to reflect my changes.
-   [x] My changes pass all existing and new tests.
-   [x] I have added new tests where necessary to cover new features or bug fixes.
-   [x] My changes do not introduce any new warnings or errors in the console/logs.
-   [x] I have considered backward compatibility.
-   [x] All necessary dependencies are listed in `requirements.txt` or equivalent.

---

## <span style="color:#dc3545; font-weight:bold;">👥 Reviewer Checklist (for reviewers)</span>

-   [ ] Code logically structured and easy to understand?
-   [ ] Does the code adhere to coding standards and best practices?
-   [ ] Are tests comprehensive and passing?
-   [ ] Is documentation accurate and up-to-date?
-   [ ] Are there any potential performance or security concerns?
-   [ ] Is the PR's scope appropriate and focused?

<p style="font-style:italic; font-size:0.9em; color:#666; text-align:center; margin-top:20px;">
  Thank you for your contribution!
</p>