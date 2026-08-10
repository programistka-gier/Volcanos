# Volcano ELT Pipeline — kontekst projektu

## Kontekst autorki
Senior Unity Developer (C#, 10 lat doświadczenia), uczy się Data Engineering.
To jest projekt portfolio — **kod ma być produkcyjny/profesjonalny**, nie tylko "działający".

## Jak pracujemy (styl współpracy)
- Ucz krok po kroku. Nie dawaj gotowych rozwiązań do zadań/ćwiczeń bez pytania — niech autorka
  spróbuje sama, potem sprawdzam i poprawiam.
- Wyjątek: gdy autorka pokazuje kod z błędami do przejrzenia — wtedy wymieniam WSZYSTKIE błędy
  naraz i od razu podaję poprawki (nie na raty).
- Pytania koncepcyjne/o konwencje ("czemu tak", "co jest profesjonalne") — odpowiadam wprost,
  z uzasadnieniem, to nie są ćwiczenia.
- Przy okazji uczę konwencji komercyjnych i dobrych praktyk, nawet jeśli nie pytała wprost.

## Architektura
```
extract/extract.py   — pobiera dane z API (NASA EONET, NOAA NGDC), zwraca listy/dicty
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
- `extract/extract.py` — ✅ gotowe (EONET + NOAA z paginacją, error handling)
- `load/load.py` — ✅ gotowe (save_to_file, RAW_DIR z configu, mkdir)
- `config.py` — ✅ gotowe (URL-e, limity, RAW_DIR, CLEAN_DIR, EONET_FILENAME, NOAA_FILENAME)
- `pipeline.py` — ✅ minimalna wersja (load_eonet + load_noaa, guard `__main__`)
- `transform/transform.py` — 🟡 w toku:
  - ma `data_check()` / `check_noaa()` / `check_eonet()` — eksploracja
  - BUG: ma `if __name__ == "__main__"` — do usunięcia (narusza konwencje)
  - brak `transform_noaa()`, `transform_eonet()`, `save_to_clean()`
- `tests/` — ○ nie zaczęte
- `notebooks/` — dwa pliki (szkic autorki + wygenerowany przez Claude). Nie uruchamiać bez prośby.
- `README.md` — nieaktualny (stara struktura). Do zaktualizowania po Silver Layer.
- `PROJECT_ROADMAP.html` — ✅ szczegółowa roadmapa z mikrokrokami, zapamiętuje checkboxy.

## Konwencje pandas (Silver Layer)
- Kolumny: snake_case (rename z camelCase z API)
- Nulle z decyzją domenową: `vei.fillna(-1)` — NIE 0 (VEI 0 = erupcja nieeksplozywna, -1 = brak danych)
- `deaths_total.fillna(0)` — brak danych o ofiarach = 0
- Cast po fillna: `.astype(int)` dla vei i deaths_total
- `month`, `day` — zostaw jako float64 z NaN (int nie przyjmuje NaN)
- Zagnieżdżony JSON: `.apply(lambda g: g[0]['klucz'])` do wypakowania geometry
- GeoJSON: `coordinates = [longitude, latitude]` — longitude PIERWSZA (pułapka!)
- Zapis Silver: `df.to_parquet(path, index=False)` — index=False standard
- Logowanie shape przed i po transformacji: `logging.info(f"shape: {df.shape}")`

## Do zrobienia dalej
1. Usuń `if __name__ == "__main__"` z `transform/transform.py`
2. Dodaj `CLEAN_NOAA_FILENAME`, `CLEAN_EONET_FILENAME` do `config.py`
3. Napisz `transform_noaa()` — 13 kolumn z 43, nulle, typy, deduplikacja
4. Napisz `transform_eonet()` — flatten geometry, apply lambda, to_datetime, is_active
5. Napisz `save_to_clean()` — to_parquet(index=False)
6. Wpięcie transform do `pipeline.py`
7. Testy pytest z zamockowanym requests.get
8. Aktualizacja README
