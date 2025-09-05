import os
import streamlit as st
import requests
from datetime import datetime
import pandas as pd

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.set_page_config(
    page_title="Speecher - Audio Transcription",
    page_icon="🎙️",
    layout="wide"
)

def main():
    st.title("🎙️ Speecher - Advanced Audio Transcription")
    st.markdown("---")
    
    # Sidebar z konfiguracją
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Cloud provider selection
        cloud_provider = st.selectbox(
            "Cloud Provider",
            ["AWS Transcribe", "Azure Speech", "Google Speech-to-Text"],
            help="Select transcription service"
        )
        
        # Language selection
        language = st.selectbox(
            "Transcription Language",
            {
                "Polish": "pl-PL",
                "English (US)": "en-US",
                "English (UK)": "en-GB",
                "German": "de-DE",
                "Spanish": "es-ES",
                "French": "fr-FR",
                "Italian": "it-IT",
                "Portuguese": "pt-PT",
                "Russian": "ru-RU",
                "Chinese": "zh-CN",
                "Japanese": "ja-JP"
            }.items(),
            format_func=lambda x: x[0]
        )
        
        # Diarization options
        st.subheader("Speaker Diarization")
        enable_diarization = st.checkbox(
            "Enable speaker recognition",
            value=True,
            help="Automatic recognition of different speakers"
        )
        
        if enable_diarization:
            max_speakers = st.slider(
                "Maximum number of speakers",
                min_value=2,
                max_value=10,
                value=4,
                help="Expected number of different speakers in the recording"
            )
        else:
            max_speakers = None
        
        # Output options
        st.subheader("Output Format")
        output_format = st.multiselect(
            "Download formats",
            ["TXT", "SRT (subtitles)", "JSON", "VTT", "PDF"],
            default=["TXT"]
        )
        
        include_timestamps = st.checkbox(
            "Include timestamps",
            value=True
        )
        
        # Cost estimation
        st.subheader("💰 Cost Estimation")
        show_cost_estimate = st.checkbox(
            "Show estimated costs",
            value=True
        )
    
    # Główna część aplikacji
    tabs = st.tabs(["📤 New Transcription", "📊 History", "ℹ️ Information"])
    
    with tabs[0]:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Upload Audio File")
            
            uploaded_file = st.file_uploader(
                "Choose audio file",
                type=["wav", "mp3", "m4a", "flac"],
                help="Supported formats: WAV, MP3, M4A, FLAC"
            )
            
            if uploaded_file:
                # Informacje o pliku
                file_details = {
                    "Filename": uploaded_file.name,
                    "Size": f"{uploaded_file.size / (1024*1024):.2f} MB",
                    "Type": uploaded_file.type
                }
                
                st.info("📁 File Details:")
                for key, value in file_details.items():
                    st.text(f"{key}: {value}")
                
                # Szacowanie kosztów
                if show_cost_estimate:
                    estimated_duration = (uploaded_file.size / (1024*1024)) * 2  # przybliżone
                    costs = calculate_costs(cloud_provider, estimated_duration)
                    
                    st.warning(f"💵 Estimated cost: ${costs:.4f}")
                
                # Przycisk transkrypcji
                if st.button("🚀 Start Transcription", type="primary", use_container_width=True):
                    with st.spinner("Processing... This may take a few minutes."):
                        result = transcribe_file(
                            uploaded_file,
                            cloud_provider,
                            language[1],
                            enable_diarization,
                            max_speakers,
                            include_timestamps
                        )
                        
                        if result["success"]:
                            st.success("✅ Transcription completed successfully!")
                            
                            # Wyświetlenie wyniku
                            st.subheader("📝 Transcription Result")
                            
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
                                    "Transcription",
                                    result["transcript"],
                                    height=300
                                )
                            
                            # Opcje pobierania
                            st.subheader("⬇️ Download Results")
                            col1, col2, col3 = st.columns(3)
                            
                            for format in output_format:
                                if format == "TXT":
                                    with col1:
                                        st.download_button(
                                            "📄 Download TXT",
                                            result["transcript"],
                                            f"transcript_{datetime.now():%Y%m%d_%H%M%S}.txt",
                                            mime="text/plain"
                                        )
                                elif format == "JSON":
                                    with col2:
                                        st.download_button(
                                            "📊 Download JSON",
                                            str(result),
                                            f"transcript_{datetime.now():%Y%m%d_%H%M%S}.json",
                                            mime="application/json"
                                        )
                                elif format == "SRT (napisy)":
                                    with col3:
                                        srt_content = generate_srt(result)
                                        st.download_button(
                                            "🎬 Download SRT",
                                            srt_content,
                                            f"transcript_{datetime.now():%Y%m%d_%H%M%S}.srt",
                                            mime="text/plain"
                                        )
                        else:
                            st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        with col2:
            st.subheader("💡 Tips")
            st.info(
                """
                **Best Practices:**
                - Use WAV files for best quality
                - Ensure recording is clean
                - Select correct language
                - Enable diarization for multiple speakers
                
                **Limits:**
                - Max file size: 500 MB
                - Max duration: 4 hours
                - Supported languages depend on provider
                """
            )
    
    with tabs[1]:
        st.subheader("📜 Transcription History")
        
        # Filtrowanie
        col1, col2, col3 = st.columns(3)
        with col1:
            search_query = st.text_input("🔍 Search", placeholder="Filename...")
        with col2:
            date_filter = st.date_input("📅 Date from", value=None)
        with col3:
            provider_filter = st.selectbox("☁️ Provider", ["All", "AWS", "Azure", "GCP"])
        
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
                    "filename": "File",
                    "provider": "Provider",
                    "language": "Language",
                    "created_at": st.column_config.DatetimeColumn("Date", format="DD.MM.YYYY HH:mm"),
                    "duration": st.column_config.NumberColumn("Duration (s)", format="%.1f")
                }
            )
            
            # Szczegóły wybranej transkrypcji
            selected_id = st.selectbox(
                "Select transcription to preview",
                df['id'].tolist(),
                format_func=lambda x: df[df['id'] == x]['filename'].values[0]
            )
            
            if selected_id:
                selected = df[df['id'] == selected_id].iloc[0]
                st.subheader(f"📋 {selected['filename']}")
                st.text_area("Transcription", selected['transcript'], height=200)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "⬇️ Download TXT",
                        selected['transcript'],
                        f"{selected['filename']}.txt"
                    )
                with col2:
                    if st.button("🗑️ Delete", type="secondary"):
                        if delete_transcription(selected_id):
                            st.success("Deleted!")
                            st.rerun()
        else:
            st.info("No transcription history")
    
    with tabs[2]:
        st.subheader("ℹ️ About")
        st.markdown(
            """
            ### Speecher - Advanced Transcription Tool
            
            **Features:**
            - 🌐 Support for 3 major cloud providers
            - 🗣️ Automatic speaker diarization
            - 🌍 Multi-language support
            - 💾 Transcription history in MongoDB
            - 📊 Export in various formats
            - 🐳 Docker containerization
            
            **Technologies:**
            - Frontend: Streamlit
            - Backend: FastAPI
            - Database: MongoDB
            - Cloud: AWS, Azure, GCP
            
            **Version:** 1.2.0
            """
        )
        
        # Status połączeń
        st.subheader("🔌 Connection Status")
        backend_status = check_backend_status()
        
        col1, col2 = st.columns(2)
        with col1:
            if backend_status:
                st.success("✅ Backend API: Connected")
            else:
                st.error("❌ Backend API: Not connected")
        
        with col2:
            db_status = check_database_status()
            if db_status:
                st.success("✅ MongoDB: Connected")
            else:
                st.error("❌ MongoDB: Not connected")

def transcribe_file(file, provider, language, diarization, max_speakers, timestamps):
    """Send file to backend API"""
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
    """Fetch transcription history from backend"""
    try:
        params = {}
        if search:
            params["search"] = search
        if date_from:
            params["date_from"] = date_from.isoformat()
        if provider and provider != "All":
            params["provider"] = provider.lower()
        
        response = requests.get(f"{BACKEND_URL}/history", params=params)
        response.raise_for_status()
        return response.json()
    except:
        return []

def delete_transcription(transcription_id):
    """Delete transcription"""
    try:
        response = requests.delete(f"{BACKEND_URL}/transcription/{transcription_id}")
        response.raise_for_status()
        return True
    except:
        return False

def generate_srt(result):
    """Generate SRT format from results"""
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
    """Estimate transcription costs"""
    costs = {
        "AWS Transcribe": 0.024,  # per minuta
        "Azure Speech": 0.016,     # per minuta
        "Google Speech-to-Text": 0.018  # per minuta
    }
    return costs.get(provider, 0.02) * duration_minutes

def check_backend_status():
    """Check backend API status"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def check_database_status():
    """Check MongoDB status"""
    try:
        response = requests.get(f"{BACKEND_URL}/db/health", timeout=2)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    main()