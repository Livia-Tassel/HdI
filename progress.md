Original prompt: i have replace part of english of web with chinese, please check the unpdated code and make sure all the english of web has been replaced and there are no bugs been taken in, you can use git

- Started audit of current dashboard-only diff in `dashboard/index.html`, `dashboard/app.js`, and `dashboard/styles.css`.
- Need to verify all user-facing web copy is now Chinese and that recent edits did not introduce UI regressions.
- Localized remaining dynamic dashboard strings in `dashboard/app.js`, including context cards, spotlight modal, chart labels, budget/objective labels, province names, country search labels, and no-data fallbacks.
- Updated `dashboard/styles.css` to prefer an Alimama-style Chinese font stack with offline-safe local fallbacks.
- Verification:
- `node --check dashboard/app.js` passed.
- Real browser screenshot pass completed via Playwright against a local static server after installing Chromium; the default dashboard view renders in Chinese without obvious layout breakage.
