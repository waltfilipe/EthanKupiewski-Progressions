import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import pandas as pd
import numpy as np
from streamlit_image_coordinates import streamlit_image_coordinates
from io import BytesIO
import os

st.set_page_config(layout="wide")
st.title("Carry → Pass Map Interativo")

# ==========================
# Coordenadas (trios)
# ==========================
coords = [
    (51.19, 38.34),(79.12, 58.29),(86.93, 77.57),
    (24.59, 45.49),(41.55, 56.46),(43.88, 70.75),
    (54.02, 25.04),(75.13, 15.73),(75.79, 7.42),
    (12.29, 38.84),(27.75, 29.53),(26.09, 9.08),
    (44.71, 18.72),(61.50, 39.34),(65.82, 51.47),
]

# ==========================
# Criar dataframe
# ==========================
dados = []

for i in range(0, len(coords), 3):
    start = coords[i]
    carry_end = coords[i+1]
    pass_end = coords[i+2]

    dados.append({
        "id": i // 3,
        "x_start": start[0],
        "y_start": start[1],
        "x_carry_end": carry_end[0],
        "y_carry_end": carry_end[1],
        "x_pass_end": pass_end[0],
        "y_pass_end": pass_end[1],
    })

df = pd.DataFrame(dados)

# ==========================
# Função para desenhar campo
# ==========================
def draw_pitch(df):
    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color='#f5f5f5',
        line_color='#4a4a4a'
    )

    fig, ax = pitch.draw(figsize=(10, 7))

    for _, row in df.iterrows():

        # condução
        pitch.lines(
            row.x_start,
            row.y_start,
            row.x_carry_end,
            row.y_carry_end,
            color=(0.2, 0.2, 0.2, 0.4),
            lw=1.8,
            linestyle='dotted',
            ax=ax
        )

        # passe
        pitch.arrows(
            row.x_carry_end,
            row.y_carry_end,
            row.x_pass_end,
            row.y_pass_end,
            color=(0.6, 0.9, 0.6, 0.9),
            width=2.2,
            headwidth=4,
            headlength=4,
            ax=ax
        )

    # pontos clicáveis (importante!)
    pitch.scatter(df.x_carry_end, df.y_carry_end, color='red', s=40, ax=ax, zorder=5)

    return fig

# ==========================
# Converter figura → imagem
# ==========================
fig = draw_pitch(df)

buf = BytesIO()
fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
buf.seek(0)

# ==========================
# Clique na imagem
# ==========================
coords_click = streamlit_image_coordinates(buf)

col1, col2 = st.columns([2,1])

with col1:
    st.image(buf)

# ==========================
# Encontrar evento clicado
# ==========================
if coords_click is not None:

    x_click = coords_click["x"]
    y_click = coords_click["y"]

    # converter pixel → coordenada do campo
    # ajuste fino pode ser necessário dependendo do tamanho
    x_norm = x_click / 1000 * 120
    y_norm = y_click / 700 * 80

    df["dist"] = np.sqrt(
        (df["x_carry_end"] - x_norm)**2 +
        (df["y_carry_end"] - y_norm)**2
    )

    evento = df.loc[df["dist"].idxmin()]

    evento_id = int(evento["id"])

    with col2:
        st.subheader(f"Evento {evento_id}")

        video_path = f"videos/evento_{evento_id}.mp4"

        if os.path.exists(video_path):
            st.video(video_path)
        else:
            st.warning("Vídeo não encontrado")
