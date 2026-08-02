import streamlit as st
from googleapiclient.discovery import build
from google import genai

# Streamlit Sayfa Ayarları
st.set_page_config(page_title="Crypto Check AI Panel", page_icon="📈", layout="wide")

st.title("🚀 Crypto Check - Canlı AI Analiz Paneli")

# Sol Menüden Şifre Girişleri
st.sidebar.header("🔑 API Bağlantı Ayarları")
youtube_key = st.sidebar.text_input("YouTube API Key", type="password")
gemini_key = st.sidebar.text_input("Gemini API Key", type="password")
channel_id = st.sidebar.text_input("YouTube Kanal ID")

if st.sidebar.button("Analizi Başlat"):
    if not youtube_key or not gemini_key or not channel_id:
        st.error("Lütfen sol menüdeki tüm alanları doldurun!")
    else:
        try:
            # 1. YouTube Data API Bağlantısı
            youtube = build('youtube', 'v3', developerKey=youtube_key)
            request = youtube.channels().list(
                part='statistics,snippet',
                id=channel_id
            ).execute()

            channel = request['items'][0]
            title = channel['snippet']['title']
            views = int(channel['statistics']['viewCount'])
            subscribers = int(channel['statistics']['subscriberCount'])
            videos = int(channel['statistics']['videoCount'])

            # Metrikleri Göster
            col1, col2, col3 = st.columns(3)
            col1.metric("Toplam İzlenme", f"{views:,}")
            col2.metric("Abone Sayısı", f"{subscribers:,}")
            col3.metric("Video Sayısı", f"{videos:,}")

            st.divider()

            # 2. Gemini AI Analizi (Dinamik Model Seçimi)
            st.subheader("🤖 AI Ajanının Kanal Strateji Raporu")
            with st.spinner("Yapay zeka verileri inceliyor..."):
                client = genai.Client(api_key=gemini_key)
                
                # Kullanılabilir modelleri API'den çek
                model_list = [m.name for m in client.models.list()]
                
                # Uygun metin modelini bul (İçinde 'flash' veya 'pro' geçen ilk model)
                selected_model = None
                for m_name in model_list:
                    if 'flash' in m_name or 'pro' in m_name or 'gemini' in m_name:
                        selected_model = m_name
                        break
                
                if not selected_model and len(model_list) > 0:
                    selected_model = model_list[0]

                if not selected_model:
                    st.error("Hesabınıza tanımlı aktif bir Gemini modeli bulunamadı.")
                else:
                    prompt = f"""
                    Sen profesyonel bir YouTube Kripto Kanalı Stratejistisin.
                    Kanal Adı: {title}
                    Toplam İzlenme: {views}
                    Abone Sayısı: {subscribers}
                    Video Sayısı: {videos}

                    Bu verilere göre:
                    1. Kanalın mevcut performansını değerlendir.
                    2. Kripto piyasasındaki son trendlere uygun çekilebilecek 3 spesifik video konusu öner (Başlık fikirleriyle birlikte).
                    3. Tıklama oranını (CTR) ve izleyici tutmayı artıracak 1 altın tavsiye ver.
                    """
                    
                    response = client.models.generate_content(
                        model=selected_model,
                        contents=prompt
                    )
                    st.markdown(response.text)

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
else:
    st.info("👈 Analizi başlatmak için sol taraftaki menüden API anahtarlarınızı girip 'Analizi Başlat' butonuna basın.")
