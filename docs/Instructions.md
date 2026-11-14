# Instructions

Skonsolidowany zapis: zasady współpracy, plan i to, co zostało zrobione. Dwa wątki: projekt techniczny (Volcano ELT) i działania około-karierowe (CV, Substack).

---

## Część 1 — Projekt techniczny: Volcano ELT Pipeline

### Kontekst autorki

Senior Unity Developer (C#, 10 lat doświadczenia), uczy się Data Engineering. To jest projekt portfolio — kod ma być produkcyjny/profesjonalny, nie tylko "działający".

### Zasady współpracy (prompt)

- Ucz krok po kroku. Nie dawaj gotowych rozwiązań do zadań/ćwiczeń bez pytania — niech autorka spróbuje sama, potem sprawdzam i poprawiam.
- Wyjątek: gdy autorka pokazuje kod z błędami do przejrzenia — wtedy wymieniam WSZYSTKIE błędy naraz i od razu podaję poprawki (nie na raty).
- Pytania koncepcyjne/o konwencje ("czemu tak", "co jest profesjonalne") — odpowiadam wprost, z uzasadnieniem, to nie są ćwiczenia.
- Przy okazji uczę konwencji komercyjnych i dobrych praktyk, nawet jeśli nie pytała wprost.
- CLAUDE.md i PROJECT_ROADMAP.html mają być na bieżąco aktualizowane, żeby odzwierciedlały prawdziwy stan projektu.

### Jak odpalić projekt

```bash
cd /Users/weronikaslusarczyk/Workspace/DE_Journey/Volcanos
source venv/bin/activate
pip install -r requirements.txt   # tylko przy nowych zależnościach / świeżym klonie
python pipeline.py                # JEDYNY plik odpalany bezpośrednio
```

`extract/`, `load/`, `transform/` nie są odpalane bezpośrednio — `config.py` w rootcie nie jest widoczny w `sys.path`, jeśli odpalisz plik wewnątrz podfolderu.

### Źródła danych

- **NOAA NGDC hazard-service — volcanoes**: 900 rekordów, 5 stron po 200.
- **NOAA NGDC hazard-service — earthquakes**: 6692 rekordy, 34 strony po 200. Pole `volcanoEventId` to prawdziwy klucz obcy do zdarzeń wulkanicznych.
- **EONET (NASA) — usunięte z projektu.** 75 rekordów bez wspólnego klucza z NOAA, żadna analiza go nie używała. Zastąpione przez earthquakes z tego samego hazard-service.

### Architektura (Medallion)

```
extract/extract.py     — pobiera dane z API (NOAA volcanoes + earthquakes), zwraca listy/dicty
load/load.py            — zapisuje surowe dane do data/raw/ (Bronze, bez modyfikacji)
transform/transform.py  — pandas: czyszczenie, selekcja kolumn (Silver)
transform/schemas.py    — kontrakty jakości danych (Pandera DataFrameSchema)
pipeline.py             — JEDYNY punkt wejścia; orkiestruje extract → load → transform → validate → save
config.py               — stałe: URL-e API, limity, ścieżki (Path, zakotwiczone przez __file__)
```

- **Bronze** (`data/raw/`) — surowe JSON, 1:1 z API, nienaruszalne.
- **Silver** (`data/clean/`) — Parquet, oczyszczone, walidowane schematem Pandera.
- **Gold** (`data/gold/`) — star schema, agregacje. Planowane, opcjonalne (Faza 4).

### Ustalone konwencje produkcyjne

- Config: ścieżki jako `pathlib.Path`, zakotwiczone `BASE_DIR = Path(__file__).resolve().parent` (wzorzec jak Django `BASE_DIR`), nie gołe względne stringi.
- Separacja transform/save: `transform_*()` tylko czyszczą i zwracają `pd.DataFrame`, nigdy nie zapisują na dysk. Zapis robi `save_to_clean()`, wołana explicite z `pipeline.py`.
- Importy: jawne (`from extract.extract import extract_x`), bez reeksportu w `__init__.py` (to kod aplikacyjny, nie biblioteka).
- Docstringi: potrójne cudzysłowy, krótki opis w pierwszej linii.
- Orkiestracja wyłącznie w `pipeline.py` — żadnych `if __name__ == "__main__":` z testowymi wywołaniami w modułach niżej.
- Obsługa błędów: `try/except` wokół wywołań sieciowych (Timeout, ConnectionError), log + `raise` dalej.
- Walidacja danych: Pandera zamiast gołych `assert` — `schema.validate(df, lazy=True)` zbiera wszystkie naruszenia naraz, nie znika w trybie `-O` (w przeciwieństwie do `assert`), i ten sam schemat działa też na silnikach rozproszonych (pyspark.pandas, dask), gdyby projekt kiedyś wyszedł poza pandas.

### Konwencje pandas (Silver Layer)

- Kolumny: snake_case (rename z camelCase z API).
- `vei.fillna(-1)` — NIE 0 (VEI 0 = erupcja nieeksplozywna, -1 = brak danych, sentinel).
- `deaths_total.fillna(0)` — brak danych o ofiarach = 0 (semantyka licznika).
- Klucze obce (`volcano_event_id`, `earthquake_event_id`) — NIE fillna sentinelem. Nullable `Int64`, żeby zachować prawdziwy brak wartości zamiast zmyślonego ID.
- `month`, `day`, `latitude`, `longitude`, `magnitude` (w earthquakes) — zostają `NaN` gdzie brak, brak sensownego defaultu domenowego.
- Selekcja + rename jednym słownikiem: `df[list(COLUMN_MAP)].rename(columns=COLUMN_MAP)`.
- Zapis: `df.to_parquet(path, index=False)`.

### Stan projektu — co zrobione

- `extract/extract.py` — gotowe: paginacja, error handling, docstringi poprawione (w tym błąd "volcano events" → "earthquake events" w `extract_earthquakes_from_noaa`).
- `load/load.py` — gotowe: `load_noaa_volcanoes()`, `load_noaa_earthquakes()`, `save_to_file()`.
- `config.py` — gotowe, ścieżki odporne na cwd.
- `transform/transform.py` — gotowe: obie funkcje transformujące, `save_to_clean()`, separacja odpowiedzialności zachowana.
- `transform/schemas.py` — **nowe**: `volcanoes_schema` i `earthquakes_schema` (Pandera), zastępują wcześniejsze gołe asserty w `pipeline.py`. `unique=["id"]` zamiast pełnego `duplicated()` na wierszu.
- `pipeline.py` — gotowe end-to-end, woła `schema.validate(df, lazy=True)` przed zapisem do Silver.
- `requirements.txt` — `pandas==3.0.3`, `requests==2.34.2`, `pyarrow==25.0.1`, `pandera` (wersję dopisać po `pip show pandera`).
- `requirements-dev.txt` — jak wyżej + `pytest` (wersję dopisać analogicznie) + zależności Jupytera.
- `.gitignore` — `data/` całość + `*.parquet`.
- `README.md` — zaktualizowany: architektura, pivot EONET→earthquakes, decyzje o null-handlingu, poprawiony status sekcji testów (nie "in progress", tylko "jeszcze nie zaczęte").
- Repo zsynchronizowane z GitHub (`git push` wykonany, branch `main` up to date z `origin/main`).

### Faza 3 — testy (w trakcie)

- `tests/__init__.py` — utworzony (pusty).
- `tests/test_extract.py` — szkielet z podpowiedziami w komentarzu (mock `requests.get` w miejscu użycia, `side_effect` na kolejne strony paginacji), ciało `test_extract_volcanoes_from_noaa_success()` do napisania samodzielnie.
- Do rozważenia: `pandera_schema.example(size=...)` do generowania danych testowych zgodnych ze schematem, zamiast ręcznego klepania fikcyjnych DataFrame'ów.

### Do zrobienia dalej

1. Dokończyć testy pytest (`test_extract.py`, potem `test_transform.py`) z zamockowanym `requests.get`.
2. (Opcjonalnie) Gold Layer — star schema (Faza 4).

---

## Część 2 — Działania około-karierowe

### List motywacyjny do DataFuze

- Cel: aplikacja do DataFuze (warszawski software house, DE/Snowflake Select partner; stack: PostgreSQL, MySQL, C++, Angular, Kafka, ElasticSearch, Snowflake, Oracle DB, Airflow, NiFi, dbt, Python, Java, Oracle APEX).
- Ton: bezpośredni, "Gen Z, ale na serio" — bez korporacyjnych sloganów, z konkretnym odniesieniem do projektu Volcano ELT jako dowodu samodzielnej nauki DE (Medallion, realny FK join NOAA volcanoes↔earthquakes, decyzje o obsłudze null).
- Plik: `list_motywacyjny_DataFuze.docx`, zbudowany przez `docx` (npm), zweryfikowany wizualnie (render do PDF → JPG → odczyt).

### Post na Substacka — pivot kariery

- Plik: `substack_post_pivot.md`.
- Temat: przejście z 10 lat w gamedevie do Data Engineeringu.
- Ton: osobisty, surowy, w Twoim głosie — kilka rund poprawek usuwających zbyt "literacki"/wygładzony język na rzecz bezpośredniości.
- Kluczowe wątki w treści: wypalenie zawodowe i sytuacja w branży gier (fale zwolnień), Radio Naukowe Karoliny Głowackiej jako punkt zapalny, konkretnie odcinek 312 z dr Anną Durkalec ("Galaktyki właśnie stały się jeszcze większą zagadką" — teleskop Very Rubin, galaktyki o niskiej jasności powierzchniowej niewidoczne bez odpowiedniego sprzętu) jako metafora dla danych czekających na pipeline, moment olśnienia w Las Cañadas del Teide, próby innych ścieżek (Unreal, backend C#) przed odkryciem DE.
- Poprawki jakościowe: literówki (Zaczełam→Zaczęłam, bedzie→będzie, brakujące przecinki), złamane zdanie o CV, nazwa geograficzna (Las Canadas de Teide → Las Cañadas del Teide), redukcja powtórzeń rdzenia "wypal-".
- Zakończenie: zapowiedź serii + link do repo Volcano ELT (github.com/programistka-gier/Volcanos) + CTA do zostania/komentowania (zamiast dwóch osobnych, słabszych CTA).
- Ustalenia do publikacji na Substacku: komentarze włączone dla wszystkich, audience "Everyone", tagi (career change, data engineering, gamedev), przycisk Subscribe i Leave a comment wstawione w treści, obrazek (rekomendacja: własne zdjęcie z Teide albo z plaży, nie stockowe).
- Podtytuł — kilka wariantów zaproponowanych, ostateczny wybór do potwierdzenia.
- Substack Note (teaser do promocji posta) — kilka wariantów zaproponowanych, do wyboru przed publikacją.
