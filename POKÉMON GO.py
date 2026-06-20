import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import requests
from PIL import Image, ImageTk
from io import BytesIO
import tkintermapview
import os
import random

API_WEATHER = "3b3ddc5f98b8f6502b43eea92f40a73d"
URL_WEATHER = "http://api.openweathermap.org/data/2.5/weather"
API_POKE = "https://pokeapi.co/api/v2"
URL_MOEDA = "https://economia.awesomeapi.com.br/last/USD-EUR"

COR_FUNDO_APP = "#CC0000"
COR_FUNDO_PAINEL = "#FFFFFF"
COR_FUNDO_DEX = "#2E2E2E"
COR_BOTAO_CATCH = "#FF4444"
COR_TEXTO_CLARO = "white"

CUSTO_POKEBOLAS = 5
RECOMPENSA_CATCH = 15

# Auentar a percentage de robabilidade para cada tipo
CLIMA_TIPO = {
    "Rain":"water",
    "Snow":"ice",
    "Thunderstorm": "electric",
    "Fog":"ghost",
    "Mist": "ghost",
    "Clouds": "flying"
}

TODOS_OS_TIPOS = [
    "normal", "fighting", "flying", "poison", "ground", "rock", "bug", "ghost", 
    "steel", "fire", "water", "grass", "electric", "psychic", "ice", "dragon", "dark", "fairy"
]

jogador = "Mestre"
PokéDolars = 100.0
Pokébolas = 10
inventário = {}
pokemon_atual = None
totalCapturados = None
id_atual = None
cidade_atual = ""
preco_atual = 0.0
imagemAtual = None
taxaCapturaAtual = 255
isRaroAtual = False
job_fuga = None
job_spawn = None

# Jogo
def Status():
    totalcapturados = sum(inventário.values)
    textoStatus = f"{PokéDolars}€, pokebolas: {Pokébolas}, Pokémons: {totalCapturados}"
    labelStatus.config(text=textoStatus)

def ComprarPokebolas():
    global PokéDolars, Pokébolas
    if PokéDolars >= CUSTO_POKEBOLAS:
        Pokébolas + 1
        PokéDolars - 5
        Status()
        messagebox.showinfo("PokéMart", "Compraste 5 Pokébolas!")
    else:
        messagebox.showwarning("PokéMart", "Não tens dinheiro suficiente!")
    