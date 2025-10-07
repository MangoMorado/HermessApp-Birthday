#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot de scraping para HermessApp - Lista de Cumpleaños
Extrae la información de cumpleaños de los pacientes y la guarda en formato n8n
"""

import os
import json
import time
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv

class HermessBirthdayBot:
    def __init__(self):
        """Inicializa el bot con configuración desde variables de entorno"""
        load_dotenv('config.env')
        
        self.email = os.getenv('HERMESS_EMAIL')
        self.password = os.getenv('HERMESS_PASSWORD')
        self.login_url = os.getenv('HERMESS_LOGIN_URL', 'https://hermessapp.com/login')
        self.birthdays_url = os.getenv('HERMESS_BIRTHDAYS_URL', 'https://hermessapp.com/pacientescumple')
        self.n8n_webhook_url = os.getenv('N8N_WEBHOOK_URL') or os.getenv('n8n_workflow')
        
        if not self.email or not self.password:
            raise ValueError("Debes configurar HERMESS_EMAIL y HERMESS_PASSWORD en config.env")
        
        if not self.n8n_webhook_url:
            raise ValueError("Debes configurar N8N_WEBHOOK_URL o n8n_workflow en config.env")
        
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Configura el driver de Chrome con opciones optimizadas"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        chrome_options.add_argument("--user-data-dir=/tmp/selenium")
        chrome_options.add_argument("--headless")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def login(self):
        """Inicia sesión en HermessApp"""
        try:
            print("🔄 Iniciando sesión en HermessApp...")
            self.driver.get(self.login_url)
            
            # Esperar a que cargue la página de login
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "form[action*='login']"))
            )
            
            # Buscar campos de login usando los selectores correctos del HTML
            email_field = self.driver.find_element(By.CSS_SELECTOR, "input[name='email']")
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[name='password']")
            
            # Ingresar credenciales
            email_field.clear()
            email_field.send_keys(self.email)
            
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Buscar y hacer clic en el botón de login
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Esperar a que se complete el login
            time.sleep(3)
            
            print("✅ Sesión iniciada exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error durante el login: {str(e)}")
            return False
    
    def navigate_to_birthdays(self):
        """Navega a la página de cumpleaños"""
        try:
            print("🔄 Navegando a la página de cumpleaños...")
            self.driver.get(self.birthdays_url)
            time.sleep(3)
            
            # Hacer debug para ver qué hay en la página
            self._debug_page_content()
            
            # Esperar a que cargue algún contenido
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
                )
            except:
                pass
            
            print("✅ Página de cumpleaños cargada")
            return True
            
        except Exception as e:
            print(f"❌ Error navegando a la página de cumpleaños: {str(e)}")
            return False
    
    def _debug_page_content(self):
        """Hace debug del contenido de la página para entender su estructura"""
        try:
            print("🔍 Analizando contenido de la página...")
            
            # Obtener el título de la página
            title = self.driver.title
            print(f"📄 Título de la página: {title}")
            
            # Buscar texto que contenga "cumpleaños"
            birthday_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'cumpleaños') or contains(text(), 'cumpleañeros') or contains(text(), 'birthday')]")
            if birthday_elements:
                print(f"🎂 Encontrados {len(birthday_elements)} elementos con texto de cumpleaños:")
                for elem in birthday_elements[:3]:  # Solo mostrar los primeros 3
                    print(f"  - {elem.text[:100]}...")
            
            # Buscar formularios
            forms = self.driver.find_elements(By.CSS_SELECTOR, "form")
            print(f"📝 Encontrados {len(forms)} formularios")
            
            # Buscar tablas
            tables = self.driver.find_elements(By.CSS_SELECTOR, "table")
            print(f"📊 Encontradas {len(tables)} tablas HTML")
            
            # Buscar divs que puedan contener datos
            data_divs = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='data'], div[class*='list'], div[class*='table']")
            print(f"📋 Encontrados {len(data_divs)} divs potenciales de datos")
            
            # Mostrar las primeras líneas del HTML para debug
            page_source = self.driver.page_source
            if "cumpleaños" in page_source.lower() or "cumpleañeros" in page_source.lower():
                print("✅ La página contiene texto relacionado con cumpleaños")
            else:
                print("⚠️ No se encontró texto relacionado con cumpleaños en la página")
                
        except Exception as e:
            print(f"⚠️ Error en debug: {str(e)}")
    
    def extract_birthday_data(self):
        """Extrae los datos de cumpleaños de la tabla"""
        try:
            print("🔄 Extrayendo datos de cumpleaños...")
            
            # Esperar un poco más para que la página cargue completamente
            time.sleep(2)
            
            # Buscar la tabla con selectores más específicos
            table_selectors = [
                "table",
                ".table",
                "[class*='table']",
                "div[role='table']",
                "[class*='list']",
                "div[class*='overflow']",  # Para tablas con scroll
                "div[class*='container']"  # Para contenedores de datos
            ]
            
            table = None
            for selector in table_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        # Verificar si el elemento contiene datos de cumpleaños
                        if self._contains_birthday_data(element):
                            table = element
                            break
                    if table:
                        break
                except NoSuchElementException:
                    continue
            
            if not table:
                # Si no encontramos tabla, buscar por texto que contenga "cumpleaños"
                try:
                    birthday_text = self.driver.find_element(By.XPATH, "//*[contains(text(), 'cumpleaños') or contains(text(), 'cumpleañeros')]")
                    print(f"📍 Encontrado texto relacionado: {birthday_text.text}")
                    # Buscar el contenedor padre que pueda contener la tabla
                    table = birthday_text.find_element(By.XPATH, "./ancestor::div[contains(@class, 'container') or contains(@class, 'table') or contains(@class, 'list')]")
                except:
                    pass
            
            if not table:
                raise Exception("No se pudo encontrar la tabla de cumpleaños")
            
            print(f"📍 Tabla encontrada con selector: {table.tag_name}")
            
            # Extraer filas de la tabla
            rows = table.find_elements(By.CSS_SELECTOR, "tr, [role='row'], div[class*='row']")
            
            if not rows:
                # Si no hay filas, buscar elementos que parezcan filas de datos
                rows = table.find_elements(By.CSS_SELECTOR, "div[class*='item'], div[class*='entry'], div[class*='data']")
            
            print(f"📍 Encontradas {len(rows)} filas potenciales")
            
            birthdays_data = []
            
            for i, row in enumerate(rows):
                try:
                    # Buscar celdas con diferentes selectores
                    cells = row.find_elements(By.CSS_SELECTOR, "td, [role='cell'], div[class*='cell'], span, div")
                    
                    if len(cells) >= 3:  # Mínimo 3 columnas (nombre, fecha, edad)
                        # Extraer texto de las celdas
                        cell_texts = [cell.text.strip() for cell in cells if cell.text.strip()]
                        
                        if len(cell_texts) >= 3:
                            # Intentar identificar qué es cada columna
                            birthday_entry = self._parse_birthday_row(cell_texts)
                            if birthday_entry:
                                birthdays_data.append(birthday_entry)
                                print(f"  ✅ Fila {i+1}: {birthday_entry['nombre']} - {birthday_entry['cumpleanos']}")
                        
                except Exception as e:
                    print(f"⚠️ Error procesando fila {i+1}: {str(e)}")
                    continue
            
            print(f"✅ Se extrajeron {len(birthdays_data)} registros de cumpleaños")
            return birthdays_data
            
        except Exception as e:
            print(f"❌ Error extrayendo datos: {str(e)}")
            return []
    
    def _contains_birthday_data(self, element):
        """Verifica si un elemento contiene datos de cumpleaños"""
        try:
            text = element.text.lower()
            birthday_keywords = ['cumpleaños', 'cumpleañeros', 'fecha', 'edad', 'nombre']
            return any(keyword in text for keyword in birthday_keywords)
        except:
            return False
    
    def _parse_birthday_row(self, cell_texts):
        """Parsea una fila de datos de cumpleaños"""
        try:
            # Buscar patrones comunes en los datos
            nombre = ""
            fecha = ""
            celular = ""
            edad = ""
            
            for text in cell_texts:
                text = text.strip()
                if not text:
                    continue
                
                # Identificar nombre (texto largo, sin números)
                if len(text) > 5 and not any(char.isdigit() for char in text) and not nombre:
                    nombre = text
                
                # Identificar fecha (formato DD/MM o similar)
                elif '/' in text and len(text) <= 5 and not fecha:
                    fecha = text
                
                # Identificar celular (10 dígitos)
                elif text.isdigit() and len(text) == 10 and not celular:
                    celular = text
                
                # Identificar edad (1-3 dígitos)
                elif text.isdigit() and 1 <= len(text) <= 3 and not edad:
                    edad = text
            
            # Solo retornar si tenemos al menos nombre y fecha
            if nombre and fecha:
                # Convertir fecha a formato compatible con n8n (solo año de ejecución)
                cumpleanos = self._convert_date_to_n8n_format(fecha)
                
                # Formatear nombre con primera letra en mayúscula
                nombre_formateado = self._format_name(nombre)
                
                return {
                    "nombre": nombre_formateado,
                    "cumpleanos": cumpleanos,
                    "celular": celular,
                    "edad": edad
                }
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error parseando fila: {str(e)}")
            return None
    
    def _reorder_name(self, nombre):
        """Reordena el nombre de 'Apellido1 Apellido2 Nombre1 Nombre2' a 'Nombre1 Nombre2 Apellido1 Apellido2'"""
        try:
            if not nombre:
                return nombre
            
            palabras = nombre.split()
            
            if len(palabras) < 2:
                return nombre
            
            # Estrategia inteligente para casos complejos
            if len(palabras) == 5:
                # Caso especial: DE LA OSSA TAMARA LUZ ANGELA
                # Patrón: ApellidoCompuesto(3) + Apellido2(1) + Nombres(2)
                
                # Detectar apellidos compuestos comunes
                apellidos_compuestos_inicio = ['DE', 'DEL', 'VAN', 'VON', 'MAC', 'MC']
                
                if palabras[0].upper() in apellidos_compuestos_inicio:
                    # Verificar si es un apellido compuesto de 3 palabras
                    if palabras[0].upper() in ['DE', 'DEL'] and palabras[1].upper() in ['LA', 'LOS', 'LAS']:
                        # Patrón: DE LA OSSA TAMARA LUZ ANGELA
                        # Apellido compuesto: DE LA OSSA (3 palabras)
                        # Segundo apellido: TAMARA (1 palabra)
                        # Nombres: LUZ ANGELA (2 palabras)
                        return f"{palabras[3]} {palabras[4]} {palabras[0]} {palabras[1]} {palabras[2]}"
                    elif palabras[0].upper() in ['VAN', 'VON'] and palabras[1].upper() == 'DER':
                        # Patrón: VAN DER BERG CARLOS ALBERTO
                        # Apellido compuesto: VAN DER BERG (3 palabras)
                        # Nombres: CARLOS ALBERTO (2 palabras)
                        return f"{palabras[3]} {palabras[4]} {palabras[0]} {palabras[1]} {palabras[2]}"
                    else:
                        # Otros casos de apellidos compuestos de 2 palabras
                        # Patrón: MAC DONALD JOHN MICHAEL
                        return f"{palabras[3]} {palabras[4]} {palabras[0]} {palabras[1]} {palabras[2]}"
                else:
                    # Patrón estándar: Apellido1 Apellido2 Apellido3 Nombre1 Nombre2
                    return f"{palabras[3]} {palabras[4]} {palabras[0]} {palabras[1]} {palabras[2]}"
            
            elif len(palabras) == 6:
                # Caso muy complejo: DE LA OSSA MARQUEZ TAMARA LUZ ANGELA
                # Patrón: ApellidoCompuesto(3) + Apellido2(1) + Apellido3(1) + Nombres(2)
                
                apellidos_compuestos_inicio = ['DE', 'DEL', 'VAN', 'VON']
                
                if palabras[0].upper() in apellidos_compuestos_inicio:
                    if palabras[0].upper() in ['DE', 'DEL'] and palabras[1].upper() in ['LA', 'LOS', 'LAS']:
                        # Patrón: DE LA OSSA MARQUEZ TAMARA LUZ ANGELA
                        # Apellidos: DE LA OSSA MARQUEZ (4 palabras)
                        # Nombres: TAMARA LUZ ANGELA (3 palabras)
                        # Pero esto es muy raro, usar lógica de 3+3
                        return f"{palabras[3]} {palabras[4]} {palabras[5]} {palabras[0]} {palabras[1]} {palabras[2]}"
                    else:
                        # Otros casos complejos
                        mitad = len(palabras) // 2
                        apellidos = palabras[:mitad]
                        nombres = palabras[mitad:]
                        return f"{' '.join(nombres)} {' '.join(apellidos)}"
                else:
                    # Lógica general para 6 palabras
                    mitad = len(palabras) // 2
                    apellidos = palabras[:mitad]
                    nombres = palabras[mitad:]
                    return f"{' '.join(nombres)} {' '.join(apellidos)}"
            
            elif len(palabras) == 4:
                # Caso estándar: Apellido1 Apellido2 Nombre1 Nombre2
                return f"{palabras[2]} {palabras[3]} {palabras[0]} {palabras[1]}"
            
            elif len(palabras) == 3:
                # Apellido1 Apellido2 Nombre1 → Nombre1 Apellido1 Apellido2
                return f"{palabras[2]} {palabras[0]} {palabras[1]}"
            
            elif len(palabras) == 2:
                # Apellido1 Nombre1 → Nombre1 Apellido1
                return f"{palabras[1]} {palabras[0]}"
            
            else:
                # Para otros casos, usar lógica general
                mitad = len(palabras) // 2
                apellidos = palabras[:mitad]
                nombres = palabras[mitad:]
                return f"{' '.join(nombres)} {' '.join(apellidos)}"
            
        except Exception as e:
            print(f"⚠️ Error reordenando nombre '{nombre}': {str(e)}")
            return nombre
    
    def _format_name(self, nombre):
        """Formatea el nombre con primera letra en mayúscula y resto en minúsculas"""
        try:
            if not nombre:
                return nombre
            
            # Primero reordenar el nombre
            nombre_reordenado = self._reorder_name(nombre)
            
            # Dividir el nombre en palabras (por espacios)
            palabras = nombre_reordenado.split()
            
            # Formatear cada palabra
            palabras_formateadas = []
            for palabra in palabras:
                if palabra:
                    # Primera letra en mayúscula, resto en minúsculas
                    palabra_formateada = palabra[0].upper() + palabra[1:].lower()
                    palabras_formateadas.append(palabra_formateada)
            
            # Unir las palabras con espacios
            return " ".join(palabras_formateadas)
            
        except Exception as e:
            print(f"⚠️ Error formateando nombre '{nombre}': {str(e)}")
            return nombre
    
    def _convert_date_to_n8n_format(self, fecha_dd_mm):
        """Convierte fecha DD/MM a formato YYYY-MM-DD usando siempre el año de ejecución"""
        try:
            if '/' not in fecha_dd_mm:
                return fecha_dd_mm
            
            # Separar día y mes
            partes = fecha_dd_mm.split('/')
            if len(partes) != 2:
                return fecha_dd_mm
            
            dia = int(partes[0])
            mes = int(partes[1])
            
            # Siempre usar el año de ejecución del script
            año_ejecucion = datetime.now().year
            
            # Crear fecha completa con el año de ejecución
            fecha_completa = datetime(año_ejecucion, mes, dia)
            
            # Formato ISO 8601 (YYYY-MM-DD) compatible con n8n
            return fecha_completa.strftime("%Y-%m-%d")
            
        except Exception as e:
            print(f"⚠️ Error convirtiendo fecha {fecha_dd_mm}: {str(e)}")
            return fecha_dd_mm
    
    def _remove_duplicates(self, data):
        """Elimina registros duplicados basados en nombre y celular"""
        try:
            seen = set()
            unique_data = []
            duplicates_removed = 0
            
            for entry in data:
                # Crear clave única basada en nombre y celular
                key = (entry.get('nombre', ''), entry.get('celular', ''))
                
                if key not in seen:
                    seen.add(key)
                    unique_data.append(entry)
                else:
                    duplicates_removed += 1
                    print(f"🔄 Duplicado eliminado: {entry.get('nombre', 'Sin nombre')}")
            
            if duplicates_removed > 0:
                print(f"✅ Se eliminaron {duplicates_removed} registros duplicados")
            
            return unique_data
            
        except Exception as e:
            print(f"⚠️ Error eliminando duplicados: {str(e)}")
            return data
    
    def send_to_n8n_webhook(self, data):
        """Envía los datos extraídos al webhook de n8n"""
        # Eliminar duplicados antes de enviar
        data_unique = self._remove_duplicates(data)
        
        try:
            # Crear estructura de datos con metadatos para n8n
            payload = {
                "metadata": {
                    "fecha_extraccion": datetime.now().isoformat(),
                    "total_registros": len(data_unique),
                    "formato_fecha": "YYYY-MM-DD",
                    "año_ejecucion": datetime.now().year,
                    "fuente": "HermessApp",
                    "descripcion": "Lista de cumpleaños de pacientes extraída automáticamente"
                },
                "cumpleanos": data_unique
            }
            
            # Configurar headers para la petición
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'HermessApp-Birthday-Bot/1.0'
            }
            
            print(f"🔄 Enviando datos al webhook de n8n...")
            print(f"📊 Total de registros únicos: {len(data_unique)}")
            print(f"🌐 URL del webhook: {self.n8n_webhook_url}")
            
            # Enviar petición POST al webhook
            response = requests.post(
                self.n8n_webhook_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            # Verificar respuesta
            if response.status_code == 200:
                print(f"✅ Datos enviados exitosamente al webhook de n8n")
                print(f"📊 Total de registros enviados: {len(data_unique)}")
                print(f"📅 Formato de fecha: YYYY-MM-DD")
                print(f"📅 Año de ejecución: {datetime.now().year}")
                return True
            else:
                print(f"❌ Error enviando datos al webhook. Código de respuesta: {response.status_code}")
                print(f"📄 Respuesta del servidor: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print(f"❌ Timeout al enviar datos al webhook de n8n")
            return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Error de conexión al webhook de n8n")
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Error enviando datos al webhook: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Error inesperado enviando datos: {str(e)}")
            return False
    
    def run(self):
        """Ejecuta el bot completo"""
        try:
            print("🚀 Iniciando bot de HermessApp...")
            
            self.setup_driver()
            
            if not self.login():
                return None
            
            if not self.navigate_to_birthdays():
                return None
            
            birthdays_data = self.extract_birthday_data()
            
            if birthdays_data:
                success = self.send_to_n8n_webhook(birthdays_data)
                if success:
                    print(f"🎉 Datos enviados exitosamente al webhook de n8n")
                    return birthdays_data
                else:
                    print("❌ Error enviando datos al webhook")
                    return None
            else:
                print("❌ No se pudieron extraer datos")
                return None
                
        except Exception as e:
            print(f"❌ Error general: {str(e)}")
            return None
            
        finally:
            if self.driver:
                self.driver.quit()
                print("🔒 Navegador cerrado")

def main():
    """Función principal"""
    try:
        bot = HermessBirthdayBot()
        result = bot.run()
        
        if result:
            print(f"\n🎉 Bot ejecutado exitosamente!")
            print(f"📊 Total de registros extraídos: {len(result)}")
            print("\n📋 Primeros 3 registros:")
            for i, entry in enumerate(result[:3], 1):
                print(f"  {i}. {entry['nombre']} - {entry['cumpleanos']} ({entry['edad']} años)")
        else:
            print("\n❌ El bot no pudo completar la tarea")
            
    except Exception as e:
        print(f"❌ Error en la ejecución: {str(e)}")

if __name__ == "__main__":
    main()
