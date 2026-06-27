import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO
import tkintermapview
import random

# ==========================================
# CONSTANTES (APIs, Cores e Valores Fixos)
# ==========================================
API_POKE_URL = "https://pokeapi.co/api/v2/pokemon/"
API_POKE_TYPE_URL = "https://pokeapi.co/api/v2/type/"
API_POKE_SPECIES_URL = "https://pokeapi.co/api/v2/pokemon-species/"

# Substitui pela tua chave gratuita do OpenWeatherMap
URL_WEATHER = "http://api.openweathermap.org/data/2.5/weather"
API_WEATHER = "3b3ddc5f98b8f6502b43eea92f40a73d"

COR_FUNDO_APP = "#FFF065"
COR_FUNDO_PAINEL = "#FFFFFF"
COR_FUNDO_DEX = "#FFFFFF"
COR_BOTAO_CATCH = "#FF0000"
COR_TEXTO_CLARO = "#7A7A7A"

CUSTO_POKEBOLAS = 20
RECOMPENSA_CATCH = 15

CLIMA_TIPO = {
    "Rain": "water",
    "Snow": "ice",
    "Thunderstorm": "electric",
    "Clouds": "grass",
    "Mist": "ghost",
    "Fog": "ghost",
}

TODOS_OS_TIPOS = [
    "normal", "fighting", "flying", "poison", "ground", "rock", "bug", "ghost", 
    "steel", "fire", "water", "grass", "electric", "psychic", "ice", "dragon", "dark", "fairy"
]

# ==========================================
# VARIÁVEIS DE ESTADO
# ==========================================
pokeDollars = 100
pokeBolas = 5
inventario = {}
pokemonAtual = None
imagemAtual = None
taxaCapturaAtual = 255
isRaroAtual = False

# ==========================================
# LÓGICA DO JOGO
# ==========================================

def atualizarStatus():
    totalCapturados = sum(inventario.values())
    textoStatus = f"🪙 {pokeDollars}€  |  🔴 Bolas: {pokeBolas}  |  🎒 Total: {totalCapturados}"
    labelStatus.config(text=textoStatus)

def comprarPokeBolas():
    global pokeDollars, pokeBolas
    
    if pokeDollars >= CUSTO_POKEBOLAS:
        pokeDollars -= CUSTO_POKEBOLAS
        pokeBolas += 5
        atualizarStatus()
        messagebox.showinfo("PokéMart", "Compraste 5 Pokébolas!")
    else:
        messagebox.showwarning("PokéMart", "Não tens dinheiro suficiente!")

def explorarArea():
    global pokemonAtual, imagemAtual, taxaCapturaAtual, isRaroAtual
    cidadeEscolhida = entryCidade.get()
    
    if not cidadeEscolhida:
        messagebox.showerror("Erro", "Escreve o nome de uma cidade!")
        return

    try:
        # 1. Clima e Mapa
        params = {'q': cidadeEscolhida, 'appid': API_WEATHER, 'units': 'metric', 'lang': 'pt'}
        resp_clima = requests.get(URL_WEATHER, params=params).json()

        if resp_clima.get("cod") != 200:
            labelEncontro.config(text="Radar sem sinal. Tenta outra cidade.")
            return

        lat, lon = resp_clima["coord"]["lat"], resp_clima["coord"]["lon"]
        clima = resp_clima["weather"][0]["main"]
        temperatura = resp_clima["main"]["temp"]

        mapaWidget.set_position(lat, lon)
        mapaWidget.set_zoom(13)

        # 2. Lógica Dinâmica de Tipos (Temperaturas Altas vs Céu Limpo)
        if temperatura >= 30.0:
            tipo_pkmn = random.choice(["fire", "rock", "grass", "steel", "bug"])
        elif clima == "Clear":
            tipo_pkmn = random.choice(TODOS_OS_TIPOS)
        elif clima == "Night":
            tipo_pkmn = random.choice(["ghost", "poison"])
        else:
            tipo_pkmn = CLIMA_TIPO.get(clima, "normal")

        # 3. PokéAPI (Sorteio por Tipo)
        resp_tipo = requests.get(f"{API_POKE_TYPE_URL}{tipo_pkmn}").json()
        escolha = random.choice(resp_tipo["pokemon"])
        
        pokemonAtual = escolha["pokemon"]["name"].capitalize()
        id_atual = escolha["pokemon"]["url"].split("/")[-2]

        # 4. Avaliar a Raridade e a Taxa de Captura
        resp_especie = requests.get(f"{API_POKE_SPECIES_URL}{id_atual}/").json()
        isRaroAtual = resp_especie["is_legendary"] or resp_especie["is_mythical"]
        taxaCapturaAtual = resp_especie["capture_rate"]

        # 5. Processar e Mostrar a Imagem do Pokémon escolhido
        respostaApi = requests.get(f"{API_POKE_URL}{id_atual}/").json()
        urlImagem = respostaApi["sprites"]["other"]["official-artwork"]["front_default"]
        
        # Caso o Pokémon não tenha "official-artwork", tentamos o sprite normal
        if not urlImagem:
            urlImagem = respostaApi["sprites"]["front_default"]

        dadosImagem = requests.get(urlImagem).content
        imagemFormatada = Image.open(BytesIO(dadosImagem)).resize((130, 130))
        imagemAtual = ImageTk.PhotoImage(imagemFormatada)

        labelImagemPkmn.config(image=imagemAtual)
        
        # Indica se é raro ou não na interface e exibe o clima
        prefixoRaro = "🌟 LENDÁRIO/MÍTICO! " if isRaroAtual else ""
        labelEncontro.config(text=f"{prefixoRaro}Um {pokemonAtual} apareceu em {cidadeEscolhida}!\n(Clima: {clima} | Temp: {temperatura}°C)")
        
        btnCapturar.config(state="normal")
        
    except Exception as erro:
        print(f"Erro detalhado: {erro}")
        messagebox.showerror("Erro", "Falha ao contactar o radar Pokémon ou a Meteorologia.")

def capturarPokemon():
    global pokeBolas, pokemonAtual, pokeDollars

    if pokeBolas <= 0:
        messagebox.showwarning("Aviso", "Sem Pokébolas! Vai à loja comprar mais.")
        return

    pokeBolas -= 1
    taxaCapturaAtual = 255
    # Sorteio com base na taxa de captura oficial (0 a 255)
    # Quanto maior a taxaCapturaAtual (ex: Pidgey=255), mais fácil é o sorteio.
    sorteio = random.randint(0, 255)
    capturaSucesso = sorteio <= taxaCapturaAtual

    if capturaSucesso:
        if pokemonAtual in inventario:
            inventario[pokemonAtual] += 1
        else:
            inventario[pokemonAtual] = 1
            
        # Podes dar mais dinheiro se for lendário
        recompensaExtra = RECOMPENSA_CATCH * 5 if isRaroAtual else RECOMPENSA_CATCH
        pokeDollars += recompensaExtra
        
        messagebox.showinfo("Sucesso!", f"Capturaste o {pokemonAtual}!\nRecebeste {recompensaExtra}€.")
    else:
        messagebox.showerror("Oh não!", f"O {pokemonAtual} partiu a bola e fugiu!")

    # Limpar ecrã após tentativa
    labelImagemPkmn.config(image="")
    labelEncontro.config(text="Procura noutra cidade...")
    btnCapturar.config(state="disabled")
    pokemonAtual = None
    
    atualizarStatus()

# ==========================================
# POKÉDEX (NOVA JANELA)
# ==========================================

def abrirPokedex():
    janelaDex = tk.Toplevel()
    janelaDex.title("Pokédex")
    janelaDex.geometry("300x350")
    janelaDex.configure(bg=COR_FUNDO_DEX)
    
    labelTitulo = tk.Label(janelaDex, text="📖 A Tua Pokédex", font=("Arial", 14, "bold"), bg=COR_FUNDO_DEX, fg=COR_TEXTO_CLARO)
    labelTitulo.pack(pady=10)
    
    listaDex = tk.Listbox(janelaDex, font=("Arial", 12))
    listaDex.pack(fill="both", expand=True, padx=20, pady=10)
    
    for nomePkmn, quantidadePkmn in inventario.items():
        listaDex.insert(tk.END, f"{nomePkmn} (Quantidade: {quantidadePkmn})")

# ==========================================
# INTERFACE GRÁFICA PRINCIPAL
# ==========================================

def desenharInterface():
    global janelaPrincipal, labelStatus, entryCidade, mapaWidget
    global labelImagemPkmn, labelEncontro, btnCapturar

    janelaPrincipal = tk.Tk()
    janelaPrincipal.title("PokéDex Global - Aula")
    janelaPrincipal.geometry("600x780")
    janelaPrincipal.configure(bg=COR_FUNDO_APP)

    # --- Barra de Status ---
    frameStatus = tk.Frame(janelaPrincipal, bg=COR_FUNDO_PAINEL, bd=3, relief="ridge")
    frameStatus.pack(pady=10, fill="x", padx=10)
    
    labelStatus = tk.Label(frameStatus, font=("Arial", 12, "bold"), bg=COR_FUNDO_PAINEL)
    labelStatus.pack(pady=5)

    # --- Topo: Pesquisa ---
    frameTopo = tk.Frame(janelaPrincipal, bg=COR_FUNDO_APP)
    frameTopo.pack(pady=5)
    
    labelCidade = tk.Label(frameTopo, text="Cidade:", bg=COR_FUNDO_APP, fg=COR_TEXTO_CLARO, font=("Arial", 12, "bold"))
    labelCidade.grid(row=0, column=0, padx=5)
    
    entryCidade = tk.Entry(frameTopo, font=("Arial", 12))
    entryCidade.grid(row=0, column=1, padx=5)
    
    btnExplorar = tk.Button(frameTopo, text="🌍 Explorar", command=explorarArea, font=("Arial", 10, "bold"))
    btnExplorar.grid(row=0, column=2, padx=5)

    # --- Mapa ---
    frameMapa = tk.Frame(janelaPrincipal, bd=3, relief="sunken")
    frameMapa.pack(pady=10)
    
    mapaWidget = tkintermapview.TkinterMapView(frameMapa, width=500, height=200)
    mapaWidget.pack()
    mapaWidget.set_position(39.3999, -8.2245) # Coordenadas padrão de Portugal
    mapaWidget.set_zoom(6)

    # --- Área de Captura ---
    frameCombate = tk.Frame(janelaPrincipal, bg=COR_FUNDO_PAINEL, bd=5)
    frameCombate.pack(pady=10, fill="x", padx=25)
    
    labelImagemPkmn = tk.Label(frameCombate, bg=COR_FUNDO_PAINEL)
    labelImagemPkmn.pack(pady=5)
    
    labelEncontro = tk.Label(frameCombate, text="Escreve uma cidade e clica em Explorar...", bg=COR_FUNDO_PAINEL, font=("Arial", 12))
    labelEncontro.pack(pady=5)
    
    btnCapturar = tk.Button(frameCombate, text="🔴 LANÇAR POKéBOLA", command=capturarPokemon, state="disabled", font=("Arial", 14, "bold"), bg=COR_BOTAO_CATCH, fg=COR_TEXTO_CLARO)
    btnCapturar.pack(pady=10)

    # --- Botões Inferiores ---
    frameBotoes = tk.Frame(janelaPrincipal, bg=COR_FUNDO_APP)
    frameBotoes.pack(pady=10)
    
    btnLoja = tk.Button(frameBotoes, text=f"🛒 COMPRAR POKéBOLAS ({CUSTO_POKEBOLAS}€)", command=comprarPokeBolas, bg="lightblue", font=("Arial", 10, "bold"))
    btnLoja.grid(row=0, column=0, padx=10)
    
    btnDex = tk.Button(frameBotoes, text="📖 ABRIR POKéDEX", command=abrirPokedex, bg="#ED6A6A", fg="#FFFFFF", font=("Arial", 10, "bold"))
    btnDex.grid(row=0, column=1, padx=10)

    # Iniciar o jogo e abrir a janela
    atualizarStatus()
    janelaPrincipal.mainloop()

# ==========================================
# INÍCIO DO PROGRAMA
# ==========================================
if __name__ == "__main__":
    desenharInterface()