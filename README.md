# Speecher

Narzędzie do automatycznej transkrypcji plików audio .wav przy użyciu Amazon Web Services (AWS) Transcribe.

## Opis

Speecher to aplikacja konsolowa napisana w Pythonie, która umożliwia:

- Wgrywanie plików audio .wav do Amazon S3
- Uruchamianie zadania transkrypcji przy użyciu Amazon Transcribe
- Automatyczną identyfikację mówców (speaker diarization)
- Wyświetlanie i zapisywanie transkrypcji z podziałem na mówców
- Dodawanie znaczników czasu do transkrypcji
- Szacowanie kosztów transkrypcji

## Wymagania

- Python 3.11+
- Poetry
- Konto AWS z poprawnie skonfigurowanymi poświadczeniami (~/.aws/credentials)
- Uprawnienia do:
  - tworzenia bucketów S3 lub korzystania z istniejących
  - korzystania z usługi Amazon Transcribe

## Instalacja

```bash
# Klonowanie repozytorium
git clone <url-repozytorium>
cd speecher

# Instalacja zależności przy użyciu Poetry
poetry install
```

Opcjonalnie, dla dokładniejszego szacowania kosztów:
```bash
poetry add pydub
```

## Użycie

Podstawowe użycie:

```bash
poetry run python -m speecher.cli --audio-file plik.wav --language pl-PL
```

### Przykłady

#### Transkrypcja pliku audio w języku hiszpańskim:

```bash
poetry run python -m speecher.cli --audio-file nagranie.wav --language es-ES
```

#### Zapisanie transkrypcji do pliku:

```bash
poetry run python -m speecher.cli --audio-file nagranie.wav --language es-ES --output-file transkrypcja.txt
```

#### Transkrypcja z wyłączonymi znacznikami czasu:

```bash
poetry run python -m speecher.cli --audio-file nagranie.wav --no-timestamps
```

#### Użycie istniejącego bucketu S3:

```bash
poetry run python -m speecher.cli --audio-file nagranie.wav --bucket-name moj-bucket-s3
```

#### Transkrypcja z wyświetleniem szacowanych kosztów:

```bash
poetry run python -m speecher.cli --audio-file nagranie.wav --show-cost
```

#### Określenie maksymalnej liczby mówców:

```bash
poetry run python -m speecher.cli --audio-file nagranie.wav --max-speakers 3
```

#### Zachowanie zasobów AWS po zakończeniu transkrypcji:

```bash
poetry run python -m speecher.cli --audio-file nagranie.wav --keep-resources
```

### Wszystkie dostępne opcje:

```bash
poetry run python -m speecher.cli --help
```

```
usage: python -m speecher.cli [-h] [--audio-file AUDIO_FILE] [--keep-resources] [--region REGION] [--bucket-name BUCKET_NAME]
                              [--language LANGUAGE] [--max-speakers MAX_SPEAKERS] [--output-file OUTPUT_FILE]
                              [--include-timestamps] [--no-timestamps] [--audio-length AUDIO_LENGTH] [--show-cost]

Transkrypcja pliku audio .wav z użyciem AWS Transcribe

options:
  -h, --help            show this help message and exit
  --audio-file AUDIO_FILE
                        Ścieżka do pliku audio .wav (domyślnie: audio.wav)
  --keep-resources      Nie usuwaj zasobów AWS po zakończeniu
  --region REGION       Region AWS (domyślnie: region z konfiguracji AWS)
  --bucket-name BUCKET_NAME
                        Użyj istniejącego bucketu S3 zamiast tworzenia nowego
  --language LANGUAGE   Kod języka do transkrypcji (domyślnie: pl-PL, np. es-ES dla hiszpańskiego)
  --max-speakers MAX_SPEAKERS
                        Maksymalna liczba mówców do identyfikacji (domyślnie: 5)
  --output-file OUTPUT_FILE
                        Ścieżka do pliku wyjściowego, gdzie zostanie zapisana transkrypcja
  --include-timestamps  Czy dołączać znaczniki czasu do transkrypcji (domyślnie: włączone)
  --no-timestamps       Wyłącz znaczniki czasu w transkrypcji
  --audio-length AUDIO_LENGTH
                        Długość pliku audio w sekundach (do oszacowania kosztów)
  --show-cost           Pokaż szacunkowy koszt usługi
```

## Format wyjściowy

Transkrypcja jest wyświetlana w formacie:

```
[MM:SS.ms] spk_X: Tekst wypowiedzi.
```

Gdzie:
- `[MM:SS.ms]` - znacznik czasu w formacie minuty:sekundy.milisekundy
- `spk_X` - identyfikator mówcy (np. spk_0, spk_1)
- `Tekst wypowiedzi.` - treść wypowiedzi

Przykład:
```
[00:05.120] spk_0: Dzień dobry, witam na spotkaniu.
[00:07.840] spk_1: Dzień dobry wszystkim.
```

## Funkcje dodatkowe

### Obsługa wielu języków

Narzędzie wspiera różne języki dostępne w Amazon Transcribe, m.in.:
- Polski (pl-PL)
- Hiszpański (es-ES)
- Angielski (en-US, en-GB)
- Niemiecki (de-DE)
- Francuski (fr-FR)
- Włoski (it-IT)
- Portugalski (pt-PT)
- Rosyjski (ru-RU)

### Szacowanie kosztów

Funkcja `--show-cost` wyświetla szacunkowy koszt przeprowadzonej transkrypcji, uwzględniając:
- Koszt usługi Amazon Transcribe
- Koszt przechowywania danych w S3
- Koszt operacji na S3

## Rozwiązywanie problemów

### Brak uprawnień do tworzenia bucketów S3

Jeśli pojawi się błąd:
```
An error occurred (AccessDenied) when calling the CreateBucket operation: User is not authorized to perform: s3:CreateBucket
```

Użyj istniejącego bucketu S3 z opcją `--bucket-name`:
```bash
poetry run python -m speecher.cli --audio-file nagranie.wav --bucket-name moj-istniejacy-bucket
```

### Problemy z określeniem długości pliku audio

Zainstaluj bibliotekę pydub:
```bash
poetry add pydub
```

Lub podaj długość ręcznie:
```bash
poetry run python -m speecher.cli --audio-file nagranie.wav --show-cost --audio-length 300
```

## Licencja

Projekt na licencji MIT.

## Autor

Rafał Łagowski