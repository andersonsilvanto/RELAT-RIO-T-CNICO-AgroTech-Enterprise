import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime

# Adicionado suppress_callback_exceptions=True para suportar componentes em abas dinâmicas
app = dash.Dash(__name__, title="AgroTech Enterprise Global Platform & M&A", suppress_callback_exceptions=True)

FAZENDAS_CONFIG = {
    "Fazenda Santa Rita (S. J. da Boa Vista - SP)": {
        "lat": -21.9706, "lon": -46.7972, "base_iot": 45, 
        "cultura": "Café Especial", "hectares": 1200, "ip_edge": "192.168.10.15",
        "valor_compra": 12000000, "valor_mercado": 15500000, "custo_op_anual": 1800000, "receita_est": 3500000, "status_ativo": "Operacional (Matriz)"
    },
    "Grupo Agro Ribeirão (Ribeirão Preto - SP)": {
        "lat": -21.1775, "lon": -47.8103, "base_iot": 210, 
        "cultura": "Cana / Citros", "hectares": 4500, "ip_edge": "10.200.4.50",
        "valor_compra": 45000000, "valor_mercado": 58000000, "custo_op_anual": 6200000, "receita_est": 12500000, "status_ativo": "Operacional"
    },
    "Fazenda Boa Vista (Rio Verde - GO)": {
        "lat": -17.7989, "lon": -50.9194, "base_iot": 340, 
        "cultura": "Soja / Milho", "hectares": 8900, "ip_edge": "172.16.50.12",
        "valor_compra": 75000000, "valor_mercado": 96000000, "custo_op_anual": 9800000, "receita_est": 21000000, "status_ativo": "Operacional"
    },
    "Agropecuária Chapadão (Sorriso - MT)": {
        "lat": -12.5427, "lon": -55.7196, "base_iot": 520, 
        "cultura": "Soja Extensiva", "hectares": 15000, "ip_edge": "10.50.12.99",
        "valor_compra": 130000000, "valor_mercado": 170000000, "custo_op_anual": 15000000, "receita_est": 38000000, "status_ativo": "Operacional"
    }
}

def buscar_dados_enterprise_avancados(nome_fazenda):
    config = FAZENDAS_CONFIG.get(nome_fazenda, list(FAZENDAS_CONFIG.values())[0])
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={config['lat']}&longitude={config['lon']}&current=temperature_2m,relative_humidity_2m,precipitation,soil_temperature_0cm,soil_moisture_0_to_1cm"
    
    temp, umidade, chuva, temp_solo, umidade_solo = 28.0, 50.0, 0.0, 25.0, 0.28
    try:
        response = requests.get(url, timeout=4)
        if response.status_code == 200:
            data = response.json().get("current", {})
            temp = data.get("temperature_2m", 28.0)
            umidade = data.get("relative_humidity_2m", 50.0)
            chuva = data.get("precipitation", 0.0)
            temp_solo = data.get("soil_temperature_0cm", 25.0)
            umidade_solo = data.get("soil_moisture_0_to_1cm", 0.28) * 100
    except:
        pass

    horas = ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00"]
    sensores = [config['base_iot'] + (i*4) for i in range(len(horas))]
    cpu_edge = [min(99, int(40 + (temp * 0.5) + (i * 2))) for i in range(len(horas))]
    latencia = [round(90 + (temp * 0.2), 1) for _ in horas]
    consumo_banda = [round(1.5 + (temp * 0.05) + (i * 0.1), 2) for i in range(len(horas))]

    df = pd.DataFrame({
        "Hora": horas, "Sensores_IoT": sensores, "CPU_Edge_Pct": cpu_edge,
        "Latencia_Rede_ms": latencia, "Banda_Satelite_MBs": consumo_banda
    })

    buffer_disco = round(12.4 + (temp * 0.15), 1)
    rssi_lora = -72 if chuva == 0 else -85
    status_node = "SAUDÁVEL" if temp <= 32 else ("ALERTA TÉRMICO" if temp <= 38 else "CRÍTICO")
    cor_status = "#2ea043" if temp <= 32 else ("#d29922" if temp <= 38 else "#f85149")

    metrica_clima = {
        "temp": temp, "umidade": umidade, "chuva": chuva, "temp_solo": temp_solo,
        "umidade_solo": round(umidade_solo, 1), "cultura": config["cultura"],
        "hectares": f"{config['hectares']:,} ha", "ip_edge": config["ip_edge"],
        "status_node": status_node, "cor_status": cor_status, "buffer_disco": buffer_disco, "rssi_lora": rssi_lora
    }
    return df, metrica_clima

COR_FUNDO = "#0d1117"
COR_CARD = "#161b22"
COR_TEXTO = "#c9d1d9"
COR_BORDA = "#30363d"

app.layout = html.Div(style={'fontFamily': 'sans-serif', 'padding': '30px', 'backgroundColor': COR_FUNDO, 'color': COR_TEXTO, 'minHeight': '100vh'}, children=[
    
    html.Div(style={'textAlign': 'center', 'marginBottom': '20px', 'borderBottom': f'1px solid {COR_BORDA}', 'paddingBottom': '15px'}, children=[
        html.H1("🛰️ AgroTech Enterprise | Cloud Edge & Land M&A Management", style={'color': '#58a6ff', 'margin': '0', 'fontSize': '22px'}),
        html.P("Plataforma Integrada de Observabilidade de Borda e Governança Financeira de Ativos Rurais", style={'color': '#8b949e', 'marginTop': '6px', 'fontSize': '13px'}),
    ]),

    dcc.Tabs(id='abas-principal', value='aba-noc', children=[
        dcc.Tab(label='📡 NOC & Telemetria de Borda', value='aba-noc', style={'backgroundColor': COR_CARD, 'color': COR_TEXTO, 'borderColor': COR_BORDA}, selected_style={'backgroundColor': '#21262d', 'color': '#58a6ff', 'fontWeight': 'bold', 'borderColor': COR_BORDA}),
        dcc.Tab(label='💼 Portfólio de Terras, M&A & Cadastro', value='aba-financeiro', style={'backgroundColor': COR_CARD, 'color': COR_TEXTO, 'borderColor': COR_BORDA}, selected_style={'backgroundColor': '#21262d', 'color': '#58a6ff', 'fontWeight': 'bold', 'borderColor': COR_BORDA}),
    ], style={'marginBottom': '20px'}),

    html.Div(id='conteudo-abas')
])

@app.callback(
    Output('conteudo-abas', 'children'),
    [Input('abas-principal', 'value')]
)
def renderizar_conteudo_abas(aba):
    if aba == 'aba-noc':
        opcoes_dropdown = [{'label': k, 'value': k} for k in FAZENDAS_CONFIG.keys()]
        primeira_chave = list(FAZENDAS_CONFIG.keys())[0]
        
        return html.Div([
            html.Div(style={'width': '50%', 'margin': '0 auto 20px auto', 'textAlign': 'center', 'backgroundColor': COR_CARD, 'padding': '12px', 'borderRadius': '8px', 'border': f'1px solid {COR_BORDA}'}, children=[
                html.Label("Selecione o Cluster / Unidade Agrícola:", style={'fontSize': '13px', 'color': COR_TEXTO}),
                dcc.Dropdown(id='filtro-fazenda', options=opcoes_dropdown, value=primeira_chave, clearable=False, style={'marginTop': '8px', 'color': '#333'})
            ]),
            html.Div(id='badge-status-sistema', style={'textAlign': 'center', 'marginBottom': '20px'}),
            html.Div(id='cards-api-avancado', style={'display': 'flex', 'justifyContent': 'center', 'gap': '10px', 'marginBottom': '20px', 'flexWrap': 'wrap'}),
            
            html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=[
                html.Div(style={'flex': '1', 'backgroundColor': COR_CARD, 'padding': '15px', 'borderRadius': '8px', 'border': f'1px solid {COR_BORDA}'}, children=[dcc.Graph(id='grafico-iot')]),
                html.Div(style={'flex': '1', 'backgroundColor': COR_CARD, 'padding': '15px', 'borderRadius': '8px', 'border': f'1px solid {COR_BORDA}'}, children=[dcc.Graph(id='grafico-hardware')])
            ]),
            html.Div(style={'display': 'flex', 'gap': '20px'}, children=[
                html.Div(style={'flex': '1.2', 'backgroundColor': COR_CARD, 'padding': '15px', 'borderRadius': '8px', 'border': f'1px solid {COR_BORDA}'}, children=[dcc.Graph(id='grafico-banda')]),
                html.Div(style={'flex': '0.8', 'backgroundColor': '#010409', 'padding': '15px', 'borderRadius': '8px', 'border': f'1px solid {COR_BORDA}', 'fontFamily': 'monospace', 'fontSize': '12px', 'color': '#7ee787'}, children=[
                    html.P("💻 Systemd Edge Kernel & WireGuard VPN Logs:", style={'color': '#8b949e', 'borderBottom': f'1px solid {COR_BORDA}', 'paddingBottom': '6px', 'margin': '0 0 10px 0'}),
                    html.Div(id='terminal-logs')
                ])
            ])
        ])
    
    elif aba == 'aba-financeiro':
        portfolio_dados = []
        patrimonio_total = 0
        lucro_liquido_total = 0

        for nome, cfg in FAZENDAS_CONFIG.items():
            v_compra = cfg["valor_compra"]
            v_mercado = cfg["valor_mercado"]
            ganho_capital = v_mercado - v_compra
            roi_pct = round((ganho_capital / v_compra) * 100, 1)
            lucro_op = cfg["receita_est"] - cfg["custo_op_anual"]
            
            patrimonio_total += v_mercado
            lucro_liquido_total += lucro_op

            portfolio_dados.append({
                "Unidade": nome.split("(")[0].strip(),
                "Cultura": cfg["cultura"],
                "Área (ha)": f"{cfg['hectares']:,}",
                "Aquisição": f"R$ {v_compra:,.2f}",
                "Mercado Atual": f"R$ {v_mercado:,.2f}",
                "Ganho Capital": f"+R$ {ganho_capital:,.2f} ({roi_pct}%)",
                "Receita Est.": f"R$ {cfg['receita_est']:,.2f}",
                "Custo Op.": f"R$ {cfg['custo_op_anual']:,.2f}",
                "Lucro Líq. Anual": f"R$ {lucro_op:,.2f}"
            })
        
        df_port = pd.DataFrame(portfolio_dados)

        return html.Div([
            html.Div(style={'display': 'flex', 'justifyContent': 'center', 'gap': '20px', 'marginBottom': '20px', 'flexWrap': 'wrap'}, children=[
                html.Div([html.H3(f"R$ {patrimonio_total:,.2f}", style={'color': '#58a6ff', 'margin': '0', 'fontSize': '16px'}), html.P("AUM (Patrimônio Total em Terras)", style={'margin': '0', 'color': '#8b949e', 'fontSize': '11px'})], style={'backgroundColor': COR_CARD, 'padding': '12px 20px', 'borderRadius': '6px', 'border': f'1px solid {COR_BORDA}', 'textAlign': 'center'}),
                html.Div([html.H3(f"R$ {lucro_liquido_total:,.2f}", style={'color': '#2ea043', 'margin': '0', 'fontSize': '16px'}), html.P("Projeção de Lucro Líquido Anual", style={'margin': '0', 'color': '#8b949e', 'fontSize': '11px'})], style={'backgroundColor': COR_CARD, 'padding': '12px 20px', 'borderRadius': '6px', 'border': f'1px solid {COR_BORDA}', 'textAlign': 'center'}),
                html.Div([html.H3(f"{len(FAZENDAS_CONFIG)} Unidades", style={'color': '#bc8cff', 'margin': '0', 'fontSize': '16px'}), html.P("Ativos Rurais em Portfólio", style={'margin': '0', 'color': '#8b949e', 'fontSize': '11px'})], style={'backgroundColor': COR_CARD, 'padding': '12px 20px', 'borderRadius': '6px', 'border': f'1px solid {COR_BORDA}', 'textAlign': 'center'})
            ]),

            html.Div(style={'backgroundColor': COR_CARD, 'padding': '20px', 'borderRadius': '8px', 'border': f'1px solid {COR_BORDA}', 'marginBottom': '20px'}, children=[
                html.H4("➕ Cadastrar Nova Fazenda / Aquisição de Ativo (M&A)", style={'color': '#58a6ff', 'marginTop': '0', 'fontSize': '15px'}),
                html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(3, 1fr)', 'gap': '12px', 'marginBottom': '12px'}, children=[
                    dcc.Input(id='input-nome', type='text', placeholder='Nome da Fazenda / Região', style={'padding': '8px', 'backgroundColor': '#0d1117', 'color': '#fff', 'border': '1px solid #30363d', 'borderRadius': '4px'}),
                    dcc.Input(id='input-cultura', type='text', placeholder='Cultura (ex: Batata, Pecuária, Soja)', style={'padding': '8px', 'backgroundColor': '#0d1117', 'color': '#fff', 'border': '1px solid #30363d', 'borderRadius': '4px'}),
                    dcc.Input(id='input-hectares', type='number', placeholder='Área em Hectares (ha)', style={'padding': '8px', 'backgroundColor': '#0d1117', 'color': '#fff', 'border': '1px solid #30363d', 'borderRadius': '4px'}),
                    dcc.Input(id='input-venda-compra', type='number', placeholder='Valor de Aquisição (R$)', style={'padding': '8px', 'backgroundColor': '#0d1117', 'color': '#fff', 'border': '1px solid #30363d', 'borderRadius': '4px'}),
                    dcc.Input(id='input-mercado', type='number', placeholder='Valor de Mercado Atual (R$)', style={'padding': '8px', 'backgroundColor': '#0d1117', 'color': '#fff', 'border': '1px solid #30363d', 'borderRadius': '4px'}),
                    dcc.Input(id='input-receita', type='number', placeholder='Receita Anual Estimada (R$)', style={'padding': '8px', 'backgroundColor': '#0d1117', 'color': '#fff', 'border': '1px solid #30363d', 'borderRadius': '4px'}),
                ]),
                html.Button('Registrar Nova Fazenda no Portfólio', id='btn-cadastrar', n_clicks=0, style={'backgroundColor': '#238636', 'color': '#fff', 'border': 'none', 'padding': '10px 15px', 'borderRadius': '6px', 'cursor': 'pointer', 'fontWeight': 'bold'}),
                html.Div(id='mensagem-cadastro', style={'marginTop': '10px', 'fontSize': '13px', 'color': '#7ee787'})
            ]),

            html.Div(style={'backgroundColor': COR_CARD, 'padding': '20px', 'borderRadius': '8px', 'border': f'1px solid {COR_BORDA}'}, children=[
                html.H3("📊 Extrato Consolidado de Ativos Rurais e Projeções Financeiras", style={'color': '#58a6ff', 'marginTop': '0', 'fontSize': '15px'}),
                dash_table.DataTable(
                    data=df_port.to_dict('records'),
                    columns=[{"name": i, "id": i} for i in df_port.columns],
                    style_header={'backgroundColor': '#21262d', 'color': '#58a6ff', 'fontWeight': 'bold', 'border': '1px solid #30363d'},
                    style_cell={'backgroundColor': '#161b22', 'color': COR_TEXTO, 'border': '1px solid #30363d', 'textAlign': 'center', 'padding': '8px', 'fontSize': '12px'},
                    style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#1a202c'}]
                )
            ])
        ])

@app.callback(
    [Output('grafico-iot', 'figure'), Output('grafico-hardware', 'figure'),
     Output('grafico-banda', 'figure'), Output('cards-api-avancado', 'children'),
     Output('badge-status-sistema', 'children'), Output('terminal-logs', 'children')],
    [Input('filtro-fazenda', 'value')]
)
def atualizar_noc(fazenda):
    if not fazenda or fazenda not in FAZENDAS_CONFIG:
            fazenda = list(FAZENDAS_CONFIG.keys())[0]
            
    df, m = buscar_dados_enterprise_avancados(fazenda)

    fig_iot = px.bar(df, x="Hora", y="Sensores_IoT", title="Pacotes MQTT / Sensores IoT Ativos")
    fig_iot.update_layout(paper_bgcolor=COR_CARD, plot_bgcolor=COR_CARD, font={'color': COR_TEXTO}, title_x=0.5, margin=dict(t=35, b=25, l=35, r=15))
    fig_iot.update_traces(marker_color='#2ea043')

    fig_hw = go.Figure()
    fig_hw.add_trace(go.Scatter(x=df["Hora"], y=df["Latencia_Rede_ms"], mode='lines+markers', name='Latência (ms)', line=dict(color='#f85149', width=2)))
    fig_hw.add_trace(go.Scatter(x=df["Hora"], y=df["CPU_Edge_Pct"], mode='lines+markers', name='CPU (%)', line=dict(color='#d29922', width=2)))
    fig_hw.update_layout(title="Telemetria de Hardware & Rede", paper_bgcolor=COR_CARD, plot_bgcolor=COR_CARD, font={'color': COR_TEXTO}, title_x=0.5, margin=dict(t=35, b=25, l=35, r=15), legend=dict(x=0.01, y=0.99))

    fig_banda = px.area(df, x="Hora", y="Banda_Satelite_MBs", title="Largura de Banda Link Upstream (MB/s)")
    fig_banda.update_layout(paper_bgcolor=COR_CARD, plot_bgcolor=COR_CARD, font={'color': COR_TEXTO}, title_x=0.5, margin=dict(t=35, b=25, l=35, r=15))
    fig_banda.update_traces(line_color='#58a6ff', fillcolor='rgba(88, 166, 255, 0.2)')

    cards_html = [
        html.Div([html.H3(f"{m['ip_edge']}", style={'color': '#58a6ff', 'margin': '0', 'fontSize': '13px'}), html.P("IP Edge", style={'margin': '0', 'color': '#8b949e', 'fontSize': '10px'})], style={'backgroundColor': '#21262d', 'padding': '8px 10px', 'borderRadius': '6px', 'border': f'1px solid {COR_BORDA}', 'textAlign': 'center'}),
        html.Div([html.H3(f"{m['temp']}°C", style={'color': '#f85149', 'margin': '0'}), html.P("Temp. Ext.", style={'margin': '0', 'color': '#8b949e', 'fontSize': '10px'})], style={'backgroundColor': '#21262d', 'padding': '8px 10px', 'borderRadius': '6px', 'border': f'1px solid {COR_BORDA}', 'textAlign': 'center'}),
        html.Div([html.H3(f"{m['umidade_solo']}%", style={'color': '#2ea043', 'margin': '0'}), html.P("Umidade Solo", style={'margin': '0', 'color': '#8b949e', 'fontSize': '10px'})], style={'backgroundColor': '#21262d', 'padding': '8px 10px', 'borderRadius': '6px', 'border': f'1px solid {COR_BORDA}', 'textAlign': 'center'}),
        html.Div([html.H3(f"{m['buffer_disco']}%", style={'color': '#d29922', 'margin': '0'}), html.P("Buffer NVMe", style={'margin': '0', 'color': '#8b949e', 'fontSize': '10px'})], style={'backgroundColor': '#21262d', 'padding': '8px 10px', 'borderRadius': '6px', 'border': f'1px solid {COR_BORDA}', 'textAlign': 'center'}),
        html.Div([html.H3(f"{m['rssi_lora']} dBm", style={'color': '#33b3ae', 'margin': '0'}), html.P("LoRaWAN", style={'margin': '0', 'color': '#8b949e', 'fontSize': '10px'})], style={'backgroundColor': '#21262d', 'padding': '8px 10px', 'borderRadius': '6px', 'border': f'1px solid {COR_BORDA}', 'textAlign': 'center'}),
        html.Div([html.H3(f"Ativo", style={'color': '#58a6ff', 'margin': '0'}), html.P("WireGuard", style={'margin': '0', 'color': '#8b949e', 'fontSize': '10px'})], style={'backgroundColor': '#21262d', 'padding': '8px 10px', 'borderRadius': '6px', 'border': f'1px solid {COR_BORDA}', 'textAlign': 'center'}),
    ]

    badge = html.Span(f"● Status do Nó de Borda ({m['cultura']}): {m['status_node']}", style={
        'color': '#fff', 'fontWeight': 'bold', 'backgroundColor': m['cor_status'], 
        'padding': '5px 12px', 'borderRadius': '20px', 'fontSize': '12px'
    })

    logs = [
        html.P(f"[{datetime.now().strftime('%H:%M:%S')}] INFO: Edge node sync active.", style={'margin': '2px 0'}),
        html.P(f"[{datetime.now().strftime('%H:%M:%S')}] CULTURA: {m['cultura']} | Area telemetry nominal.", style={'margin': '2px 0'}),
        html.P(f"[{datetime.now().strftime('%H:%M:%S')}] STATUS: Node health -> {m['status_node']}", style={'margin': '2px 0', 'color': m['cor_status']})
    ]

    return fig_iot, fig_hw, fig_banda, cards_html, badge, logs

if __name__ == '__main__':
    app.run(debug=True, port=8050)