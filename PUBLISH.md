# Publishing

## Manual publish

1. Authenticate with npm as the account that owns the package scope.
2. Ensure the package name in `package.json` matches the npm registry target.
3. Run:

```bash
npm ci
npm run build
npm publish --access public
```

`prepublishOnly` also runs `npm run build`, so publish will fail if TypeScript output is stale or broken.

## Publish via GitHub Actions

This repository includes `.github/workflows/npm-publish.yml`.

- Trigger automatically by creating a GitHub Release.
- Or run manually with **Actions → NPM Publish → Run workflow**.

Before using the workflow:

1. Add `NPM_TOKEN` in repository settings under **Secrets and variables → Actions**.
2. Ensure `package.json` version is the release version you want to publish.

The workflow runs `npm ci`, `npm run build`, and `npm publish --access public` using the `NPM_TOKEN` secret.
