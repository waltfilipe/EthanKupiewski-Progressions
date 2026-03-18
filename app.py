import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import pandas as pd
import numpy as np
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
        "label": f"Progression {i // 3}",
        "x_start": start[0],
        "y_start": start[1],
        "x_carry_end": carry_end[0],
        "y_carry_end": carry_end[1],
        "x_pass_end": pass_end[0],
        "y_pass_end": pass_end[1],
    })

df = pd.DataFrame(dados)

# ==========================
# SELECTOR
# ==========================
def ordinal(n):
    return ["1st", "2nd", "3rd"][n-1] if n <= 3 else f"{n}th"

evento_selecionado = st.selectbox(
    "Selecione a Progression",
    df["id"],
    format_func=lambda x: f"{ordinal(x+1)} Progression"
)
# ==========================
# Função para desenhar campo
# ==========================
def draw_pitch(df, selected_id):
    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color='#f5f5f5',
        line_color='#4a4a4a'
    )

    fig, ax = pitch.draw(figsize=(10, 7))

    for _, row in df.iterrows():

        is_selected = row["id"] == selected_id

        # condução
        pitch.lines(
            row.x_start,
            row.y_start,
            row.x_carry_end,
            row.y_carry_end,
            color=(0, 0, 0, 0.2) if not is_selected else (0, 0, 0, 0.8),
            lw=1.5 if not is_selected else 3,
            linestyle='dotted',
            ax=ax
        )

        # passe
        pitch.arrows(
            row.x_carry_end,
            row.y_carry_end,
            row.x_pass_end,
            row.y_pass_end,
            color=(0.6, 0.9, 0.6, 0.3) if not is_selected else (0.1, 0.8, 0.1, 1),
            width=2 if not is_selected else 3,
            headwidth=4,
            headlength=4,
            ax=ax
        )

    # ponto do evento selecionado
    selected = df[df["id"] == selected_id]

    pitch.scatter(
        selected.x_carry_end,
        selected.y_carry_end,
        color='red',
        s=80,
        ax=ax,
        zorder=5
    )

    return fig

# ==========================
# Layout
# ==========================
col1, col2 = st.columns([2,1])

with col1:
    fig = draw_pitch(df, evento_selecionado)

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    buf.seek(0)

    st.image(buf)

# ==========================
# Vídeo
# ==========================
with col2:
    st.subheader(f"Progression {evento_selecionado}")

    video_map = {
    0: "Progression 1 LOW.mp4",
    1: "Progression 2 LOW.mp4",
    2: "Progression 3 LOW.mp4",
    3: "Progression 4 LOW.mp4",
    4: "Progression 4 LOW.mp4",
}

    video_file = video_map.get(evento_selecionado)

    video_path = os.path.join("videos", video_file)

    if os.path.exists(video_path):
        st.video(video_path)
    else:
        st.warning("Vídeo não encontrado")
