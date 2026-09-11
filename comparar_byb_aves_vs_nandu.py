import json
import numpy as np
import scipy.io.wavfile as wavfile
from scipy.signal import hilbert
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---- Config ----
SMOOTH_MS = 40  # ventana de suavizado de la envolvente de Hilbert
OUT_DIR = "C:/Users/labo6y7/Desktop/Miranda_y_Petra/labo7/clase7"
TARGET_FS_RAW = 500   # Hz efectivos a los que se submuestrea la señal cruda para graficar
TARGET_FS_ENV = 100   # Hz efectivos para la envolvente (ya viene suavizada a 40ms, no necesita mas)

VOCALES = ["A", "E", "I", "O", "U"]
MUSCULOS = ["belly", "oris", "plat", "zygo"]

# Paleta seaborn Set2, sin el amarillo (indice 5). Verde y naranja.
_set2 = sns.color_palette("Set2").as_hex()
COLOR_AVES = _set2[0]   # verde
COLOR_NANDU = _set2[1]  # naranja

# ---- Rutas ----
rutas_clase7 = {
    (v, m): f"C:/Users/labo6y7/Desktop/Miranda_y_Petra/labo7/clase7/clase7_byb/clase7_{v}_{m}.wav"
    for v in VOCALES for m in MUSCULOS
}

rutas_clase5 = {
    (v, m): (
        "C:/Users/labo6y7/Desktop/Miranda_y_Petra/labo7/clase7/"
        f"csv_byb-20260910T173152Z-1-001/csv_byb/{m}_byb_clase_5/{v}_{m}_clase_5.wav"
    )
    for v in VOCALES for m in MUSCULOS
}


def cargar_senal(path):
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
    # Reduce la cantidad de puntos a graficar segun la fs real de cada
    # archivo, apuntando a target_fs puntos/seg efectivos (no cambia el
    # analisis, solo lo que se dibuja) para que el HTML no pese tanto.
    factor = max(1, int(round(fs / target_fs)))
    return t[::factor], y[::factor]


def hacer_figura_musculo(musculo):
    fig = make_subplots(rows=5, cols=1, shared_xaxes=False, vertical_spacing=0.04)

    # legendgroup -> lista de indices globales de traza (para el reordenamiento por click)
    grupos = {"aves_raw": [], "nandu_raw": [], "aves_env": [], "nandu_env": []}

    for i, v in enumerate(VOCALES, start=1):
        t5, y5, fs5 = cargar_senal(rutas_clase5[(v, musculo)])
        env5 = envolvente_hilbert(y5, fs5)

        t7, y7, fs7 = cargar_senal(rutas_clase7[(v, musculo)])
        env7 = envolvente_hilbert(y7, fs7)

        primero = (i == 1)
        base = len(fig.data)  # indice global antes de agregar este bloque de 4 trazas

        t5_r, y5_r = submuestrear(t5, y5, fs5, TARGET_FS_RAW)
        t7_r, y7_r = submuestrear(t7, y7, fs7, TARGET_FS_RAW)
        t5_e, env5_r = submuestrear(t5, env5, fs5, TARGET_FS_ENV)
        t7_e, env7_r = submuestrear(t7, env7, fs7, TARGET_FS_ENV)

        # Crudo - legendgroup propio para cada cuarto, separado del de envolvente
        fig.add_trace(go.Scatter(x=t5_r, y=y5_r, mode="lines", name="byb cuarto aves",
                                  legendgroup="aves_raw", showlegend=primero,
                                  line=dict(color=COLOR_AVES), visible=True),
                      row=i, col=1)
        fig.add_trace(go.Scatter(x=t7_r, y=y7_r, mode="lines", name="byb cuarto ñandú",
                                  legendgroup="nandu_raw", showlegend=primero,
                                  line=dict(color=COLOR_NANDU), visible=True),
                      row=i, col=1)

        # Envolvente - legendgroup propio, independiente del crudo
        fig.add_trace(go.Scatter(x=t5_e, y=env5_r, mode="lines", name="byb cuarto aves",
                                  legendgroup="aves_env", showlegend=False,
                                  line=dict(color=COLOR_AVES), visible=False),
                      row=i, col=1)
        fig.add_trace(go.Scatter(x=t7_e, y=env7_r, mode="lines", name="byb cuarto ñandú",
                                  legendgroup="nandu_env", showlegend=False,
                                  line=dict(color=COLOR_NANDU), visible=False),
                      row=i, col=1)

        grupos["aves_raw"].append(base + 0)
        grupos["nandu_raw"].append(base + 1)
        grupos["aves_env"].append(base + 2)
        grupos["nandu_env"].append(base + 3)

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

    # ---- JS: al clickear una entrada de la leyenda, esa traza (y su
    # contraparte en las otras vocales) pasa a dibujarse arriba de todo,
    # ademas del toggle on/off por defecto de Plotly. ----
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

    out_path = f"{OUT_DIR}/{musculo}_cuarto_aves_vs_nandu.html"
    # include_plotlyjs="cdn": no embebe la libreria de Plotly (~3MB) en
    # cada HTML, la carga desde internet al abrir. Si vas a abrir estos
    # archivos sin conexion, cambia esto de nuevo a True.
    fig.write_html(out_path, post_script=post_script, include_plotlyjs="cdn")
    print(f"Guardado: {out_path}")


for musculo in MUSCULOS:
    hacer_figura_musculo(musculo)
