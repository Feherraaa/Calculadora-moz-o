import streamlit as st
import pandas as pd

from math import ceil
from io import BytesIO

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)

# ==========================================================
# CONFIG
# ==========================================================

st.set_page_config(
    page_title="Cálculo Sofia",
    page_icon="🏗️",
    layout="wide"
)

# ==========================================================
# FUNÇÕES
# ==========================================================

def arredondar_5(valor):

    return int(
        ceil(valor / 5) * 5
    )


def carga_acidental(tipo):

    tabela = {

        "Residencial": 1.5,

        "Escritório": 2.5,

        "Sala de Aula": 3.0,

        "Biblioteca": 4.0,

        "Auditório": 3.0,

        "Corredor": 3.0
    }

    return tabela[tipo]


def espessura_laje(lx, ly):

    menor = min(lx, ly)

    h = (
        menor * 100
    ) / 40

    return max(
        ceil(h),
        8
    )


def peso_proprio_laje(h_cm):

    return (
        h_cm / 100
    ) * 25


def altura_viga(tipo, vao):

    if tipo == "Interna":

        h = (
            vao * 100
        ) / 12

    elif tipo == "Externa":

        h = (
            vao * 100
        ) / 10

    else:

        h = (
            vao * 100
        ) / 5

    return arredondar_5(h)


def secao_pilar(carga):
    """
    Trabalho acadêmico

    Área mínima = 360 cm²
    Menor face = 19 cm
    """

    sigma_adm = 1.0

    area_necessaria = carga / sigma_adm

    area_necessaria = max(
        area_necessaria,
        360
    )

    lado = ceil(
        area_necessaria ** 0.5
    )

    lado = max(
        lado,
        19
    )

    lado = arredondar_5(lado)

    secao = f"{lado} x {lado}"

    return (
        secao,
        area_necessaria,
        lado * lado
    )

# ==========================================================
# PDF
# ==========================================================

def gerar_pdf(

    aluno,
    disciplina,
    professor,

    df_lajes,
    df_vigas,
    df_pilares

):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer
    )

    styles = getSampleStyleSheet()

    elementos = []

    elementos.append(

        Paragraph(
            "RELATÓRIO DE PRÉ-DIMENSIONAMENTO",
            styles["Title"]
        )
    )

    elementos.append(
        Spacer(1, 20)
    )

    elementos.append(
        Paragraph(
            f"Aluno: {aluno}",
            styles["Normal"]
        )
    )

    elementos.append(
        Paragraph(
            f"Disciplina: {disciplina}",
            styles["Normal"]
        )
    )

    elementos.append(
        Paragraph(
            f"Professor: {professor}",
            styles["Normal"]
        )
    )

    elementos.append(
        Spacer(1, 20)
    )

    # ======================================================
    # LAJES
    # ======================================================

    elementos.append(
        Paragraph(
            "LAJES",
            styles["Heading1"]
        )
    )

    for _, row in df_lajes.iterrows():

        elementos.append(

            Paragraph(
                (
                    f"{row['Laje']} | "
                    f"Área = {row['Área (m²)']} m² | "
                    f"Espessura = {row['Espessura (cm)']} cm"
                ),
                styles["Normal"]
            )
        )

    elementos.append(
        PageBreak()
    )

    # ======================================================
    # VIGAS
    # ======================================================

    elementos.append(
        Paragraph(
            "VIGAS",
            styles["Heading1"]
        )
    )

    for _, row in df_vigas.iterrows():

        elementos.append(

            Paragraph(
                (
                    f"{row['Viga']} | "
                    f"{row['Tipo']} | "
                    f"Vão = {row['Vão (m)']} m | "
                    f"Altura = {row['Altura (cm)']} cm | "
                    f"Seção = {row['Seção']}"
                ),
                styles["Normal"]
            )
        )

    elementos.append(
        PageBreak()
    )

    # ======================================================
    # PILARES
    # ======================================================

    elementos.append(
        Paragraph(
            "PILARES",
            styles["Heading1"]
        )
    )

    for _, row in df_pilares.iterrows():

        elementos.append(

            Paragraph(
                (
                    f"{row['Pilar']} | "
                    f"Ainf = {row['Área Influência (m²)']} m² | "
                    f"Carga = {row['Carga (kN)']} kN | "
                    f"Área Necessária = {row['Área Necessária (cm²)']} cm² | "
                    f"Seção Adotada = {row['Seção Adotada']} | "
                    f"Área Adotada = {row['Área Adotada (cm²)']} cm²"
                ),
                styles["Normal"]
            )
        )

    doc.build(
        elementos
    )

    pdf = buffer.getvalue()

    buffer.close()

    return pdf

# ==========================================================
# TÍTULO
# ==========================================================

st.title(
    "🏗️ Cálculo Sofia"
)

st.caption(
    "Pré-dimensionamento para trabalhos acadêmicos"
)

# ==========================================================
# DADOS GERAIS
# ==========================================================

st.header(
    "📋 Dados Gerais"
)

col1, col2, col3 = st.columns(3)

with col1:

    aluno = st.text_input(
        "Aluno"
    )

with col2:

    disciplina = st.text_input(
        "Disciplina"
    )

with col3:

    professor = st.text_input(
        "Professor"
    )

col1, col2 = st.columns(2)

with col1:

    uso = st.selectbox(

        "Uso da edificação",

        [
            "Residencial",
            "Escritório",
            "Sala de Aula",
            "Biblioteca",
            "Auditório",
            "Corredor"
        ]
    )

with col2:

    pavimentos = st.number_input(
        "Número de pavimentos",
        min_value=1,
        max_value=100,
        value=1
    )

# ==========================================================
# QUANTIDADES
# ==========================================================

st.header(
    "📐 Quantidades"
)

col1, col2, col3 = st.columns(3)

with col1:

    qtd_lajes = st.number_input(
        "Quantidade de Lajes",
        min_value=1,
        max_value=200,
        value=1
    )

with col2:

    qtd_vigas = st.number_input(
        "Quantidade de Vigas",
        min_value=1,
        max_value=500,
        value=1
    )

with col3:

    qtd_pilares = st.number_input(
        "Quantidade de Pilares",
        min_value=1,
        max_value=500,
        value=1
    )

# ==========================================================
# LAJES
# ==========================================================

st.header(
    "🧱 Lajes"
)

lajes = {}

for i in range(qtd_lajes):

    with st.expander(
        f"Laje L{i+1}",
        expanded=(i == 0)
    ):

        col1, col2 = st.columns(2)

        with col1:

            lx = st.number_input(
                f"Lx L{i+1} (m)",
                min_value=0.10,
                value=4.00,
                step=0.10,
                key=f"lx_{i}"
            )

        with col2:

            ly = st.number_input(
                f"Ly L{i+1} (m)",
                min_value=0.10,
                value=5.00,
                step=0.10,
                key=f"ly_{i}"
            )

        tipo = st.selectbox(

            f"Tipo da Laje L{i+1}",

            [
                "Maciça",
                "Treliçada",
                "Pré-moldada"
            ],

            key=f"tipo_laje_{i}"
        )

        area = lx * ly

        h = espessura_laje(
            lx,
            ly
        )

        peso = peso_proprio_laje(
            h
        )

        lajes[f"L{i+1}"] = {

            "tipo": tipo,

            "lx": lx,

            "ly": ly,

            "area": round(
                area,
                2
            ),

            "espessura": h,

            "peso": round(
                peso,
                2
            )
        }

# ==========================================================
# VIGAS
# ==========================================================

st.header(
    "🏗️ Vigas"
)

vigas = []

for i in range(qtd_vigas):

    with st.expander(
        f"Viga V{i+1}",
        expanded=(i == 0)
    ):

        tipo = st.selectbox(

            f"Tipo V{i+1}",

            [
                "Interna",
                "Externa",
                "Balanço"
            ],

            key=f"tipo_viga_{i}"
        )

        vao = st.number_input(

            f"Vão V{i+1} (m)",

            min_value=0.10,

            value=5.00,

            step=0.10,

            key=f"vao_{i}"
        )

        altura = altura_viga(
            tipo,
            vao
        )

        secao = (
            f"15 x {altura}"
        )

        vigas.append({

            "nome": f"V{i+1}",

            "tipo": tipo,

            "vao": vao,

            "altura": altura,

            "secao": secao
        })

        
# ==========================================================
# PILARES
# ==========================================================

st.header(
    "🏢 Pilares"
)

pilares = []

nomes_lajes = list(
    lajes.keys()
)

carga_padrao = (

    3.0      # revestimentos

    +

    1.0      # peso próprio médio

    +

    carga_acidental(
        uso
    )
)

for i in range(qtd_pilares):

    with st.expander(
        f"Pilar P{i+1}",
        expanded=(i == 0)
    ):

        lajes_pilar = st.multiselect(

            f"Lajes que descarregam em P{i+1}",

            nomes_lajes,

            key=f"mult_lajes_pilar_{i}"
        )

        area_influencia = 0

        for laje in lajes_pilar:

            area_influencia += (
                lajes[laje]["area"]
            )

        carga = (

            area_influencia

            *

            carga_padrao

            *

            pavimentos
        )

        (
            secao,
            area_secao_req,
            area_secao_adotada
        ) = secao_pilar(
            carga
        )

        pilares.append({

            "nome": f"P{i+1}",

            "area": round(
                area_influencia,
                2
            ),

            "carga": round(
                carga,
                2
            ),

            "secao": secao,

            "area_secao_req": round(
                area_secao_req,
                2
            ),

            "area_secao_adotada": round(
                area_secao_adotada,
                2
            ),

            "lajes": ", ".join(
                lajes_pilar
            )
        })

# ==========================================================
# DATAFRAMES
# ==========================================================

df_lajes = pd.DataFrame(

    [

        {

            "Laje": nome,

            "Tipo": dados["tipo"],

            "Lx (m)": dados["lx"],

            "Ly (m)": dados["ly"],

            "Área (m²)": dados["area"],

            "Espessura (cm)": dados["espessura"],

            "Peso Próprio (kN/m²)": dados["peso"]

        }

        for nome, dados in lajes.items()

    ]
)

df_vigas = pd.DataFrame(

    [

        {

            "Viga": v["nome"],

            "Tipo": v["tipo"],

            "Vão (m)": v["vao"],

            "Altura (cm)": v["altura"],

            "Seção": v["secao"]

        }

        for v in vigas

    ]
)

df_pilares = pd.DataFrame(

    [

        {

            "Pilar": p["nome"],

            "Área Influência (m²)": p["area"],

            "Carga (kN)": p["carga"],

            "Área Necessária (cm²)": p["area_secao_req"],

            "Seção Adotada": p["secao"],

            "Área Adotada (cm²)": p["area_secao_adotada"],

            "Lajes": p["lajes"]

        }

        for p in pilares

    ]
)

# ==========================================================
# RESULTADOS
# ==========================================================

st.header(
    "📊 Resultados"
)

tab1, tab2, tab3 = st.tabs(

    [
        "Lajes",
        "Vigas",
        "Pilares"
    ]
)

with tab1:

    st.subheader(
        "Resumo das Lajes"
    )

    st.dataframe(
        df_lajes,
        use_container_width=True
    )

with tab2:

    st.subheader(
        "Resumo das Vigas"
    )

    st.dataframe(
        df_vigas,
        use_container_width=True
    )

with tab3:

    st.subheader(
        "Resumo dos Pilares"
    )

    st.dataframe(
        df_pilares,
        use_container_width=True
    )

    # ==========================================================
# RESUMO GERAL
# ==========================================================

st.header(
    "📈 Resumo Geral"
)

area_total = 0

for _, row in df_lajes.iterrows():

    area_total += row["Área (m²)"]

carga_total = 0

for _, row in df_pilares.iterrows():

    carga_total += row["Carga (kN)"]

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Lajes",
        len(df_lajes)
    )

with col2:

    st.metric(
        "Vigas",
        len(df_vigas)
    )

with col3:

    st.metric(
        "Pilares",
        len(df_pilares)
    )

with col4:

    st.metric(
        "Área Total",
        f"{area_total:.2f} m²"
    )

st.metric(
    "Carga Total da Estrutura",
    f"{carga_total:.2f} kN"
)

# ==========================================================
# VERIFICAÇÕES
# ==========================================================

st.header(
    "🔎 Verificações"
)

if area_total == 0:

    st.warning(
        "Nenhuma laje cadastrada."
    )

if len(df_pilares) == 0:

    st.warning(
        "Nenhum pilar cadastrado."
    )

for _, row in df_pilares.iterrows():

    if row["Área Influência (m²)"] <= 0:

        st.warning(

            f"{row['Pilar']} não possui "
            f"lajes vinculadas."
        )

# ==========================================================
# ESTATÍSTICAS
# ==========================================================

st.header(
    "📋 Estatísticas"
)

if len(df_lajes) > 0:

    st.write(

        f"Área média das lajes: "
        f"{df_lajes['Área (m²)'].mean():.2f} m²"
    )

if len(df_vigas) > 0:

    st.write(

        f"Vão médio das vigas: "
        f"{df_vigas['Vão (m)'].mean():.2f} m"
    )

if len(df_pilares) > 0:

    st.write(

        f"Carga média dos pilares: "
        f"{df_pilares['Carga (kN)'].mean():.2f} kN"
    )

    st.write(

        f"Área média dos pilares: "
        f"{df_pilares['Área Adotada (cm²)'].mean():.2f} cm²"
    )

# ==========================================================
# EXPORTAÇÃO PDF
# ==========================================================

st.header(
    "📄 Exportação"
)

pdf = gerar_pdf(

    aluno=aluno,

    disciplina=disciplina,

    professor=professor,

    df_lajes=df_lajes,

    df_vigas=df_vigas,

    df_pilares=df_pilares
)

st.download_button(

    label="📥 Baixar Relatório PDF",

    data=pdf,

    file_name="relatorio_calculo_sofia.pdf",

    mime="application/pdf"
)

# ==========================================================
# RESUMO FINAL
# ==========================================================

st.header(
    "🎓 Resumo Final"
)

st.success(
    "Pré-dimensionamento concluído."
)

st.write(
    f"Aluno: {aluno}"
)

st.write(
    f"Disciplina: {disciplina}"
)

st.write(
    f"Professor: {professor}"
)

st.write(
    f"Pavimentos: {pavimentos}"
)

st.write(
    f"Uso: {uso}"
)

st.write(
    f"Área total das lajes: "
    f"{area_total:.2f} m²"
)

st.write(
    f"Carga total estimada: "
    f"{carga_total:.2f} kN"
)

if len(df_pilares) > 0:

    maior_carga = (
        df_pilares["Carga (kN)"].max()
    )

    st.write(
        f"Maior carga em pilar: "
        f"{maior_carga:.2f} kN"
    )

# ==========================================================
# RODAPÉ
# ==========================================================

st.divider()

st.caption(
    "Cálculo Sofia • Ferramenta acadêmica "
    "para pré-dimensionamento estrutural."
)