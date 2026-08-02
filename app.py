import streamlit as st
from googleapiclient.discovery import build
from groq import Groq

# Streamlit Sayfa Ayarları
st.set_page_config(page_title="Crypto Check AI Panel", page_icon="📈", layout="wide")

st.title("🚀 Crypto Check - Canlı AI Analiz Paneli")

# Sol Menüden Şifre Girişleri
st.sidebar.header("🔑 API Bağlantı Ayarları")
youtube_key = st.sidebar.text_input("YouTube API Key", type="password")
groq_key = st.sidebar.text_input("Groq API Key (Ücretsiz)", type="password")
channel_id = st.sidebar.text_input("YouTube Kanal ID")

if st.sidebar.button("Analizi Başlat"):
    if not youtube_key or not groq_key or not channel_id:
        st.error("Lütfen sol menüdeki tüm alanları doldurun!")
    else:
        try:
            # 1. YouTube Data API
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

            # 2. AI Strateji Analizi (Groq Llama 3.3)
            st.subheader("🤖 AI Ajanının Kanal Strateji Raporu")
            with st.spinner("Yapay zeka verileri inceliyor..."):
                client = Groq(api_key=groq_key)
                
                # Türkçe karakter uyumu için açık UTF-8 prompt tanımı
                prompt = f"""
                You are a professional YouTube Crypto Channel Strategist.
                Channel Name: {title}
                Total Views: {views}
                Subscribers: {subscribers}
                Video Count: {videos}

                Please provide your detailed evaluation and strategy report strictly in Turkish:
                1. Kanalın mevcut performansını değerlendir.
                2. Kripto piyasasındaki son trendlere uygun çekilebilecek 3 spesifik video konusu öner (Başlık fikirleriyle birlikte).
                3. Tıklama oranını (CTR) ve izleyici tutmayı artıracak 1 altın tavsiye ver.
                """
                
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model="llama-3.3-70b-versatile",
                )

                st.markdown(chat_completion.choices[0].message.content)

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
else:
    st.info("👈 Sol menüden YouTube API Key ve Groq API Key girip 'Analizi Başlat' butonuna basın.")
