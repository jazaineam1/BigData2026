import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(ROOT, "Cuadernos", "12_MongoDB_Atlas_NoSQL_Moderno.ipynb")

with open(path, encoding="utf-8") as f:
    content = f.read()

# En el JSON raw los quotes del codigo Python aparecen escapados como \"
# Reemplazar en la celda de codigo (con quotes escapados)
old_code = '\\"preserveNullAndEmpty\\": True'
new_code = '\\"preserveNullAndEmptyArrays\\": True'
count_code = content.count(old_code)
print(f"En celda codigo: {count_code} ocurrencia(s)")

# Reemplazar en la celda de markdown (sin quotes, solo el nombre de opcion)
old_md = "`preserveNullAndEmpty`"
new_md = "`preserveNullAndEmptyArrays`"
count_md = content.count(old_md)
print(f"En celda markdown: {count_md} ocurrencia(s)")

fixed = content.replace(old_code, new_code).replace(old_md, new_md)

with open(path, "w", encoding="utf-8") as f:
    f.write(fixed)
print("OK — corregido")
