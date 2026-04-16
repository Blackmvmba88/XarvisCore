# Administrador personal (plantillas y limpieza de procesos)

## ✨ Resumen
- `scripts/clean_idle_processes.sh`: script seguro que identifica procesos inactivos de tu usuario y te pregunta antes de matarlos. Usa `--dry-run` para probar o `--force` para matar sin preguntar.
- `templates/profile.yaml`, `templates/tasks.md`, `templates/finances.csv`: plantillas para guardar tus datos.

## ⚠️ Seguridad
- **No almacenes contraseñas en texto plano.** Usa el Llavero de macOS (Keychain) o un gestor (1Password, Bitwarden).
- Si quieres cifrar archivos: usa `gpg -c file` para cifrar con contraseña o `gpg --symmetric`.

## Uso del script
1. Dar permiso de ejecución: `chmod +x scripts/clean_idle_processes.sh`
2. Probar sin matar: `./scripts/clean_idle_processes.sh --dry-run`
3. Matar solo con confirmación: `./scripts/clean_idle_processes.sh`
4. Matar automáticamente (con cuidado): `./scripts/clean_idle_processes.sh --force`

## Ejecución periódica (opcional)
- Puedo sugerir y generar un `LaunchAgent` para ejecutar el script automáticamente, pero **te pediré confirmación** antes de crear o habilitar servicios que se ejecuten en tu equipo.

---
Si quieres, puedo:
- Ajustar los umbrales (CPU/RSS/edad) a tus preferencias ✅
- Añadir más plantillas (calendario, contactos, salud, etc.) ✅
- Habilitar un LaunchAgent para limpieza periódica (te pediré confirmación) ✅

---

# Secrets & Assistant (MVP)

He añadido un **módulo mínimo de gestión de secretos** (Keyring + opcional cifrado) y una **puerta de enlace al asistente** (endpoint local que reenvía mensajes a la API del asistente).

## Quickstart
1. Crea un virtualenv e instala dependencias: `pip install -r requirements.txt`
2. Guarda la API key administrativa (local) para usar los endpoints:
   - `python scripts/set_api_key.py --admin mylocalkey`
3. (Opcional) Guarda tu OpenAI API key (si quieres que el asistente haga llamadas reales):
   - `python scripts/set_api_key.py --openai sk-...`
4. Ejecuta la API: `uvicorn app.main:app --reload`
5. Prueba el asistente en dry-run (no gastará llamadas):
   - `python scripts/assistant_cli.py "hola"`

## WebUI (MVP)
Puedes arrancar una interfaz mínima en `web/` que se comunica con la API local.

1. En la carpeta `web/` instala dependencias:
   - `cd web && npm install`
2. Ejecuta el dev server:
   - `npm run dev`
3. Abre `http://localhost:5173` en tu navegador.

Notas:
- La WebUI pedirá la `X-API-KEY` (admin) para listar y gestionar secretos; no guardes la clave en la UI si no quieres.
- Por defecto la WebUI usa el modo *dry-run* para el asistente (no consume llamadas). Para habilitar llamadas reales guarda la OpenAI key con `scripts/set_api_key.py --openai <key>` y modifica la llamada a `dry_run: false` en el frontend si lo deseas.

## Notas
- Esto es un MVP local: **no** expongas el servicio a Internet sin TLS y controles de acceso.
- Para más seguridad puedes habilitar cifrado Fernet dentro del módulo de secretos (requiere `cryptography`).

## Using encrypted secrets (Fernet)
- Puedes almacenar secretos cifrados con Fernet (la clave de Fernet se guarda en Keyring). Ejemplo con el helper script:
  - `python scripts/set_secret.py --service myservice --username me --encrypt`
  - El script pedirá el secreto de forma segura si no lo pasas en la línea de comandos.

- Para guardar la OpenAI key cifrada:
  - `python scripts/set_secret.py --service openai --username api_key --encrypt`

- Notas:
  - `cryptography` debe estar instalada (`pip install cryptography`).
  - La clave de Fernet se guarda en Keyring bajo `fernet_key:<service>` para evitar que el material de claves quede en archivos de texto.

- Si quieres, puedo:
  - Añadir una WebUI simple para gestionar secretos ✅
  - Guardar un historial cifrado de conversaciones (opcional) ✅
  - Integrar Bitwarden o Vaultwarden para gestión avanzada ✅

## PWA & favicons
- He añadido soporte PWA básico: `web/manifest.webmanifest` y un `service worker` (`web/src/sw.js`) que precacha los activos principales para permitir instalación en móviles y funcionamiento offline básico.
- Generé favicons PNG y `favicon.ico` en `web/public/favicons/` y añadí referencias en `web/index.html`.
- Para revisar/ajustar: puedes editar `web/manifest.webmanifest` (nombre, descripción, colores) o mejorar el `service worker` para manejar estrategias de cache más avanzadas.

## Vault CLI
He añadido un pequeño CLI `scripts/vault.py` para manejar tus secretos desde la línea de comandos.

Ejemplos:
- Añadir un secreto (te pedirá el valor si no lo pasas):
  - `python scripts/vault.py add --service mysite --username me --encrypt`
- Leer (por defecto no muestra el valor; usar `--show` para mostrarlo):
  - `python scripts/vault.py get --service mysite --username me --show --decrypt`
- Listar secretos:
  - `python scripts/vault.py list`
- Borrar secreto:
  - `python scripts/vault.py delete --service mysite --username me`
- Exportar a JSON o cifrar con GPG:
  - `python scripts/vault.py export --out backup.json`
  - `python scripts/vault.py export --out backup.json.gpg --gpg`
- Importar (JSON o .gpg):
  - `python scripts/vault.py import --in backup.json`
  - `python scripts/vault.py import --in backup.json.gpg` (gpg pedirá la contraseña)

Notas de seguridad:
- `scripts/vault.py` usa Keyring para almacenar valores (Keychain en macOS).
- Usa `--encrypt` para guardar blobs cifrados con Fernet (requiere `cryptography`).
- Para cifrar exports usa GPG: `gpg --symmetric --cipher-algo AES256 -o backup.json.gpg backup.json`.


---
