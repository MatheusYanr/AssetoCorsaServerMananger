#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AC Server Manager v4.0 - Enhanced Edition
Gerenciador visual completo para Assetto Corsa
"""

import os
import sys
import ctypes
import shutil
import subprocess
import json
import re
import configparser
import urllib.request
import zipfile
import ssl

# ================================================================
#  AUTO-INSTALACAO DE DEPENDENCIAS
# ================================================================
def auto_install_packages():
    required = {"ttkbootstrap": "ttkbootstrap"}
    for module_name, pip_name in required.items():
        try:
            __import__(module_name)
        except ImportError:
            print(f"  > Instalando {pip_name}...")
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", pip_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                print(f"  OK - {pip_name} instalado!")
            except Exception:
                print(f"  FALHA ao instalar {pip_name}.")
                print(f"    Instale manualmente: pip install {pip_name}")
                input("Pressione ENTER para sair...")
                sys.exit(1)

auto_install_packages()

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

import ttkbootstrap as ttkb
from ttkbootstrap.constants import *  # noqa: F403

try:
    from ttkbootstrap.widgets import ToolTip
except ImportError:
    try:
        from ttkbootstrap.tooltip import ToolTip
    except ImportError:
        class ToolTip:
            def __init__(self, *a, **kw):
                pass

# ================================================================
#  CONSTANTES
# ================================================================
APP_NAME = "AC Server Manager"
APP_VERSION = "4.0"
CONFIG_FILE = "ac_manager_config.json"
GITHUB_API = "https://api.github.com/repos/compujuckel/AssettoServer/releases/latest"

WEATHER_LIST = [
    "1_heavy_fog", "2_light_fog", "3_clear", "4_mid_clear",
    "5_light_clouds", "6_mid_clouds", "7_heavy_clouds",
    "8_rain", "9_thunderstorm",
]

ABS_TC_OPTS = ["0 - Desligado", "1 - Fabrica", "2 - Forcado Ligado"]

START_RULES = [
    "0 - Carro Bloqueado na Largada",
    "1 - Teleporta ao Pit",
    "2 - Drive-Through Penalidade",
]

LISTBOX_KW = dict(
    bg="#2b2b2b", fg="#e0e0e0",
    selectbackground="#375a7f", selectforeground="#ffffff",
    font=("Segoe UI", 10), relief="flat", borderwidth=0,
    highlightthickness=1, highlightcolor="#375a7f",
)


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


# ================================================================
#  CLASSE PRINCIPAL
# ================================================================
class ACServerManager:
    def __init__(self, root: ttkb.Window):
        self.root = root
        self.root.title(f"{APP_NAME}  v{APP_VERSION}")

        # Caminhos
        self.game_path = tk.StringVar()
        self.server_path = tk.StringVar()

        # Servidor
        self.server_name = tk.StringVar(value="Meu Servidor AC")
        self.server_password = tk.StringVar()
        self.admin_password = tk.StringVar(value="admin1234")
        self.welcome_msg = tk.StringVar()
        self.udp_port = tk.IntVar(value=9600)
        self.tcp_port = tk.IntVar(value=9600)
        self.http_port = tk.IntVar(value=8081)
        self.max_clients = tk.IntVar(value=24)
        self.register_lobby = tk.BooleanVar(value=True)
        self.pickup_mode = tk.BooleanVar(value=True)
        self.loop_mode = tk.BooleanVar(value=True)
        self.locked_entry = tk.BooleanVar(value=False)
        self.sleep_time = tk.IntVar(value=1)
        self.client_send_hz = tk.IntVar(value=18)
        self.num_threads = tk.IntVar(value=2)
        self.kick_quorum = tk.IntVar(value=85)
        self.voting_quorum = tk.IntVar(value=80)
        self.vote_duration = tk.IntVar(value=20)

        # Pista
        self.track_var = tk.StringVar()
        self.layout_var = tk.StringVar()
        self.pit_boxes_info = tk.StringVar(value="--")
        self.track_layouts = {}

        # Sessoes
        self.booking_enabled = tk.BooleanVar(value=False)
        self.booking_time = tk.IntVar(value=5)
        self.practice_enabled = tk.BooleanVar(value=True)
        self.practice_time = tk.IntVar(value=10)
        self.qualify_enabled = tk.BooleanVar(value=True)
        self.qualify_time = tk.IntVar(value=10)
        self.race_laps = tk.IntVar(value=5)
        self.race_wait_time = tk.IntVar(value=60)
        self.race_over_time = tk.IntVar(value=180)
        self.result_screen_time = tk.IntVar(value=60)
        self.reversed_grid = tk.IntVar(value=0)
        self.qualify_max_wait = tk.IntVar(value=120)

        # Realismo
        self.abs_mode = tk.StringVar(value="1 - Fabrica")
        self.tc_mode = tk.StringVar(value="1 - Fabrica")
        self.stability_allowed = tk.BooleanVar(value=False)
        self.autoclutch_allowed = tk.BooleanVar(value=True)
        self.tyre_blankets = tk.BooleanVar(value=True)
        self.force_virtual_mirror = tk.BooleanVar(value=False)
        self.damage_rate = tk.IntVar(value=50)
        self.fuel_rate = tk.IntVar(value=100)
        self.tyre_wear = tk.IntVar(value=100)
        self.pit_speed_limit = tk.IntVar(value=80)
        self.allowed_tyres_out = tk.IntVar(value=2)
        self.start_rule = tk.StringVar(value=START_RULES[0])
        self.race_gas_penalty = tk.BooleanVar(value=False)
        self.max_contacts_km = tk.IntVar(value=-1)
        self.legal_tyres = tk.StringVar(value="V;E;H;M;S;SS;US;ST;I;W")
        self.max_ballast = tk.IntVar(value=0)
        self.pit_window_start = tk.IntVar(value=0)
        self.pit_window_end = tk.IntVar(value=0)

        # CSP Extra Options (pit limiter real)
        self.csp_disable_pit_limiter = tk.BooleanVar(value=False)
        self.csp_pit_speed = tk.IntVar(value=80)
        self.csp_keep_collisions = tk.BooleanVar(value=False)
        self.csp_allow_wrong_way = tk.BooleanVar(value=True)

        # Clima
        self.weather_type = tk.StringVar(value="3_clear")
        self.temp_ambient = tk.IntVar(value=26)
        self.temp_var_ambient = tk.IntVar(value=2)
        self.temp_road = tk.IntVar(value=34)
        self.temp_var_road = tk.IntVar(value=2)
        self.sun_angle = tk.DoubleVar(value=0)
        self.time_mult = tk.IntVar(value=1)
        self.wind_min = tk.IntVar(value=0)
        self.wind_max = tk.IntVar(value=5)
        self.wind_dir = tk.IntVar(value=30)
        self.wind_var = tk.IntVar(value=15)

        # Pista Dinamica
        self.dyn_start = tk.IntVar(value=95)
        self.dyn_random = tk.IntVar(value=1)
        self.dyn_lap_gain = tk.IntVar(value=15)
        self.dyn_transfer = tk.IntVar(value=90)

        # Internos
        self.server_cars = []
        self.all_game_cars = []
        self.server_process = None

        self._load_config()
        self._build_ui()

        if self.game_path.get() and self.server_path.get():
            self._refresh_all()

    # ============================================================
    #  UI CONSTRUCTION
    # ============================================================
    def _build_ui(self):
        # Header
        hdr = ttkb.Frame(self.root, bootstyle="dark")
        hdr.pack(fill="x")
        ttkb.Label(
            hdr, text=f"AC Server Manager  v{APP_VERSION}",
            font=("Segoe UI", 18, "bold"), bootstyle="inverse-dark",
        ).pack(pady=10)

        # Status Bar
        self.status_var = tk.StringVar(value="Pronto")
        ttkb.Label(
            self.root, textvariable=self.status_var,
            bootstyle="inverse-secondary", anchor="w", padding=(10, 4),
        ).pack(fill="x", side="bottom")

        # Bottom Action Bar
        action = ttkb.Frame(self.root, padding=8)
        action.pack(fill="x", side="bottom")

        ttkb.Button(
            action, text="SALVAR TUDO", bootstyle="success",
            command=self._save_all, width=20,
        ).pack(side="left", padx=4)
        ttkb.Button(
            action, text="Gerar Entry List", bootstyle="info",
            command=self._gen_entry_list, width=20,
        ).pack(side="left", padx=4)
        ttkb.Button(
            action, text="Iniciar Servidor", bootstyle="warning",
            command=self._start_server, width=20,
        ).pack(side="left", padx=4)
        ttkb.Button(
            action, text="Parar Servidor", bootstyle="danger",
            command=self._stop_server, width=18,
        ).pack(side="left", padx=4)
        ttkb.Button(
            action, text="Reiniciar Servidor", bootstyle="warning-outline",
            command=self._restart_server, width=20,
        ).pack(side="left", padx=4)
        ttkb.Button(
            action, text="Abrir Pasta", bootstyle="secondary-outline",
            command=self._open_folder, width=16,
        ).pack(side="right", padx=4)

        # Notebook
        self.nb = ttkb.Notebook(self.root, bootstyle="dark")
        self.nb.pack(expand=True, fill="both", padx=6, pady=(4, 0))

        tabs = {
            "  Instalacao  ": self._build_tab_setup,
            "  Servidor  ": self._build_tab_server,
            "  Carros  ": self._build_tab_cars,
            "  Pista & Sessoes  ": self._build_tab_track,
            "  Realismo  ": self._build_tab_realism,
            "  Clima  ": self._build_tab_weather,
        }
        for label, builder in tabs.items():
            frame = ttkb.Frame(self.nb)
            self.nb.add(frame, text=label)
            builder(frame)

    # -- TAB 1: Instalacao ---
    def _build_tab_setup(self, parent):
        frm = ttk.LabelFrame(parent, text="  Caminhos  ", padding=15)
        frm.pack(pady=15, padx=15, fill="x")

        self._path_row(frm, "Pasta do Jogo (Steam):", self.game_path)
        self._path_row(frm, "Pasta do Servidor:", self.server_path)

        ttkb.Separator(parent, orient="horizontal").pack(fill="x", padx=15, pady=8)

        btn = ttkb.Button(
            parent, text="BAIXAR E INSTALAR AssettoServer (GitHub)",
            bootstyle="success", command=self._install_server,
        )
        btn.pack(pady=10, padx=30, fill="x", ipady=8)
        ToolTip(btn, text="Baixa a versao mais recente do AssettoServer e configura automaticamente")

        info = ttkb.Frame(parent)
        info.pack(pady=10)
        if is_admin():
            ttkb.Label(info, text="Executando como Administrador - Symlinks habilitados",
                       bootstyle="success", font=("Segoe UI", 10)).pack()
        else:
            ttkb.Label(info, text="Sem privilegios de Admin - sera usada copia de arquivos (mais lento)",
                       bootstyle="warning", font=("Segoe UI", 10)).pack()

        dica = ttk.LabelFrame(parent, text="  Dica  ", padding=10)
        dica.pack(padx=15, pady=10, fill="x")
        ttkb.Label(dica, text=(
            "1. Selecione a pasta do jogo (onde esta assettocorsa.exe)\n"
            "2. Selecione uma pasta vazia para o servidor\n"
            "3. Clique em 'Baixar e Instalar' para configuracao automatica\n"
            "4. Configure carros, pista, regras e clima nas outras abas\n"
            "5. Clique em 'SALVAR TUDO' e depois 'Iniciar Servidor'"
        ), bootstyle="secondary", wraplength=800, justify="left").pack()

    # -- TAB 2: Servidor ---
    def _build_tab_server(self, parent):
        top = ttkb.Frame(parent)
        top.pack(fill="both", expand=True, padx=10, pady=8)

        col1 = ttk.LabelFrame(top, text="  Informacoes  ", padding=10)
        col1.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self._entry_row(col1, "Nome do Servidor:", self.server_name)
        self._entry_row(col1, "Senha (Jogadores):", self.server_password)
        self._entry_row(col1, "Senha Admin:", self.admin_password)
        self._entry_row(col1, "Msg Boas-Vindas:", self.welcome_msg)

        ttkb.Separator(col1, orient="horizontal").pack(fill="x", pady=10)

        self._spin_row(col1, "Max. Jogadores:", self.max_clients, 1, 100)
        ToolTip(col1.winfo_children()[-1], text="Deve ser <= ao numero de pit boxes da pista")

        col2 = ttk.LabelFrame(top, text="  Rede & Opcoes  ", padding=10)
        col2.pack(side="left", fill="both", expand=True, padx=(5, 0))

        self._spin_row(col2, "Porta UDP:", self.udp_port, 1024, 65535)
        ToolTip(col2.winfo_children()[-1], text="Porta UDP usada para a comunicacao do jogo com os jogadores.\nDeve estar aberta (liberada) no firewall e no roteador.\nSe nao souber, deixe em 9600. Todos jogadores conectam por esta porta.")
        self._spin_row(col2, "Porta TCP:", self.tcp_port, 1024, 65535)
        ToolTip(col2.winfo_children()[-1], text="Porta TCP usada para conexao inicial e troca de dados.\nNormalmente igual a porta UDP.\nTambem precisa estar aberta no firewall/roteador.")
        self._spin_row(col2, "Porta HTTP:", self.http_port, 1024, 65535)
        ToolTip(col2.winfo_children()[-1], text="Porta HTTP para a pagina de informacoes do servidor.\nPermite ver status do servidor pelo navegador (ex: http://seuip:8081).\nSe nao for usar, pode deixar o padrao 8081.")

        ttkb.Separator(col2, orient="horizontal").pack(fill="x", pady=10)

        self._check_row(col2, "Registrar no Lobby (publico)", self.register_lobby)
        ToolTip(col2.winfo_children()[-1], text="Se ativado, o servidor aparece na lista publica do Assetto Corsa.\nDesative se quiser um servidor privado (so entra quem tiver o IP).")
        self._check_row(col2, "Pickup Mode", self.pickup_mode)
        ToolTip(col2.winfo_children()[-1], text="Permite que jogadores entrem e saiam a qualquer momento.\nSe desativado, so entra quem estiver na Entry List antes da corrida.")
        self._check_row(col2, "Loop Mode", self.loop_mode)
        ToolTip(col2.winfo_children()[-1], text="O servidor reinicia automaticamente a sessao apos o termino da corrida.\nSe desativado, o servidor para apos uma corrida.")
        self._check_row(col2, "Entry List Bloqueada", self.locked_entry)
        ToolTip(col2.winfo_children()[-1], text="Se ativado, apenas jogadores com GUID na entry_list.ini podem entrar.\nUtil para campeonatos ou servidores fechados.")

        ttkb.Separator(col2, orient="horizontal").pack(fill="x", pady=10)

        self._spin_row(col2, "Client Send Hz:", self.client_send_hz, 10, 60)
        ToolTip(col2.winfo_children()[-1], text="Frequencia de envio de dados para cada jogador (pacotes por segundo).\nValor maior = jogo mais fluido, mas usa mais banda de internet.\nRecomendado: 18 (padrao). Aumente para 30+ se tiver boa conexao.")
        self._spin_row(col2, "Threads:", self.num_threads, 1, 8)
        ToolTip(col2.winfo_children()[-1], text="Numero de threads do processador usadas pelo servidor.\nRecomendado: 2 para a maioria dos casos.\nAumente se tiver muitos jogadores e um processador potente.")
        self._spin_row(col2, "Kick Quorum (%):", self.kick_quorum, 0, 100)
        ToolTip(col2.winfo_children()[-1], text="Porcentagem de votos necessaria para expulsar um jogador.\nEx: 85 = 85%% dos jogadores precisam votar SIM para o kick passar.")
        self._spin_row(col2, "Voting Quorum (%):", self.voting_quorum, 0, 100)
        ToolTip(col2.winfo_children()[-1], text="Porcentagem minima de jogadores que precisam votar\npara qualquer votacao (kick, pular sessao, etc) ser valida.\nEx: 80 = pelo menos 80%% dos jogadores devem votar.")
        self._spin_row(col2, "Duracao Voto (s):", self.vote_duration, 5, 120)
        ToolTip(col2.winfo_children()[-1], text="Tempo em segundos que uma votacao fica aberta.\nDepois desse tempo, a votacao encerra automaticamente.")

    # -- TAB 3: Carros ---
    def _build_tab_cars(self, parent):
        main = ttkb.Frame(parent)
        main.pack(fill="both", expand=True, padx=10, pady=8)

        left = ttk.LabelFrame(main, text="  Carros Disponiveis  ", padding=5)
        left.pack(side="left", fill="both", expand=True)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._filter_cars)
        se = ttkb.Entry(left, textvariable=self.search_var, bootstyle="info")
        se.pack(fill="x", padx=5, pady=(5, 2))
        ToolTip(se, text="Digite para filtrar carros")

        self.lb_game = tk.Listbox(left, selectmode=tk.EXTENDED, **LISTBOX_KW)
        sb1 = ttkb.Scrollbar(left, orient="vertical", command=self.lb_game.yview)
        self.lb_game.configure(yscrollcommand=sb1.set)
        sb1.pack(side="right", fill="y", padx=(0, 5), pady=5)
        self.lb_game.pack(fill="both", expand=True, padx=(5, 0), pady=5)

        mid = ttkb.Frame(main, padding=10)
        mid.pack(side="left", fill="y")

        ttkb.Button(mid, text="Adicionar >>", bootstyle="success",
                    command=self._add_car, width=15).pack(pady=6)
        ttkb.Button(mid, text="<< Remover", bootstyle="danger",
                    command=self._remove_car, width=15).pack(pady=6)

        ttkb.Separator(mid, orient="horizontal").pack(fill="x", pady=15)

        ttkb.Button(mid, text="Limpar Grid", bootstyle="warning-outline",
                    command=self._clear_grid, width=15).pack(pady=6)

        self.grid_count_var = tk.StringVar(value="Grid: 0")
        ttkb.Label(mid, textvariable=self.grid_count_var,
                   font=("Segoe UI", 12, "bold"), bootstyle="success").pack(pady=15)

        right = ttk.LabelFrame(main, text="  Grid do Servidor  ", padding=5)
        right.pack(side="left", fill="both", expand=True)

        self.lb_grid = tk.Listbox(right, **LISTBOX_KW)
        sb2 = ttkb.Scrollbar(right, orient="vertical", command=self.lb_grid.yview)
        self.lb_grid.configure(yscrollcommand=sb2.set)
        sb2.pack(side="right", fill="y", padx=(0, 5), pady=5)
        self.lb_grid.pack(fill="both", expand=True, padx=(5, 0), pady=5)

    # -- TAB 4: Pista & Sessoes ---
    def _build_tab_track(self, parent):
        top = ttkb.Frame(parent)
        top.pack(fill="both", expand=True, padx=10, pady=8)

        col1 = ttk.LabelFrame(top, text="  Pista  ", padding=10)
        col1.pack(side="left", fill="both", expand=True, padx=(0, 5))

        ttkb.Label(col1, text="Pista:").pack(anchor="w")
        self.combo_track = ttkb.Combobox(col1, textvariable=self.track_var, state="readonly")
        self.combo_track.pack(fill="x", pady=(0, 8))
        self.combo_track.bind("<<ComboboxSelected>>", self._on_track_change)

        ttkb.Label(col1, text="Layout:").pack(anchor="w")
        self.combo_layout = ttkb.Combobox(col1, textvariable=self.layout_var, state="readonly")
        self.combo_layout.pack(fill="x", pady=(0, 8))
        self.combo_layout.bind("<<ComboboxSelected>>", self._on_layout_change)

        ttkb.Button(col1, text="Recarregar Pistas", bootstyle="warning-outline",
                    command=self._refresh_tracks).pack(pady=5, fill="x")

        ttkb.Separator(col1, orient="horizontal").pack(fill="x", pady=10)

        pit_frame = ttk.LabelFrame(col1, text="  Pit Boxes  ", padding=8)
        pit_frame.pack(fill="x")
        ttkb.Label(pit_frame, text="Pit boxes nesta pista/layout:", bootstyle="secondary").pack(anchor="w")
        ttkb.Label(pit_frame, textvariable=self.pit_boxes_info,
                   font=("Segoe UI", 20, "bold"), bootstyle="warning").pack(pady=5)
        ttkb.Label(pit_frame, text="(Max. Jogadores deve ser <= Pit Boxes)",
                   bootstyle="secondary", font=("Segoe UI", 8)).pack()

        ttkb.Separator(col1, orient="horizontal").pack(fill="x", pady=10)

        self._spin_row(col1, "Grid Invertido (pos.):", self.reversed_grid, 0, 100)
        ToolTip(col1.winfo_children()[-1], text="0 = desligado. Ex: 8 = top 8 invertidos")
        self._spin_row(col1, "Qualify Max Espera (%):", self.qualify_max_wait, 50, 200)

        col2 = ttk.LabelFrame(top, text="  Sessoes  ", padding=10)
        col2.pack(side="left", fill="both", expand=True, padx=(5, 0))

        bf = ttk.LabelFrame(col2, text="Booking", padding=6)
        bf.pack(fill="x", pady=3)
        self._check_row(bf, "Ativar Booking", self.booking_enabled)
        self._spin_row(bf, "Tempo (min):", self.booking_time, 1, 60)

        pf = ttk.LabelFrame(col2, text="Treino Livre", padding=6)
        pf.pack(fill="x", pady=3)
        self._check_row(pf, "Ativar Treino", self.practice_enabled)
        self._spin_row(pf, "Tempo (min):", self.practice_time, 0, 180)

        qf = ttk.LabelFrame(col2, text="Classificacao", padding=6)
        qf.pack(fill="x", pady=3)
        self._check_row(qf, "Ativar Qualify", self.qualify_enabled)
        self._spin_row(qf, "Tempo (min):", self.qualify_time, 0, 60)

        rf = ttk.LabelFrame(col2, text="Corrida", padding=6)
        rf.pack(fill="x", pady=3)
        self._spin_row(rf, "Voltas:", self.race_laps, 1, 999)
        self._spin_row(rf, "Espera Pre-Corrida (s):", self.race_wait_time, 10, 300)

        ttkb.Separator(col2, orient="horizontal").pack(fill="x", pady=8)
        self._spin_row(col2, "Race Over Time (s):", self.race_over_time, 30, 600)
        self._spin_row(col2, "Tela Resultado (s):", self.result_screen_time, 10, 300)

    # -- TAB 5: Realismo ---
    def _build_tab_realism(self, parent):
        top = ttkb.Frame(parent)
        top.pack(fill="both", expand=True, padx=10, pady=8)

        c1 = ttk.LabelFrame(top, text="  Assistencias  ", padding=10)
        c1.pack(side="left", fill="both", expand=True, padx=(0, 4))

        ttkb.Label(c1, text="ABS:").pack(anchor="w")
        ttkb.Combobox(c1, textvariable=self.abs_mode, values=ABS_TC_OPTS,
                      state="readonly").pack(fill="x", pady=(0, 8))

        ttkb.Label(c1, text="Controle de Tracao:").pack(anchor="w")
        ttkb.Combobox(c1, textvariable=self.tc_mode, values=ABS_TC_OPTS,
                      state="readonly").pack(fill="x", pady=(0, 8))

        ttkb.Separator(c1, orient="horizontal").pack(fill="x", pady=8)

        self._check_row(c1, "Controle de Estabilidade", self.stability_allowed)
        self._check_row(c1, "Autoclutch Permitido", self.autoclutch_allowed)
        self._check_row(c1, "Cobertores de Pneu", self.tyre_blankets)
        self._check_row(c1, "Forcar Espelho Virtual", self.force_virtual_mirror)

        c2 = ttk.LabelFrame(top, text="  Taxas & Pit  ", padding=10)
        c2.pack(side="left", fill="both", expand=True, padx=4)

        self._spin_row(c2, "Dano (%):", self.damage_rate, 0, 400)
        self._spin_row(c2, "Consumo Combustivel (%):", self.fuel_rate, 0, 400)
        self._spin_row(c2, "Desgaste Pneus (%):", self.tyre_wear, 0, 400)

        ttkb.Separator(c2, orient="horizontal").pack(fill="x", pady=8)

        self._spin_row(c2, "Limite Pit (km/h):", self.pit_speed_limit, 20, 99999)
        self._spin_row(c2, "Pneus Fora da Pista:", self.allowed_tyres_out, 0, 4)
        self._spin_row(c2, "Max. Lastro (kg):", self.max_ballast, 0, 300)

        ttkb.Separator(c2, orient="horizontal").pack(fill="x", pady=8)

        self._spin_row(c2, "Pit Window Inicio:", self.pit_window_start, 0, 999)
        self._spin_row(c2, "Pit Window Fim:", self.pit_window_end, 0, 999)
        ToolTip(c2.winfo_children()[-1], text="0 = sem pit obrigatorio")

        c2b = ttk.LabelFrame(top, text="  CSP Pit Limiter  ", padding=10)
        c2b.pack(side="left", fill="both", expand=True, padx=4)

        self._check_row(c2b, "Desativar Limitador Forcado", self.csp_disable_pit_limiter)
        ToolTip(c2b.winfo_children()[-1], text="Desativa o limitador de velocidade nos boxes (CSP).\nSe ativado, ignora o campo velocidade abaixo.")

        self._spin_row(c2b, "Velocidade Pit (km/h):", self.csp_pit_speed, 20, 99999)
        ToolTip(c2b.winfo_children()[-1], text="Velocidade maxima nos boxes quando o limitador esta ativo.\nSo funciona se 'Desativar Limitador' estiver DESLIGADO.")

        ttkb.Separator(c2b, orient="horizontal").pack(fill="x", pady=8)

        self._check_row(c2b, "Manter Fantasma nos Boxes", self.csp_keep_collisions)
        ToolTip(c2b.winfo_children()[-1], text="Mantem colisao desativada (ghosting) dentro dos boxes.")

        self._check_row(c2b, "Permitir Contramao", self.csp_allow_wrong_way)
        ToolTip(c2b.winfo_children()[-1], text="Permite andar na contramao sem punicao.")

        ttkb.Separator(c2b, orient="horizontal").pack(fill="x", pady=8)
        ttkb.Label(c2b, text="Essas opcoes geram o arquivo\ncsp_extra_options.ini na pasta cfg.",
                   bootstyle="secondary", font=("Segoe UI", 8), justify="left").pack(anchor="w")

        c3 = ttk.LabelFrame(top, text="  Regras  ", padding=10)
        c3.pack(side="left", fill="both", expand=True, padx=(4, 0))

        ttkb.Label(c3, text="Regra de Largada:").pack(anchor="w")
        ttkb.Combobox(c3, textvariable=self.start_rule, values=START_RULES,
                      state="readonly").pack(fill="x", pady=(0, 8))

        ttkb.Separator(c3, orient="horizontal").pack(fill="x", pady=8)

        self._check_row(c3, "Penalidade Gas na Corrida", self.race_gas_penalty)
        self._spin_row(c3, "Max. Contatos/Km:", self.max_contacts_km, -1, 50)
        ToolTip(c3.winfo_children()[-1], text="-1 = sem limite (anti-wreck)")

        ttkb.Separator(c3, orient="horizontal").pack(fill="x", pady=8)

        ttkb.Label(c3, text="Pneus Legais:").pack(anchor="w")
        ttkb.Entry(c3, textvariable=self.legal_tyres).pack(fill="x", pady=(0, 4))
        ttkb.Label(c3, text="Separados por ; (ex: V;E;H;M;S)",
                   bootstyle="secondary", font=("Segoe UI", 8)).pack(anchor="w")

    # -- TAB 6: Clima ---
    def _build_tab_weather(self, parent):
        top = ttkb.Frame(parent)
        top.pack(fill="both", expand=True, padx=10, pady=8)

        c1 = ttk.LabelFrame(top, text="  Clima & Temperatura  ", padding=10)
        c1.pack(side="left", fill="both", expand=True, padx=(0, 4))

        ttkb.Label(c1, text="Tipo de Clima:").pack(anchor="w")
        ttkb.Combobox(c1, textvariable=self.weather_type, values=WEATHER_LIST,
                      state="readonly").pack(fill="x", pady=(0, 10))

        ttkb.Separator(c1, orient="horizontal").pack(fill="x", pady=5)

        self._spin_row(c1, "Temp. Ambiente (C):", self.temp_ambient, -10, 50)
        self._spin_row(c1, "Variacao Ambiente (C):", self.temp_var_ambient, 0, 15)
        self._spin_row(c1, "Temp. Pista (C):", self.temp_road, 0, 70)
        self._spin_row(c1, "Variacao Pista (C):", self.temp_var_road, 0, 15)

        ttkb.Separator(c1, orient="horizontal").pack(fill="x", pady=8)

        sf = ttkb.Frame(c1)
        sf.pack(fill="x", pady=4)
        ttkb.Label(sf, text="Posicao do Sol:", width=20, anchor="w").pack(side="left")
        self._sun_label = ttkb.Label(sf, text=f"{self.sun_angle.get():.0f}", width=5)
        self._sun_label.pack(side="right")
        sun_scale = ttkb.Scale(
            c1, from_=-80, to=80, variable=self.sun_angle, bootstyle="warning",
            command=lambda v: self._sun_label.config(text=f"{float(v):.0f}"),
        )
        sun_scale.pack(fill="x", pady=(0, 8))
        ToolTip(sun_scale, text="-80 = noite | 0 = meio-dia | 80 = por-do-sol")

        self._spin_row(c1, "Multiplicador Tempo:", self.time_mult, 0, 60)
        ToolTip(c1.winfo_children()[-1], text="Velocidade do ciclo dia/noite. 0=desligado, 1=real")

        c2 = ttk.LabelFrame(top, text="  Vento  ", padding=10)
        c2.pack(side="left", fill="both", expand=True, padx=4)

        self._spin_row(c2, "Vel. Min. (km/h):", self.wind_min, 0, 100)
        self._spin_row(c2, "Vel. Max. (km/h):", self.wind_max, 0, 100)
        self._spin_row(c2, "Direcao (graus):", self.wind_dir, 0, 359)
        self._spin_row(c2, "Variacao Dir. (graus):", self.wind_var, 0, 180)

        c3 = ttk.LabelFrame(top, text="  Pista Dinamica  ", padding=10)
        c3.pack(side="left", fill="both", expand=True, padx=(4, 0))

        self._spin_row(c3, "Grip Inicial (%):", self.dyn_start, 50, 100)
        ToolTip(c3.winfo_children()[-1], text="% de grip no inicio da sessao")
        self._spin_row(c3, "Aleatoriedade:", self.dyn_random, 0, 10)
        self._spin_row(c3, "Ganho por Volta:", self.dyn_lap_gain, 0, 100)
        ToolTip(c3.winfo_children()[-1], text="Quanto grip cada volta adiciona")
        self._spin_row(c3, "Transfer Sessao (%):", self.dyn_transfer, 0, 100)
        ToolTip(c3.winfo_children()[-1], text="% do grip mantido entre sessoes")

    # ============================================================
    #  UI HELPERS
    # ============================================================
    def _path_row(self, parent, label, variable):
        f = ttkb.Frame(parent)
        f.pack(fill="x", pady=4)
        ttkb.Label(f, text=label, width=24, anchor="w").pack(side="left")
        ttkb.Entry(f, textvariable=variable, bootstyle="info").pack(side="left", fill="x", expand=True, padx=5)
        ttkb.Button(f, text="...", width=3, bootstyle="info-outline",
                    command=lambda: self._browse(variable)).pack(side="left")

    def _entry_row(self, parent, label, variable, **kw):
        f = ttkb.Frame(parent)
        f.pack(fill="x", pady=3)
        ttkb.Label(f, text=label, width=22, anchor="w").pack(side="left")
        ttkb.Entry(f, textvariable=variable, **kw).pack(side="left", fill="x", expand=True)

    def _spin_row(self, parent, label, variable, vmin, vmax, **kw):
        f = ttkb.Frame(parent)
        f.pack(fill="x", pady=3)
        ttkb.Label(f, text=label, width=22, anchor="w").pack(side="left")
        ttkb.Spinbox(f, from_=vmin, to=vmax, textvariable=variable, width=8, **kw).pack(side="right")

    def _check_row(self, parent, label, variable):
        f = ttkb.Frame(parent)
        f.pack(fill="x", pady=3)
        ttkb.Checkbutton(f, text=label, variable=variable,
                         bootstyle="success-round-toggle").pack(anchor="w")

    # ============================================================
    #  TRACK LOGIC
    # ============================================================
    def _refresh_tracks(self):
        tracks_dir = os.path.join(self.game_path.get(), "content", "tracks")
        if not os.path.isdir(tracks_dir):
            return
        tracks = sorted(d for d in os.listdir(tracks_dir)
                        if os.path.isdir(os.path.join(tracks_dir, d)))
        self.combo_track["values"] = tracks
        if tracks and not self.track_var.get():
            self.combo_track.current(0)
            self._on_track_change()

    def _on_track_change(self, event=None):
        track = self.track_var.get()
        if not track:
            return
        self.track_layouts = self._detect_layouts(track)
        layout_names = list(self.track_layouts.keys())
        self.combo_layout["values"] = layout_names
        if layout_names:
            self.layout_var.set(layout_names[0])
        self._on_layout_change()

    def _on_layout_change(self, event=None):
        layout = self.layout_var.get()
        pits = self.track_layouts.get(layout, 0)
        self.pit_boxes_info.set(str(pits) if pits > 0 else "? (nao detectado)")

    def _detect_layouts(self, track_name):
        track_dir = os.path.join(self.game_path.get(), "content", "tracks", track_name)
        ui_dir = os.path.join(track_dir, "ui")
        layouts = {}

        if not os.path.isdir(ui_dir):
            return {"": 0}

        for item in sorted(os.listdir(ui_dir)):
            sub = os.path.join(ui_dir, item)
            if os.path.isdir(sub):
                jf = os.path.join(sub, "ui_track.json")
                if os.path.exists(jf):
                    layouts[item] = self._read_pitboxes(jf)

        if not layouts:
            main_json = os.path.join(ui_dir, "ui_track.json")
            if os.path.exists(main_json):
                layouts[""] = self._read_pitboxes(main_json)
            else:
                layouts[""] = 0

        return layouts

    def _read_pitboxes(self, json_path):
        try:
            with open(json_path, "r", encoding="utf-8-sig") as f:
                content = f.read()
            content = re.sub(r",\s*}", "}", content)
            content = re.sub(r",\s*]", "]", content)
            data = json.loads(content)
            return int(data.get("pitboxes", 0))
        except Exception:
            return 0

    # ============================================================
    #  CAR LOGIC
    # ============================================================
    def _filter_cars(self, *_):
        term = self.search_var.get().lower()
        self.lb_game.delete(0, tk.END)
        for car in self.all_game_cars:
            if term in car.lower():
                self.lb_game.insert(tk.END, car)

    def _add_car(self):
        sel = self.lb_game.curselection()
        if not sel:
            return
        car_name = self.lb_game.get(sel[0])
        qty = simpledialog.askinteger(
            "Quantidade", f"Quantos slots de {car_name}?",
            minvalue=1, maxvalue=50, initialvalue=1,
        )
        if not qty:
            return

        src = os.path.join(self.game_path.get(), "content", "cars", car_name)
        dst_dir = os.path.join(self.server_path.get(), "content", "cars")
        dst = os.path.join(dst_dir, car_name)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        if not os.path.exists(dst):
            try:
                os.symlink(src, dst, target_is_directory=True)
            except (OSError, NotImplementedError):
                try:
                    shutil.copytree(src, dst)
                except Exception as e:
                    messagebox.showerror("Erro", f"Falha ao copiar carro:\n{e}")
                    return

        self.server_cars.append({"model": car_name, "qty": qty})
        self._update_grid_ui()

    def _remove_car(self):
        sel = self.lb_grid.curselection()
        if not sel:
            return
        for idx in sorted(sel, reverse=True):
            if idx < len(self.server_cars):
                del self.server_cars[idx]
        self._update_grid_ui()

    def _clear_grid(self):
        if messagebox.askyesno("Limpar", "Remover todos os carros do grid?"):
            self.server_cars.clear()
            self._update_grid_ui()

    def _update_grid_ui(self):
        self.lb_grid.delete(0, tk.END)
        total = 0
        for item in self.server_cars:
            self.lb_grid.insert(tk.END, f"  {item['qty']}x  |  {item['model']}")
            total += item["qty"]
        self.grid_count_var.set(f"Grid: {total}")

        for i in range(self.nb.index("end")):
            if "Carros" in self.nb.tab(i, "text"):
                self.nb.tab(i, text=f"  Carros ({total})  ")
                break

    # ============================================================
    #  REFRESH
    # ============================================================
    def _refresh_all(self):
        self.lb_game.delete(0, tk.END)
        self.all_game_cars = []
        cars_dir = os.path.join(self.game_path.get(), "content", "cars")
        if os.path.isdir(cars_dir):
            self.all_game_cars = sorted(
                d for d in os.listdir(cars_dir)
                if os.path.isdir(os.path.join(cars_dir, d))
            )
            for c in self.all_game_cars:
                self.lb_game.insert(tk.END, c)
        self._refresh_tracks()
        self._load_server_config()
        self._update_grid_ui()

    # ============================================================
    #  BROWSE
    # ============================================================
    def _browse(self, var):
        folder = filedialog.askdirectory()
        if folder:
            var.set(folder)
            self._save_config()
            self._refresh_all()

    # ============================================================
    #  CARREGAR CONFIG DO SERVIDOR (INI)
    # ============================================================
    def _load_server_config(self):
        """Le server_cfg.ini e entry_list.ini do servidor e carrega no app."""
        srv = self.server_path.get()
        if not srv:
            return

        cfg_path = os.path.join(srv, "cfg", "server_cfg.ini")
        if not os.path.exists(cfg_path):
            return

        try:
            config = configparser.ConfigParser(strict=False)
            config.optionxform = str  # preserva maiusculas
            config.read(cfg_path, encoding="utf-8")

            # --- [SERVER] ---
            if config.has_section("SERVER"):
                s = config["SERVER"]

                # Strings
                str_map = {
                    "NAME": self.server_name,
                    "PASSWORD": self.server_password,
                    "ADMIN_PASSWORD": self.admin_password,
                    "WELCOME_MESSAGE": self.welcome_msg,
                    "LEGAL_TYRES": self.legal_tyres,
                }
                for key, var in str_map.items():
                    if key in s:
                        var.set(s[key])

                # Inteiros
                int_map = {
                    "UDP_PORT": self.udp_port,
                    "TCP_PORT": self.tcp_port,
                    "HTTP_PORT": self.http_port,
                    "MAX_CLIENTS": self.max_clients,
                    "SLEEP_TIME": self.sleep_time,
                    "CLIENT_SEND_INTERVAL_HZ": self.client_send_hz,
                    "NUM_THREADS": self.num_threads,
                    "KICK_QUORUM": self.kick_quorum,
                    "VOTING_QUORUM": self.voting_quorum,
                    "VOTE_DURATION": self.vote_duration,
                    "MAX_BALLAST_KG": self.max_ballast,
                    "QUALIFY_MAX_WAIT_PERC": self.qualify_max_wait,
                    "RACE_PIT_WINDOW_START": self.pit_window_start,
                    "RACE_PIT_WINDOW_END": self.pit_window_end,
                    "REVERSED_GRID_RACE_POSITIONS": self.reversed_grid,
                    "FUEL_RATE": self.fuel_rate,
                    "DAMAGE_MULTIPLIER": self.damage_rate,
                    "TYRE_WEAR_RATE": self.tyre_wear,
                    "ALLOWED_TYRES_OUT": self.allowed_tyres_out,
                    "PIT_SPEED_LIMIT": self.pit_speed_limit,
                    "RACE_OVER_TIME": self.race_over_time,
                    "TIME_OF_DAY_MULT": self.time_mult,
                    "RESULT_SCREEN_TIME": self.result_screen_time,
                    "MAX_CONTACTS_PER_KM": self.max_contacts_km,
                }
                for key, var in int_map.items():
                    if key in s:
                        try:
                            var.set(int(s[key]))
                        except (ValueError, tk.TclError):
                            pass

                # Float
                if "SUN_ANGLE" in s:
                    try:
                        self.sun_angle.set(float(s["SUN_ANGLE"]))
                    except (ValueError, tk.TclError):
                        pass

                # Booleans (1/0)
                bool_map = {
                    "REGISTER_TO_LOBBY": self.register_lobby,
                    "PICKUP_MODE_ENABLED": self.pickup_mode,
                    "LOOP_MODE": self.loop_mode,
                    "LOCKED_ENTRY_LIST": self.locked_entry,
                    "STABILITY_ALLOWED": self.stability_allowed,
                    "AUTOCLUTCH_ALLOWED": self.autoclutch_allowed,
                    "TYRE_BLANKETS_ALLOWED": self.tyre_blankets,
                    "FORCE_VIRTUAL_MIRROR": self.force_virtual_mirror,
                }
                for key, var in bool_map.items():
                    if key in s:
                        try:
                            var.set(s[key].strip() == "1")
                        except tk.TclError:
                            pass

                # RACE_GAS_PENALTY_DISABLED e invertido
                if "RACE_GAS_PENALTY_DISABLED" in s:
                    try:
                        self.race_gas_penalty.set(s["RACE_GAS_PENALTY_DISABLED"].strip() == "0")
                    except tk.TclError:
                        pass

                # ABS / TC
                abs_tc_map = {"0": "0 - Desligado", "1": "1 - Fabrica", "2": "2 - Forcado Ligado"}
                if "ABS_ALLOWED" in s:
                    self.abs_mode.set(abs_tc_map.get(s["ABS_ALLOWED"].strip(), self.abs_mode.get()))
                if "TC_ALLOWED" in s:
                    self.tc_mode.set(abs_tc_map.get(s["TC_ALLOWED"].strip(), self.tc_mode.get()))

                # Start Rule
                start_map = {str(i): START_RULES[i] for i in range(len(START_RULES))}
                if "START_RULE" in s:
                    self.start_rule.set(start_map.get(s["START_RULE"].strip(), self.start_rule.get()))

                # Pista e layout
                track_name = s.get("TRACK", "").strip()
                config_track = s.get("CONFIG_TRACK", "").strip()
                if track_name:
                    self.track_var.set(track_name)
                    self._on_track_change()
                    if config_track:
                        self.layout_var.set(config_track)
                        self._on_layout_change()

            # --- [DYNAMIC_TRACK] ---
            if config.has_section("DYNAMIC_TRACK"):
                dt = config["DYNAMIC_TRACK"]
                for key, var in [
                    ("SESSION_START", self.dyn_start),
                    ("RANDOMNESS", self.dyn_random),
                    ("LAP_GAIN", self.dyn_lap_gain),
                    ("SESSION_TRANSFER", self.dyn_transfer),
                ]:
                    if key in dt:
                        try:
                            var.set(int(dt[key]))
                        except (ValueError, tk.TclError):
                            pass

            # --- Sessoes ---
            self.booking_enabled.set(config.has_section("BOOKING"))
            if config.has_section("BOOKING") and "TIME" in config["BOOKING"]:
                try:
                    self.booking_time.set(int(config["BOOKING"]["TIME"]))
                except (ValueError, tk.TclError):
                    pass

            self.practice_enabled.set(config.has_section("PRACTICE"))
            if config.has_section("PRACTICE") and "TIME" in config["PRACTICE"]:
                try:
                    self.practice_time.set(int(config["PRACTICE"]["TIME"]))
                except (ValueError, tk.TclError):
                    pass

            self.qualify_enabled.set(config.has_section("QUALIFY"))
            if config.has_section("QUALIFY") and "TIME" in config["QUALIFY"]:
                try:
                    self.qualify_time.set(int(config["QUALIFY"]["TIME"]))
                except (ValueError, tk.TclError):
                    pass

            if config.has_section("RACE"):
                r = config["RACE"]
                if "LAPS" in r:
                    try:
                        self.race_laps.set(int(r["LAPS"]))
                    except (ValueError, tk.TclError):
                        pass
                if "WAIT_TIME" in r:
                    try:
                        self.race_wait_time.set(int(r["WAIT_TIME"]))
                    except (ValueError, tk.TclError):
                        pass

            # --- [WEATHER_0] ---
            if config.has_section("WEATHER_0"):
                w = config["WEATHER_0"]
                if "GRAPHICS" in w:
                    self.weather_type.set(w["GRAPHICS"])
                for key, var in [
                    ("BASE_TEMPERATURE_AMBIENT", self.temp_ambient),
                    ("VARIATION_AMBIENT", self.temp_var_ambient),
                    ("BASE_TEMPERATURE_ROAD", self.temp_road),
                    ("VARIATION_ROAD", self.temp_var_road),
                    ("WIND_BASE_SPEED_MIN", self.wind_min),
                    ("WIND_BASE_SPEED_MAX", self.wind_max),
                    ("WIND_BASE_DIRECTION", self.wind_dir),
                    ("WIND_VARIATION_DIRECTION", self.wind_var),
                ]:
                    if key in w:
                        try:
                            var.set(int(w[key]))
                        except (ValueError, tk.TclError):
                            pass

            # --- CSP Extra Options ---
            csp_path = os.path.join(srv, "cfg", "csp_extra_options.ini")
            if os.path.exists(csp_path):
                csp = configparser.ConfigParser(strict=False)
                csp.optionxform = str
                csp.read(csp_path, encoding="utf-8")
                if csp.has_section("PITS_SPEED_LIMITER"):
                    ps = csp["PITS_SPEED_LIMITER"]
                    if "DISABLE_FORCED" in ps:
                        try:
                            self.csp_disable_pit_limiter.set(ps["DISABLE_FORCED"].strip() == "1")
                        except tk.TclError:
                            pass
                    if "SPEED_KMH" in ps:
                        try:
                            self.csp_pit_speed.set(int(ps["SPEED_KMH"].strip()))
                        except (ValueError, tk.TclError):
                            pass
                    if "KEEP_COLLISIONS" in ps:
                        try:
                            self.csp_keep_collisions.set(ps["KEEP_COLLISIONS"].strip() == "1")
                        except tk.TclError:
                            pass
                if csp.has_section("EXTRA_RULES"):
                    er = csp["EXTRA_RULES"]
                    if "ALLOW_WRONG_WAY" in er:
                        try:
                            self.csp_allow_wrong_way.set(er["ALLOW_WRONG_WAY"].strip() == "1")
                        except tk.TclError:
                            pass

            # --- Entry List ---
            self._load_entry_list()

            self.status_var.set("Configuracoes carregadas do servidor!")
        except Exception as e:
            print(f"Erro ao carregar config do servidor: {e}")

    def _load_entry_list(self):
        """Le entry_list.ini e reconstroi o grid de carros."""
        srv = self.server_path.get()
        if not srv:
            return

        entry_path = os.path.join(srv, "cfg", "entry_list.ini")
        if not os.path.exists(entry_path):
            return

        try:
            config = configparser.ConfigParser(strict=False)
            config.optionxform = str
            config.read(entry_path, encoding="utf-8")

            # Conta quantidade de cada modelo
            car_counts = {}
            for section in sorted(config.sections()):
                if section.startswith("CAR_"):
                    model = config[section].get("MODEL", "").strip()
                    if model:
                        car_counts[model] = car_counts.get(model, 0) + 1

            if car_counts:
                self.server_cars = [{"model": m, "qty": q} for m, q in car_counts.items()]
        except Exception as e:
            print(f"Erro ao carregar entry list: {e}")

    # ============================================================
    #  CONFIG SAVE / LOAD
    # ============================================================
    def _save_config(self):
        data = {}
        for name in dir(self):
            obj = getattr(self, name, None)
            if isinstance(obj, tk.StringVar):
                data[name] = obj.get()
            elif isinstance(obj, tk.IntVar):
                data[name] = obj.get()
            elif isinstance(obj, tk.DoubleVar):
                data[name] = obj.get()
            elif isinstance(obj, tk.BooleanVar):
                data[name] = obj.get()
        data["server_cars"] = self.server_cars
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for key, value in data.items():
                if key == "server_cars":
                    self.server_cars = value
                    continue
                obj = getattr(self, key, None)
                if obj is None:
                    continue
                if isinstance(obj, (tk.StringVar, tk.IntVar, tk.DoubleVar, tk.BooleanVar)):
                    try:
                        obj.set(value)
                    except Exception:
                        pass
        except Exception:
            pass

    # ============================================================
    #  GERAR server_cfg.ini
    # ============================================================
    def _save_all(self):
        srv = self.server_path.get()
        if not srv:
            messagebox.showwarning("Aviso", "Defina a pasta do servidor primeiro!")
            return

        cfg_dir = os.path.join(srv, "cfg")
        os.makedirs(cfg_dir, exist_ok=True)

        unique_cars = list(dict.fromkeys(c["model"] for c in self.server_cars))
        cars_str = ";".join(unique_cars) if unique_cars else ""
        total_slots = sum(c["qty"] for c in self.server_cars)

        if total_slots > self.max_clients.get():
            messagebox.showwarning(
                "Aviso",
                f"Grid ({total_slots}) > Max. Jogadores ({self.max_clients.get()})!\n"
                "Ajustando Max. Jogadores automaticamente.",
            )
            self.max_clients.set(total_slots)

        abs_v = self.abs_mode.get().split(" ")[0]
        tc_v = self.tc_mode.get().split(" ")[0]
        sr_v = self.start_rule.get().split(" ")[0]
        layout = self.layout_var.get()

        content = f"""[SERVER]
NAME={self.server_name.get()}
CARS={cars_str}
TRACK={self.track_var.get()}
CONFIG_TRACK={layout}
SUN_ANGLE={self.sun_angle.get():.0f}
PASSWORD={self.server_password.get()}
ADMIN_PASSWORD={self.admin_password.get()}
UDP_PORT={self.udp_port.get()}
TCP_PORT={self.tcp_port.get()}
HTTP_PORT={self.http_port.get()}
MAX_BALLAST_KG={self.max_ballast.get()}
QUALIFY_MAX_WAIT_PERC={self.qualify_max_wait.get()}
RACE_PIT_WINDOW_START={self.pit_window_start.get()}
RACE_PIT_WINDOW_END={self.pit_window_end.get()}
REVERSED_GRID_RACE_POSITIONS={self.reversed_grid.get()}
LOCKED_ENTRY_LIST={1 if self.locked_entry.get() else 0}
PICKUP_MODE_ENABLED={1 if self.pickup_mode.get() else 0}
LOOP_MODE={1 if self.loop_mode.get() else 0}
SLEEP_TIME={self.sleep_time.get()}
CLIENT_SEND_INTERVAL_HZ={self.client_send_hz.get()}
SEND_BUFFER_SIZE=0
RACE_OVER_TIME={self.race_over_time.get()}
KICK_QUORUM={self.kick_quorum.get()}
VOTING_QUORUM={self.voting_quorum.get()}
VOTE_DURATION={self.vote_duration.get()}
BLACKLIST_MODE=1
FUEL_RATE={self.fuel_rate.get()}
DAMAGE_MULTIPLIER={self.damage_rate.get()}
TYRE_WEAR_RATE={self.tyre_wear.get()}
ALLOWED_TYRES_OUT={self.allowed_tyres_out.get()}
ABS_ALLOWED={abs_v}
TC_ALLOWED={tc_v}
STABILITY_ALLOWED={1 if self.stability_allowed.get() else 0}
AUTOCLUTCH_ALLOWED={1 if self.autoclutch_allowed.get() else 0}
TYRE_BLANKETS_ALLOWED={1 if self.tyre_blankets.get() else 0}
FORCE_VIRTUAL_MIRROR={1 if self.force_virtual_mirror.get() else 0}
START_RULE={sr_v}
RACE_GAS_PENALTY_DISABLED={0 if self.race_gas_penalty.get() else 1}
TIME_OF_DAY_MULT={self.time_mult.get()}
RESULT_SCREEN_TIME={self.result_screen_time.get()}
MAX_CONTACTS_PER_KM={self.max_contacts_km.get()}
REGISTER_TO_LOBBY={1 if self.register_lobby.get() else 0}
MAX_CLIENTS={self.max_clients.get()}
NUM_THREADS={self.num_threads.get()}
UDP_PLUGIN_LOCAL_PORT=0
UDP_PLUGIN_ADDRESS=
AUTH_PLUGIN_ADDRESS=
LEGAL_TYRES={self.legal_tyres.get()}
PIT_SPEED_LIMIT={self.pit_speed_limit.get()}
WELCOME_MESSAGE={self.welcome_msg.get()}
EXTERNAL_SERVER_IP=

[DYNAMIC_TRACK]
SESSION_START={self.dyn_start.get()}
RANDOMNESS={self.dyn_random.get()}
LAP_GAIN={self.dyn_lap_gain.get()}
SESSION_TRANSFER={self.dyn_transfer.get()}
"""
        if self.booking_enabled.get():
            content += f"""
[BOOKING]
NAME=Booking
TIME={self.booking_time.get()}
"""

        if self.practice_enabled.get():
            content += f"""
[PRACTICE]
NAME=Practice
TIME={self.practice_time.get()}
IS_OPEN=1
"""

        if self.qualify_enabled.get():
            content += f"""
[QUALIFY]
NAME=Qualify
TIME={self.qualify_time.get()}
IS_OPEN=1
"""

        content += f"""
[RACE]
NAME=Race
LAPS={self.race_laps.get()}
WAIT_TIME={self.race_wait_time.get()}
IS_OPEN=1

[WEATHER_0]
GRAPHICS={self.weather_type.get()}
BASE_TEMPERATURE_AMBIENT={self.temp_ambient.get()}
VARIATION_AMBIENT={self.temp_var_ambient.get()}
BASE_TEMPERATURE_ROAD={self.temp_road.get()}
VARIATION_ROAD={self.temp_var_road.get()}
WIND_BASE_SPEED_MIN={self.wind_min.get()}
WIND_BASE_SPEED_MAX={self.wind_max.get()}
WIND_BASE_DIRECTION={self.wind_dir.get()}
WIND_VARIATION_DIRECTION={self.wind_var.get()}
"""

        try:
            cfg_path = os.path.join(cfg_dir, "server_cfg.ini")
            with open(cfg_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Gerar csp_extra_options.ini
            csp_content = f"""[PITS_SPEED_LIMITER]
DISABLE_FORCED={1 if self.csp_disable_pit_limiter.get() else 0}
SPEED_KMH={self.csp_pit_speed.get()}
KEEP_COLLISIONS={1 if self.csp_keep_collisions.get() else 0}

[EXTRA_RULES]
ALLOW_WRONG_WAY={1 if self.csp_allow_wrong_way.get() else 0}
"""
            csp_path = os.path.join(cfg_dir, "csp_extra_options.ini")
            with open(csp_path, "w", encoding="utf-8") as f:
                f.write(csp_content)

            self._copy_track_content()

            self._save_config()
            self.status_var.set(f"Configuracao salva!  |  Carros: {len(unique_cars)}  |  Slots: {total_slots}")
            messagebox.showinfo(
                "Salvo",
                f"Configuracao salva com sucesso!\n\n"
                f"Pista: {self.track_var.get()} {('(' + layout + ')') if layout else ''}\n"
                f"Carros: {len(unique_cars)} modelos, {total_slots} slots\n"
                f"Max. Jogadores: {self.max_clients.get()}\n"
                f"Pit Speed: {self.pit_speed_limit.get()} km/h",
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar:\n{e}")

    def _copy_track_content(self):
        track = self.track_var.get()
        if not track:
            return
        src = os.path.join(self.game_path.get(), "content", "tracks", track)
        dst_dir = os.path.join(self.server_path.get(), "content", "tracks")
        dst = os.path.join(dst_dir, track)
        if not os.path.exists(src):
            return
        os.makedirs(dst_dir, exist_ok=True)
        if not os.path.exists(dst):
            try:
                os.symlink(src, dst, target_is_directory=True)
            except (OSError, NotImplementedError):
                try:
                    shutil.copytree(src, dst)
                except Exception:
                    pass

    # ============================================================
    #  GERAR entry_list.ini
    # ============================================================
    def _gen_entry_list(self):
        srv = self.server_path.get()
        if not srv:
            messagebox.showwarning("Aviso", "Defina a pasta do servidor!")
            return
        if not self.server_cars:
            messagebox.showwarning("Aviso", "Adicione carros ao grid primeiro!")
            return

        cfg_dir = os.path.join(srv, "cfg")
        os.makedirs(cfg_dir, exist_ok=True)

        try:
            lines = []
            counter = 0
            for item in self.server_cars:
                model = item["model"]
                skins_path = os.path.join(srv, "content", "cars", model, "skins")
                skins = []
                if os.path.isdir(skins_path):
                    skins = [d for d in os.listdir(skins_path)
                             if os.path.isdir(os.path.join(skins_path, d))]

                for i in range(item["qty"]):
                    skin = skins[i % len(skins)] if skins else "default"
                    lines.append(
                        f"[CAR_{counter}]\n"
                        f"MODEL={model}\n"
                        f"SKIN={skin}\n"
                        f"SPECTATOR_MODE=0\n"
                        f"DRIVERNAME=\n"
                        f"TEAM=\n"
                        f"GUID=\n"
                        f"BALLAST=0\n"
                        f"RESTRICTOR=0\n"
                    )
                    counter += 1

            with open(os.path.join(cfg_dir, "entry_list.ini"), "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            self.status_var.set(f"Entry list gerada com {counter} slots!")
            messagebox.showinfo("Sucesso", f"Entry list salva com {counter} slots!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar entry list:\n{e}")

    # ============================================================
    #  INSTALAR SERVIDOR
    # ============================================================
    def _install_server(self):
        dest = self.server_path.get()
        src_game = self.game_path.get()
        if not dest or not src_game:
            messagebox.showwarning("Aviso", "Selecione as pastas do jogo e do servidor!")
            return

        if os.path.exists(dest) and os.listdir(dest):
            if messagebox.askyesno("Limpar", "A pasta destino nao esta vazia.\nDeseja limpar antes de instalar?"):
                try:
                    shutil.rmtree(dest)
                    os.makedirs(dest)
                except Exception as e:
                    messagebox.showerror("Erro", f"Falha ao limpar pasta:\n{e}")
                    return
            else:
                return

        os.makedirs(dest, exist_ok=True)
        self.status_var.set("Baixando AssettoServer...")
        self.root.update()

        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            req = urllib.request.Request(GITHUB_API, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, context=ctx) as r:
                data = json.loads(r.read().decode())
                dl_url = next(
                    (a["browser_download_url"] for a in data["assets"] if "win-x64" in a["name"]), None
                )

            if not dl_url:
                messagebox.showerror("Erro", "Nao foi possivel encontrar o download win-x64!")
                return

            self.status_var.set("Baixando...")
            self.root.update()

            zip_path = os.path.join(dest, "server.zip")
            with urllib.request.urlopen(dl_url, context=ctx) as r, open(zip_path, "wb") as f:
                shutil.copyfileobj(r, f)

            self.status_var.set("Extraindo...")
            self.root.update()

            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(dest)
            os.remove(zip_path)

            for rel in ["server/acServer.exe", "acServer.exe"]:
                orig = os.path.join(src_game, rel)
                if os.path.exists(orig):
                    shutil.copy2(orig, dest)
                    break

            self.status_var.set("AssettoServer instalado com sucesso!")
            messagebox.showinfo("Sucesso", "AssettoServer instalado com sucesso!")
        except Exception as e:
            self.status_var.set("Erro na instalacao")
            messagebox.showerror("Erro", f"Falha na instalacao:\n{e}")

    # ============================================================
    #  INICIAR SERVIDOR
    # ============================================================
    def _start_server(self):
        srv = self.server_path.get()
        if not srv:
            messagebox.showwarning("Aviso", "Defina a pasta do servidor!")
            return
        if self.server_process and self.server_process.poll() is None:
            messagebox.showinfo("Info", "O servidor ja esta rodando!\nPare-o primeiro ou use Reiniciar.")
            return
        for exe_name in ["AssettoServer.exe", "acServer.exe"]:
            exe = os.path.join(srv, exe_name)
            if os.path.exists(exe):
                try:
                    self.server_process = subprocess.Popen(
                        ["cmd.exe", "/c", "start", "AC Server", "/wait", exe],
                        cwd=srv,
                    )
                    self.status_var.set(f"Servidor iniciado: {exe_name}  (CMD aberto)")
                    return
                except Exception as e:
                    messagebox.showerror("Erro", f"Falha ao iniciar:\n{e}")
                    return
        messagebox.showerror(
            "Nao Encontrado",
            "Nenhum executavel do servidor encontrado!\n"
            "Procurado: AssettoServer.exe, acServer.exe",
        )

    def _stop_server(self):
        stopped = False
        # Tenta matar pelo processo guardado
        if self.server_process and self.server_process.poll() is None:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                stopped = True
            except Exception:
                try:
                    self.server_process.kill()
                    stopped = True
                except Exception:
                    pass
            self.server_process = None

        # Tambem tenta matar por nome (caso o CMD tenha aberto separado)
        for exe_name in ["AssettoServer.exe", "acServer.exe"]:
            try:
                result = subprocess.run(
                    ["taskkill", "/f", "/im", exe_name],
                    capture_output=True, text=True,
                )
                if result.returncode == 0:
                    stopped = True
            except Exception:
                pass

        if stopped:
            self.status_var.set("Servidor parado!")
            messagebox.showinfo("Parado", "Servidor encerrado com sucesso!")
        else:
            self.status_var.set("Nenhum servidor encontrado rodando")
            messagebox.showinfo("Info", "Nenhum processo do servidor foi encontrado rodando.")

    def _restart_server(self):
        self.status_var.set("Reiniciando servidor...")
        self.root.update()
        # Para o servidor atual
        if self.server_process and self.server_process.poll() is None:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except Exception:
                try:
                    self.server_process.kill()
                except Exception:
                    pass
            self.server_process = None
        for exe_name in ["AssettoServer.exe", "acServer.exe"]:
            try:
                subprocess.run(["taskkill", "/f", "/im", exe_name],
                               capture_output=True, text=True)
            except Exception:
                pass
        # Espera um momento e inicia novamente
        self.root.after(1500, self._start_server)

    # ============================================================
    #  ABRIR PASTA
    # ============================================================
    def _open_folder(self):
        srv = self.server_path.get()
        if srv and os.path.isdir(srv):
            os.startfile(srv)
        else:
            messagebox.showwarning("Aviso", "Pasta do servidor nao definida ou nao existe!")


# ================================================================
#  MAIN
# ================================================================
if __name__ == "__main__":
    try:
        root = ttkb.Window(
            title=f"{APP_NAME} v{APP_VERSION}",
            themename="superhero",
            size=(1150, 850),
            minsize=(950, 700),
        )
        root.place_window_center()
        app = ACServerManager(root)
        root.mainloop()
    except Exception as e:
        import traceback
        print("\n" + "=" * 60)
        print("  ERRO AO INICIAR O AC SERVER MANAGER")
        print("=" * 60)
        traceback.print_exc()
        print("=" * 60)
        input("\nPressione ENTER para fechar...")
