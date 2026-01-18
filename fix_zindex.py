import re

# Leer el archivo
with open('hoja_de_vida/apps/perfil/static/perfil/css/pdf/cv_template_web.css', 'r', encoding='utf-8') as f:
    content = f.read()

# Agregar z-index al header
content = re.sub(
    r'\.cv-header \{ background: linear-gradient\(135deg, #1e3a5f 0%, #0d2436 50%, #0f2940 100%\); padding: 14px 20px; color: white; -webkit-print-color-adjust: exact; print-color-adjust: exact; box-shadow: 0 1px 2px rgba\(0,0,0,0\.08\); width: 100%; margin: 0; \}',
    '.cv-header { background: linear-gradient(135deg, #1e3a5f 0%, #0d2436 50%, #0f2940 100%); padding: 14px 20px; color: white; -webkit-print-color-adjust: exact; print-color-adjust: exact; box-shadow: 0 1px 2px rgba(0,0,0,0.08); width: 100%; margin: 0; position: relative; z-index: 10; }',
    content
)

# Escribir el archivo corregido
with open('hoja_de_vida/apps/perfil/static/perfil/css/pdf/cv_template_web.css', 'w', encoding='utf-8') as f:
    f.write(content)

print('Z-index aplicado correctamente al header')

