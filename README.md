<div align="center">
<h1>StreetX Store</h1>
<p><strong>Python · Django · HTML · CSS</strong></p>
</div>

Product catalog using Fake Store API, category presentation, validated product data, and cached fallback responses.

## 🖥️ Website preview

<a href="screenshots/Home.jpg"><img src="screenshots/Home.jpg" alt="streetx-store-django: Home" width="100%" /></a>

Click any image to open the original full-resolution capture.

### 📸 All page previews

<details>
<summary><strong>Men</strong></summary>
<br />
<a href="screenshots/Men.jpg"><img src="screenshots/Men.jpg" alt="streetx-store-django: Men" width="100%" /></a>
</details>

<details>
<summary><strong>Women</strong></summary>
<br />
<a href="screenshots/Women.jpg"><img src="screenshots/Women.jpg" alt="streetx-store-django: Women" width="100%" /></a>
</details>

<details>
<summary><strong>Jewelry</strong></summary>
<br />
<a href="screenshots/Jewelry.jpg"><img src="screenshots/Jewelry.jpg" alt="streetx-store-django: Jewelry" width="100%" /></a>
</details>

<details>
<summary><strong>Electronics</strong></summary>
<br />
<a href="screenshots/Electronics.jpg"><img src="screenshots/Electronics.jpg" alt="streetx-store-django: Electronics" width="100%" /></a>
</details>

<details>
<summary><strong>Loved</strong></summary>
<br />
<a href="screenshots/Loved.jpg"><img src="screenshots/Loved.jpg" alt="streetx-store-django: Loved" width="100%" /></a>
</details>

<details>
<summary><strong>Product View</strong></summary>
<br />
<a href="screenshots/Product%20View.png"><img src="screenshots/Product%20View.png" alt="streetx-store-django: Product View" width="100%" /></a>
</details>

## Run locally (Windows PowerShell)

Use Python 3.14, matching the submitted project environment. Dependencies below were identified from the supplied environment metadata.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:DJANGO_SECRET_KEY = (.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(50))")
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Open http://127.0.0.1:8000/.

## Configuration

See `.env.example` for variable names. Set variables in your shell; this project does not automatically load `.env` files. If `DJANGO_SECRET_KEY` is omitted, a temporary random key is generated at startup; set a stable key to retain sessions across restarts.

## Scope

Catalog demonstration; no real checkout, payment processing, or order fulfilment.

This is a learning/portfolio project. Local development settings are enabled by default. Production hosting requires a separate deployment configuration.

## Project layout

- `manage.py`: Django commands.
- `myproject/`: settings and root routes.
- `home/`: application views and routes.
- `templates/` and `static/`: interface templates and assets.

## Validation

Python syntax and Django system checks were run during portfolio preparation. External API responses and browser interactions were not tested end to end.
