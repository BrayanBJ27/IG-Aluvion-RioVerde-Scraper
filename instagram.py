import os
import time
import re
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException

# Dependiendo del navegador, se importan los módulos correspondientes.
def get_driver(driver_path: str, browser: str = "edge"):
    browser = browser.lower()
    if browser == "edge":
        from selenium.webdriver.edge.service import Service as EdgeService
        from selenium.webdriver.edge.options import Options as EdgeOptions
        service = EdgeService(driver_path)
        options = EdgeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        return webdriver.Edge(service=service, options=options)
    elif browser == "chrome":
        from selenium.webdriver.chrome.service import Service as ChromeService
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        service = ChromeService(driver_path)
        options = ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        return webdriver.Chrome(service=service, options=options)
    else:
        raise ValueError("Navegador no soportado. Usa 'edge' o 'chrome'.")

class InstagramScraper:
    def __init__(self, driver_path: str, username: str, password: str, hashtag: str, browser: str = "edge"):
        """
        Inicializa el scraper de Instagram.

        Args:
            driver_path (str): Ruta al driver (msedgedriver o chromedriver).
            username (str): Usuario de Instagram.
            password (str): Contraseña de Instagram.
            hashtag (str): Hashtag a buscar (por ejemplo, "aluvion baños").
            browser (str, optional): Navegador a utilizar ('edge' o 'chrome'). Defaults a "edge".
        """
        self.driver = get_driver(driver_path, browser)
        self.wait = WebDriverWait(self.driver, 20)
        self.username = username
        self.password = password
        self.hashtag = hashtag

    def wait_and_find_element(self, by: By, value: str, timeout: int = 20):
        """Espera y retorna un elemento en la página."""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            logging.error(f"Timeout esperando elemento: {value}")
            return None

    def wait_and_find_elements(self, by: By, value: str, timeout: int = 20):
        """Espera y retorna una lista de elementos en la página."""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, value))
            )
        except TimeoutException:
            logging.error(f"Timeout esperando elementos: {value}")
            return []

    def iniciar_sesion(self):
        """Realiza el login en Instagram."""
        self.driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(5)  # Espera a que cargue la página de login
        username_input = self.wait_and_find_element(By.NAME, "username")
        password_input = self.wait_and_find_element(By.NAME, "password")
        if not username_input or not password_input:
            raise Exception("No se pudieron encontrar los campos de inicio de sesión")
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        login_button = self.wait_and_find_element(By.XPATH, "//button[@type='submit']")
        if login_button:
            login_button.click()
            time.sleep(20)  # Espera a que se complete el login
            logging.info("Inicio de sesión exitoso.")
        else:
            raise Exception("No se pudo encontrar el botón de inicio de sesión")

    def navegar_hashtag(self):
        """Navega a la sección de búsqueda del hashtag especificado."""
        try:
            self.driver.get(f"https://www.instagram.com/explore/search/keyword/?q={self.hashtag}")
            time.sleep(8)
        except Exception as e:
            logging.error(f"Error al navegar al hashtag: {e}")

    def scroll_page(self, max_scrolls: int = 3):
        """Realiza scroll en la página para cargar más publicaciones."""
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scrolls = 0
            while scrolls < max_scrolls:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                scrolls += 1
        except Exception as e:
            logging.error(f"Error durante el scroll: {e}")

    @staticmethod
    def limpiar_contenido(texto: str) -> str:
        """
        Limpia el contenido eliminando partes no deseadas.
        """
        patron_meta = r"Meta; Información; Blog;.*?© \d{4} Instagram from Meta; Inicio; Buscar; Explorar;.*"
        texto = re.sub(patron_meta, "", texto, flags=re.DOTALL)
        texto = re.sub(r"Inicia la conversación\.;?", "", texto, flags=re.DOTALL)
        texto = re.sub(r"^(.*?); •; \1", r"\1", texto, flags=re.MULTILINE)
        return texto.strip()

    def extraer_publicaciones(self, limit: int = 10):
        """
        Extrae publicaciones a partir de enlaces encontrados que contienen "/p/".

        Args:
            limit (int, optional): Número máximo de publicaciones a extraer. Defaults a 10.

        Returns:
            list: Lista de diccionarios con datos de cada publicación.
        """
        data = []
        max_intentos = 3
        enlaces = self.wait_and_find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
        enlaces_urls = [enlace.get_attribute("href") for enlace in enlaces[:limit]]
        for url in enlaces_urls:
            intentos = 0
            while intentos < max_intentos:
                try:
                    self.driver.get(url)
                    time.sleep(5)
                    # Se prueban dos selectores para extraer el contenido de la publicación.
                    contenido_selector = "//div[contains(@class, 'x9f619') and contains(@class, 'xjbqb8w')]//span[contains(@class, 'x1lliihq')]"
                    contenido_selector_alt = "//div[contains(@class, 'x9f619')]//span[@dir='auto']"
                    contenido = self.wait_and_find_element(By.XPATH, contenido_selector)
                    if not contenido:
                        logging.info("Primer selector falló, intentando alternativo...")
                        contenido = self.wait_and_find_element(By.XPATH, contenido_selector_alt)
                    contenido_texto = self.limpiar_contenido(contenido.text) if contenido else "Contenido no disponible"
                    
                    # Extraer número de reacciones (likes)
                    try:
                        likes_element = self.wait_and_find_element(By.XPATH, "//section//div[contains(text(),'me gusta')]")
                        likes_text = likes_element.text
                        likes_match = re.search(r"([\d,.]+)", likes_text)
                        reacciones = likes_match.group(1) if likes_match else "Reacciones no disponibles"
                    except Exception as e:
                        reacciones = "Reacciones no disponibles"
                    
                    # Extraer comentarios
                    comentarios = self.wait_and_find_elements(By.XPATH, "//div[contains(@class, 'x9f619')]//span[@dir='auto']")
                    lista_comentarios = [com.text for com in comentarios[1:] if com.text.strip()] if comentarios else []
                    
                    # Extraer hashtags
                    hashtags = re.findall(r"(#\w+)", contenido_texto)
                    
                    data.append({
                        "Usuario": url.split('/')[4] if len(url.split('/')) > 4 else "Desconocido",
                        "Contenido": contenido_texto,
                        "Reacciones": reacciones,
                        "Comentarios": "; ".join(lista_comentarios),
                        "Hashtags": hashtags,
                        "URL": url
                    })
                    logging.info(f"Procesada URL: {url}")
                    logging.info(f"Contenido encontrado: {contenido_texto[:100]}...")
                    break
                except StaleElementReferenceException:
                    intentos += 1
                    logging.warning(f"Intento {intentos} fallido para URL {url}")
                    time.sleep(3)
                except Exception as e:
                    logging.error(f"Error al procesar URL {url}: {e}")
                    break
        return data

    def close(self):
        """Cierra el navegador."""
        self.driver.quit()

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    driver_path = os.getenv("DRIVER_PATH", "C:\\msedgedriver.exe")
    username = os.getenv("INSTAGRAM_USERNAME", "tu_usuario")
    password = os.getenv("INSTAGRAM_PASSWORD", "tu_contraseña")
    hashtag = os.getenv("INSTAGRAM_HASHTAG", "aluvion baños")
    browser = os.getenv("BROWSER", "edge")  # O 'chrome'

    scraper = InstagramScraper(driver_path, username, password, hashtag, browser)
    try:
        scraper.iniciar_sesion()
        scraper.navegar_hashtag()
        scraper.scroll_page()
        data = scraper.extraer_publicaciones(limit=10)
        if data:
            df = pd.DataFrame(data)
            df.to_csv("instagram_scraped_data.csv", index=False, encoding="utf-8")
            logging.info("Datos guardados en 'instagram_scraped_data.csv'")
        else:
            logging.warning("No se extrajo ninguna publicación.")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
