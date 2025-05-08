#!/usr/bin/env python3
"""
Transcription Processor Module

Moduł zawierający funkcje do przetwarzania wyników transkrypcji.
"""

import json
import logging

# Konfiguracja loggera
logger = logging.getLogger(__name__)

def process_transcription_result(transcription_data, output_file=None, include_timestamps=True):
    """
    Przetwarza dane JSON z transkrypcji i wypisuje je z podziałem na mówców.
    Opcjonalnie zapisuje transkrypcję do pliku.
    
    Args:
        transcription_data: Dane transkrypcji w formacie JSON
        output_file: Opcjonalna ścieżka do pliku wyjściowego
        include_timestamps: Czy dołączać znaczniki czasu do transkrypcji
        
    Returns:
        bool: True jeśli przetwarzanie się powiodło, False w przypadku błędu
    """
    try:
        result = transcription_data['results']
        
        # Sprawdźmy czy transkrypcja zawiera identyfikację mówców
        if not result.get('speaker_labels') or not result.get('items'):
            logger.error("Dane transkrypcji nie zawierają informacji o mówcach")
            return False
        
        speaker_segments = result['speaker_labels']['segments']
        items = result['items']
        
        # Lista do przechowywania chronologicznych wypowiedzi
        chronological_segments = []
        
        # Przygotujmy słownik wszystkich elementów z indeksami bazującymi na czasie
        items_dict = {}
        
        # Słownik do przechowywania elementów interpunkcyjnych
        punctuation_items = []
        
        # Najpierw zbierzmy wszystkie elementy interpunkcyjne, które nie mają czasu
        for i, item in enumerate(items):
            if item.get('type') == 'punctuation':
                punctuation_items.append((i, item))
            elif item.get('start_time') and item.get('end_time'):
                time_key = (float(item['start_time']), float(item['end_time']))
                items_dict[time_key] = item
        
        # Zaczynamy od metody segmentów chronologicznych
        for segment in speaker_segments:
            speaker_label = segment['speaker_label']
            segment_start = float(segment['start_time'])
            segment_end = float(segment['end_time'])
            
            # Zbierz wszystkie słowa z zakresu czasu tego segmentu wraz z interpunkcją
            segment_items = []
            
            # Dla każdego segmentu czasu, znajdź wszystkie słowa, które są w jego zakresie
            for item in items:
                # Pomijamy tymczasowo interpunkcję, bo dodamy ją później
                if item.get('type') == 'punctuation':
                    continue
                    
                if not item.get('start_time') or not item.get('end_time'):
                    continue
                    
                item_start = float(item['start_time'])
                item_end = float(item['end_time'])
                
                # Sprawdź czy element jest w zakresie tego segmentu
                if segment_start <= item_start and item_end <= segment_end:
                    segment_items.append(item)
            
            # Sortujemy elementy według czasu
            segment_items.sort(key=lambda x: float(x['start_time']))
            
            # Teraz dla każdego elementu sprawdź, czy następny element w items jest interpunkcją
            final_text_elements = []
            
            for i, segment_item in enumerate(segment_items):
                if not segment_item.get('alternatives') or not segment_item['alternatives']:
                    continue
                
                content = segment_item['alternatives'][0].get('content', '')
                final_text_elements.append(content)
                
                # Szukamy interpunkcji zaraz po tym elemencie
                item_index = items.index(segment_item)
                if item_index + 1 < len(items) and items[item_index + 1].get('type') == 'punctuation':
                    punct_content = items[item_index + 1]['alternatives'][0].get('content', '')
                    # Dodajemy interpunkcję bez spacji
                    final_text_elements[-1] += punct_content
            
            # Łączymy elementy tekstowe w czytelny tekst
            if final_text_elements:
                # Formatowanie tekstu - dodanie wielkiej litery na początku zdania i inne poprawki
                text = ' '.join(final_text_elements)
                
                # Zastąp wielokrotne spacje pojedynczą spacją
                text = ' '.join(text.split())
                
                # Upewnij się, że jest wielka litera na początku
                if text and len(text) > 0:
                    text = text[0].upper() + text[1:]
                
                # Dodaj kropkę na końcu zdania, jeśli nie ma interpunkcji
                if text and not text[-1] in ['.', '!', '?', ',', ';', ':', '-']:
                    text += '.'
                
                chronological_segments.append({
                    'speaker': speaker_label,
                    'text': text,
                    'start_time': segment_start,
                    'end_time': segment_end
                })
        
        # Jeśli metoda poprzednia nie wypełniła listy, spróbuj alternatywną metodę
        if not chronological_segments:
            logger.info("Używam alternatywnej metody grupowania wypowiedzi z interpunkcją")
            
            # Słownik do przechowywania treści dla każdego mówcy i segmentu
            current_speaker = None
            current_text_elements = []
            current_start_time = None
            current_end_time = None
            
            # Grupuj słowa według mówcy, ale zachowaj chronologię
            for segment in speaker_segments:
                speaker = segment['speaker_label']
                segment_start = float(segment['start_time'])
                segment_end = float(segment['end_time'])
                
                # Jeśli zmienił się mówca, zapisz poprzednią wypowiedź z poprawkami
                if current_speaker is not None and current_speaker != speaker and current_text_elements:
                    text = ' '.join(current_text_elements)
                    
                    # Zastąp wielokrotne spacje pojedynczą spacją
                    text = ' '.join(text.split())
                    
                    # Upewnij się, że jest wielka litera na początku
                    if text and len(text) > 0:
                        text = text[0].upper() + text[1:]
                    
                    # Dodaj kropkę na końcu zdania, jeśli nie ma interpunkcji
                    if text and not text[-1] in ['.', '!', '?', ',', ';', ':', '-']:
                        text += '.'
                    
                    chronological_segments.append({
                        'speaker': current_speaker,
                        'text': text,
                        'start_time': current_start_time,
                        'end_time': current_end_time
                    })
                    current_text_elements = []
                
                # Aktualizacja aktualnego mówcy i czasu rozpoczęcia
                current_speaker = speaker
                if current_start_time is None:
                    current_start_time = segment_start
                current_end_time = segment_end
                
                # Znajdź wszystkie słowa i interpunkcję w tym segmencie
                for i, item in enumerate(items):
                    if not item.get('start_time') and item.get('type') == 'punctuation':
                        # Jeśli to interpunkcja i mamy poprzedni element, dodaj do niego
                        if current_text_elements:
                            current_text_elements[-1] += item['alternatives'][0].get('content', '')
                        continue
                        
                    if not item.get('start_time') or not item.get('end_time'):
                        continue
                        
                    item_start = float(item['start_time'])
                    item_end = float(item['end_time'])
                    
                    # Sprawdź czy element jest w zakresie tego segmentu
                    if segment_start <= item_start and item_end <= segment_end:
                        if item.get('alternatives') and len(item['alternatives']) > 0:
                            word = item['alternatives'][0].get('content', '')
                            current_text_elements.append(word)
                            
                            # Sprawdź czy następny element to interpunkcja
                            if i + 1 < len(items) and items[i + 1].get('type') == 'punctuation':
                                punct = items[i + 1]['alternatives'][0].get('content', '')
                                current_text_elements[-1] += punct
            
            # Dodaj ostatni segment z poprawkami
            if current_speaker is not None and current_text_elements:
                text = ' '.join(current_text_elements)
                
                # Zastąp wielokrotne spacje pojedynczą spacją
                text = ' '.join(text.split())
                
                # Upewnij się, że jest wielka litera na początku
                if text and len(text) > 0:
                    text = text[0].upper() + text[1:]
                
                # Dodaj kropkę na końcu zdania, jeśli nie ma interpunkcji
                if text and not text[-1] in ['.', '!', '?', ',', ';', ':', '-']:
                    text += '.'
                
                chronological_segments.append({
                    'speaker': current_speaker,
                    'text': text,
                    'start_time': current_start_time,
                    'end_time': current_end_time
                })
        
        # Jeśli nadal brak transkrypcji, użyj prostej metody
        if not chronological_segments:
            logger.info("Używam prostej metody z podstawową interpunkcją")
            
            # Zbierz wszystkie słowa bez podziału na mówców
            all_words = []
            
            for item in items:
                if item.get('alternatives') and len(item['alternatives']) > 0:
                    word = item['alternatives'][0].get('content', '')
                    
                    # Interpunkcja
                    if item.get('type') == 'punctuation':
                        if all_words:
                            all_words[-1] += word
                        continue
                        
                    all_words.append(word)
            
            if all_words:
                text = ' '.join(all_words)
                
                # Zastąp wielokrotne spacje pojedynczą spacją
                text = ' '.join(text.split())
                
                # Upewnij się, że jest wielka litera na początku
                if text and len(text) > 0:
                    text = text[0].upper() + text[1:]
                
                # Dodaj kropkę na końcu zdania, jeśli nie ma interpunkcji
                if text and not text[-1] in ['.', '!', '?', ',', ';', ':', '-']:
                    text += '.'
                
                chronological_segments.append({
                    'speaker': 'Speaker',
                    'text': text,
                    'start_time': 0.0,
                    'end_time': 0.0
                })
        
        # Sortuj segmenty chronologicznie według czasu rozpoczęcia
        chronological_segments.sort(key=lambda x: x['start_time'])
        
        # Wypisz wyniki
        print("\n=== TRANSKRYPCJA (CHRONOLOGICZNIE) ===\n")
        if not chronological_segments:
            print("Nie udało się przetworzyć transkrypcji. Sprawdź format danych.")
            return False
            
        # Przygotuj zawartość transkrypcji do wyświetlenia i zapisania
        transcript_lines = []
        for segment in chronological_segments:
            # Formatowanie czasu w formacie [MM:SS.ms]
            minutes = int(segment['start_time'] // 60)
            seconds = segment['start_time'] % 60
            time_str = f"[{minutes:02d}:{seconds:06.3f}]"
            
            if include_timestamps:
                line = f"{time_str} {segment['speaker']}: {segment['text']}"
            else:
                line = f"{segment['speaker']}: {segment['text']}"
                
            print(line)
            transcript_lines.append(line)
        
        # Zapisz do pliku, jeśli podano ścieżkę
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("\n".join(transcript_lines))
                logger.info(f"Zapisano transkrypcję chronologiczną do pliku: {output_file}")
            except Exception as e:
                logger.error(f"Błąd podczas zapisywania transkrypcji do pliku: {e}")
                return False
                
        return True
    except KeyError as e:
        logger.error(f"Błąd podczas przetwarzania danych transkrypcji - brak klucza: {e}")
        # Wypisz strukturę danych dla celów diagnostycznych
        try:
            logger.debug(f"Struktura transcription_data: {json.dumps(transcription_data, indent=2)[:1000]}...")
        except:
            pass
        return False
    except Exception as e:
        logger.error(f"Nieoczekiwany błąd podczas przetwarzania transkrypcji: {e}")
        return False