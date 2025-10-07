# Bot de Scraping para HermessApp - Lista de Cumpleaños

Este bot automatiza la extracción de la lista de cumpleaños de pacientes desde HermessApp usando Selenium y Python, enviando los datos directamente a un webhook de n8n.

## 🚀 Características

- **Login automático** en HermessApp
- **Extracción de datos** de la tabla de cumpleaños
- **Envío automático a webhook de n8n** para integración directa
- **Formato n8n** compatible con workflows
- **Eliminación automática de duplicados**
- **Fechas con año de ejecución** (siempre actualizado)
- **Estructura optimizada** para n8n
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
   N8N_WEBHOOK_URL=https://tu-webhook-de-n8n.com/webhook/birthday-data
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
5. ✅ Envío directo al webhook de n8n
6. ✅ Formato optimizado para workflows de n8n

## 📊 Formato de Datos Enviados

Los datos se envían al webhook de n8n con la siguiente estructura:

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

### 🔄 **Integración Directa con n8n**

El bot envía automáticamente los datos al webhook de n8n en formato **JSON** optimizado:

- **`cumpleanos`**: Formato YYYY-MM-DD para n8n
- **Año de ejecución**: Todas las fechas usan el año de ejecución del script
- **Sin duplicados**: Eliminación automática de registros duplicados
- **Metadatos**: Información útil para workflows de n8n
- **Envío automático**: No necesitas manejar archivos, los datos llegan directamente a n8n

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

## 🎯 **Configuración del Webhook en n8n**

Para recibir los datos del bot, configura un nodo **Webhook** en n8n:

1. **Crear un nodo Webhook** en tu workflow de n8n
2. **Copiar la URL del webhook** generada por n8n
3. **Agregar la URL** a tu archivo `config.env` como `N8N_WEBHOOK_URL`
4. **Configurar el método** como POST en el nodo webhook
5. **Los datos llegarán automáticamente** cada vez que ejecutes el bot

### Ejemplo de workflow n8n:
1. **Nodo Webhook** (recibe datos del bot)
2. **Filtrar cumpleaños** del mes actual
3. **Identificar cumpleaños próximos** (esta semana)
4. **Generar notificaciones** automáticas
5. **Crear reportes mensuales**

Los datos se envían automáticamente sin necesidad de manejar archivos.

## 🔒 Seguridad

- **Nunca** subas `config.env` a control de versiones
- Las credenciales se mantienen solo en tu máquina local
- El bot cierra automáticamente el navegador al terminar

## 📝 Notas

- El bot incluye delays para evitar ser detectado como bot
- Los datos se extraen respetando la estructura de la tabla original
- Los datos se envían directamente al webhook de n8n sin generar archivos locales
- Incluye manejo robusto de errores de conexión y timeout

## 🤝 Soporte

Si encuentras problemas:
1. Verifica que las credenciales sean correctas
2. Asegúrate de tener todas las dependencias instaladas (incluyendo `requests`)
3. Revisa que Chrome esté actualizado
4. Verifica que la URL del webhook de n8n sea correcta
5. Ejecuta en modo no-headless para ver qué está pasando
6. Revisa los logs de conexión al webhook

---

**Desarrollado para extracción automática de datos de HermessApp por Mango Morado 💜** 🎂