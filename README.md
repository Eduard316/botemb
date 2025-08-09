# Telegram Bot para Render (Python 3.13 compatible)

Este proyecto usa `python-telegram-bot==13.15` con **webhook** y un *shim* de `imghdr` para correr en Python 3.13.

## Variables de entorno en Render
- `TELEGRAM_TOKEN`: el token de tu bot.
- `PUBLIC_URL`: URL pública del servicio (p. ej., `https://tu-servicio.onrender.com`). Añádela tras el primer deploy y vuelve a desplegar.

## Pasos
1. Sube este repo a GitHub o deployea el ZIP en Render como Web Service.
2. Define las variables de entorno anteriores.
3. Primer deploy -> copia la URL pública -> guárdala en `PUBLIC_URL` -> Redeploy.
4. En Telegram, escribe `/start` al bot.

Ruta de webhook: `https://<PUBLIC_URL>/webhook/<TELEGRAM_TOKEN>`
