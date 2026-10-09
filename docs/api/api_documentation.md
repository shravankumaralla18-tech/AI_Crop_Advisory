# API reference

Base URL: `http://localhost:8000/api`. Interactive docs: `http://localhost:8000/docs`.
All endpoints except register, login and health need the header `Authorization: Bearer <token>`.

## Auth
| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/auth/register` | `{name, email, password (8+), location?}` | user |
| POST | `/auth/login` | `{email, password}` | `{access_token, token_type, user}` |
| GET | `/auth/me` | | user |
| GET / PUT | `/users/me` | PUT: `{name?, location?, phone?}` | user |

## Disease detection
| Method | Path | Notes |
|---|---|---|
| GET | `/disease/model-status` | Reports whether model weights are installed and lists crops in the configured class labels |
| GET | `/disease/supported-crops` | Supported crop names derived from `ai-model/models/class_names.json` |
| POST | `/disease/detect` | multipart fields `crop` and `file` (JPG/PNG/WebP, max 8 MB). Returns result with `confidence`, `low_confidence`, `top_predictions`, `description`, `symptoms`, `treatment`, `image_url` |
| GET | `/disease/history` | Latest 50 checks for the current user |
| GET | `/disease/{id}` | One check (owner only) |
| DELETE | `/disease/{id}` | Deletes the record and photo |

Errors: 415 wrong type, 413 too large, 400 not an image, 422 unsupported/mismatched crop, 503 model not trained or runtime missing. Upload reads are capped at the configured size plus one byte before inference. A prediction is saved only after successful inference and crop validation.

## Market
| Method | Path | Query |
|---|---|---|
| GET | `/market/prices` | `crop?`, `region?`, `market?`, `start_date?`, `end_date?`: latest price per market in the selected date range, with 7-day change and `source`/`is_sample` provenance |
| GET | `/market/trends` | `crop`, `days` (7-90), `market?`, `start_date?`, `end_date?`: daily modal-price average and provenance |
| GET | `/market/advisory` | `crop`: `signal` is `sell`, `hold` or `monitor`, with reason, best available market, averages, data date and provenance |

The current bundled source is synthetic sample data. Signal rules: sell if the latest recorded value is 5%+ above the 30-day average, or the 7-day average fell more than 3% week on week while still above the 30-day average; hold if 5%+ below the 30-day average; otherwise monitor. These are price-trend heuristics only and omit transport/storage costs.

## Crops and advisory
| Method | Path | Query |
|---|---|---|
| GET | `/crops` | List crops |
| GET | `/crops/{crop_id}` | Crop with growing details |
| GET | `/advisory/crop/{crop_id}` | `lat?`, `lon?`: details, weather, alerts, market signal |
| GET | `/advisory/recommendations` | `month?` (1-12, default current): crops to sow or harvest |

## Other
`GET /health` returns `{"status": "ok"}`. Uploaded photos are served from `/uploads/<file>` (not under `/api`).
