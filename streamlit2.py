# -*- coding: utf-8 -*-
"""
Franco Olivares
"""
import pandas as pd
import logging
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

import pandas as pd
import logging
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.microsoft import EdgeChromiumDriverManager

def scrape_sbs():
    url = "https://www.sbs.gob.pe/app/pp/INT_CN/Paginas/Busqueda/BusquedaPortal.aspx"
    service = EdgeService(EdgeChromiumDriverManager().install())
    options = Options()
    options.headless = True  # Ejecutar en modo headless
    driver = webdriver.Edge(service=service, options=options)

    logging.basicConfig(level=logging.INFO)
    
    try:
        # Abrir la página web
        driver.get(url)
        logging.info("Página web abierta con éxito.")

        # Esperar explícitamente a que el contenido se cargue
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "rgMasterTable"))
        )
        logging.info("Contenido cargado con éxito.")

        # Tomar una captura de pantalla para verificar el contenido cargado
        driver.save_screenshot('screenshot.png')
        logging.info("Captura de pantalla tomada.")

        # Definir las rutas XPath para los datos
        norma_xpath_template = '//*[@id="ctl00_ContentPlaceHolder1_rdgUltimaVersionNormas_ctl00__{}"]/td[2]'
        definicion_xpath_template = '//*[@id="ctl00_ContentPlaceHolder1_rdgUltimaVersionNormas_ctl00__{}"]/td[4]'
        tipo_xpath_template = '//*[@id="ctl00_ContentPlaceHolder1_rdgUltimaVersionNormas_ctl00__{}"]/td[5]'
        fecha_xpath_template = '//*[@id="ctl00_ContentPlaceHolder1_rdgUltimaVersionNormas_ctl00__{}"]/td[8]'
        sistema_xpath_template = '//*[@id="ctl00_ContentPlaceHolder1_rdgUltimaVersionNormas_ctl00__{}"]/td[7]'

        normas = []
        definiciones = []
        tipos = []
        fechas = []
        sistemas = []

        # Obtener el número de filas dinámicamente
        rows = driver.find_elements(By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_rdgUltimaVersionNormas_ctl00"]/tbody/tr')
        num_rows = len(rows)

        # Iterar sobre las filas
        for i in range(num_rows):
            try:
                norma_xpath = norma_xpath_template.format(i)
                definicion_xpath = definicion_xpath_template.format(i)
                tipo_xpath = tipo_xpath_template.format(i)
                fecha_xpath = fecha_xpath_template.format(i)
                sistema_xpath = sistema_xpath_template.format(i)

                # Extraer los datos
                norma_element = driver.find_element(By.XPATH, norma_xpath)
                definicion_element = driver.find_element(By.XPATH, definicion_xpath)
                tipo_element = driver.find_element(By.XPATH, tipo_xpath)
                fecha_element = driver.find_element(By.XPATH, fecha_xpath)
                sistema_element = driver.find_element(By.XPATH, sistema_xpath)

                normas.append(norma_element.text.strip())
                definiciones.append(definicion_element.text.strip())
                tipos.append(tipo_element.text.strip())
                fechas.append(fecha_element.text.strip())
                sistemas.append(sistema_element.text.strip())
            except NoSuchElementException:
                logging.warning(f"Elemento no encontrado en la posición {i}.")
                continue

    except TimeoutException:
        logging.error("El contenido no se cargó a tiempo.")
        return None
    except WebDriverException as e:
        logging.error(f"Error del WebDriver: {e}")
        return None
    finally:
        # Cerrar el navegador
        driver.quit()
        logging.info("Navegador cerrado.")

    # Crear un DataFrame con los datos extraídos
    df = pd.DataFrame({
        'Norma': normas,
        'Definición': definiciones,
        'Tipo': tipos,
        'Fecha': fechas,
        'Sistema': sistemas
    })

    # Convertir la columna "Fecha" al formato de fecha
    df['Fecha'] = pd.to_datetime(df['Fecha'], format="%d/%m/%Y", errors='coerce')

    # Rellenar valores en blanco con el valor de la siguiente fila
    df['Fecha'] = df['Fecha'].fillna(method='bfill')

    # Formatear la columna "Fecha" en el formato "dd/mm/yyyy"
    df['Fecha'] = df['Fecha'].dt.strftime("%d/%m/%Y")

    return df

# Llamar a la función y mostrar el DataFrame
sbs = scrape_sbs()

"-------------------------------- SMV normativa ---------------------------------------"

import pandas as pd
import logging
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import re

def scrape_smv():
    url = "https://www.smv.gob.pe/ServicioConsultaNormas/Frm_Resoluciones?data=28E2BCB3AAF0F6112BFB80F90A370B9923A973B3D2"
    service = EdgeService(EdgeChromiumDriverManager().install())
    options = Options()
    options.headless = True  # Ejecutar en modo headless
    driver = webdriver.Edge(service=service, options=options)

    logging.basicConfig(level=logging.INFO)
    
    try:
        # Abrir la página web
        driver.get(url)
        logging.info("Página web abierta con éxito.")

        # Esperar explícitamente a que el contenido se cargue
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "MainContent_lisAnio"))
        )
        logging.info("Contenido cargado con éxito.")

        # Seleccionar el año actual en el desplegable
        select_anio = Select(driver.find_element(By.ID, "MainContent_lisAnio"))
        select_anio.select_by_visible_text("2025")
        logging.info("Año seleccionado con éxito.")

        # Hacer clic en el botón de consulta
        driver.find_element(By.ID, "btnConsultar").click()
        logging.info("Botón de consulta clicado con éxito.")

        # Esperar a que la tabla se cargue
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "MainContent_grdCabecera_lblCabDato3_0"))
        )
        logging.info("Tabla cargada con éxito.")

        # Inicializar listas para almacenar los datos extraídos
        cabecera_datos = []
        subcabecera_datos = []

        # Iterar sobre los elementos del 0 al 9 y extraer los datos
        for i in range(10):
            try:
                cabecera_xpath = f'//*[@id="MainContent_grdCabecera_lblCabDato3_{i}"]'
                subcabecera_xpath = f'//*[@id="MainContent_grdCabecera_grdSubCabecera_{i}_lblCabDato4_0"]'

                cabecera_element = driver.find_element(By.XPATH, cabecera_xpath)
                subcabecera_element = driver.find_element(By.XPATH, subcabecera_xpath)

                cabecera_datos.append(cabecera_element.text.strip())
                subcabecera_datos.append(subcabecera_element.text.strip())
            except NoSuchElementException:
                logging.warning(f"Elemento no encontrado en la posición {i}.")
                continue

    except TimeoutException:
        logging.error("El contenido no se cargó a tiempo.")
        return None
    except WebDriverException as e:
        logging.error(f"Error del WebDriver: {e}")
        return None
    finally:
        # Cerrar el navegador
        driver.quit()
        logging.info("Navegador cerrado.")

    # Crear un DataFrame con los datos extraídos
    df = pd.DataFrame({
        'Norma': cabecera_datos,
        'Definición': subcabecera_datos
    })

    # Función para extraer la fecha
    def extract_date(norma):
        match = re.search(r'\d{2}/\d{2}/\d{4}', norma)
        return match.group(0) if match else None

    # Crear la nueva columna "Fecha"
    df['Fecha'] = df['Norma'].apply(extract_date)

    # Convertir la columna Fecha a formato datetime y formatearla como "DD/MM/YYYY"
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y', errors='coerce').dt.strftime('%d/%m/%Y')

    return df

# Llamar a la función y mostrar el DataFrame
smv = scrape_smv()

"--------------///// SBS Pre Publicaciones /////---------------------------------"

import pandas as pd
import logging
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.microsoft import EdgeChromiumDriverManager

def scrape_sbs_pre():
    base_url = "https://www.sbs.gob.pe/app/pp/PreProyectos/interno.asp?n="
    urls = [f"{base_url}{i:02}" for i in range(1, 14) if i not in [5, 7, 8, 9, 10]]
    sistema_mapping = {
        "01": "Normas Generales",
        "02": "Sistema Financiero",
        "03": "Sistema de Seguros",
        "04": "Sistema Privado de Pensiones",
        "06": "Otras entidades",
        "11": "PLAFT",
        "12": "COOPAC",
        "13": "AFOCAT"
    }

    service = EdgeService(EdgeChromiumDriverManager().install())
    options = Options()
    options.headless = True
    driver = webdriver.Edge(service=service, options=options)

    logging.basicConfig(level=logging.INFO)

    data = {sistema: [] for sistema in sistema_mapping.values()}

    try:
        for url in urls:
            try:
                driver.get(url)
                logging.info(f"Página web {url} abierta con éxito.")

                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//table/tbody/tr[3]/td[2]/div/a/u/strong'))
                )

                try:
                    elemento1 = driver.find_element(By.XPATH, '//table/tbody/tr[3]/td[2]/div/a/u/strong').text.strip()
                    fecha1 = driver.find_element(By.XPATH, '/html/body/table/tbody/tr/td/div/table/tbody/tr/td/table/tbody/tr[3]/td[2]/div/i').text.strip()
                except NoSuchElementException:
                    elemento1, fecha1 = None, None

                try:
                    elemento2 = driver.find_element(By.XPATH, '//table/tbody/tr[4]/td[2]/div/a/u/strong').text.strip()
                    fecha2 = driver.find_element(By.XPATH, '/html/body/table/tbody/tr/td/div/table/tbody/tr/td/table/tbody/tr[4]/td[2]/div/i').text.strip()
                except NoSuchElementException:
                    elemento2, fecha2 = None, None

                sistema = sistema_mapping[url.split("=")[-1]]

                if elemento1 or elemento2:
                    if elemento1:
                        data[sistema].append({'Definición': elemento1, 'Fecha2': fecha1})
                    if elemento2:
                        data[sistema].append({'Definición': elemento2, 'Fecha2': fecha2})
            except (TimeoutException, WebDriverException) as e:
                logging.warning(f"Error al cargar la página {url}: {e}")
                continue
    finally:
        driver.quit()
        logging.info("Navegador cerrado.")

    # Crear DataFrames y limpiar datos
    dataframes = {sistema: pd.DataFrame(info) for sistema, info in data.items() if info}

    for df in dataframes.values():
        df['Fecha'] = df['Fecha2'].apply(lambda x: x.split('-')[0].strip('()'))
        df['Fecha2'] = df['Fecha2'].apply(lambda x: x.split('-')[1].strip('()'))

        df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y').dt.strftime('%d/%m/%Y')
        df['Fecha2'] = pd.to_datetime(df['Fecha2'], format='%d/%m/%Y').dt.strftime('%d/%m/%Y')

        df['Norma'] = 'Pre publicación SBS'

    return dataframes

dataframes_sbs = scrape_sbs_pre()

# Crear un DataFrame único combinando todos los DataFrames del diccionario
sbs_pre = pd.concat(dataframes_sbs.values(), ignore_index=True)

# Eliminar la columna "Fecha2" del DataFrame combinado
sbs_pre.drop(columns=['Fecha2'], inplace=True)
    

"""
OSCE - WEB SCRAPING
"""

def scrape_osce():
    driver = webdriver.Edge()
    driver.get("https://prod2.seace.gob.pe/seacebus-uiwd-pub/buscadorPublico/buscadorPublico.xhtml")
    driver.implicitly_wait(15)
    
    tab_panel = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, 'tbBuscador:tab1'))
    )
    
    def click_element(xpath, retries=3):
        for _ in range(retries):
            try:
                element = WebDriverWait(tab_panel, 60).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                driver.execute_script("arguments[0].click();", element)
                return True
            except:
                time.sleep(1)
        return False
    
    click_element('//*[@id="tbBuscador:idFormBuscarProceso:j_idt47"]/div[3]/span')
    click_element('//*[@id="tbBuscador:idFormBuscarProceso:j_idt47_panel"]/div/ul/li[text()="Servicio"]')
    click_element('//*[@id="tbBuscador:idFormBuscarProceso:btnBuscarSelToken"]/span[2]')
    
    element_1_list, element_2_list, element_3_list = [], [], []
    
    def extract_data():
        for i in range(1, 16):
            try:
                element_1 = tab_panel.find_element(By.XPATH, f'//*[@id="tbBuscador:idFormBuscarProceso:dtProcesos_data"]/tr[{i}]/td[2]').text
                element_2 = tab_panel.find_element(By.XPATH, f'//*[@id="tbBuscador:idFormBuscarProceso:dtProcesos_data"]/tr[{i}]/td[7]').text
                element_3 = tab_panel.find_element(By.XPATH, f'//*[@id="tbBuscador:idFormBuscarProceso:dtProcesos_data"]/tr[{i}]/td[3]').text
                
                element_1_list.append(element_1)
                element_2_list.append(element_2)
                element_3_list.append(element_3)
            except:
                continue
    
    extract_data()
    current_page = 1
    while current_page < 34:
        if click_element('//*[@id="tbBuscador:idFormBuscarProceso:dtProcesos_paginator_bottom"]/span[5]/span'):
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="tbBuscador:idFormBuscarProceso:dtProcesos_data"]/tr[1]/td[2]'))
            )
            extract_data()
            current_page += 1
        else:
            break
    
    driver.quit()
    return pd.DataFrame({'Entidad': element_1_list, 'Definición': element_2_list, 'Fecha': element_3_list})

st.set_page_config(page_title="Radar Regulatorio FRM", page_icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS14bSWA3akUYXe-VV04Nw2K0QnQCwCV9SG8g&s")
st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS14bSWA3akUYXe-VV04Nw2K0QnQCwCV9SG8g&s", width=250)
st.title("Radar Regulatorio FRM")
st.markdown("### Plataforma de consulta de normativa financiera")

# Sección de botones para ejecutar el scraping
if st.button("Ejecutar Scraping SBS"):
    with st.spinner("Obteniendo datos de la SBS..."):
        sbs_data = scrape_sbs()
        st.session_state['sbs_data'] = sbs_data
        st.success("Datos obtenidos correctamente.")

if st.button("Ejecutar Scraping SMV"):
    with st.spinner("Obteniendo datos de la SMV..."):
        smv_data = scrape_smv()
        st.session_state['smv_data'] = smv_data
        st.success("Datos obtenidos correctamente.")

if st.button("Ejecutar Scraping SBS Pre Publicaciones"):
    with st.spinner("Obteniendo datos de SBS Pre Publicaciones..."):
        sbs_pre_data = scrape_sbs_pre()
        sbs_pre_df = pd.concat(sbs_pre_data.values(), ignore_index=True)
        st.session_state['sbs_pre_data'] = sbs_pre_df
        st.success("Datos obtenidos correctamente.")

if st.button("Ejecutar Scraping OSCE"):
    with st.spinner("Extrayendo datos de OSCE..."):
        df_osce = scrape_osce()
        st.session_state['df_osce'] = df_osce
        st.success("Scraping de OSCE completado.")

# Sección para visualizar las tablas individualmente
st.markdown("### Visualización de Datos")
option = st.selectbox("Selecciona una tabla para visualizar:", ["SBS", "SMV", "SBS Pre Publicaciones", "OSCE"])

data_map = {
    "SBS": 'sbs_data',
    "SMV": 'smv_data',
    "SBS Pre Publicaciones": 'sbs_pre_data',
    "OSCE": 'df_osce'
}

data_key = data_map.get(option)
if data_key in st.session_state:
    st.dataframe(st.session_state[data_key])
else:
    st.write(f"Aún no se ha ejecutado el scraping de {option}.")

# Opción para descargar los datos
for key, name in data_map.items():
    if name in st.session_state:
        df = st.session_state[name]
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"Descargar datos {key} en CSV",
            data=csv,
            file_name=f"{key}_data.csv",
            mime='text/csv'
        )

# Pie de página
st.markdown("---")
st.markdown("FRM Trainee - Franco Olivares")


