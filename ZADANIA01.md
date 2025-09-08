# ZADANIA01 - Plan Poprawy Testów i Pokrycia Kodu

## Status Obecny
- **Pokrycie testami**: 51% (1501 stwierdzeń, 734 brakujących)
- **Status testów**: 8 nieudanych, 101 przeszło, 3 pominięte
- **Data analizy**: 2025-09-07

## Priorytet 1: Naprawa Nieudanych Testów [PILNE]

### 1.1 Testy AWS (4 testy)
**Pliki**: `tests/test_aws.py`

- [ ] `test_create_s3_bucket_client_error` - Mock zwraca string zamiast False
- [ ] `test_create_s3_bucket_non_us_east_1` - Mock nie jest wywoływany
- [ ] `test_create_s3_bucket_us_east_1` - Mock nie jest wywoływany  
- [ ] `test_upload_file_to_s3_error` - Problem z wartością zwracaną

**Opis problemu**: Funkcje AWS zwracają bucket name zamiast boolean, trzeba dostosować testy do nowej logiki.

### 1.2 Testy Azure (2 testy)
**Pliki**: `tests/test_azure.py`

- [ ] `test_transcribe_short_audio` - AssertionError w asercji
- [ ] `test_upload_file_to_blob` - Problem z wartością zwracaną

**Opis problemu**: Podobnie jak AWS, funkcje zwracają rzeczywiste wartości zamiast boolean.

### 1.3 Test Docker Integration (1 test)
**Plik**: `tests/test_docker_integration.py`

- [ ] `test_transcribe_missing_provider_config` - Brak konfiguracji providera

**Opis problemu**: Test wymaga właściwej konfiguracji zmiennych środowiskowych dla providerów.

### 1.4 Test Main Module (1 test)
**Plik**: `tests/test_main.py`

- [ ] `test_main_function_keep_resources` - Mock logger nie znajduje oczekiwanego wywołania

**Opis problemu**: Funkcja używa dynamicznie generowanego job_name zamiast stałego.

## Priorytet 2: Uzupełnienie Brakujących Testów

### 2.1 Moduł GCP - 0% pokrycia [KRYTYCZNE]
**Plik**: `src/speecher/gcp.py` (186 linii, 0% pokrycia)

- [ ] Utworzyć `tests/test_gcp.py`
- [ ] Testy dla `upload_file_to_gcs()`
- [ ] Testy dla `transcribe_audio_gcp()`
- [ ] Testy dla `wait_for_gcp_operation()`
- [ ] Testy dla `process_gcp_result()`
- [ ] Testy obsługi błędów i edge cases

**Cel**: Minimum 70% pokrycia

### 2.2 Moduł Cloud Wrappers - 14% pokrycia [WYSOKIE]
**Plik**: `src/backend/cloud_wrappers.py` (73 linie, 63 brakujące)

- [ ] Testy dla wrapper AWS
- [ ] Testy dla wrapper Azure
- [ ] Testy dla wrapper GCP
- [ ] Testy integracyjne między wrapperami

**Cel**: Minimum 60% pokrycia

### 2.3 Moduł API Keys - 31% pokrycia [ŚREDNIE]
**Plik**: `src/backend/api_keys.py` (163 linie, 112 brakujących)

- [ ] Testy walidacji kluczy API
- [ ] Testy rotacji kluczy
- [ ] Testy bezpieczeństwa (rate limiting, ekspiracja)
- [ ] Testy przechowywania w MongoDB

**Cel**: Minimum 70% pokrycia

### 2.4 Moduł Streaming - 33% pokrycia [ŚREDNIE]
**Plik**: `src/backend/streaming.py` (93 linie, 62 brakujące)

- [ ] Testy WebSocket connection
- [ ] Testy streaming audio
- [ ] Testy buforowania
- [ ] Testy obsługi błędów połączenia

**Cel**: Minimum 60% pokrycia

## Priorytet 3: Standardy Jakości Kodu

### 3.1 Konfiguracja CI/CD
- [ ] Ustawić minimalny próg pokrycia na 70% w GitHub Actions
- [ ] Dodać badge pokrycia do README
- [ ] Skonfigurować codecov.io lub podobny serwis
- [ ] Automatyczne komentarze PR z raportem pokrycia

### 3.2 Pre-commit Hooks
- [ ] Hook dla uruchomienia testów przed commitem
- [ ] Hook dla sprawdzenia pokrycia (warning jeśli <70%)
- [ ] Hook dla lintingu (flake8, black, mypy)

### 3.3 Dokumentacja Testów
- [ ] README dla katalogu tests/
- [ ] Instrukcje uruchamiania testów lokalnie
- [ ] Instrukcje uruchamiania testów w Docker
- [ ] Best practices dla pisania nowych testów

## Priorytet 4: Testy Integracyjne i E2E

### 4.1 Testy Docker Setup
- [ ] Test pełnego flow z docker-compose
- [ ] Test healthchecków wszystkich serwisów
- [ ] Test woluminów i persystencji danych
- [ ] Test restartów i odporności na błędy

### 4.2 Testy End-to-End
- [ ] E2E test dla AWS (upload → transcribe → zapis)
- [ ] E2E test dla Azure (upload → transcribe → zapis)
- [ ] E2E test dla GCP (upload → transcribe → zapis)
- [ ] E2E test dla streamingu audio

### 4.3 Testy Wydajnościowe
- [ ] Test obciążenia dla endpointów API
- [ ] Test wielkości plików (limity)
- [ ] Test współbieżności requestów
- [ ] Benchmark czasu odpowiedzi

## Metryki Sukcesu

| Metryka | Obecna | Docelowa | Deadline |
|---------|---------|----------|----------|
| Pokrycie ogólne | 51% | 70% | 2 tygodnie |
| Failing testy | 8 | 0 | 2 dni |
| Moduły bez testów | 1 (GCP) | 0 | 1 tydzień |
| CI/CD z coverage | ❌ | ✅ | 3 dni |
| E2E testy | Częściowe | Kompletne | 2 tygodnie |

## Harmonogram

### Tydzień 1
1. Dzień 1-2: Naprawa wszystkich failing testów
2. Dzień 3-4: Dodanie testów dla modułu GCP
3. Dzień 5: Konfiguracja CI/CD z progiem pokrycia

### Tydzień 2
1. Dzień 1-2: Testy dla cloud_wrappers
2. Dzień 3-4: Testy dla api_keys i streaming
3. Dzień 5: Testy integracyjne Docker

### Tydzień 3
1. Dzień 1-3: Testy E2E dla wszystkich providerów
2. Dzień 4-5: Testy wydajnościowe i dokumentacja

## Notatki Techniczne

### Narzędzia
- **Framework testowy**: pytest
- **Pokrycie**: pytest-cov
- **Mocking**: unittest.mock, pytest-mock
- **E2E**: pytest + requests
- **Performance**: locust lub pytest-benchmark

### Komendy
```bash
# Uruchom wszystkie testy z pokryciem
make test-coverage

# Uruchom testy w Docker
make docker-test

# Uruchom tylko failing testy
pytest tests/test_aws.py tests/test_azure.py tests/test_docker_integration.py tests/test_main.py -v

# Generuj raport HTML pokrycia
pytest --cov=src --cov-report=html
```

### Przykładowe Struktury Testów

#### Test z mockiem AWS
```python
@patch('boto3.client')
def test_aws_function(mock_client):
    mock_s3 = MagicMock()
    mock_client.return_value = mock_s3
    mock_s3.upload_file.return_value = None
    
    # Test logic here
```

#### Test asynchroniczny
```python
@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/endpoint", json={})
        assert response.status_code == 200
```

## Kontakt i Wsparcie
- **Owner**: Team Speecher
- **Slack**: #speecher-dev
- **Dokumentacja**: /docs/testing.md