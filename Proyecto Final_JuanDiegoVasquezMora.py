# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 16:54:20 2024

@author: Mora
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
import sqlite3
from flask import Flask, jsonify, request
import seaborn as sns
import matplotlib.pyplot as plt
import time

# Web Scraping
def extraer_datos():
    URL = 'https://www.scrapethissite.com/pages/simple/'
    respuesta = requests.get(URL)
    olla_de_carne = BeautifulSoup(respuesta.text, 'html.parser')
    
    paises = olla_de_carne.find_all('div', class_='country')
    
    nombres = []
    capitales = []
    poblaciones = []
    areas = []
    
    for pais in paises:
        nombre = pais.find('h3', class_='country-name').get_text(strip=True)
        capital = pais.find('span', class_='country-capital').get_text(strip=True)
        poblacion = pais.find('span', class_='country-population').get_text(strip=True)
        area = pais.find('span', class_='country-area').get_text(strip=True)
        
        nombres.append(nombre)
        capitales.append(capital)
        poblaciones.append(poblacion)
        areas.append(area)
    
    df = pd.DataFrame({
        'Nombre del país': nombres,
        'Capital': capitales,
        'Población': poblaciones,
        'Área (km²)': areas
    })
    
    return df

def guardar_en_bd(df):
    conexion = sqlite3.connect('countries.db')
    df.to_sql('Countries', conexion, if_exists='replace', index=False)
    conexion.close()

# Flask API
app = Flask(__name__)

@app.route('/api/paises', methods=['GET'])
def obtener_paises():
    capital = request.args.get('capital', None)
    
    consulta = "SELECT * FROM Countries"
    if capital:
        consulta += " WHERE Capital = ?"
        parametros = (capital,)
    else:
        parametros = ()
    
    conexion = sqlite3.connect('countries.db')
    df = pd.read_sql_query(consulta, conexion, params=parametros)
    conexion.close()
    
    return jsonify(df.to_dict(orient='records'))

#analizamos y visualizamos os datos
def analizar_y_visualizar():
    # tiempo de espera
    time.sleep(5)
    
    # Datos de api
    respuesta = requests.get('http://127.0.0.1:5000/api/paises')
    datos = respuesta.json()
    
    # creamos dataframe
    df = pd.DataFrame(datos)
    
    # nomrbes columnas
    print("Columnas en el DataFrame:", df.columns)
    
    # chequeo de lineas
    print("Primeros datos en el DataFrame:")
    print(df.head())
    
    print(df.columns)

    df['Población'] = pd.to_numeric(df['Población'], errors='coerce')
    df['Área (km²)'] = pd.to_numeric(df['Área (km²)'], errors='coerce')

    # Gráfico de distribución
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Población'], bins=10, kde=True)
    plt.title('Distribución de la Población')
    plt.savefig('grafico_distribucion.png')
    plt.show()

    # Gráfico relacional
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='Área (km²)', y='Población')
    plt.title('Relación entre Área y Población')
    plt.savefig('grafico_relacional.png')
    plt.show()

    # Gráfico categorico
    top_countries = df.nlargest(10, 'Población')
    top_countries.rename(columns={'Nombre del país': 'Nombre'}, inplace=True)

    plt.figure(figsize=(12, 6))
    sns.barplot(data=top_countries, x='Nombre', y='Población', palette='viridis')
    plt.title('Top 10 Países por Población')
    plt.xticks(rotation=40)
    plt.xlabel('Nombre del País')
    plt.ylabel('Población')
    plt.savefig('grafico_top_poblacion.png')
    plt.show()
    

if __name__ == '__main__':
    df = extraer_datos()
    guardar_en_bd(df)
    