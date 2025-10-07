# Bot de Scraping para HermessApp - Lista de Cumpleaños

Este bot automatiza la extracción de la lista de cumpleaños de pacientes desde HermessApp usando Selenium y Python.

## 🚀 Características

- **Login automático** en HermessApp
- **Extracción de datos** de la tabla de cumpleaños
- **Formato n8n** compatible con workflows
- **Nombres de archivo por mes** (ej: `septiembre.json`)
- **Eliminación automática de duplicados**
- **Fechas con año de ejecución** (siempre actualizado)
- **Estructura simplificada** (solo campo `cumpleanos`)
- **Configuración por variables de entorno**

## 📋 Requisitos Previos

- **Python 3.7+**
- **Chrome/Chromium**
- **Credenciales** de HermessApp

## 🛠️ Instalación


## ⚙️ Configuración

1. **Copiar archivo de configuración:**
   ```bash
   copy config.env.example config.env
   ```

2. **Editar `config.env` con tus credenciales:**
   ```env
   HERMESS_EMAIL=tu_email@ejemplo.com
   HERMESS_PASSWORD=tu_contraseña
   HERMESS_LOGIN_URL=https://hermessapp.com/login
   HERMESS_BIRTHDAYS_URL=https://hermessapp.com/pacientescumple
   ```

## 🚀 Uso

### Ejecutar el bot:
```bash
python hermess_birthday_bot.py
```

### El bot realizará automáticamente:
1. ✅ Inicio de sesión en HermessApp
2. ✅ Navegación a la página de cumpleaños
3. ✅ Extracción de datos de la tabla
4. ✅ Eliminación automática de duplicados
5. ✅ Guardado en archivo JSON con nombre del mes (ej: `septiembre.json`)
6. ✅ Formato n8n listo para usar en workflows

## 📊 Formato de Salida

Los datos se guardan en un archivo JSON con la siguiente estructura:

```json
{
  "metadata": {
    "fecha_extraccion": "2025-09-15T10:30:00.000000",
    "total_registros": 19,
    "formato_fecha": "YYYY-MM-DD",
    "año_ejecucion": 2025,
    "fuente": "HermessApp",
    "descripcion": "Lista de cumpleaños de pacientes extraída automáticamente"
  },
  "cumpleanos": [
    {
      "nombre": "Pepito Perez Perez",
      "cumpleanos": "2011-11-11",
      "celular": "3111111111",
      "edad": "11"
    }
  ]
}
```

### 🔄 **Compatibilidad con n8n**

El bot genera automáticamente fechas en formato **YYYY-MM-DD** (ISO 8601) que son 100% compatibles con n8n:

- **`cumpleanos`**: Formato YYYY-MM-DD para n8n
- **Año de ejecución**: Todas las fechas usan el año de ejecución del script
- **Sin duplicados**: Eliminación automática de registros duplicados
- **Metadatos**: Información útil para workflows de n8n

### ✨ **Formateo Automático de Nombres**

Los nombres se formatean automáticamente para mayor consistencia:

## 🔧 Personalización

### Modo Headless (sin interfaz gráfica)
En `hermess_birthday_bot.py`, descomenta esta línea:
```python
chrome_options.add_argument("--headless")
```

### Cambiar selectores CSS
Si la estructura de la página cambia, modifica los selectores en el método `extract_birthday_data()`.

## 🐛 Solución de Problemas

### Error: "ChromeDriver not found"
- Asegúrate de tener Chrome instalado
- El bot descargará automáticamente el driver compatible

### Error: "Element not found"
- La página puede haber cambiado su estructura
- Revisa los selectores CSS en el código

### Error de login
- Verifica que las credenciales en `config.env` sean correctas
- Asegúrate de que la cuenta no tenga autenticación de dos factores

## 📁 Estructura del Proyecto

```
ANI-cumpleaños/
├── hermess_birthday_bot.py           # Bot principal
├── config.env.example                # Plantilla de configuración
├── requirements.txt                  # Dependencias Python
└── README.md                        # Este archivo
```

## 🎯 **Ejemplo de Uso en n8n**

Se incluye un archivo `n8n_workflow_example.json` que muestra cómo:

1. **Leer el archivo JSON** generado por el bot (ej: `septiembre.json`)
2. **Filtrar cumpleaños** del mes actual
3. **Identificar cumpleaños próximos** (esta semana)
4. **Generar notificaciones** automáticas
5. **Crear reportes mensuales**

Para usar este workflow:
1. Importa el archivo en n8n
2. Actualiza la ruta del archivo JSON al mes correspondiente
3. Personaliza las notificaciones según tus necesidades

## 🔒 Seguridad

- **Nunca** subas `config.env` a control de versiones
- Las credenciales se mantienen solo en tu máquina local
- El bot cierra automáticamente el navegador al terminar

## 📝 Notas

- El bot incluye delays para evitar ser detectado como bot
- Los datos se extraen respetando la estructura de la tabla original
- Se generan archivos JSON con timestamp para evitar sobrescrituras

## 🤝 Soporte

Si encuentras problemas:
1. Verifica que las credenciales sean correctas
2. Asegúrate de tener todas las dependencias instaladas
3. Revisa que Chrome esté actualizado
4. Ejecuta en modo no-headless para ver qué está pasando

---

**Desarrollado para extracción automática de datos de HermessApp por Mango Morado 💜** 🎂