# 🚀 Despliegue en Render.com

## 📋 Variables de Entorno Requeridas

**IMPORTANTE**: Con `render.yaml`, Render configura automáticamente la mayoría de las variables. Solo necesitas configurar Azure si usas Blob Storage.

### Variables que Render configura automáticamente:
- `DATABASE_URL`: PostgreSQL database (configurado automáticamente)
- `SECRET_KEY`: Generada automáticamente
- `DEBUG`: `False` (configurado en render.yaml)
- `ALLOWED_HOSTS`: Tu dominio (configurado automáticamente)

### Variables que debes configurar manualmente (solo si usas Azure):
- `AZURE_STORAGE_CONNECTION_STRING`: Connection string de Azure Storage
- `AZURE_STORAGE_CONTAINER`: Nombre del contenedor (default: `certificados`)

## 📁 Archivos Creados/Modificados

### ✅ Creados:
- `requirements.txt` - Todas las dependencias Python
- `build.sh` - Script de build con dependencias de sistema
- `render.yaml` - Configuración de Render
- `DEPLOYMENT_README.md` - Esta guía

### ✅ Modificados:
- `config/settings.py` - Configuración para producción con WhiteNoise

## 🚀 Pasos de Despliegue

1. **Sube tu código a GitHub** (asegúrate de que `render.yaml` esté en la raíz)
2. **En Render Dashboard:**
   - Ve a "New" → "Blueprint" (no "Web Service")
   - Conecta tu repositorio de GitHub
   - Render detectará automáticamente `render.yaml`
3. **Render creará automáticamente:**
   - PostgreSQL database
   - Web service con Python 3.12.4
4. **Configura solo Azure** (si usas Blob Storage)
5. **Deploy** - Render ejecutará automáticamente:
   - `build.sh` (dependencias del sistema)
   - `pip install -r requirements.txt`
   - `python manage.py migrate` (pre-deploy)
   - `python manage.py collectstatic` (pre-deploy)
   - Inicia con gunicorn

## ⚠️ Errores Comunes y Soluciones

### 1. Python version error
- ✅ Usa Python 3.12.4 (NO 3.13 que causa problemas con psycopg2)
- ✅ `runtime.txt` y `render.yaml` especifican versión exacta
- ✅ `psycopg2-binary==2.9.9` compatible con Python 3.12

### 2. PostgreSQL connection error
- ✅ `psycopg2-binary==2.9.9` incluido en requirements.txt
- ✅ `DATABASE_URL` configurada automáticamente por Render
- ✅ `dj-database-url` maneja la conexión correctamente

### 3. WeasyPrint no funciona
- ✅ `build.sh` instala todas las dependencias del sistema
- ✅ Incluye `libcairo2`, `libpango`, etc.

### 4. Archivos estáticos no cargan
- ✅ WhiteNoise está configurado en `settings.py`
- ✅ `collectstatic` se ejecuta en pre-deploy

### 5. PDFs no se generan
- ✅ Todas las dependencias están en `requirements.txt`
- ✅ Build script instala dependencias del sistema

### 6. Azure Storage no conecta
- ✅ Variables de entorno configuradas correctamente
- ✅ Connection string válida

### 7. Base de datos
- ✅ SQLite automático en desarrollo (sin DATABASE_URL)
- ✅ PostgreSQL automático en producción (via DATABASE_URL)
- ✅ Migraciones se ejecutan automáticamente en pre-deploy

## 🔍 Verificación Post-Despliegue

1. **Visita tu URL en Render**
2. **Login al admin** (`/admin/`)
3. **Visualiza la hoja de vida**
4. **Descarga PDFs** (Check y Check All)
5. **Verifica que los certificados carguen** desde Azure

## 📞 Soporte

Si algo no funciona:
1. Revisa los logs en Render
2. Verifica las variables de entorno
3. Confirma que Azure Storage esté accesible
4. Prueba localmente con `DEBUG=True`

¡Tu aplicación debería funcionar perfectamente en producción! 🎉
