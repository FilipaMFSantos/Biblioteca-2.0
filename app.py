# ===== Bibliotecas externas =====
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from urllib.parse import quote_plus
from streamlit_echarts import st_echarts

# ===== Importações locais =====
from source.data import load_raw, clean, save_suggestion
from source.functions import (
    search,
    filter_by_genre,
    most_popular,
    hidden_gems,
    get_book_detail_by_id,
    quick_stats,
    prep_genre_stats,
    echarts_scatter_popularity_quality,
    echarts_genre_bars,
    fetch_libraries_pt_osm,
    render_libraries_map,
    echarts_genre_volume_rating_combo,
)

# ===== Configuração da página =====
st.set_page_config(page_title="BIBLIOTECA 2.0", layout="wide", initial_sidebar_state="collapsed")


# ===== Estilo Personalizado =====
st.markdown(
    """
    <style>
    /* ===== Base ===== */
    .stApp {
        background: #f6f7f9;
        color: #1f2430;
    }

    /* Fonte base */
    section[data-testid="stMain"],
    section[data-testid="stMain"] * ,
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] * {
        font-family: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, Monaco,
                    Consolas, "Liberation Mono", "Courier New", monospace !important;
        color: #1f2430;
    }

    /* ===== Títulos ===== */
    h1, h2, h3, h4 {
        font-weight: 600 !important;
        letter-spacing: 0.01em !important;
    }

    /* Texto secundário */
    small, .stCaption {
        color: #6b7280 !important;
    }

    /* ===== Título principal ===== */
    .app-title {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco,
                    Consolas, "Liberation Mono", "Courier New", monospace !important;
        font-size: clamp(2.4rem, 3.6vw, 3.3rem) !important;
        font-weight: 800 !important;
        margin: 0 0 0.45rem 0 !important;
        line-height: 1.05 !important;
    }

    /* ===== Sidebar ===== */

    /* Só fixa largura quando está EXPANDIDA */
    section[data-testid="stSidebar"][aria-expanded="true"] {
    background: #eef1f4 !important;
    border-right: 1px solid #d3d8df !important;
    width: 280px !important;
    min-width: 280px !important;
    }

    /* Quando está COLAPSADA, deixa o Streamlit mandar (ou força a 0) */
    section[data-testid="stSidebar"][aria-expanded="false"] {
    width: 0 !important;
    min-width: 0 !important;
    border-right: none !important;
    }

    /* Botões da sidebar */
    section[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    border-radius: 8px !important;

    /* importante */
    display: flex !important;
    justify-content: flex-start !important;
    text-align: left !important;

    /* sugiro não usar padding 0, senão fica “colado” demais */
    padding: 0.35rem 0.5rem !important;
    gap: 0.4rem !important;  /* espaço entre ícone e texto */
    }

    /* Força o wrapper interno a alinhar à esquerda (aqui é onde costuma falhar) */
    section[data-testid="stSidebar"] .stButton > button > div {
    display: flex !important;
    justify-content: flex-start !important;
    align-items: center !important;
    width: 100% !important;
    }

    /* Texto */
    section[data-testid="stSidebar"] .stButton > button p,
    section[data-testid="stSidebar"] .stButton > button span {
    text-align: left !important;
    margin: 0 !important;
    white-space: nowrap !important;
    }

    /* ===== Cards (containers com border=True) ===== */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }

    /* Botões do conteúdo principal (Home etc.) */
    section[data-testid="stMain"] .stButton > button {
        background: rgba(0, 0, 0, 0.02) !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em !important;
        box-shadow: none !important;
    }

    /* Hover subtil só no conteúdo principal */
    section[data-testid="stMain"] .stButton > button:hover {
        background: rgba(0, 0, 0, 0.03) !important;
    }

    /* Header topo */
    header[data-testid="stHeader"] {
        background: #f6f7f9 !important;
        border-bottom: 1px solid #e2e6ea !important;
    }

    /* Dataframes */
    .stDataFrame {
        background: #ffffff !important;
    }

    /* ===== Ícones (compatível com Material Symbols do Streamlit) ===== */
    [data-testid="stIcon"],
    [data-testid="stIcon"] * {
        font-family: "Material Symbols Rounded","Material Symbols Outlined","Material Icons" !important;
        font-weight: 400 !important;
        font-style: normal !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        line-height: 1 !important;
    }

    /* Sidebar toggle: usar fonte nativa de ícones (não IBM Plex Mono) */
    section[data-testid="stSidebar"] button[data-testid="stSidebarCollapseButton"],
    section[data-testid="stSidebar"] button[data-testid="stSidebarCollapseButton"] * ,
    section[data-testid="stSidebar"] div[data-testid="collapsedControl"],
    section[data-testid="stSidebar"] div[data-testid="collapsedControl"] * {
        font-family: "Material Symbols Rounded","Material Symbols Outlined","Material Icons" !important;
        font-weight: 400 !important;
        font-style: normal !important;
        letter-spacing: normal !important;
        line-height: 1 !important;
        text-transform: none !important;
    }

    /* Tamanho do ícone do toggle */
    button[data-testid="stSidebarCollapseButton"] [translate="no"],
    div[data-testid="collapsedControl"] [translate="no"] {
        font-size: 20px !important;
    }

    /* Topbar/header: ícones Material (evita aparecer keyboard_...) */
    header [translate="no"],
    div[data-testid="stToolbar"] [translate="no"],
    div[data-testid="stDecoration"] [translate="no"] {
        font-family: "Material Symbols Rounded","Material Symbols Outlined","Material Icons" !important;
        font-weight: 400 !important;
        font-style: normal !important;
        line-height: 1 !important;
    }

    /* Corrigir APENAS o toggle dentro da sidebar (independente do data-testid do botão) */
    section[data-testid="stSidebar"] [translate="no"] {
        font-family: "Material Symbols Rounded","Material Symbols Outlined","Material Icons" !important;
    }

    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded');

    h1.app-title{
        display: flex !important;
        align-items: center !important;
        gap: 14px !important;   
    }

    h1.app-title::before{
        content: "book";
        font-family: "Material Symbols Rounded" !important;
        font-size: 3 rem;
        line-height: 1;
        font-weight: 400;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


DISPLAY_MAP = {
    "book_id": "ID",
    "title": "Title",
    "author": "Author",
    "isbn": "ISBN",
    "rating": "Rating",
    "genres_list": "Genres",
    "totalratings": "Votes",
    "reviews": "Reviews",
    "ratings_count": "RatingsCount",
    "desc": "Description",
}


COL_ORDER = ["title", "author", "genres_list", "rating"]

@st.cache_data
def load_data(path: str = "source/GoodReads_100k_books.csv") -> pd.DataFrame | None:
    df_raw = load_raw(path)
    if df_raw is None:
        return None
    df_clean = clean(df_raw)
    return df_clean

@st.cache_data(ttl=24 * 3600, show_spinner=False)
def get_libraries_osm_cached() -> pd.DataFrame:
    return fetch_libraries_pt_osm()


def make_view(df_in: pd.DataFrame) -> pd.DataFrame:
    # 1) garante o id interno 
    if "book_id" in df_in.columns:
        base = df_in.copy()
        base["_book_id"] = base["book_id"].astype(str)
    else:
        # fallback (caso o teu df venha sem book_id por algum motivo)
        base = df_in.copy()
        base["_book_id"] = base.index.astype(str)

    # 2) seleciona colunas para UI + _book_id (interno)
    cols = ["_book_id"] + [c for c in COL_ORDER if c in base.columns]
    view = base[cols].copy().reset_index(drop=True)

    # Rating com estrelas
    if "rating" in view.columns:
        def _fmt_rating(x):
            try:
                r = float(x)
            except (TypeError, ValueError):
                return ""
            return f"{stars_for_rating(r)}"
        view["rating"] = view["rating"].apply(_fmt_rating)

    # Géneros: lista -> string
    if "genres_list" in view.columns:
        def _fmt_genres(lst):
            if isinstance(lst, (list, tuple)) and len(lst) > 0:
                out = ", ".join([str(g) for g in lst[:3]])
                return out + ("…" if len(lst) > 3 else "")
            return ""
        view["genres_list"] = view["genres_list"].apply(_fmt_genres)

    return view

def make_column_config(df_view: pd.DataFrame) -> dict:
    cfg = {}
    for c in df_view.columns:
        if c.startswith("_"):
            continue
        cfg[c] = st.column_config.Column(DISPLAY_MAP.get(c, c))
    return cfg


def build_store_links(isbn: str | None, title: str, author: str) -> dict:
    title = (title or "").strip()
    author = (author or "").strip()

    # query principal (título + autor). Se não houver autor, usa só título.
    q_text = quote_plus(f"{title} {author}".strip() if author else title)
    q_title = quote_plus(title)

    return {
        "Wook": f"https://www.wook.pt/pesquisa?keyword={q_title}",
        "Bertrand": f"https://www.bertrand.pt/pesquisa/{q_text}",
        "Fnac": f"https://www.fnac.pt/SearchResult/ResultList.aspx?Search={q_text}",
        "Google": f"https://www.google.com/search?q={q_text}+comprar+livro",
    }


def render_store_buttons(book: dict):
    title = book.get("title", "")
    author = book.get("author", "")
    isbn = book.get("isbn")

    links = build_store_links(
        isbn=isbn,
        title=title,
        author=author,
    )

    # Botão “Comparar preços” (Google) — útil e consistente
    q_text = f"{title} {author}".strip() if author else str(title).strip()
    compare_url = f"https://www.google.com/search?q={quote_plus(q_text)}+pre%C3%A7o+livro"

    st.markdown("**Comprar / pesquisar em:**")

    # Linha 1: lojas
    c1, c2, c3 = st.columns(3)
    with c1:
        st.link_button("Wook", links["Wook"], use_container_width=True)
    with c2:
        st.link_button("Bertrand", links["Bertrand"], use_container_width=True)
    with c3:
        st.link_button("Fnac", links["Fnac"], use_container_width=True)

    # Linha 2: comparar preços (sem primary)
    st.link_button(
        "**Comparar preços**",
        compare_url,
        use_container_width=True
    )

    st.caption("Os resultados, preços e disponibilidade podem variar entre lojas.")

    st.markdown("---")


def render_book_detail(book: dict, df_lib: pd.DataFrame):
    left, right = st.columns([1, 2], gap="large")

    with left:
        if book.get("img"):
            st.image(book["img"], use_container_width=True)
        if book.get("link"):
            st.markdown(f"[Ver no Goodreads]({book['link']})")

    with right:
        st.markdown(f"### {book.get('title','')}")
        st.write(f"Autor: {book.get('author','')}")

        r = book.get("rating")
        n = book.get("totalratings")

        if r is not None:
            stars = stars_for_rating(r)

            try:
                r_txt = f"{float(r):.2f}".rstrip("0").rstrip(".")
            except (TypeError, ValueError):
                r_txt = str(r)

            try:
                n_txt = f"{int(n):,}".replace(",", ".")
            except (TypeError, ValueError):
                n_txt = "—"

            st.markdown(
                f"""<div style="margin-top:0.35rem">
  <div style="font-size:0.9rem; font-weight:700; color:#6b7280 !important; margin-bottom:0.25rem;">
    Rating
  </div>    
  <div style="display:flex; align-items:baseline; gap:0.6rem;">
    <span style="font-size:1.4rem;">{stars}</span>
    <span style="font-size:1.35rem; font-weight:600;">{r_txt}</span>
    <span style="font-size:0.9rem; color:#6b7280 !important;">
      ({n_txt} avaliações)
    </span>
  </div>
</div>""",
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)

        if isinstance(book.get("genres_list"), list) and book["genres_list"]:
            st.write("**Géneros:**", ", ".join([str(g) for g in book["genres_list"]]))

        if book.get("desc"):
            st.markdown("#### Descrição")
            st.write(book["desc"])

    st.divider()
    render_store_buttons(book)

    st.markdown("### Rede Nacional de Bibliotecas")
    st.caption("Visita a biblioteca mais próxima e descobre se têm este livro disponível para empréstimo.")

    render_libraries_map(df_lib, height=480)

    st.caption("Fonte: dados do OpenStreetMap")


def stars_for_rating(rating, max_stars: int = 5) -> str:
    try:
        r = float(rating)
    except (TypeError, ValueError):
        return ""
    r = max(0.0, min(float(max_stars), r))
    filled = int(round(r))  # arredonda para estrela inteira
    return "★" * filled + "☆" * (max_stars - filled)


df = load_data()

if df is None or len(df) == 0:
    st.error("Não foi possível carregar o ficheiro de dados. Verifica o caminho do CSV.")
    st.stop()

st.markdown('<h1 class="app-title">BIBLIOTECA 2.0</h1>', unsafe_allow_html=True)

MENU_ITEMS = [
    ("Home", ":material/home:"),
    ("Explorar catálogo", ":material/search:"),
    ("Explorar por género", ":material/category:"),
    ("Livros mais populares", ":material/kid_star:"),
    ("Pérolas escondidas", ":material/diamond:"),
    ("Insights & Tendências", ":material/insights:"),
    ("Sugerir novo livro", ":material/add:"),
    ("Sobre nós", ":material/menu_book:"),
]


if "option" not in st.session_state:
    st.session_state.option = "Home"

with st.sidebar:
    st.title("Menu")
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

    for label, icon in MENU_ITEMS:
        if st.button(
            label,
            icon=icon,
            key=f"menu_{label}",
            use_container_width=True
        ):
            st.session_state.option = label

option = st.session_state.option

if "scroll_counter" not in st.session_state:
    st.session_state.scroll_counter = 0


def scroll_to_details():
    st.markdown('<div id="detalhes-livro"></div>', unsafe_allow_html=True)
    st.session_state.scroll_counter += 1
    components.html(
        f"""
        <div style="display:none">token:{st.session_state.scroll_counter}</div>
        <script>
          function go() {{
            const el =
              document.getElementById("detalhes-livro") ||
              (window.parent && window.parent.document &&
               window.parent.document.getElementById("detalhes-livro"));
            if (el) el.scrollIntoView({{ behavior: "smooth", block: "start" }});
          }}
          setTimeout(go, 100);
        </script>
        """,
        height=0,
    )


# =========================
# Conteúdo principal
# =========================

if option == "Home":
    st.markdown(
    """
Descobre livros, autores e géneros através da plataforma literária mais popular do mundo.
Explora as melhores obras, as mais populares e encontra a tua próxima grande leitura!
"""
)
    
    # Espaço extra entre o texto introdutório e o menu do Home
    st.markdown("<div style='height: 90px;'></div>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        with st.container(border=True):
            st.subheader("Explorar catálogo")
            st.write("Pesquisa por título, autor ou ISBN.")
            if st.button("Abrir", use_container_width=True, key="go_catalog"):
                st.session_state.option = "Explorar catálogo"
                st.rerun()

    with c2:
        with st.container(border=True):
            st.subheader("Explorar por género")
            st.write("Encontra livros por género.")
            if st.button("Abrir", use_container_width=True, key="go_genre"):
                st.session_state.option = "Explorar por género"
                st.rerun()

    with c3:
        with st.container(border=True):
            st.subheader("Livros mais populares")
            st.write("Vê os mais avaliados e mais lidos.")
            if st.button("Abrir", use_container_width=True, key="go_popular"):
                st.session_state.option = "Livros mais populares"
                st.rerun()

    c4, c5, c6 = st.columns(3, gap="medium")

    with c4:
        with st.container(border=True):
            st.subheader("Pérolas escondidas")
            st.write("Boas leituras com menos hype.")
            if st.button("Abrir", use_container_width=True, key="go_gems"):
                st.session_state.option = "Pérolas escondidas"
                st.rerun()

    with c5:
        with st.container(border=True):
            st.subheader("Insights & Tendências")
            st.write("Explora as tendências do catálogo.")
            if st.button("Abrir", use_container_width=True, key="go_last"):
                st.session_state.option = "Insights & Tendências"
                st.rerun()

    with c6:
        with st.container(border=True):
            st.subheader("Estatísticas rápidas")
            st.write("Resumo do catálogo e curiosidades.")
            if st.button("Abrir", use_container_width=True, key="go_stats"):
                st.session_state.option = "Estatísticas rápidas"
                st.rerun()


elif option == "Explorar catálogo":
    st.subheader("Explorar catálogo")
    query = st.text_input("Texto a pesquisar (título, autor ou ISBN):")

    if query:
        res = search(df, query)

        if res is None or len(res) == 0:
            st.warning("Nenhum livro encontrado para essa pesquisa.")
        else:
            st.write(f"Foram encontrados {len(res)} livros.")
            view = make_view(res)

            st.markdown(
                "<small style='color:#888;'>Dica: usa Ctrl/Cmd para selecionar várias linhas, ou Shift para selecionar um intervalo.</small>",
                unsafe_allow_html=True,
            )

            view_ui = view.drop(columns=["_book_id"], errors="ignore")

            evt = st.dataframe(
                view_ui,
                use_container_width=True,
                hide_index=True,
                column_config=make_column_config(view_ui),
                selection_mode="multi-row",
                on_select="rerun",
            )

            rows = (evt.selection.rows if (evt and evt.selection) else [])
            n_sel = len(rows)

            if n_sel == 0:
                st.info("Seleciona um livro na tabela para veres os detalhes.")
            else:
                selected_df = view.iloc[rows].copy()
                scroll_to_details()

                # (NOVO) carrega bibliotecas 1 vez por rerun e reutiliza
                try:
                    df_lib_global = get_libraries_osm_cached()
                except Exception:
                    df_lib_global = pd.DataFrame()

                if n_sel == 1:
                    st.subheader("Detalhes do livro")
                    chosen_id = str(selected_df.iloc[0]["_book_id"])
                    book = get_book_detail_by_id(df, chosen_id)
                    if book:
                        render_book_detail(book, df_lib_global)
                    else:
                        st.info("Não foi possível obter os detalhes deste livro.")
                else:
                    st.subheader("Detalhes dos livros selecionados")

                    tabs_labels = []
                    for _, r in selected_df.iterrows():
                        title = str(r.get("title", "")).strip()
                        label = f"{title[:35]}{'…' if len(title) > 35 else ''}"
                        tabs_labels.append(label)

                    tabs = st.tabs(tabs_labels)

                    for tab, (_, r) in zip(tabs, selected_df.iterrows()):
                        with tab:
                            chosen_id = str(r["_book_id"])
                            book = get_book_detail_by_id(df, chosen_id)
                            if book:
                                render_book_detail(book, df_lib_global)
                            else:
                                st.info("Não foi possível obter os detalhes deste livro.")


elif option == "Explorar por género":
    st.subheader("Explorar por género")

    genres = (
        sorted(
            set(
                g
                for cell in df.get("genres_list", [])
                for g in (cell if isinstance(cell, list) else [])
            )
        )
        if "genres_list" in df.columns
        else []
    )

    genre = st.selectbox("Escolhe um género:", genres) if genres else None

    if not genres:
        st.info("Não foi possível inferir a lista de géneros a partir dos dados.")
    elif genre:
        res = filter_by_genre(df, genre)

        if res is None or len(res) == 0:
            st.warning(f"Nenhum livro encontrado para o género '{genre}'.")
        else:
            st.write(f"Foram encontrados {len(res)} livros no género '{genre}'.")
            view = make_view(res)

            st.markdown(
                "<small style='color:#888;'>Dica: usa Ctrl/Cmd para selecionar várias linhas, ou Shift para selecionar um intervalo.</small>",
                unsafe_allow_html=True,
            )

            view_ui = view.drop(columns=["_book_id"], errors="ignore")

            evt = st.dataframe(
                view_ui,
                use_container_width=True,
                hide_index=True,
                column_config=make_column_config(view_ui),
                selection_mode="multi-row",
                on_select="rerun",
            )

            rows = (evt.selection.rows if (evt and evt.selection) else [])
            n_sel = len(rows)

            if n_sel == 0:
                st.info("Seleciona um livro na tabela para veres os detalhes.")
            else:
                selected_df = view.iloc[rows].copy()
                scroll_to_details()

                # (NOVO) carrega bibliotecas 1 vez por rerun e reutiliza
                try:
                    df_lib_global = get_libraries_osm_cached()
                except Exception:
                    df_lib_global = pd.DataFrame()

                if n_sel == 1:
                    st.subheader("Detalhes do livro")
                    chosen_id = str(selected_df.iloc[0]["_book_id"])
                    book = get_book_detail_by_id(df, chosen_id)
                    if book:
                        render_book_detail(book, df_lib_global)
                    else:
                        st.info("Não foi possível obter os detalhes deste livro.")
                else:
                    st.subheader("Detalhes dos livros selecionados")

                    tabs_labels = []
                    for _, r in selected_df.iterrows():
                        bid = str(r["_book_id"])
                        title = str(r.get("title", "")).strip()
                        label = f"{bid} — {title[:35]}{'…' if len(title) > 35 else ''}"
                        tabs_labels.append(label)

                    tabs = st.tabs(tabs_labels)

                    for tab, (_, r) in zip(tabs, selected_df.iterrows()):
                        with tab:
                            chosen_id = str(r["_book_id"])
                            book = get_book_detail_by_id(df, chosen_id)
                            if book:
                                render_book_detail(book, df_lib_global)
                            else:
                                st.info("Não foi possível obter os detalhes deste livro.")


elif option == "Livros mais populares":
    st.subheader("Livros mais populares")
    n = st.slider("Número de livros a mostrar:", min_value=5, max_value=50, value=20)

    res = most_popular(df, n=n)
    if res is None or len(res) == 0:
        st.warning("Não foi possível obter a lista de livros mais populares.")
    else:
        view = make_view(res)

        st.markdown(
            "<small style='color:#888;'>Dica: usa Ctrl/Cmd para selecionar várias linhas, ou Shift para selecionar um intervalo.</small>",
            unsafe_allow_html=True,
        )

        view_ui = view.drop(columns=["_book_id"], errors="ignore")

        evt = st.dataframe(
            view_ui,
            use_container_width=True,
            hide_index=True,
            column_config=make_column_config(view_ui),
            selection_mode="multi-row",
            on_select="rerun",
        )

        rows = (evt.selection.rows if (evt and evt.selection) else [])
        n_sel = len(rows)

        if n_sel == 0:
            st.info("Seleciona um livro na tabela para veres os detalhes.")
        else:
            selected_df = view.iloc[rows].copy()
            scroll_to_details()

            # IMPORTANTE: carregar bibliotecas 1 vez e reutilizar
            try:
                df_lib_global = get_libraries_osm_cached()
            except Exception:
                df_lib_global = pd.DataFrame()

            # Debug opcional (remove depois)
            # st.caption(f"Bibliotecas carregadas: {len(df_lib_global)}")

            if n_sel == 1:
                st.subheader("Detalhes do livro")
                chosen_id = str(selected_df.iloc[0]["_book_id"])
                book = get_book_detail_by_id(df, chosen_id)
                if book:
                    render_book_detail(book, df_lib_global)  # <-- passa df_lib_global
                else:
                    st.info("Não foi possível obter os detalhes deste livro.")
            else:
                st.subheader("Detalhes dos livros selecionados")

                tabs_labels = []
                for _, r in selected_df.iterrows():
                    title = str(r.get("title", "")).strip()
                    label = f"{title[:35]}{'…' if len(title) > 35 else ''}"
                    tabs_labels.append(label)

                tabs = st.tabs(tabs_labels)

                for tab, (_, r) in zip(tabs, selected_df.iterrows()):
                    with tab:
                        chosen_id = str(r["_book_id"])
                        book = get_book_detail_by_id(df, chosen_id)
                        if book:
                            render_book_detail(book, df_lib_global)  # <-- e aqui também
                        else:
                            st.info("Não foi possível obter os detalhes deste livro.")


elif option == "Pérolas escondidas":
    st.subheader("Pérolas escondidas")
    min_rating = st.slider("Rating mínimo:", 0.0, 5.0, 4.0, 0.1)
    min_ratings = st.number_input("Mínimo de avaliações:", min_value=0, value=50)
    max_ratings = st.number_input("Máximo de avaliações:", min_value=1, value=2000)
    n = st.slider("Número máximo de livros:", min_value=5, max_value=50, value=20)

    res = hidden_gems(df, min_rating=min_rating, min_ratings=min_ratings, max_ratings=max_ratings, n=n)

    if res is None or len(res) == 0:
        st.warning("Não foram encontradas pérolas com estes critérios.")
    else:
        view = make_view(res)

        st.markdown(
            "<small style='color:#888;'>Dica: usa Ctrl/Cmd para selecionar várias linhas, ou Shift para selecionar um intervalo.</small>",
            unsafe_allow_html=True,
        )

        view_ui = view.drop(columns=["_book_id"], errors="ignore")

        evt = st.dataframe(
            view_ui,
            use_container_width=True,
            hide_index=True,
            column_config=make_column_config(view_ui),
            selection_mode="multi-row",
            on_select="rerun",
        )

        rows = (evt.selection.rows if (evt and evt.selection) else [])
        n_sel = len(rows)

        if n_sel == 0:
            st.info("Seleciona um livro na tabela para veres os detalhes.")
        else:
            selected_df = view.iloc[rows].copy()
            scroll_to_details()


            try:
                df_lib_global = get_libraries_osm_cached()
            except Exception:
                df_lib_global = pd.DataFrame()


            if n_sel == 1:
                st.subheader("Detalhes do livro")
                chosen_id = str(selected_df.iloc[0]["_book_id"])
                book = get_book_detail_by_id(df, chosen_id)
                if book:
                    render_book_detail(book, df_lib_global)  
                else:
                    st.info("Não foi possível obter os detalhes deste livro.")
            else:
                st.subheader("Detalhes dos livros selecionados")

                tabs_labels = []
                for _, r in selected_df.iterrows():
                    title = str(r.get("title", "")).strip()
                    label = f"{title[:35]}{'…' if len(title) > 35 else ''}"
                    tabs_labels.append(label)

                tabs = st.tabs(tabs_labels)

                for tab, (_, r) in zip(tabs, selected_df.iterrows()):
                    with tab:
                        chosen_id = str(r["_book_id"])
                        book = get_book_detail_by_id(df, chosen_id)
                        if book:
                            render_book_detail(book, df_lib_global)
                        else:
                            st.info("Não foi possível obter os detalhes deste livro.")


elif option == "Insights & Tendências":
    st.subheader("Insights & Tendências")
    st.write("Uma leitura rápida do catálogo: popularidade, qualidade e padrões por género.")

    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

    # =========================
    # 1) Géneros: quantidade vs qualidade
    # =========================
    st.markdown("### Quantidade vs Qualidade")
    st.caption("Alguns géneros dominam em volume, mas outros destacam-se na avaliação média.")

    use_relation = st.toggle("Mostrar relação Volume vs Rating", value=True)

    if use_relation:
        option_genres = echarts_genre_volume_rating_combo(df, top_n=12)
        height_genres = "520px"
    else:
        option_genres = echarts_genre_bars(df, top_n=12)
        height_genres = "620px"

    if not option_genres.get("series"):
        st.info("Não há dados de géneros suficientes para esta análise.")
    else:
        st_echarts(
            options=option_genres,
            height=height_genres,
        )

        # Storytelling final (mantém)
        gdf = prep_genre_stats(df, top_n=12)
        if gdf is not None and not gdf.empty:
            best = gdf.sort_values("avg_rating", ascending=False).iloc[0]
            st.caption(
                f"Entre os géneros mais representados, "
                f"'{best['genre']}' tem o maior rating médio ({best['avg_rating']:.2f})."
            )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("---")

    # =========================
    # 2) Popularidade vs Qualidade
    # =========================
    st.markdown("### Popularidade vs Qualidade")
    st.caption("Nem sempre os livros mais populares são os mais bem avaliados.")

    option_scatter = echarts_scatter_popularity_quality(df)

    if not option_scatter.get("series"):
        st.info("Não há dados suficientes para gerar este gráfico.")
    else:
        st_echarts(
            options=option_scatter,
            height="480px",
        )

elif option == "Sugerir novo livro":
    st.subheader("Sugerir um novo livro")
    title = st.text_input("Título do livro:")
    author = st.text_input("Autor(a):")
    genres = st.text_input("Género(s) (opcional):")

    if st.button("Submeter sugestão"):
        if not title:
            st.warning("É necessário indicar pelo menos o título.")
        else:
            save_suggestion(title, author, genres)
            st.success("Obrigado pela tua sugestão!")


elif option == "Sobre nós":

    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

    out = quick_stats(df)
    stats = out.get("stats", {})
    c1, c2, c3 = st.columns(3)

    def format_br(n):
        if n is None:
            return "—"
        return f"{n:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

    with c1:
        st.metric("Livros", format_br(stats.get("total_livros")))
    with c2:
        st.metric("Autores", format_br(stats.get("total_autores")))
    with c3:
        rm = stats.get("rating_medio", None)
        st.metric("Rating médio", f"{float(rm):.2f}".rstrip("0").rstrip(".") if isinstance(rm, (int, float)) else "—")

    for line in out.get("lines", []):
        st.write(line)

