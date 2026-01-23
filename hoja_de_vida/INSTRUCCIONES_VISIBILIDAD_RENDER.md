# 🚀 INSTRUCCIONES PARA RENDER - VisibilidadCV

## Problema
La tabla `VisibilidadCV` en Render no tenía datos iniciales, por lo que el admin mostraba "0 visibilidad cvs".

## Solución
Se han creado tres formas de inicializar los datos:

### Opción 1: Migración Automática (RECOMENDADO) ✅
Al hacer deploy en Render, ejecutar:
```bash
python manage.py migrate
```

Esto ejecutará automáticamente la migración `0008_initialize_visibilidad_cv.py` que crea los registros para todos los perfiles activos.

### Opción 2: Comando Django
Si la migración ya se ejecutó pero necesitas ejecutarlo de nuevo:
```bash
python manage.py initialize_visibilidad_cv
```

### Opción 3: Script Python
Como alternativa:
```bash
python initialize_visibilidad.py
```

## Archivos Agregados
1. **`apps/perfil/migrations/0008_initialize_visibilidad_cv.py`** - Migración que auto-crea registros
2. **`apps/perfil/management/commands/initialize_visibilidad_cv.py`** - Comando Django customizado
3. **`initialize_visibilidad.py`** - Script standalone para ejecutar manualmente

## Qué hace
- Busca todos los perfiles con `perfilactivo=1`
- Crea un registro de `VisibilidadCV` para cada uno
- Establece todos los campos en `True` (mostrar todas las secciones)
- No sobreescribe datos existentes (usa `get_or_create`)

## Después de Deploy
Una vez hecho el deploy en Render:
1. Las migraciones se ejecutarán automáticamente
2. Los registros de `VisibilidadCV` se crearán automáticamente
3. El admin mostrará las opciones de visibilidad correctamente

¡Listo! 🎉
