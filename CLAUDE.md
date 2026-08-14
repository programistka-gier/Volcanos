# Volcano ELT Pipeline — kontekst projektu

## Kontekst autorki
Senior Unity Developer (C#, 10 lat doświadczenia), uczy się Data Engineering.
To jest projekt portfolio — **kod ma być produkcyjny/profesjonalny**, nie tylko "działający".

## Jak odpalić projekt
```bash
cd /Users/weronikaslusarczyk/Workspace/DE_Journey/Volcanos
source venv/bin/activate          # sprawdź prefiks (venv) w prompt
pip install -r requirements.txt   # tylko przy nowych zależnościach / świeżym klonie
python pipeline.py                # JEDYNY plik odpalany bezpośrednio
```
`python pipeline.py` działa bez `-m`, bo `pipeline.py` leży w rootcie. Pliki wewnątrz
`extract/`, `load/`, `transform/` nie są odpalane bezpośrednio (patrz: separacja odpowiedzialności
niżej) — próba `python transform/transform.py` (albo przycisk "Run" w VS Code dla takiego pliku)
skończy się `ModuleNotFoundError`, bo `config.py` w rootcie nie jest wtedy widoczny w `sys.path`.

## Jak pracujemy (styl współpracy)
- Ucz krok po kroku. Nie dawaj gotowych rozwiązań do zadań/ćwiczeń bez pytania — niech autorka
  spróbuje sama, potem sprawdzam i poprawiam.
- Wyjątek: gdy autorka pokazuje kod z błędami do przejrzenia — wtedy wymieniam WSZYSTKIE błędy
  naraz i od razu podaję poprawki (nie na raty).
- Pytania koncepcyjne/o konwencje ("czemu tak", "co jest profesjonalne") — odpowiadam wprost,
  z uzasadnieniem, to nie są ćwiczenia.
- Przy okazji uczę konwencji komercyjnych i dobrych praktyk, nawet jeśli nie pytała wprost.

## Źródła danych
- **NOAA NGDC hazard-service — volcanoes**: `https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/volcanoes`
  (900 rekordów, 5 stron po 200)
- **NOAA NGDC hazard-service — earthquakes**: `https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes`
  (6692 rekordy, 34 strony po 200)
- **EONET (NASA) — usunięte z projektu (2026-08-10).** Powód: 75 rekordów bez wspólnego klucza
  z NOAA, żadna z trzech analiz go nie używała. Zastąpione przez `earthquakes` z tego samego
  hazard-service co `volcanoes` — rekordy earthquakes mają pole `volcanoEventId`, prawdziwy klucz
  obcy do zdarzeń wulkanicznych (zweryfikowane na żywym API), więc join jest realny, nie fuzzy
  matching po współrzędnych.

## Architektura
```
extract/extract.py   — pobiera dane z API (NOAA volcanoes + NOAA earthquakes), zwraca listy/dicty
load/load.py          — zapisuje surowe dane do data/raw/ (bez modyfikacji, "data lake")
transform/transform.py — pandas: czyszczenie, selekcja kolumn, analizy
pipeline.py           — JEDYNY punkt wejścia; orkiestruje extract → load → transform
config.py             — stałe: URL-e API, limity, ścieżki (Path)
```

## Ustalone konwencje produkcyjne
- **Config**: wszystkie ścieżki i stałe konfiguracyjne w `config.py`, ścieżki jako `pathlib.Path`,
  zakotwiczone względem lokalizacji samego pliku: `BASE_DIR = Path(__file__).resolve().parent`,
  potem `RAW_DIR = BASE_DIR / "data" / "raw"`. Nie gołe względne stringi typu `Path("data/raw")` —
  te zależą od cwd procesu, co psuje się w notebookach (inny cwd niż root). Ten sam wzorzec co
  Django (`BASE_DIR` w `settings.py`).
- **Separacja transform/save**: funkcje `transform_*()` tylko czyszczą i zwracają `pd.DataFrame`,
  NIGDY nie zapisują na dysk. Zapis robi osobna funkcja `save_to_clean()`, wołana explicite
  z `pipeline.py`. Dzięki temu `transform_*()` da się przetestować bez dotykania dysku.
- **Ścieżki**: zawsze `pathlib`, nigdy f-string + `/` do sklejania ścieżek. Tworzenie folderów:
  `RAW_DIR.mkdir(parents=True, exist_ok=True)` przed zapisem.
- **Importy**: jawne importy konkretnych funkcji (`from extract.extract import extract_x`) —
  to jest kod aplikacyjny/pipeline, nie biblioteka do dystrybucji, więc nie robimy reeksportu
  w `__init__.py` (to wzorzec dla bibliotek publicznych typu numpy/requests).
- **Docstringi**: potrójne cudzysłowy `"""..."""`, krótki opis w pierwszej linii.
- **Separacja odpowiedzialności**: żadnych `if __name__ == "__main__":` z ręcznymi wywołaniami
  testowymi rozrzuconych po modułach `extract`/`load`/`transform` — orkiestracja wyłącznie
  w `pipeline.py`.
- **Testowanie**: docelowo pytest z zamockowanym `requests.get` (nie bijemy w prawdziwe API
  w testach jednostkowych). Jeszcze nie zaimplementowane — do zrobienia.
- **Obsługa błędów**: `try/except` wokół wywołań sieciowych (Timeout, ConnectionError),
  logowanie i `raise` dalej — decyzję co robić z błędem podejmuje `pipeline.py`, nie moduł niżej.

## Architektura Medallion (ustalone warstwy)
- **Bronze** = `data/raw/` — surowe JSON z API, 1:1, nienaruszalne. Robi: `load.py`.
- **Silver** = `data/clean/` — Parquet, oczyszczone, schematy egzekwowane. Robi: `transform.py` — ✅ gotowe.
- **Gold** = `data/gold/` — star schema, agregacje. Planowane (Faza 4, opcjonalna).

## Stan projektu (bieżąco aktualizować)
- `extract/extract.py` — ✅ gotowe: `extract_volcanoes_from_noaa()` i `extract_earthquakes_from_noaa()`,
  oba z paginacją i error handling (Timeout/ConnectionError → log + raise). Brak EONET.
- `load/load.py` — ✅ gotowe: `load_noaa_volcanoes()`, `load_noaa_earthquakes()`, `save_to_file()`
  (RAW_DIR z configu, mkdir, indent=2).
- `config.py` — ✅ gotowe: `BASE_DIR = Path(__file__).resolve().parent` (odporne na cwd —
  poprawka po buggu ze ścieżkami względnymi w notebooku), `RAW_DIR`/`CLEAN_DIR`,
  `RAW_NOAA_VOLCANOES_FILENAME`/`CLEAN_NOAA_VOLCANOES_FILENAME`,
  `RAW_NOAA_EARTHQUAKES_FILENAME`/`CLEAN_NOAA_EARTHQUAKES_FILENAME`, `NOAA_VOLCANOES`/`NOAA_EARTHQUAKES`
  (URL-e), `NOAA_PAGE_SIZE`. Brak EONET.
- `pipeline.py` — ✅ **gotowe end-to-end**: `load_noaa_earthquakes()` + `load_noaa_volcanoes()` (Bronze)
  → `transform_noaa_volcanoes()`/`transform_noaa_earthquakes()` + `save_to_clean()` dla obu (Silver).
  `logging.basicConfig()` na górze, jawne importy, guard `__main__`.
- `transform/transform.py` — ✅ **gotowe**:
  - `load_raw(path)` — helper wczytujący JSON + logujący shape
  - `NOAA_VOLCANOES_COLUMN_MAP` / `NOAA_EARTHQUAKES_COLUMN_MAP` — selekcja + rename w jednym słowniku,
    obie zawierają teraz `id` (świadomie — konsekwencja: zwykłe `drop_duplicates()` bez `subset` nigdy
    nic nie usunie, bo `id` jest unikalne; zaakceptowane jako formalność)
  - `transform_noaa_volcanoes()` — selekcja/rename, `vei.fillna(-1)`, `deaths_total.fillna(0)`,
    oba `.astype(int)`, `earthquake_event_id` jako nullable `Int64` (FK do earthquakes), dedup+reset_index,
    log shape. 12 kolumn świadomie (nie 13) — `location` pominięta.
  - `transform_noaa_earthquakes()` — analogicznie: `deaths_total` z pola `deathsTotal` (nie `deaths`,
    spójnie z volcanoes) fillna(0)+astype(int), `volcano_event_id` jako nullable `Int64` (NIE fillna
    sentinelem — to FK), `month`/`day`/`latitude`/`longitude`/`magnitude` zostają NaN gdzie brak
    (brak sensownego defaultu domenowego), dedup+reset_index, log shape
  - `save_to_clean(df, filename)` — type hints, `CLEAN_DIR.mkdir()`, `to_parquet(index=False)`, log.
    Wołana z `pipeline.py` z gołą nazwą pliku (stała z configu), NIE z `CLEAN_DIR / ...` —
    wcześniej był tu bug (podwójne sklejenie ścieżki, przypadkiem "działający" przez to że pathlib
    ignoruje lewy operand `/` gdy prawy jest absolutny) — naprawiony.
- Formatter: Ruff skonfigurowany w `.vscode/settings.json` (`editor.defaultFormatter` +
  `editor.formatOnSave` dla `[python]`) — grupuje/sortuje importy (stdlib → third-party →
  lokalne), to zamierzone zachowanie. Dodatkowo: `jupyter.notebookFileRoot: ${workspaceFolder}`
  i `notebook.output.textLineLimit: 150` (VS Code czasem ignoruje pierwsze — patrz konwencja
  `BASE_DIR` w configu jako właściwe zabezpieczenie).
- `requirements.txt` — ✅ tylko runtime deps pipeline'u: `pandas==3.0.3`, `requests==2.34.2`
- `requirements-dev.txt` — ✅ `-r requirements.txt` + Jupyter i jego zależności przechodnie
  (do pracy z notebookiem, nie potrzebne do `python pipeline.py`)
- `.gitignore` — ✅ `data/` (całość: raw+clean+gold) i `*.parquet` zamiast samego `raw/`
- `tests/` — ○ nie zaczęte
- `notebooks/` — `test_transform.ipynb` (dev-loop do testowania funkcji z `transform.py` przeciw
  zapisanym danym Bronze, bez odpalania pipeline.py). Stare `elt_volcanos.ipynb`/`volcano_elt.ipynb`
  zostały usunięte (kiedyś, poza tą sesją) — nie ma ich już na dysku. Puste, osierocone
  `notebooks/raw/`/`notebooks/clean/` — pozostałość po starym notebooku, do usunięcia.
- `README.md` — nieaktualny (stara struktura, wspomina EONET). Do zaktualizowania.
- `PROJECT_ROADMAP.html` — ✅ Faza 2 (Silver) na 6/7 — zostało tylko zadanie 2-6 (data quality
  verification). Zapamiętuje checkboxy (localStorage + stan w samym HTML).

## Konwencje pandas (Silver Layer)
- Kolumny: snake_case (rename z camelCase/mixedCase z API)
- Nulle z decyzją domenową: `vei.fillna(-1)` — NIE 0 (VEI 0 = erupcja nieeksplozywna, -1 = brak danych)
- `deaths_total.fillna(0)` — brak danych o ofiarach = 0
- Cast po fillna: `.astype(int)` dla vei i deaths_total
- `month`, `day` — zostaw jako float64 z NaN (int nie przyjmuje NaN)
- **ID/klucze obce (np. `volcanoEventId`, `tsunamiEventId`) — NIE fillna z sentinelem jak przy vei.**
  Użyj nullable `Int64` (`.astype('Int64')`), żeby zachować prawdziwy brak wartości zamiast
  zmyślonego ID. Sentinel ma sens dla miar (VEI), nie dla identyfikatorów.
- Zapis Silver: `df.to_parquet(path, index=False)` — index=False standard
- Logowanie shape przed i po transformacji: `logging.info(f"shape: {df.shape}")`
- Selekcja + rename jednym słownikiem: `df[list(COLUMN_MAP)].rename(columns=COLUMN_MAP)`

## Do zrobienia dalej
1. Zadanie 2-6: weryfikacja Silver Layer (asserty data quality — brak NaN w wymaganych kolumnach,
   zakresy VEI/współrzędnych, brak duplikatów)
2. Testy pytest z zamockowanym `requests.get` (Faza 3)
3. Usuń osierocone `notebooks/raw/`/`notebooks/clean/`
4. Aktualizacja README (wspomina jeszcze EONET, starą strukturę folderów)
5. (Opcjonalnie) Gold Layer — star schema (Faza 4)
