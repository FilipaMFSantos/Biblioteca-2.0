import re
import pandas as pd


def fix_character(value):
    """
    Tenta corrigir texto com codificação trocada,
    do tipo 'JosÃ©', 'AndrÃ©', 'DiÃ¡rio', etc.

    Estratégia:
    - se contiver caracteres suspeitos (Ã, Â, Ð, Ñ),
      tenta fazer: latin1 -> utf-8
    """
    if not isinstance(value, str):
        return value

    bad_chars = ("Ã", "Â", "Ð", "Ñ")
    if not any(ch in value for ch in bad_chars):
        return value

    try:
        fixed = value.encode("latin1", errors="ignore").decode("utf-8", errors="ignore")
        return fixed or value
    except Exception:
        return value


def _clean_isbn_value(x) -> str:
    """
    Normaliza valores ISBN/ISBN13 vindos do CSV:
    - lida com NaN
    - converte floats tipo 9.79E+12 para inteiro
    - remove sufixo .0
    - mantém apenas dígitos e X
    """
    if pd.isna(x):
        return ""

    s = str(x).strip()
    if not s or s.lower() == "nan":
        return ""

    # Ex: 9.79E+12 -> 978...
    if re.fullmatch(r"\d+\.\d+e\+\d+", s.lower()):
        try:
            s = str(int(float(s)))
        except Exception:
            return ""

    # Ex: 9781234567890.0 -> 9781234567890
    if re.fullmatch(r"\d+\.0", s):
        s = s.split(".")[0]

    # Mantém só dígitos e X
    s = re.sub(r"[^0-9Xx]", "", s).upper()
    return s


def load_raw(path):
    """
    Lê o ficheiro CSV original e devolve um DataFrame.
    Se o ficheiro não existir ou ocorrer um erro na leitura,
    devolve uma mensagem clara.
    """
    try:
        df = pd.read_csv(
            path,
            sep=";",
            encoding="utf-8",
            on_bad_lines="skip",
            dtype={"isbn": "string", "isbn13": "string"},
            keep_default_na=False,
            low_memory=False,
        )

    except UnicodeDecodeError:
        print("Aviso: erro de encoding UTF-8, a tentar latin-1...")
        df = pd.read_csv(
            path,
            encoding="latin-1",
            on_bad_lines="skip",
            dtype={"isbn": "string", "isbn13": "string"},
            keep_default_na=False,
            low_memory=False,
        )

    except FileNotFoundError:
        print(f"Erro: o ficheiro '{path}' não foi encontrado.")
        return None

    except pd.errors.EmptyDataError:
        print(f"Erro: o ficheiro '{path}' está vazio ou corrompido.")
        return None

    except Exception as e:
        print(f"Ocorreu um erro ao carregar o ficheiro: {e}")
        return None

    return df


def clean(df):
    """
    Limpa o DataFrame do GoodReads_100k_books.

    Notas importantes:
    - A coluna 'rating' é uma média de avaliação em escala 0 a 5.
    - 'totalratings' é o nº total de votos, e 'reviews' o nº de críticas escritas.
    """
    if df is None or len(df) == 0:
        print("Erro: DataFrame vazio, não é possível limpar os dados.")
        return None

    d = df.copy()

    # 1) Remover espaços supérfluos em colunas de texto (sem transformar NaN em "nan")
    text_cols = d.select_dtypes(include=["object"]).columns
    for col in text_cols:
        d[col] = d[col].apply(lambda v: v.strip() if isinstance(v, str) else v)

    # 2) Corrigir problemas de codificação em colunas de texto
    for col in text_cols:
        d[col] = d[col].apply(fix_character)

    # 3) Converter colunas numéricas
    numeric_cols = ["rating", "pages", "reviews", "totalratings", "ratings_count"]
    for col in numeric_cols:
        if col in d.columns:
            d[col] = pd.to_numeric(d[col], errors="coerce")

    # 4) Normalizar ISBN/ISBN13 (evita 9.79E+12 e 978...0)
    if "isbn" in d.columns:
        d["isbn"] = d["isbn"].apply(_clean_isbn_value)

    if "isbn13" in d.columns:
        d["isbn13"] = d["isbn13"].apply(_clean_isbn_value)

    # 5) Converter 'genre' em lista
    if "genre" in d.columns:
        d["genres_list"] = d["genre"].fillna("").apply(
            lambda x: [g.strip() for g in str(x).split(",") if g.strip()]
        )

    # 6) Converter 'author' em lista
    if "author" in d.columns:
        def split_authors(x):
            s = str(x).strip()
            if not s or s.lower() == "nan":
                return []
            if ";" in s:
                parts = s.split(";")
            else:
                parts = s.split(",")
            return [a.strip() for a in parts if a.strip()]

        d["author_list"] = d["author"].fillna("").apply(split_authors)

    # 7) Criar ID interno (mantém coerência com a app)
    d = d.reset_index(drop=True)
    if "book_id" not in d.columns:
        d["book_id"] = d.index

    return d


def save_clean(df, out_path):
    """
    Guarda o DataFrame limpo num CSV.
    """
    if df is None or len(df) == 0:
        print("Erro: DataFrame vazio, não é possível guardar os dados.")
        return None

    df.to_csv(out_path, index=False)
    return out_path


def save_suggestion(title, author, genres, path="sugestoes_livros.txt"):
    try:
        write_header = (not os.path.exists(path)) or os.path.getsize(path) == 0

        with open(path, "a", encoding="utf-8") as f:
            if write_header:
                f.write("[title] , [author] , [genre]\n")
            f.write(f"{title} , {author} , {genres}\n")

    except Exception as e:
        print(f"\nErro ao guardar a sugestão: {e}")
