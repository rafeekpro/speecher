import os
import streamlit as st
import requests
from datetime import datetime
import pandas as pd

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.set_page_config(
    page_title="Speecher - Transkrypcja Audio",
    page_icon="🎙️",
    layout="wide"
)

def main():
    st.title("🎙️ Speecher - Zaawansowana Transkrypcja Audio")
    st.markdown("---")
    
    # Sidebar z konfiguracją
    with st.sidebar:
        st.header("⚙️ Konfiguracja")
        
        # Wybór dostawcy chmury
        cloud_provider = st.selectbox(
            "Dostawca chmury",
            ["AWS Transcribe", "Azure Speech", "Google Speech-to-Text"],
            help="Wybierz usługę transkrypcji"
        )
        
        # Wybór języka
        language = st.selectbox(
            "Język transkrypcji",
            {
                "Polski": "pl-PL",
                "Angielski (US)": "en-US",
                "Angielski (UK)": "en-GB",
                "Niemiecki": "de-DE",
                "Hiszpański": "es-ES",
                "Francuski": "fr-FR",
                "Włoski": "it-IT",
                "Portugalski": "pt-PT",
                "Rosyjski": "ru-RU",
                "Chiński": "zh-CN",
                "Japoński": "ja-JP"
            }.items(),
            format_func=lambda x: x[0]
        )
        
        # Opcje diaryzacji
        st.subheader("Diaryzacja mówców")
        enable_diarization = st.checkbox(
            "Włącz rozpoznawanie mówców",
            value=True,
            help="Automatyczne rozpoznawanie różnych osób mówiących"
        )
        
        if enable_diarization:
            max_speakers = st.slider(
                "Maksymalna liczba mówców",
                min_value=2,
                max_value=10,
                value=4,
                help="Przewidywana liczba różnych osób w nagraniu"
            )
        else:
            max_speakers = None
        
        # Opcje wyjścia
        st.subheader("Format wyjściowy")
        output_format = st.multiselect(
            "Formaty do pobrania",
            ["TXT", "SRT (napisy)", "JSON", "VTT", "PDF"],
            default=["TXT"]
        )
        
        include_timestamps = st.checkbox(
            "Dołącz znaczniki czasu",
            value=True
        )
        
        # Szacowanie kosztów
        st.subheader("💰 Szacowanie kosztów")
        show_cost_estimate = st.checkbox(
            "Pokaż szacowane koszty",
            value=True
        )
    
    # Główna część aplikacji
    tabs = st.tabs(["📤 Nowa transkrypcja", "📊 Historia", "ℹ️ Informacje"])
    
    with tabs[0]:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Prześlij plik audio")
            
            uploaded_file = st.file_uploader(
                "Wybierz plik WAV",
                type=["wav", "mp3", "m4a", "flac"],
                help="Obsługiwane formaty: WAV, MP3, M4A, FLAC"
            )
            
            if uploaded_file:
                # Informacje o pliku
                file_details = {
                    "Nazwa pliku": uploaded_file.name,
                    "Rozmiar": f"{uploaded_file.size / (1024*1024):.2f} MB",
                    "Typ": uploaded_file.type
                }
                
                st.info("📁 Szczegóły pliku:")
                for key, value in file_details.items():
                    st.text(f"{key}: {value}")
                
                # Szacowanie kosztów
                if show_cost_estimate:
                    estimated_duration = (uploaded_file.size / (1024*1024)) * 2  # przybliżone
                    costs = calculate_costs(cloud_provider, estimated_duration)
                    
                    st.warning(f"💵 Szacowany koszt: ${costs:.4f}")
                
                # Przycisk transkrypcji
                if st.button("🚀 Rozpocznij transkrypcję", type="primary", use_container_width=True):
                    with st.spinner("Przetwarzanie... To może potrwać kilka minut."):
                        result = transcribe_file(
                            uploaded_file,
                            cloud_provider,
                            language[1],
                            enable_diarization,
                            max_speakers,
                            include_timestamps
                        )
                        
                        if result["success"]:
                            st.success("✅ Transkrypcja zakończona pomyślnie!")
                            
                            # Wyświetlenie wyniku
                            st.subheader("📝 Wynik transkrypcji")
                            
                            # Wyświetlanie z podziałem na mówców
                            if enable_diarization and result.get("speakers"):
                                for speaker_segment in result["speakers"]:
                                    speaker = speaker_segment.get("speaker", "Nieznany")
                                    text = speaker_segment.get("text", "")
                                    start_time = speaker_segment.get("start_time", "")
                                    
                                    if include_timestamps:
                                        st.markdown(f"**{speaker}** [{start_time}]: {text}")
                                    else:
                                        st.markdown(f"**{speaker}**: {text}")
                            else:
                                st.text_area(
                                    "Transkrypcja",
                                    result["transcript"],
                                    height=300
                                )
                            
                            # Opcje pobierania
                            st.subheader("⬇️ Pobierz wyniki")
                            col1, col2, col3 = st.columns(3)
                            
                            for format in output_format:
                                if format == "TXT":
                                    with col1:
                                        st.download_button(
                                            "📄 Pobierz TXT",
                                            result["transcript"],
                                            f"transcript_{datetime.now():%Y%m%d_%H%M%S}.txt",
                                            mime="text/plain"
                                        )
                                elif format == "JSON":
                                    with col2:
                                        st.download_button(
                                            "📊 Pobierz JSON",
                                            str(result),
                                            f"transcript_{datetime.now():%Y%m%d_%H%M%S}.json",
                                            mime="application/json"
                                        )
                                elif format == "SRT (napisy)":
                                    with col3:
                                        srt_content = generate_srt(result)
                                        st.download_button(
                                            "🎬 Pobierz SRT",
                                            srt_content,
                                            f"transcript_{datetime.now():%Y%m%d_%H%M%S}.srt",
                                            mime="text/plain"
                                        )
                        else:
                            st.error(f"❌ Błąd: {result.get('error', 'Nieznany błąd')}")
        
        with col2:
            st.subheader("💡 Wskazówki")
            st.info(
                """
                **Najlepsze praktyki:**
                - Używaj plików WAV dla najlepszej jakości
                - Upewnij się, że nagranie jest czyste
                - Wybierz właściwy język
                - Dla wielu mówców włącz diaryzację
                
                **Limity:**
                - Max rozmiar pliku: 500 MB
                - Max długość: 4 godziny
                - Obsługiwane języki zależą od dostawcy
                """
            )
    
    with tabs[1]:
        st.subheader("📜 Historia transkrypcji")
        
        # Filtrowanie
        col1, col2, col3 = st.columns(3)
        with col1:
            search_query = st.text_input("🔍 Szukaj", placeholder="Nazwa pliku...")
        with col2:
            date_filter = st.date_input("📅 Data od", value=None)
        with col3:
            provider_filter = st.selectbox("☁️ Dostawca", ["Wszystkie", "AWS", "Azure", "GCP"])
        
        # Pobierz historię z backend
        history = fetch_transcription_history(search_query, date_filter, provider_filter)
        
        if history:
            # Wyświetl jako tabelę
            df = pd.DataFrame(history)
            df['created_at'] = pd.to_datetime(df['created_at'])
            df = df.sort_values('created_at', ascending=False)
            
            st.dataframe(
                df[['filename', 'provider', 'language', 'created_at', 'duration']],
                use_container_width=True,
                column_config={
                    "filename": "Plik",
                    "provider": "Dostawca",
                    "language": "Język",
                    "created_at": st.column_config.DatetimeColumn("Data", format="DD.MM.YYYY HH:mm"),
                    "duration": st.column_config.NumberColumn("Czas (s)", format="%.1f")
                }
            )
            
            # Szczegóły wybranej transkrypcji
            selected_id = st.selectbox(
                "Wybierz transkrypcję do podglądu",
                df['id'].tolist(),
                format_func=lambda x: df[df['id'] == x]['filename'].values[0]
            )
            
            if selected_id:
                selected = df[df['id'] == selected_id].iloc[0]
                st.subheader(f"📋 {selected['filename']}")
                st.text_area("Transkrypcja", selected['transcript'], height=200)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "⬇️ Pobierz TXT",
                        selected['transcript'],
                        f"{selected['filename']}.txt"
                    )
                with col2:
                    if st.button("🗑️ Usuń", type="secondary"):
                        if delete_transcription(selected_id):
                            st.success("Usunięto!")
                            st.rerun()
        else:
            st.info("Brak historii transkrypcji")
    
    with tabs[2]:
        st.subheader("ℹ️ O aplikacji")
        st.markdown(
            """
            ### Speecher - Zaawansowane narzędzie transkrypcji
            
            **Funkcje:**
            - 🌐 Wsparcie dla 3 głównych dostawców chmury
            - 🗣️ Automatyczna diaryzacja mówców
            - 🌍 Obsługa wielu języków
            - 💾 Historia transkrypcji w MongoDB
            - 📊 Eksport w różnych formatach
            - 🐳 Konteneryzacja Docker
            
            **Technologie:**
            - Frontend: Streamlit
            - Backend: FastAPI
            - Baza danych: MongoDB
            - Chmura: AWS, Azure, GCP
            
            **Wersja:** 1.2.0
            """
        )
        
        # Status połączeń
        st.subheader("🔌 Status połączeń")
        backend_status = check_backend_status()
        
        col1, col2 = st.columns(2)
        with col1:
            if backend_status:
                st.success("✅ Backend API: Połączony")
            else:
                st.error("❌ Backend API: Brak połączenia")
        
        with col2:
            db_status = check_database_status()
            if db_status:
                st.success("✅ MongoDB: Połączona")
            else:
                st.error("❌ MongoDB: Brak połączenia")

def transcribe_file(file, provider, language, diarization, max_speakers, timestamps):
    """Wysyła plik do API backend"""
    try:
        provider_map = {
            "AWS Transcribe": "aws",
            "Azure Speech": "azure",
            "Google Speech-to-Text": "gcp"
        }
        
        files = {"file": (file.name, file.read(), file.type)}
        data = {
            "provider": provider_map[provider],
            "language": language,
            "enable_diarization": diarization,
            "max_speakers": max_speakers,
            "include_timestamps": timestamps
        }
        
        response = requests.post(
            f"{BACKEND_URL}/transcribe",
            files=files,
            data=data
        )
        response.raise_for_status()
        
        result = response.json()
        return {
            "success": True,
            "transcript": result.get("transcript", ""),
            "speakers": result.get("speakers", []),
            "id": result.get("id", "")
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def fetch_transcription_history(search=None, date_from=None, provider=None):
    """Pobiera historię transkrypcji z backend"""
    try:
        params = {}
        if search:
            params["search"] = search
        if date_from:
            params["date_from"] = date_from.isoformat()
        if provider and provider != "Wszystkie":
            params["provider"] = provider.lower()
        
        response = requests.get(f"{BACKEND_URL}/history", params=params)
        response.raise_for_status()
        return response.json()
    except:
        return []

def delete_transcription(transcription_id):
    """Usuwa transkrypcję"""
    try:
        response = requests.delete(f"{BACKEND_URL}/transcription/{transcription_id}")
        response.raise_for_status()
        return True
    except:
        return False

def generate_srt(result):
    """Generuje format SRT z wyników"""
    srt_content = []
    counter = 1
    
    for segment in result.get("speakers", []):
        start = segment.get("start_time", "00:00:00")
        end = segment.get("end_time", "00:00:05")
        text = segment.get("text", "")
        
        srt_content.append(f"{counter}")
        srt_content.append(f"{start},000 --> {end},000")
        srt_content.append(text)
        srt_content.append("")
        counter += 1
    
    return "\n".join(srt_content)

def calculate_costs(provider, duration_minutes):
    """Szacuje koszty transkrypcji"""
    costs = {
        "AWS Transcribe": 0.024,  # per minuta
        "Azure Speech": 0.016,     # per minuta
        "Google Speech-to-Text": 0.018  # per minuta
    }
    return costs.get(provider, 0.02) * duration_minutes

def check_backend_status():
    """Sprawdza status backend API"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def check_database_status():
    """Sprawdza status MongoDB"""
    try:
        response = requests.get(f"{BACKEND_URL}/db/health", timeout=2)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    main()