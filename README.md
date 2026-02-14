# AC Server Manager v4.0

Gerenciador visual completo para servidores de **Assetto Corsa**, com interface moderna e todas as configurações em um só lugar.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![Windows](https://img.shields.io/badge/Plataforma-Windows-0078D6?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/Licen%C3%A7a-Livre-green)

---

## Funcionalidades

### Instalação Automática
- Baixa e instala o [AssettoServer](https://github.com/compujuckel/AssettoServer) direto do GitHub
- Copia o executável original do jogo automaticamente
- Auto-instala dependências Python (`ttkbootstrap`) na primeira execução

### Configuração do Servidor
- Nome, senha, senha de admin e mensagem de boas-vindas
- Portas UDP, TCP e HTTP
- Max. jogadores, threads, taxa de envio (Hz)
- Modo pickup, loop, registro no lobby
- Entry list com travamento (para campeonatos)
- Votação e kick por quórum

### Gerenciamento de Carros
- Lista de carros disponíveis lida diretamente da pasta do jogo
- Adição ao grid com quantidade customizável
- Remoção individual ou completa do grid
- Cópia automática de conteúdo (carros e skins)

### Pista e Sessões
- Seleção de pista com detecção de layouts
- Preview do mapa da pista (quando disponível)
- Sessões configuráveis: Booking, Treino Livre, Classificação e Corrida
- Laps, tempo de espera, overtime e tela de resultado
- Grid invertido e pit window

### Realismo e Assistências
- ABS, Controle de Tração, Estabilidade
- Autoclutch, cobertores de pneu, espelho virtual forçado
- Taxas de dano, combustível e desgaste de pneus
- Regra de largada, penalidade de gás, contatos por km
- Pneus legais customizáveis
- Lastro máximo

### CSP Pit Limiter
- Desativar o limitador de velocidade forçado nos boxes
- Velocidade customizada dos boxes (km/h)
- Ghosting (fantasma) nos boxes
- Permitir contramão sem punição
- Gera automaticamente o arquivo `csp_extra_options.ini`

### Clima e Pista Dinâmica
- 9 tipos de clima (neblina, limpo, nublado, chuva, tempestade)
- Temperatura ambiente e do asfalto com variação
- Vento (velocidade, direção, variação)
- Ângulo do sol e multiplicador de tempo
- Pista dinâmica: aderência inicial, aleatoriedade, ganho por volta

---

## Requisitos

- **Windows 10/11**
- **Python 3.8+**
- **Assetto Corsa** instalado (para o conteúdo de carros e pistas)

> As dependências Python são instaladas automaticamente na primeira execução.

---

## Como Usar

### 1. Executar

```bash
python Servidor.py
```

Ou clique duas vezes no arquivo `Servidor.py`.

> **Dica:** Execute como administrador para criação de links simbólicos (cópia otimizada de pistas).

### 2. Configurar Pastas

Na aba **Instalação**:
- **Pasta do Jogo** → Selecione a pasta raiz do Assetto Corsa (ex: `C:\Program Files\Steam\steamapps\common\assettocorsa`)
- **Pasta do Servidor** → Selecione onde deseja instalar/manter o servidor dedicado

### 3. Instalar o Servidor

Clique em **Instalar AssettoServer** para baixar automaticamente a última versão.

### 4. Montar o Grid

Na aba **Carros**:
1. Selecione um carro da lista
2. Defina a quantidade
3. Clique em **Adicionar ao Grid**
4. Clique em **Gerar Entry List** na barra inferior

### 5. Configurar e Salvar

Ajuste as configurações nas demais abas e clique em **SALVAR TUDO**.

### 6. Iniciar

Clique em **Iniciar Servidor**. Uma janela CMD será aberta com o servidor rodando.

---

## Arquivos Gerados

| Arquivo | Localização | Descrição |
|---------|-------------|-----------|
| `server_cfg.ini` | `servidor/cfg/` | Configuração principal do servidor |
| `entry_list.ini` | `servidor/cfg/` | Lista de carros e slots |
| `csp_extra_options.ini` | `servidor/cfg/` | Opções extras CSP (pit limiter, contramão) |
| `ac_manager_config.json` | Pasta do app | Salva caminhos e preferências locais |

---

## Interface

A interface é organizada em **6 abas**:

| Aba | Conteúdo |
|-----|----------|
| Instalação | Pastas do jogo/servidor, instalação do AssettoServer |
| Servidor | Nome, senhas, portas, rede, votação |
| Carros | Seleção de carros, grid, entry list |
| Pista & Sessões | Pista, layouts, booking/treino/quali/corrida |
| Realismo | Assistências, taxas, regras, CSP Pit Limiter |
| Clima | Clima, temperaturas, vento, pista dinâmica |

---

## Controles do Servidor

Na barra inferior:

- **SALVAR TUDO** — Gera `server_cfg.ini` + `csp_extra_options.ini`
- **Gerar Entry List** — Gera `entry_list.ini` com base no grid
- **Iniciar Servidor** — Abre o servidor em uma janela CMD
- **Parar Servidor** — Encerra o processo do servidor
- **Reiniciar Servidor** — Para e reinicia automaticamente
- **Abrir Pasta** — Abre a pasta do servidor no Explorer

---

## Solução de Problemas

| Problema | Solução |
|----------|---------|
| Pit limiter travado em 80 km/h | Use as opções de **CSP Pit Limiter** na aba Realismo |
| Erro ao copiar pista | Execute como administrador (links simbólicos) |
| Dependências não instalam | Execute `pip install ttkbootstrap` manualmente |
| Servidor não inicia | Verifique se `AssettoServer.exe` ou `acServer.exe` existe na pasta |
| Carros/pistas não aparecem | Confirme que a pasta do jogo está correta |

---

## Tecnologias

- **Python 3** + **tkinter**
- **ttkbootstrap** (tema Superhero)
- **AssettoServer** (servidor dedicado)
