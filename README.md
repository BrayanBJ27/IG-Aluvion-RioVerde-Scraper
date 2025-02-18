# Instagram Scraper

## Descripción
**Instagram Scraper** es una herramienta en Python que utiliza Selenium para automatizar la extracción de publicaciones de Instagram basadas en un hashtag específico. El scraper realiza lo siguiente:

- Inicia sesión en Instagram de forma automática.
- Navega a la sección de búsqueda para el hashtag indicado.
- Realiza scroll en la página para cargar más publicaciones.
- Extrae información de las publicaciones, incluyendo:
    - Usuario
    - Contenido de la publicación (limpiado de textos no deseados)
    - Número de reacciones (likes)
    - Comentarios
    - Hashtags presentes
    - URL de la publicación
- Guarda los datos extraídos en un archivo CSV.

## Requisitos

- **Python 3.7+**
- **Selenium**  
    Instalarlo con:
    ```bash
    pip install selenium
    ```
- **Pandas**  
    Instalarlo con:
    ```bash
    pip install pandas
    ```
- **Driver Web (msedgedriver o chromedriver)**  
    Debes disponer de un driver compatible con el navegador que vayas a utilizar:
    - Microsoft Edge: Descarga msedgedriver.
    - Google Chrome: Descarga chromedriver.

## Instalación

Clonar el repositorio:
```bash
git clone https://github.com/BrayanBJ27/IG-Aluvion-RioVerde-Scraper.git
cd instagram-scraper
```

Crear un entorno virtual (opcional):
```bash
python -m venv venv
```
En Linux/Mac:
```bash
source venv/bin/activate
```
En Windows:
```bash
venv\Scripts\activate
```

Instalar las dependencias (crear primero un archivo requirements.txt):
```bash
pip install -r requirements.txt
```

## Configuración

Configura las siguientes variables de entorno:
- **DRIVER_PATH**: Ruta al driver.
- **INSTAGRAM_USERNAME**: Tu usuario de Instagram.
- **INSTAGRAM_PASSWORD**: Tu contraseña de Instagram.
- **INSTAGRAM_HASHTAG**: Hashtag a buscar.
- **BROWSER**: edge o chrome.

Puedes configurarlas en tu sistema o usar un archivo .env junto con python-dotenv.

## Ejecución

```bash
python instagram_scraper.py
```

### Advertencias

- **Uso Ético**: Cumple con los Términos y Condiciones de Instagram.
- **Manejo de Credenciales**: No compartas credenciales, usa variables de entorno.
- **Limitaciones**: Ajusta los tiempos de espera según tu conexión.

## Estructura del Proyecto

```bash
instagram-scraper/
│
├── instagram_scraper.py   # Script principal.
├── requirements.txt       # Dependencias.
└── README.md              # Documentación.
```