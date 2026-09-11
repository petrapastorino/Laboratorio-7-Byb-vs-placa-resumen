# -*- coding: utf-8 -*-
"""
Compara, en el mismo cuarto (aves) y misma compu, la placa (Clase 6)
contra el BYB (Clase 5) -- aisla el efecto del dispositivo.
"""
import json
import numpy as np
import pandas as pd
import scipy.io.wavfile as wavfile
from scipy.signal import hilbert, iirnotch, filtfilt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---- Config ----
SMOOTH_MS = 40         # ventana de suavizado de la envolvente de Hilbert
NOTCH_FREQ = 50.0       # Hz, ruido de linea (solo se aplica a la placa)
NOTCH_Q = 30.0
OUT_DIR = "C:/Users/labo6y7/Desktop/Miranda_y_Petra/labo7/clase 8"
TARGET_FS_RAW = 500     # Hz efectivos a los que se submuestrea la señal cruda para graficar
TARGET_FS_ENV = 100     # Hz efectivos para la envolvente

VOCALES = ["A", "E", "I", "O", "U"]
# Belly no tiene canal en la placa de Clase 6, asi que queda afuera de esta comparacion
MUSCULOS = ["oris", "plat", "zygo"]

# Paleta seaborn Set2. Colores por dispositivo (no por cuarto, como en
# las otras comparaciones) para no confundir con esas figuras.
_set2 = sns.color_palette("Set2").as_hex()
COLOR_PLACA = _set2[2]  # placa (Clase 6, cuarto aves)
COLOR_BYB = _set2[3]    # BYB (Clase 5, cuarto aves)

# ---- Rutas ----
rutas_placa_clase6 = {
    v: f"C:/Users/labo6y7/Desktop/Miranda_y_Petra/labo7/clase 8/clase_6_placa/clase6_{v}.csv"
    for v in VOCALES
}

rutas_byb_clase5 = {
    (v, m): (
        "C:/Users/labo6y7/Desktop/Miranda_y_Petra/labo7/clase7/"
        f"csv_byb-20260910T173152Z-1-001/csv_byb/{m}_byb_clase_5/{v}_{m}_clase_5.wav"
    )
    for v in VOCALES for m in MUSCULOS
}

# musculo -> columna de canal en la placa de Clase 6
# canal0=oris, canal1=zygo, canal2=plat
CANAL_PLACA_POR_MUSCULO = {
    "oris": "Canal 0",
    "zygo": "Canal 1",
    "plat": "Canal 2",
}


def cargar_placa(path, columna_canal):
    df = pd.read_csv(path)
    t = df["Tiempo (s)"].to_numpy()
    y = df[columna_canal].to_numpy().astype(float)

    dt = np.median(np.diff(t))
    fs = 1.0 / dt

    b, a = iirnotch(NOTCH_FREQ, NOTCH_Q, fs)
    y = filtfilt(b, a, y)

    n_offset = min(len(y), int(fs * 2))
    y = y - np.mean(y[:n_offset])

    return t, y, fs


def cargar_byb(path):
    fs, data = wavfile.read(path)
    if data.ndim > 1:
        data = data[:, 0]
    data = data.astype(float)
    n_offset = min(len(data), int(fs * 2))
    data = data - np.mean(data[:n_offset])
    t = np.arange(len(data)) / fs
    return t, data, fs


def envolvente_hilbert(data, fs, smooth_ms=SMOOTH_MS):
    env = np.abs(hilbert(data))
    win = max(1, int(fs * smooth_ms / 1000))
    kernel = np.ones(win) / win
    return np.convolve(env, kernel, mode="same")


def submuestrear(t, y, fs, target_fs):
    factor = max(1, int(round(fs / target_fs)))
    return t[::factor], y[::factor]


def normalizar(y):
    # Normaliza al pico propio de la señal, para poder comparar forma
    # entre placa y BYB aunque sus escalas de amplitud no sean comparables.
    pico = np.max(np.abs(y))
    if pico == 0:
        return y
    return y / pico


def hacer_figura_musculo(musculo):
    columna_placa = CANAL_PLACA_POR_MUSCULO[musculo]
    fig = make_subplots(rows=5, cols=1, shared_xaxes=False, vertical_spacing=0.04)

    grupos = {"placa_raw": [], "byb_raw": [], "placa_env": [], "byb_env": []}

    for i, v in enumerate(VOCALES, start=1):
        t_p, y_p, fs_p = cargar_placa(rutas_placa_clase6[v], columna_placa)
        env_p = envolvente_hilbert(y_p, fs_p)

        t_b, y_b, fs_b = cargar_byb(rutas_byb_clase5[(v, musculo)])
        env_b = envolvente_hilbert(y_b, fs_b)

        # Normalizamos cada señal a su propio pico -- placa y BYB no son
        # comparables en amplitud absoluta, solo en forma.
        y_p = normalizar(y_p)
        y_b = normalizar(y_b)
        env_p = normalizar(env_p)
        env_b = normalizar(env_b)

        primero = (i == 1)
        base = len(fig.data)

        t_p_r, y_p_r = submuestrear(t_p, y_p, fs_p, TARGET_FS_RAW)
        t_b_r, y_b_r = submuestrear(t_b, y_b, fs_b, TARGET_FS_RAW)
        t_p_e, env_p_r = submuestrear(t_p, env_p, fs_p, TARGET_FS_ENV)
        t_b_e, env_b_r = submuestrear(t_b, env_b, fs_b, TARGET_FS_ENV)

        # Crudo
        fig.add_trace(go.Scatter(x=t_p_r, y=y_p_r, mode="lines", name="placa (Clase 6, cuarto aves)",
                                  legendgroup="placa_raw", showlegend=primero,
                                  line=dict(color=COLOR_PLACA), visible=True),
                      row=i, col=1)
        fig.add_trace(go.Scatter(x=t_b_r, y=y_b_r, mode="lines", name="byb (Clase 5, cuarto aves)",
                                  legendgroup="byb_raw", showlegend=primero,
                                  line=dict(color=COLOR_BYB), visible=True),
                      row=i, col=1)

        # Envolvente
        fig.add_trace(go.Scatter(x=t_p_e, y=env_p_r, mode="lines", name="placa (Clase 6, cuarto aves)",
                                  legendgroup="placa_env", showlegend=False,
                                  line=dict(color=COLOR_PLACA), visible=False),
                      row=i, col=1)
        fig.add_trace(go.Scatter(x=t_b_e, y=env_b_r, mode="lines", name="byb (Clase 5, cuarto aves)",
                                  legendgroup="byb_env", showlegend=False,
                                  line=dict(color=COLOR_BYB), visible=False),
                      row=i, col=1)

        grupos["placa_raw"].append(base + 0)
        grupos["byb_raw"].append(base + 1)
        grupos["placa_env"].append(base + 2)
        grupos["byb_env"].append(base + 3)

        xref = "x domain" if i == 1 else f"x{i} domain"
        yref = "y domain" if i == 1 else f"y{i} domain"
        fig.add_annotation(text=v, xref=xref, yref=yref,
                            x=0.01, y=0.92, showarrow=False,
                            font=dict(size=16, color="black"),
                            bgcolor="white", bordercolor="black", borderwidth=1,
                            row=i, col=1)

    n = len(VOCALES)
    raw_visible = [True, True, False, False] * n
    env_visible = [False, False, True, True] * n

    raw_showlegend = [(pos < 2) and (v_idx == 0) for v_idx in range(n) for pos in range(4)]
    env_showlegend = [(pos >= 2) and (v_idx == 0) for v_idx in range(n) for pos in range(4)]

    fig.update_layout(
        template="plotly_white",
        height=1400,
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="left", x=0),
        updatemenus=[dict(
            type="buttons", direction="right",
            x=0.5, xanchor="center", y=1.12, yanchor="bottom",
            buttons=[
                dict(label="Crudo", method="update",
                     args=[{"visible": raw_visible, "showlegend": raw_showlegend}]),
                dict(label="Envolvente (Hilbert 40ms)", method="update",
                     args=[{"visible": env_visible, "showlegend": env_showlegend}]),
            ]
        )]
    )
    fig.update_xaxes(title_text="Tiempo (s)", row=5, col=1)
    fig.update_yaxes(title_text="Amplitud (normalizada al pico)", row=3, col=1)

    grupos_json = json.dumps(grupos)
    post_script = f"""
    var gd = document.getElementsByClassName('plotly-graph-div')[0];
    var grupos = {grupos_json};
    gd.on('plotly_legendclick', function(evt) {{
        var grupo = evt.data[evt.curveNumber].legendgroup;
        var indices = grupos[grupo];
        if (!indices) {{ return true; }}
        var destino = [];
        var total = gd.data.length;
        for (var k = 0; k < indices.length; k++) {{
            destino.push(total - indices.length + k);
        }}
        setTimeout(function() {{
            Plotly.moveTraces(gd, indices, destino);
        }}, 0);
        return true;
    }});
    """

    out_path = f"{OUT_DIR}/{musculo}_placa_clase6_vs_byb_clase5.html"
    fig.write_html(out_path, post_script=post_script, include_plotlyjs="cdn")
    print(f"Guardado: {out_path}")


for musculo in MUSCULOS:
    hacer_figura_musculo(musculo)
