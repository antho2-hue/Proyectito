import re

# Leer el archivo
with open('hoja_de_vida/apps/perfil/static/perfil/css/pdf/cv_template_web.css', 'r', encoding='utf-8') as f:
    content = f.read()

# Hacer las reversiones
content = re.sub(r'top: 48px; /\* Start below header height \*/', 'top: 0;', content)
content = re.sub(r'height: calc\(100% - 48px\); /\* Adjust height to account for header \*/', 'height: 100%;', content)
content = re.sub(r'max-height: calc\(297mm - 88px\); /\* Adjusted for header height \*/', 'max-height: calc(297mm - 40mm);', content)
content = re.sub(r'margin-top: 0; /\* Ensure no top margin pushes it down \*/', '', content)

# Escribir el archivo corregido
with open('hoja_de_vida/apps/perfil/static/perfil/css/pdf/cv_template_web.css', 'w', encoding='utf-8') as f:
    f.write(content)

print('Reversiones aplicadas correctamente')

