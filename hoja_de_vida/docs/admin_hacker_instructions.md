Integración del tema Cyberpunk para Django Admin

Archivos añadidos:
- templates/admin/base_site.html  — overload del base_site para inyectar CSS/JS y branding
- templates/admin/index.html — dashboard cards (opcional)
- apps/perfil/static/perfil/css/admin_hacker.css — estilos principales
- apps/perfil/static/perfil/js/admin_hacker.js — micro-interacciones

Pasos para integrar:
1. Copia/commita los archivos a tu repositorio (ya están en el proyecto).
2. Asegúrate que `TEMPLATES` en `settings.py` incluye el directorio `templates/` (estándar en Django projects).
3. Asegúrate que `STATICFILES_DIRS` / `STATIC_ROOT` incluyen `apps/perfil/static` o ejecuta `python manage.py collectstatic` en producción.
4. Reinicia el servidor: `python manage.py runserver` y visita `/admin/`.

Notas de accesibilidad y rendimiento:
- No usamos frameworks pesados y solo incluimos pequeñas animaciones en JS (deshabilitables si hay problemas).
- Para usar las tipografías mono (JetBrains, Fira Code), instálalas en el sistema o carga con @font-face si las quieres embebidas.
- He mantenido clases y selectores específicos para minimizar el riesgo de romper funcionalidad.

Cómo revertir:
- Elimina los archivos `templates/admin/*` y los assets `admin_hacker.*` o revierte el commit; limpia collectstatic si corresponde.
