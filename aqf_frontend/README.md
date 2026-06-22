# AQF UI V7 Runtime Patch

This patch builds the AQF UI directly from runtime artifacts in `public/runtime/`:

- `canonical_form.json`
- `field_statistics.json`
- `adaptive_form.json` (loaded as a fallback/extra source)

It only uses the backend for query execution:

- `POST /query/search`
- `GET /query/suggestions/{field_path}`

## Expected local structure

```text
your-frontend/
  public/
    runtime/
      canonical_form.json
      field_statistics.json
      adaptive_form.json
  src/
    ...
```

## Run

```powershell
npm install
npm run dev
```

Set backend URL through:

```env
VITE_API_BASE_URL=http://localhost:8000
```
