import random
import requests
from datetime import datetime

from dash import Dash, html, dcc
from dash.dependencies import Output, Input

# ==========================
# CONFIGURAÇÕES GERAIS
# ==========================

FIWARE_ORION_URL = "http://20.63.91.180:1026"
DEVICE_ID = "EnvSensor:comfort001"
FIWARE_SERVICE = "skillhub"
FIWARE_SERVICEPATH = "/"

# Para testes locais: se True, não chama o FIWARE e usa valores aleatórios
USE_MOCK_DATA = False

# Emulação de “dispositivo offline”
SIMULATE_OFFLINE = True
OFFLINE_PROBABILITY = 0.2  # 20% de chance de “não localizado”

# Limites de conforto
THRESHOLDS = {
    "temperature": {"min": 20.0, "max": 26.0},   # °C
    "humidity": {"min": 40.0, "max": 60.0},      # %
    "luminosity": {"min": 30.0, "max": 80.0},    # 0–100
}


# ==========================
# FUNÇÕES DE NEGÓCIO
# ==========================


def fetch_sensor_data():
    """
    Lê dados do FIWARE (Orion) OU gera dados mock.
    Retorna:
        dict com temperature, humidity, luminosity
        ou None se considerar que o dispositivo está offline/não encontrado.
    """
    if USE_MOCK_DATA:
        if SIMULATE_OFFLINE and random.random() < OFFLINE_PROBABILITY:
            return None

        temperature = round(random.uniform(18, 30), 1)
        humidity = round(random.uniform(30, 70), 1)
        luminosity = round(random.uniform(10, 100), 0)

        return {
            "temperature": temperature,
            "humidity": humidity,
            "luminosity": luminosity,
        }

    headers = {
        "Fiware-Service": FIWARE_SERVICE,
        "Fiware-ServicePath": FIWARE_SERVICEPATH,
    }
    url = f"{FIWARE_ORION_URL}/v2/entities/{DEVICE_ID}"

    try:
        resp = requests.get(url, headers=headers, timeout=3)
    except requests.exceptions.RequestException:
        return None

    if resp.status_code != 200:
        return None

    data = resp.json()

    try:
        temperature = float(data["temperature"]["value"])
        humidity = float(data["humidity"]["value"])
        luminosity = float(data["luminosity"]["value"])
    except Exception:
        return None

    return {
        "temperature": temperature,
        "humidity": humidity,
        "luminosity": luminosity,
    }


def evaluate_room_condition(values):
    """
    Recebe um dict com temperature, humidity, luminosity (ou None).
    Retorna:
        status_text: str   -> mensagem principal
        color_key: str     -> 'green', 'yellow', 'red', 'blue'
        out_of_range: list -> quais parâmetros estão fora do ideal
    """
    if values is None:
        return "Dispositivo não localizado", "blue", []

    out_of_range = []

    for key in ["temperature", "humidity", "luminosity"]:
        v = values.get(key)
        limits = THRESHOLDS[key]
        if v < limits["min"] or v > limits["max"]:
            out_of_range.append(key)

    if len(out_of_range) == 0:
        return "Excelente para estudos", "green", out_of_range
    elif len(out_of_range) == 1:
        return "Atenção: 1 parâmetro fora do ideal", "yellow", out_of_range
    else:
        return "Ruim para estudos: múltiplos parâmetros críticos", "red", out_of_range


# ==========================
# DASHBOARD (DASH)
# ==========================

app = Dash(__name__)
app.title = "SkillHub Comfort Monitor"

COLOR_MAP = {
    "green": "#2E7D32",
    "yellow": "#F9A825",
    "red": "#C62828",
    "blue": "#1565C0",
}

BASE_STATUS_STYLE = {
    "margin": "20px auto",
    "padding": "24px 32px",
    "borderRadius": "16px",
    "width": "100%",
    "boxShadow": "0 4px 18px rgba(0, 0, 0, 0.4)",
    "textAlign": "center",
    "fontSize": "22px",
    "fontWeight": "bold",
    "backgroundColor": "#333333",
    "transition": "background-color 0.3s ease",
}

PARAM_BOX_STYLE = {
    "padding": "16px 12px",
    "borderRadius": "12px",
    "backgroundColor": "#1E1E1E",
    "width": "30%",
    "textAlign": "center",
    "boxShadow": "0 2px 10px rgba(0, 0, 0, 0.3)",
}

app.layout = html.Div(
    style={
        "fontFamily": "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        "backgroundColor": "#121212",
        "color": "#FFFFFF",
        "minHeight": "100vh",
        "padding": "32px 16px",
    },
    children=[
        html.Div(
            style={
                "maxWidth": "960px",
                "margin": "0 auto",
            },
            children=[
                html.H1(
                    "SkillHub Comfort Monitor",
                    style={
                        "textAlign": "center",
                        "marginBottom": "4px",
                    },
                ),
                html.H4(
                    "Widget de conforto para foco, trabalho e estudo",
                    style={
                        "textAlign": "center",
                        "color": "#BBBBBB",
                        "marginTop": "0",
                    },
                ),

                # link “fake” pro SkillHub
                html.Div(
                    style={"textAlign": "center", "marginTop": "12px"},
                    children=[
                        html.A(
                            "Abrir SkillHub",
                            href="https://skillhub.example.com",  # placeholder
                            target="_blank",
                            style={
                                "color": "#64B5F6",
                                "textDecoration": "none",
                                "fontSize": "14px",
                            },
                        ),
                    ],
                ),

                # Card principal de status
                html.Div(id="status-card", style=BASE_STATUS_STYLE),

                # Boxes dos parâmetros
                html.Div(
                    style={
                        "display": "flex",
                        "justifyContent": "space-between",
                        "gap": "12px",
                        "marginTop": "24px",
                        "flexWrap": "wrap",
                    },
                    children=[
                        html.Div(id="temp-box", style=PARAM_BOX_STYLE),
                        html.Div(id="hum-box", style=PARAM_BOX_STYLE),
                        html.Div(id="lum-box", style=PARAM_BOX_STYLE),
                    ],
                ),

                # Parâmetros fora do ideal
                html.Div(
                    id="out-of-range-text",
                    style={
                        "marginTop": "28px",
                        "textAlign": "center",
                        "fontSize": "16px",
                        "color": "#CCCCCC",
                    },
                ),

                # Última atualização
                html.Div(
                    id="last-update",
                    style={
                        "marginTop": "8px",
                        "textAlign": "center",
                        "fontSize": "13px",
                        "color": "#888888",
                    },
                ),

                # Intervalo de atualização
                dcc.Interval(
                    id="interval-component",
                    interval=5 * 1000,  # 5 segundos
                    n_intervals=0,
                ),
            ],
        )
    ],
)


# ==========================
# CALLBACKS
# ==========================

@app.callback(
    [
        Output("status-card", "children"),
        Output("status-card", "style"),
        Output("temp-box", "children"),
        Output("hum-box", "children"),
        Output("lum-box", "children"),
        Output("out-of-range-text", "children"),
        Output("last-update", "children"),
    ],
    Input("interval-component", "n_intervals"),
)
def update_dashboard(n):
    values = fetch_sensor_data()
    status_text, color_key, out_of_range = evaluate_room_condition(values)

    status_style = BASE_STATUS_STYLE.copy()
    status_style["backgroundColor"] = COLOR_MAP.get(color_key, "#333333")

    if values is None:
        temp_children = [
            html.H5("Temperatura", style={"marginBottom": "8px", "color": "#AAAAAA"}),
            html.Div("—", style={"fontSize": "24px", "fontWeight": "bold"}),
        ]
        hum_children = [
            html.H5("Umidade", style={"marginBottom": "8px", "color": "#AAAAAA"}),
            html.Div("—", style={"fontSize": "24px", "fontWeight": "bold"}),
        ]
        lum_children = [
            html.H5("Luminosidade", style={"marginBottom": "8px", "color": "#AAAAAA"}),
            html.Div("—", style={"fontSize": "24px", "fontWeight": "bold"}),
        ]
        out_text = "Dispositivo ESP32 não localizado (simulação)."
    else:
        temp_children = [
            html.H5("Temperatura", style={"marginBottom": "8px", "color": "#AAAAAA"}),
            html.Div(
                f"{values['temperature']} °C",
                style={"fontSize": "24px", "fontWeight": "bold"},
            ),
            html.Div(
                f"Ideal: {THRESHOLDS['temperature']['min']}–{THRESHOLDS['temperature']['max']} °C",
                style={"fontSize": "12px", "color": "#888888"},
            ),
        ]
        hum_children = [
            html.H5("Umidade", style={"marginBottom": "8px", "color": "#AAAAAA"}),
            html.Div(
                f"{values['humidity']} %",
                style={"fontSize": "24px", "fontWeight": "bold"},
            ),
            html.Div(
                f"Ideal: {THRESHOLDS['humidity']['min']}–{THRESHOLDS['humidity']['max']} %",
                style={"fontSize": "12px", "color": "#888888"},
            ),
        ]
        lum_children = [
            html.H5("Luminosidade", style={"marginBottom": "8px", "color": "#AAAAAA"}),
            html.Div(
                f"{values['luminosity']} (0–100)",
                style={"fontSize": "24px", "fontWeight": "bold"},
            ),
            html.Div(
                f"Ideal: {THRESHOLDS['luminosity']['min']}–{THRESHOLDS['luminosity']['max']}",
                style={"fontSize": "12px", "color": "#888888"},
            ),
        ]

        if len(out_of_range) == 0:
            out_text = "Todos os parâmetros estão dentro da faixa ideal."
        else:
            labels = {
                "temperature": "Temperatura",
                "humidity": "Umidade",
                "luminosity": "Luminosidade",
            }
            nomes = [labels[k] for k in out_of_range]
            out_text = "Parâmetros fora do ideal: " + ", ".join(nomes) + "."

    last_update = (
        "Última atualização: "
        + datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    )

    return (
        status_text,
        status_style,
        temp_children,
        hum_children,
        lum_children,
        out_text,
        last_update,
    )


# ==========================
# MAIN
# ==========================

if __name__ == "__main__":
    app.run(debug=True)
