Napisz program w Pythonie, który korzysta z Amazon Web Services (AWS) do transkrypcji pliku audio `.wav` z lokalnej ścieżki `audio.wav`. Program powinien:

1. Wgrać plik do Amazon S3 (użyj unikalnej nazwy bucketu).
2. Uruchomić zadanie transkrypcji przy użyciu Amazon Transcribe z następującymi ustawieniami:
   - Język: polski (`pl-PL`)
   - Format pliku: `wav`
   - Automatyczna identyfikacja mówców (speaker diarization)
   - Maksymalna liczba mówców: 5
3. Poczekać aż zadanie się zakończy (polling).
4. Pobierz wynik z podanego URL.
5. Przetwórz JSON wynikowy i wypisz transkrypcję na konsoli z podziałem na osoby, np.:

Speaker 0: Dzień dobry, witam wszystkich.
Speaker 1: Dzień dobry, zaczynajmy spotkanie.
...

Założenia:
- Użytkownik ma poprawnie skonfigurowane AWS credentials (`~/.aws/credentials`).
- Użyj `boto3` i `requests`.
- Zadbaj o przejrzysty kod i komentarze.
- Obsłuż ewentualne błędy (np. brak połączenia, błędy A
