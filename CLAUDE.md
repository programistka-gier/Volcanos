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
- **Config**: wszystkie ścieżki i stałe konfiguracyjne w `config.py`, ścieżki jako `pathlib.Path`
  (np. `RAW_DIR = Path("data/raw")`), nie gołe stringi porozrzucane po modułach.
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
- **Silver** = `data/clean/` — Parquet, oczyszczone, schematy egzekwowane. Robi: `transform.py` (w trakcie).
- **Gold** = `data/gold/` — star schema, agregacje. Planowane.

## Stan projektu (bieżąco aktualizować)
- `extract/extract.py` — ✅ gotowe: `extract_volcanoes_from_noaa()` i `extract_earthquakes_from_noaa()`,
  oba z paginacją i error handling (Timeout/ConnectionError → log + raise). Brak EONET.
- `load/load.py` — ✅ gotowe: `load_noaa_volcanoes()`, `load_noaa_earthquakes()`, `save_to_file()`
  (RAW_DIR z configu, mkdir, indent=2). Literówka `load_noaa_eathquakes` poprawiona.
- `config.py` — ✅ gotowe: `RAW_DIR`/`CLEAN_DIR`, `RAW_NOAA_VOLCANOES_FILENAME`/`CLEAN_NOAA_VOLCANOES_FILENAME`,
  `RAW_NOAA_EARTHQUAKES_FILENAME`/`CLEAN_NOAA_EARTHQUAKES_FILENAME`, `NOAA_VOLCANOES`/`NOAA_EARTHQUAKES` (URL-e),
  `NOAA_PAGE_SIZE`. Brak EONET.
- `pipeline.py` — ✅ gotowe dla Bronze (`load_noaa_volcanoes()` + `load_noaa_earthquakes()`, guard `__main__`);
  transform jeszcze niewpięty (roadmapa: zadanie t2-5)
- `transform/transform.py` — 🟡 w toku:
  - `if __name__ == "__main__"` usunięty ✅
  - `load_raw(path)` — helper wczytujący JSON + logujący shape ✅
  - `NOAA_VOLCANOES_COLUMN_MAP` (selekcja + rename w jednym słowniku) ✅
  - `transform_noaa()` — ✅ gotowe: sygnatura z type hint + docstring, selekcja/rename,
    obsługa nulli (`fillna` + `astype` dla `vei` i `deaths_total`), `drop_duplicates()`,
    `reset_index(drop=True)`, log shape. Świadoma decyzja: 12 kolumn zamiast 13 —
    `location` pominięta, `country` wystarcza do analiz.
  - `transform_noaa_earthquakes()` — 🟡 zaczęte: ma sygnaturę i wczytuje raw, ale docstring
    nadal mówi o EONET (nieaktualny, do poprawy) i brak logiki czyszczenia — selekcja/rename
    kolumn (`NOAA_EARTHQUAKES_COLUMN_MAP`), `deaths_total` fillna+astype, `volcanoEventId`/
    `tsunamiEventId` jako nullable `Int64` (NIE sentinel -1 — to FK, nie miara), dedup, reset_index
  - `save_to_clean()` — nie zaczęte
- Formatter: Ruff skonfigurowany w `.vscode/settings.json` (`editor.defaultFormatter` +
  `editor.formatOnSave` dla `[python]`) — grupuje/sortuje importy (stdlib → third-party →
  lokalne), to zamierzone zachowanie.
- `requirements.txt` — ✅ tylko runtime deps pipeline'u: `pandas==3.0.3`, `requests==2.34.2`
- `requirements-dev.txt` — ✅ `-r requirements.txt` + Jupyter i jego zależności przechodnie
  (do pracy z notebookiem, nie potrzebne do `python pipeline.py`)
- `.gitignore` — ✅ `data/` (całość: raw+clean+gold) i `*.parquet` zamiast samego `raw/`
- `tests/` — ○ nie zaczęte
- `notebooks/` — dwa pliki (szkic autorki + wygenerowany przez Claude). Nie uruchamiać bez prośby.
- `README.md` — nieaktualny (stara struktura, wspomina EONET). Do zaktualizowania po Silver Layer.
- `PROJECT_ROADMAP.html` — ✅ szczegółowa roadmapa z mikrokrokami, zapamiętuje checkboxy
  (localStorage + stan w samym HTML). Zaktualizowana pod pivot EONET→earthquakes.

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
1. Popraw docstring `transform_noaa_earthquakes()` (nadal mówi o EONET, nieaktualny)
2. Dokończ `transform_noaa_earthquakes()` — `NOAA_EARTHQUAKES_COLUMN_MAP`, fillna/astype dla
   `deaths_total`, nullable `Int64` dla `volcanoEventId`/`tsunamiEventId`, dedup, reset_index, log shape
3. Napisz `save_to_clean()` — to_parquet(index=False)
4. Wpięcie transform do `pipeline.py`
5. Testy pytest z zamockowanym requests.get
6. Aktualizacja README (wspomina jeszcze EONET, starą strukturę folderów)
