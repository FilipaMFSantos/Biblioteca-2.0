
import pandas as pd
from streamlit_echarts import JsCode

def search(df: pd.DataFrame, query: str) -> pd.DataFrame:
    if df is None or df.empty:
        return df

    q = str(query).strip() if query is not None else ""
    if not q:
        return df

    q_lower = q.lower()

    # compatível com 'author' ou 'authors'
    author_col = "author" if "author" in df.columns else ("authors" if "authors" in df.columns else None)

    mask = pd.Series(False, index=df.index)

    if "title" in df.columns:
        mask |= df["title"].fillna("").astype(str).str.lower().str.contains(q_lower, na=False)

    if author_col:
        mask |= df[author_col].fillna("").astype(str).str.lower().str.contains(q_lower, na=False)

    res = df[mask].copy()
    if not res.empty:
        return res

    # fallback: ISBN-10 (match exato)
    if "isbn" in df.columns:
        res = df[df["isbn"].fillna("").astype(str).str.strip() == q].copy()
        if not res.empty:
            return res

    return df.head(0)

def filter_by_genre(df: pd.DataFrame, genre: str) -> pd.DataFrame:
    """
    Filtra livros por género.
    Preferência: 'genres_list' (lista). Fallback: 'genre' (texto).
    """
    if df is None or len(df) == 0:
        return df
    if not genre:
        return df

    genre = str(genre).strip().lower()

    if "genres_list" in df.columns:
        mask = df["genres_list"].apply(
            lambda lst: isinstance(lst, (list, tuple)) and genre in [str(g).lower() for g in lst]
        )
        return df[mask].copy()

    if "genre" in df.columns:
        mask = df["genre"].fillna("").astype(str).str.lower().str.contains(genre, na=False)
        return df[mask].copy()

    return df.head(0)

def most_popular(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """
    Retorna os n livros com mais avaliações.
    Tenta usar 'totalratings'. Se não existir, tenta 'reviews' ou 'ratings_count'.
    """
    if df is None or len(df) == 0:
        return df

    col = None
    for candidate in ["totalratings", "reviews", "ratings_count"]:
        if candidate in df.columns:
            col = candidate
            break

    if col is None:
        return df.head(0)

    d = df.copy()
    d[col] = pd.to_numeric(d[col], errors="coerce").fillna(0)
    return d.sort_values(col, ascending=False).head(int(n))

def hidden_gems(
    df: pd.DataFrame,
    min_rating: float = 4.0,
    min_ratings: int = 50,
    max_ratings: int = 2000,
    n: int = 20,
) -> pd.DataFrame:
    """
    Encontra 'pérolas escondidas': rating alto, mas ainda relativamente poucos votos.
    """
    if df is None or len(df) == 0:
        return df

    for col in ["rating", "totalratings"]:
        if col not in df.columns:
            return df.head(0)

    d = df.copy()
    d["rating"] = pd.to_numeric(d["rating"], errors="coerce")
    d["totalratings"] = pd.to_numeric(d["totalratings"], errors="coerce")

    mask = (
        (d["rating"] >= float(min_rating))
        & (d["totalratings"] >= int(min_ratings))
        & (d["totalratings"] <= int(max_ratings))
    )
    d = d[mask]
    if d.empty:
        return d

    d = d.sort_values(["rating", "totalratings"], ascending=[False, True])
    return d.head(int(n))

def quick_stats(df: pd.DataFrame) -> dict:
    """
    Calcula estatísticas rápidas e devolve:
      - stats: valores numéricos (para métricas)
      - lines: frases prontas a mostrar no Streamlit
      - top_genres: lista de géneros mais frequentes
    """
    if df is None or len(df) == 0:
        return {
            "stats": {},
            "lines": ["Ups, a nossa estante está vazia... Não há estatísticas para mostrar."],
            "top_genres": [],
        }

    def rating_to_stars(r):
        if r is None or pd.isna(r):
            return ""
        n_full = int(round(float(r)))
        n_full = max(0, min(5, n_full))
        return "★" * n_full + "☆" * (5 - n_full)

    stats = {}
    stats["total_livros"] = int(len(df))
    stats["total_autores"] = int(df["author"].dropna().nunique()) if "author" in df.columns else None

    if "rating" in df.columns:
        ratings = pd.to_numeric(df["rating"], errors="coerce")
        stats["rating_medio"] = float(ratings.mean()) if ratings.notna().any() else None
    else:
        stats["rating_medio"] = None

    if "pages" in df.columns:
        pages = pd.to_numeric(df["pages"], errors="coerce")
        stats["paginas_medias"] = float(pages.mean()) if pages.notna().any() else None
    else:
        stats["paginas_medias"] = None

    # =========================
    # Limpeza de géneros
    # =========================
    BAD_GENRES = {"****", "", "nan", "none", "unknown"}

    top_genres = []
    if "genre" in df.columns:
        g = (
            df["genre"]
            .dropna()
            .astype(str)
            .str.split(",", n=1)
            .str[0]
            .str.strip()
        )

        g = g[
            g.str.lower().notna()
            & ~g.str.lower().isin(BAD_GENRES)
        ]

        counts = g.value_counts().head(5)
        top_genres = list(counts.index)

    lines = []

    if stats["rating_medio"] is not None:
        estrelas = rating_to_stars(stats["rating_medio"])
        lines.append(
            f"Em média, os nossos leitores dão uma nota de **{stats['rating_medio']:.2f}** "
            f"em 5 estrelas (**{estrelas}**)."
        )

    if stats["paginas_medias"] is not None:
        lines.append(
            f"Quanto ao tamanho, cada livro anda ali pelas **{int(stats['paginas_medias'])}** páginas, "
            "mais coisa menos coisa."
        )

    if top_genres:
        if len(top_genres) == 1:
            frase = f"O género que mais se lê por aqui é **{top_genres[0]}**."
        elif len(top_genres) == 2:
            frase = f"Os géneros que mais se lêem por aqui são **{top_genres[0]}** e **{top_genres[1]}**."
        else:
            primeiros = ", ".join(f"**{g}**" for g in top_genres[:3])
            restantes = ", ".join(f"**{g}**" for g in top_genres[3:])
            frase = f"Os géneros que mais se lêem por aqui são {primeiros}, mas também há muito {restantes}."
        lines.append(frase)

    lines.append("\nObrigado por visitares a nossa biblioteca. Continua a explorar!")

    return {"stats": stats, "lines": lines, "top_genres": top_genres}

def get_book_detail_by_id(df: pd.DataFrame, book_id) -> dict | None:
    """
    Devolve um único livro (dict) pelo book_id.
    """
    if df is None or len(df) == 0:
        return None
    if "book_id" not in df.columns:
        return None

    sub = df[df["book_id"].astype(str) == str(book_id)]
    if sub.empty:
        return None
    return sub.iloc[0].to_dict()

def prep_popularity_vs_quality(df: pd.DataFrame) -> pd.DataFrame:
    """
    Devolve um DF com colunas necessárias para o scatter:
    - totalratings (x)
    - rating (y)
    - title/author (para tooltip)
    Limpa NA e garante tipos numéricos.
    """
    cols = [c for c in ["title", "author", "genres_list", "rating", "totalratings"] if c in df.columns]
    if not cols:
        return pd.DataFrame(columns=["title", "author", "genres_list", "rating"])

    out = df[cols].copy()

    if "rating" in out.columns:
        out["rating"] = pd.to_numeric(out["rating"], errors="coerce")
    if "totalratings" in out.columns:
        out["totalratings"] = pd.to_numeric(out["totalratings"], errors="coerce")

    # garantir que temos as colunas críticas antes de filtrar
    if "rating" not in out.columns or "totalratings" not in out.columns:
        return pd.DataFrame(columns=["title", "author", "rating", "totalratings"])

    out = out.dropna(subset=["rating", "totalratings"])
    out = out[(out["totalratings"] > 0) & (out["rating"] > 0)]
    return out

def prep_genre_stats(df: pd.DataFrame, top_n: int = 12) -> pd.DataFrame:
    """
    Agrega por género:
    - n_books
    - avg_rating
    - median_rating
    - avg_totalratings
    Devolve top_n por n_books.
    """
    if "genres_list" not in df.columns:
        return pd.DataFrame(columns=["genre", "n_books", "avg_rating", "median_rating", "avg_totalratings"])

    base_cols = [c for c in ["genres_list", "rating", "totalratings"] if c in df.columns]
    if "genres_list" not in base_cols:
        return pd.DataFrame(columns=["genre", "n_books", "avg_rating", "median_rating", "avg_totalratings"])

    tmp = df[base_cols].copy()

    if "rating" in tmp.columns:
        tmp["rating"] = pd.to_numeric(tmp["rating"], errors="coerce")
    else:
        tmp["rating"] = pd.NA

    if "totalratings" in tmp.columns:
        tmp["totalratings"] = pd.to_numeric(tmp["totalratings"], errors="coerce")
    else:
        tmp["totalratings"] = pd.NA

    tmp = tmp.explode("genres_list").rename(columns={"genres_list": "genre"})
    tmp["genre"] = tmp["genre"].astype(str).str.strip()

    # remover vazios
    tmp = tmp[tmp["genre"].ne("") & tmp["genre"].ne("nan")]

    agg = (
        tmp.groupby("genre", as_index=False)
        .agg(
            n_books=("genre", "size"),
            avg_rating=("rating", "mean"),
            median_rating=("rating", "median"),
            avg_totalratings=("totalratings", "mean"),
        )
        .sort_values("n_books", ascending=False)
        .head(top_n)
    )
    return agg

def echarts_scatter_popularity_quality(df: pd.DataFrame) -> dict:
    d = prep_popularity_vs_quality(df)
    if d is None or d.empty:
        return {"series": []}

    # amostra para performance
    if len(d) > 8000:
        d = d.sample(8000, random_state=42)

    # referências para quadrantes
    y_ref = float(d["rating"].median())
    x_ref = float(d["totalratings"].quantile(0.75))

    r_min = float(d["rating"].min())
    r_max = float(d["rating"].max())

    # fallback de segurança (caso rating seja constante)
    if r_min == r_max:
        r_min = max(0.0, r_min - 0.1)
        r_max = min(5.0, r_max + 0.1)

    def stars_text(r: float) -> str:
        full = int(r)
        half = (r - full) >= 0.5
        return "★" * full + ("½" if half else "")

    source = []
    for _, r in d.iterrows():
        rating = float(r["rating"])
        votes = int(r["totalratings"])
        source.append({
            "votes": votes,
            "rating": rating,
            "title": str(r.get("title", "")).strip(),
            "author": str(r.get("author", "")).strip(),
            "stars": stars_text(rating),
        })

    option = {
        "backgroundColor": "rgba(0,0,0,0)",
        "grid": {"left": 70, "right": 30, "top": 40, "bottom": 60},
        "dataset": {"source": source},

        # Cor (opaco, sem neon)
        "visualMap": {
            "show": False,
            "type": "continuous",
            "dimension": "rating",
            "min": r_min,
            "max": r_max,
            "inRange": {
                "color": [
                    "#6F7C6B",  # olive grey
                    "#9FA68B",  # muted khaki
                    "#C2BDA8",  # warm sand
                    "#586B84",  # muted denim
                    "#4E647B",  # petrol blue
                ]
            },
        },

        "tooltip": {
            "trigger": "item",
            "confine": True,
            "backgroundColor": "rgba(20, 24, 32, 0.92)",
            "borderWidth": 0,
            "textStyle": {"color": "#fff", "fontFamily": "IBM Plex Mono, monospace"},
        },
        "xAxis": {
            "type": "log",
            "name": "Nº de Avaliações",
            "nameLocation": "middle",
            "nameGap": 30,
            "nameTextStyle": {"color": "#6b7280", "fontFamily": "IBM Plex Mono, monospace","fontSize": 12},
            "axisLabel": {"color": "#6b7280","fontFamily": "IBM Plex Mono, monospace"},
            "axisLine": {"lineStyle": {"color": "rgba(0,0,0,0.12)"}},
            "splitLine": {"lineStyle": {"color": "rgba(0,0,0,0.06)"}},
        },
        "yAxis": {
            "type": "value",
            "min": 1.5,
            "max": 5.5,
            "name": "Rating médio",
            "nameLocation": "middle",
            "nameRotate": 90,
            "nameGap": 30,
            "nameTextStyle": {"color": "#6b7280","fontFamily": "IBM Plex Mono, monospace","fontSize": 12},
            "axisLabel": {"color": "#6b7280","fontFamily": "IBM Plex Mono, monospace"},
            "axisLine": {"lineStyle": {"color": "rgba(0,0,0,0.12)"}},
            "splitLine": {"lineStyle": {"color": "rgba(0,0,0,0.06)"}},
        },

        "series": [
            {
                "type": "scatter",
                "symbolSize": 7,

                "itemStyle": {
                    "opacity": 0.42,
                    "borderColor": "rgba(0,0,0,0.18)",
                    "borderWidth": 0.4,
                },
                "emphasis": {
                    "scale": 1.05,
                    "itemStyle": {
                        "opacity": 0.95,
                        "borderColor": "rgba(0,0,0,0.55)",
                        "borderWidth": 1.1,
                    },
                },

                "encode": {
                    "x": "votes",
                    "y": "rating",
                    "tooltip": ["title", "author", "rating", "stars", "votes"],
                },

                # Linhas de referência
                "markLine": {
                    "silent": True,
                    "symbol": ["none", "none"],
                    "label": {
                        "color": "#6b7280",
                        "fontFamily": "IBM Plex Mono, monospace",
                        "formatter": "{b}",
                        "position": "end",
                    },
                    "lineStyle": {"type": "dashed", "width": 1, "opacity": 0.6},
                    "data": [
                        {"name": "Rating (mediana)", "yAxis": y_ref},
                        {"name": "Popularidade", "xAxis": x_ref},
                    ],
                },

                # Quadrantes
                "markArea": {
                    "silent": True,
                    "itemStyle": {"opacity": 0.06},
                    "label": {
                        "show": True,
                        "color": "#6b7280",
                        "fontFamily": "IBM Plex Mono, monospace",
                        "fontSize": 11,
                    },
                    "data": [
                        [{"name": "Livros mais populares", "xAxis": x_ref, "yAxis": y_ref},
                         {"xAxis": "max", "yAxis": "max"}],

                        [{"name": "Pérolas escondidas", "xAxis": "min", "yAxis": y_ref},
                         {"xAxis": x_ref, "yAxis": "max"}],

                        [{"name": "Populares mas fracos", "xAxis": x_ref, "yAxis": "min"},
                         {"xAxis": "max", "yAxis": y_ref}],

                        [{"name": "Baixa atenção", "xAxis": "min", "yAxis": "min"},
                         {"xAxis": x_ref, "yAxis": y_ref}],
                    ],
                },
            }
        ],
    }
    return option

def echarts_scatter_popularity_quality_dataset(data: list) -> dict:
   
    return {
        "backgroundColor": "rgba(0,0,0,0)",
        "grid": {"left": 56, "right": 24, "top": 18, "bottom": 48},
        "dataset": {
            "dimensions": ["votes", "rating", "title", "author", "stars"],
            "source": data,
        },
        "tooltip": {
            "trigger": "item",
            "confine": True,
            "backgroundColor": "rgba(20, 24, 32, 0.92)",
            "borderWidth": 0,
            "textStyle": {"color": "#fff", "fontFamily": "IBM Plex Mono, monospace"},
            "formatter": JsCode(r"""
                function (p) {
                const d = p.data || {};
                const title = d.title || '';
                const author = d.author || '';
                const rating = d.rating;
                const votes = d.votes;

                const full = Math.floor(rating);
                const half = (rating - full) >= 0.5;
                const stars = '★'.repeat(full) + (half ? '½' : '');

                return 
                    <div style="max-width:320px">
                    <div style="font-weight:700;margin-bottom:4px">${title}</div>
                    <div style="opacity:.85;margin-bottom:8px">${author}</div>
                    <div style="display:flex;gap:18px">
                        <div>
                        <span style="opacity:.7">Rating</span><br/>
                        <b>${Number(rating).toFixed(2)}</b>
                        <div style="opacity:.85;margin-top:4px">${stars}</div>
                        </div>
                        <div>
                        <span style="opacity:.7">Avaliações</span><br/>
                        <b>${Number(votes).toLocaleString('pt-PT')}</b>
                        </div>
                    </div>
                    </div>;
                }
            """),
        },
        "xAxis": {
            "type": "log",
            "name": "Nº de avaliações (log)",
            "nameGap": 28,
            "nameTextStyle": {"color": "#6b7280", "fontFamily": "IBM Plex Mono, monospace"},
            "axisLabel": {"color": "#6b7280", "fontFamily": "IBM Plex Mono, monospace"},
            "axisLine": {"lineStyle": {"color": "rgba(0,0,0,0.12)"}},
            "splitLine": {"lineStyle": {"color": "rgba(0,0,0,0.06)"}},
        },
        "yAxis": {
            "type": "value",
            "min": 0,
            "max": 5,
            "name": "Rating médio",
            "nameGap": 26,
            "nameTextStyle": {"color": "#6b7280", "fontFamily": "IBM Plex Mono, monospace"},
            "axisLabel": {"color": "#6b7280", "fontFamily": "IBM Plex Mono, monospace"},
            "axisLine": {"lineStyle": {"color": "rgba(0,0,0,0.12)"}},
            "splitLine": {"lineStyle": {"color": "rgba(0,0,0,0.06)"}},
        },
        "series": [
            {
                "type": "scatter",
                "symbolSize": 7,
                "itemStyle": {"opacity": 0.55, "color": "rgba(30, 41, 59, 0.55)"},
                "emphasis": {"itemStyle": {"opacity": 0.95}},
                "encode": {
                    "x": "votes",
                    "y": "rating",
                    "tooltip": ["title", "author", "rating", "stars", "votes"],
                },
            }
        ],
    }

def echarts_genre_bars(df: pd.DataFrame, top_n: int = 12) -> dict:
    gdf = prep_genre_stats(df, top_n=top_n)
    if gdf is None or gdf.empty:
        return {"series": []}

    # paleta retro/vintage (baixa saturação, sem brilho)
    palette = [
        "#3A3F45",  # charcoal
        "#6F7C6B",  # olive grey
        "#9FA68B",  # muted khaki
        "#C2BDA8",  # warm sand
        "#7F8F7A",  # moss green
        "#5E7A63",  # forest muted
        "#6E6A78",  # slate violet
        "#505B66",  # steel grey
        "#7A8796",  # blue-grey
        "#8F8176",  # taupe
        "#586B84",  # muted denim
        "#A08787",  # dusty rose
        "#4E647B",  # petrol blue
        "#6B7682",  # graphite
        "#9BA4AF",  # soft ash
        "#7A6A58",  # warm brown
    ]

    # mapa cor por género (consistente entre gráficos)
    # usa a ordem por n_books para fixar mapping de forma estável
    base_order = gdf.sort_values("n_books", ascending=False)["genre"].astype(str).tolist()
    color_map = {genre: palette[i % len(palette)] for i, genre in enumerate(base_order)}

    # duas ordenações diferentes, mas mesmas cores
    gdf_books = gdf.sort_values("n_books", ascending=True).copy()
    gdf_rating = gdf.sort_values("avg_rating", ascending=True).copy()

    genres_books = gdf_books["genre"].astype(str).tolist()
    values_books = [int(x) for x in gdf_books["n_books"].fillna(0).tolist()]
    bars_books = [{
            "value": v,
            "label": {"formatter": f"{v:,}".replace(",", "."),},
            "itemStyle": {"color": color_map.get(g, "rgba(30,41,59,0.55)")},}
        for g, v in zip(genres_books, values_books)
    ]

    genres_rating = gdf_rating["genre"].astype(str).tolist()
    values_rating = [round(float(x), 2) for x in gdf_rating["avg_rating"].fillna(0).tolist()]
    bars_rating = [
        {"value": v, "itemStyle": {"color": color_map.get(g, "rgba(30,41,59,0.55)")}}
        for g, v in zip(genres_rating, values_rating)
    ]

    # eixo rating “zoom”
    rmin = max(0, float(gdf["avg_rating"].min()) - 0.2)
    rmax = min(5, float(gdf["avg_rating"].max()) + 0.2)
    if rmax - rmin < 0.6:
        rmin = max(0, rmin - 0.2)
        rmax = min(5, rmax + 0.2)

    axis_common_hide_numbers = {
        "axisLabel": {"show": False},
        "axisTick": {"show": False},
        "axisLine": {"show": False},
        "splitLine": {"show": False},
    }

    option = {
        "backgroundColor": "rgba(0,0,0,0)",
        "grid": [
            {"left": 80, "right": 28, "top": 52, "bottom": 22, "width": "44%"},
            {"left": "66%", "right": 28, "top": 52, "bottom": 22, "width": "41%"},
        ],
        "title": [
            {"text": "Géneros por Número de Livros Publicados", "left": 12, "top": 10,
             "textStyle": {"fontSize": 13, "fontWeight": 600, "color": "#1f2430"}},
            {"text": "Géneros por Rating Médio", "left": "66%", "top": 10,
             "textStyle": {"fontSize": 13, "fontWeight": 600, "color": "#1f2430"}},
        ],
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"},
            "confine": True,
            "backgroundColor": "rgba(20,24,32,.92)",
            "borderWidth": 0,
            "textStyle": {"color": "#fff", "fontFamily": "IBM Plex Mono, monospace"},
        },
        "xAxis": [
            {
                "type": "value",
                "gridIndex": 0,
                **axis_common_hide_numbers,
            },
            {
                "type": "value",
                "gridIndex": 1,
                "min": rmin,
                "max": rmax,
                **axis_common_hide_numbers,
            },
        ],
        "yAxis": [
            {
                "type": "category",
                "gridIndex": 0,
                "data": genres_books,
                "axisLabel": {"color": "#6b7280", "overflow": "truncate", "width": 150,
                              "fontFamily": "IBM Plex Mono, monospace"},
                "axisLine": {"show": False},
                "axisTick": {"show": False},
            },
            {
                "type": "category",
                "gridIndex": 1,
                "data": genres_rating,
                "axisLabel": {"color": "#6b7280", "overflow": "truncate", "width": 150,
                              "fontFamily": "IBM Plex Mono, monospace"},
                "axisLine": {"show": False},
                "axisTick": {"show": False},
            },
        ],
        "series": [
            {
                "name": "Nº de livros",
                "type": "bar",
                "xAxisIndex": 0,
                "yAxisIndex": 0,
                "data": bars_books,
                "barWidth": 14,
                "itemStyle": {"borderRadius": 6},
                "label": {
                    "show": True,
                    "position": "right",
                    "color": "#6b7280",
                    "fontFamily": "IBM Plex Mono, monospace",
                },
                "emphasis": {"focus": "self"},
                "blur": {"itemStyle": {"opacity": 0.15}},
            },
            {
                "name": "Rating médio",
                "type": "bar",
                "xAxisIndex": 1,
                "yAxisIndex": 1,
                "data": bars_rating,
                "barWidth": 14,
                "itemStyle": {"borderRadius": 6},
                "label": {
                    "show": True,
                    "position": "right",
                    "formatter": "{c}",
                    "color": "#6b7280",
                    "fontFamily": "IBM Plex Mono, monospace",
                },
                "emphasis": {"focus": "self"},
                "blur": {"itemStyle": {"opacity": 0.15}},
            },
        ],
    }
    return option

def echarts_genre_volume_rating_combo(df: pd.DataFrame, top_n: int = 12) -> dict:
    gdf = prep_genre_stats(df, top_n=top_n)
    if gdf is None or gdf.empty:
        return {"series": []}

    palette = [
        "#3A3F45", "#6F7C6B", "#9FA68B", "#C2BDA8",
        "#7F8F7A", "#5E7A63", "#6E6A78", "#505B66",
        "#7A8796", "#8F8176", "#586B84", "#A08787",
        "#4E647B", "#6B7682", "#9BA4AF", "#7A6A58",
    ]

    # Ordem base por volume
    gdf = gdf.sort_values("n_books", ascending=False).copy()
    genres = gdf["genre"].astype(str).tolist()

    color_map = {
        genre: palette[i % len(palette)]
        for i, genre in enumerate(genres)
    }

    values_books = gdf["n_books"].astype(int).tolist()
    values_rating = gdf["avg_rating"].round(2).tolist()

    bars_books = [
        {
            "value": v,
            "itemStyle": {
                "color": color_map.get(g),
                "borderRadius": [6, 6, 0, 0],
            },
        }
        for g, v in zip(genres, values_books)
    ]

    # Eixo rating (zoom discreto)
    rmin = max(0, float(min(values_rating)) - 0.2)
    rmax = min(5, float(max(values_rating)) + 0.2)


    option = {
        "backgroundColor": "rgba(0,0,0,0)",
        "grid": {"left": 90, "right": 90, "top": 60, "bottom": 70},

        "title": {
            "text": "Volume vs Rating por Género",
            "left": "center",
            "top": 10,
            "textStyle": {
                "fontSize": 14,
                "fontWeight": 600,
                "color": "#1f2430",
            },
        },

        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"},
            "confine": True,
            "backgroundColor": "rgba(20,24,32,.92)",
            "borderWidth": 0,
            "textStyle": {
                "color": "#fff",
                "fontFamily": "IBM Plex Mono, monospace",
            },
        },

        "legend": {
            "data": ["Rating médio"],
            "top": 32,
            "left": "center",
            "textStyle": {
                "color": "#6b7280",
                "fontFamily": "IBM Plex Mono, monospace",
            },
        },

        "xAxis": {
            "type": "category",
            "data": genres,
            "axisLabel": {
                "rotate": 35,
                "color": "#6b7280",
                "fontFamily": "IBM Plex Mono, monospace",
            },
            "axisLine": {"lineStyle": {"color": "rgba(0,0,0,0.12)"}},
            "axisTick": {"show": False},
        },

        "yAxis": [
            {
                "type": "value",
                "name": "Nº de livros",
                "nameLocation": "middle",
                "nameRotate": 90,
                "nameGap": 60,
                "nameTextStyle": {
                    "color": "#6b7280",
                    "fontFamily": "IBM Plex Mono, monospace",
                },
                "axisLabel": {
                    "color": "#6b7280",
                    "fontFamily": "IBM Plex Mono, monospace",
                },
                "splitLine": {
                    "lineStyle": {"color": "rgba(0,0,0,0.06)"}
                },
            },
            {
                "type": "value",
                "name": "Rating médio",
                "position": "right",
                "min": rmin,
                "max": rmax,
                "nameLocation": "middle",
                "nameRotate": 90,
                "nameGap": 60,
                "nameTextStyle": {
                    "color": "#6b7280",
                    "fontFamily": "IBM Plex Mono, monospace",
                },
                "axisLabel": {
                    "color": "#6b7280",
                    "fontFamily": "IBM Plex Mono, monospace",
                },
                "splitLine": {"show": False},
            },
        ],

        "series": [
            {
                "name": "Nº de livros",
                "type": "bar",
                "data": bars_books,
                "barWidth": 26,
                "emphasis": {"focus": "series"},
            },
            {
                "name": "Rating médio",
                "type": "line",
                "yAxisIndex": 1,
                "data": values_rating,
                "smooth": True,
                "symbol": "circle",
                "symbolSize": 7,
                "itemStyle": {"color": "#9FC27C"},
                "lineStyle": {"width": 2},
            },
        ],
    }

    return option

def render_libraries_map(df_lib: pd.DataFrame, height: int = 480):
    """
    Mapa interativo com tooltip legível (PyDeck).
    """
    import pydeck as pdk
    import streamlit as st

    if df_lib is None or df_lib.empty:
        st.info("Não foi possível obter bibliotecas para mostrar.")
        return

    center_lat = float(df_lib["lat"].mean())
    center_lon = float(df_lib["lon"].mean())

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_lib,
        get_position="[lon, lat]",
        get_radius=900,
        radius_min_pixels=3,
        radius_max_pixels=16,
        pickable=True,
        auto_highlight=True,
        opacity=0.65,
    )

    # Tooltip bem contrastado (e “blindado” contra o teu CSS com !important)
    tooltip = {
        "html": """
        <div style="
            color:#fff !important;
            font-size:12px;
            line-height:1.35;
            text-shadow: 0 1px 1px rgba(0,0,0,.45);
        ">
        <div style="font-weight:700; color:#fff !important;">{name}</div>
        <div style="opacity:.9; color:#fff !important;">{contact}</div>
        </div>
        """,
        "style": {
            "backgroundColor": "rgba(20,24,32,0.96)",
            "border": "1px solid rgba(255,255,255,0.10)",
            "color": "white",
            "padding": "12px",
            "borderRadius": "12px",
            "maxWidth": "340px",
        },
    }

    # Basemap claro 
    map_style = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"

    st.pydeck_chart(
        pdk.Deck(
            map_style=map_style,
            initial_view_state=pdk.ViewState(
                latitude=center_lat,
                longitude=center_lon,
                zoom=6,
            ),
            layers=[layer],
            tooltip=tooltip,
        ),
        height=height,
    )

def fetch_libraries_pt_osm() -> pd.DataFrame:
    """
    Bibliotecas em Portugal via Overpass (OSM).
    """
    import requests

    query = """
    [out:json][timeout:60];
    area["name"="Portugal"]["boundary"="administrative"]["admin_level"="2"]->.pt;
    (
      nwr["amenity"="library"](area.pt);
    );
    out center tags;
    """

    url = "https://overpass-api.de/api/interpreter"
    r = requests.post(url, data={"data": query}, timeout=90)
    r.raise_for_status()

    data = r.json()
    rows = []

    for el in data.get("elements", []):
        tags = el.get("tags", {}) or {}

        lat = el.get("lat") or (el.get("center", {}) or {}).get("lat")
        lon = el.get("lon") or (el.get("center", {}) or {}).get("lon")
        if lat is None or lon is None:
            continue

        name = tags.get("name") or "Biblioteca (sem nome)"
        # contactos úteis (quando existirem)
        contact = (
            tags.get("website")
            or tags.get("contact:website")
            or tags.get("phone")
            or tags.get("contact:phone")
            or ""
        )

        rows.append({
            "name": str(name),
            "contact": str(contact),
            "lat": float(lat),
            "lon": float(lon),
            "source": "OSM",
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        # Portugal aprox. (filtro simples)
        df = df[df["lat"].between(36, 43) & df["lon"].between(-10.7, -5.0)]

    return df
