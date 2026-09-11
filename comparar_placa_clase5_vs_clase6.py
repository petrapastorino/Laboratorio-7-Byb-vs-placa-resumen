# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 10:55:50 2026

@author: labo6y7
"""
import json
import numpy as np
import pandas as pd
from scipy.signal import hilbert, iirnotch, filtfilt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---- Config ----
SMOOTH_MS = 40        # ventana de suavizado de la envolvente de Hilbert
NOTCH_FREQ = 50.0      # Hz, ruido de linea
NOTCH_Q = 30.0          # factor de calidad del notch
OUT_DIR = "C:/Users/labo6y7/Desktop/Miranda_y_Petra/labo7/clase 8"
TARGET_FS_RAW = 500     # Hz efectivos a los que se submuestrea la señal cruda para graficar
TARGET_FS_ENV = 100     # Hz efectivos para la envolvente

VOCALES = ["A", "E", "I", "O", "U"]

# Paleta seaborn Set2, sin el amarillo. Verde = cuarto aves (Clase 6),
# naranja = cuarto ñandu (Clase 5) -- misma convencion que en la
# comparacion de BYB.
_set2 = sns.color_palette("Set2").as_hex()
COLOR_CLASE6_AVES = _set2[0]   # verde
COLOR_CLASE5_NANDU = _set2[1]  # naranja

# ---- Rutas ----
rutas_clase6 = {
    v: f"C:/Users/labo6y7/Desktop/Miranda_y_Petra/labo7/clase 8/clase_6_placa/clase6_{v}.csv"
    for v in VOCALES
}

rutas_clase5 = {
    v: f"C:/Users/labo6y7/Desktop/Miranda_y_Petra/labo7/clase 8/clase5_m1/med1_{v}.csv"
    for v in VOCALES
}

# musculo -> (columna canal en clase5, columna canal en clase6)
# Clase 5 (Med1): canal3=Plat, canal1=Oris, canal2=Zygo
# Clase 6: canal0=oris, canal1=zygo, canal2=plat
CANAL_POR_MUSCULO = {
    "plat": ("Canal 3", "Canal 2"),
    "oris": ("Canal 1", "Canal 0"),
    "zygo": ("Canal 2", "Canal 1"),
}


def cargar_senal(path, columna_canal):
    df = pd.read_csv(path)
    t = df["Tiempo (s)"].to_numpy()
    y = df[columna_canal].to_numpy().astype(float)

    dt = np.median(np.diff(t))
    fs = 1.0 / dt

    # Notch 50Hz
    b, a = iirnotch(NOTCH_FREQ, NOTCH_Q, fs)
    y = filtfilt(b, a, y)

    # Offset: resta el promedio de los primeros 2 segundos
    n_offset = min(len(y), int(fs * 2))
    y = y - np.mean(y[:n_offset])

    return t, y, fs


def envolvente_hilbert(data, fs, smooth_ms=SMOOTH_MS):
    env = np.abs(hilbert(data))
    win = max(1, int(fs * smooth_ms / 1000))
    kernel = np.ones(win) / win
    return np.convolve(env, kernel, mode="same")


def submuestrear(t, y, fs, target_fs):
    factor = max(1, int(round(fs / target_fs)))
    return t[::factor], y[::factor]


def hacer_figura_musculo(musculo):
    col_clase5, col_clase6 = CANAL_POR_MUSCULO[musculo]
    fig = make_subplots(rows=5, cols=1, shared_xaxes=False, vertical_spacing=0.04)

    grupos = {"clase6_raw": [], "clase5_raw": [], "clase6_env": [], "clase5_env": []}

    for i, v in enumerate(VOCALES, start=1):
        t6, y6, fs6 = cargar_senal(rutas_clase6[v], col_clase6)
        env6 = envolvente_hilbert(y6, fs6)

        t5, y5, fs5 = cargar_senal(rutas_clase5[v], col_clase5)
        env5 = envolvente_hilbert(y5, fs5)

        primero = (i == 1)
        base = len(fig.data)

        t6_r, y6_r = submuestrear(t6, y6, fs6, TARGET_FS_RAW)
        t5_r, y5_r = submuestrear(t5, y5, fs5, TARGET_FS_RAW)
        t6_e, env6_r = submuestrear(t6, env6, fs6, TARGET_FS_ENV)
        t5_e, env5_r = submuestrear(t5, env5, fs5, TARGET_FS_ENV)

        # Crudo
        fig.add_trace(go.Scatter(x=t6_r, y=y6_r, mode="lines", name="placa cuarto aves (Clase 6)",
                                  legendgroup="clase6_raw", showlegend=primero,
                                  line=dict(color=COLOR_CLASE6_AVES), visible=True),
                      row=i, col=1)
        fig.add_trace(go.Scatter(x=t5_r, y=y5_r, mode="lines", name="placa cuarto ñandú (Clase 5)",
                                  legendgroup="clase5_raw", showlegend=primero,
                                  line=dict(color=COLOR_CLASE5_NANDU), visible=True),
                      row=i, col=1)

        # Envolvente
        fig.add_trace(go.Scatter(x=t6_e, y=env6_r, mode="lines", name="placa cuarto aves (Clase 6)",
                                  legendgroup="clase6_env", showlegend=False,
                                  line=dict(color=COLOR_CLASE6_AVES), visible=False),
                      row=i, col=1)
        fig.add_trace(go.Scatter(x=t5_e, y=env5_r, mode="lines", name="placa cuarto ñandú (Clase 5)",
                                  legendgroup="clase5_env", showlegend=False,
                                  line=dict(color=COLOR_CLASE5_NANDU), visible=False),
                      row=i, col=1)

        grupos["clase6_raw"].append(base + 0)
        grupos["clase5_raw"].append(base + 1)
        grupos["clase6_env"].append(base + 2)
        grupos["clase5_env"].append(base + 3)

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
        title=None,
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

    out_path = f"{OUT_DIR}/{musculo}_placa_clase5_vs_clase6.html"
    fig.write_html(out_path, post_script=post_script, include_plotlyjs="cdn")
    print(f"Guardado: {out_path}")


for musculo in CANAL_POR_MUSCULO:
    hacer_figura_musculo(musculo)
