# -*- coding: utf-8 -*-
"""
Created on Sun Mar 30 14:30:56 2025

@author: usuario
"""

import streamlit as st
import pandas as pd
from Draft import scrape_sbs, scrape_smv, scrape_sbs_pre
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

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


