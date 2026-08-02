import streamlit as st
from googleapiclient.discovery import build
from groq import Groq
import pandas as pd
import plotly.express as px

# Streamlit Sayfa Ayarları
st.set_page_config(page_title="Crypto Check Pro Analytics", page_icon="📈", layout="wide")

st.title("🚀 Crypto Check - Profesyonel AI Analiz & Metrik Paneli")

# Sol Menü
st.sidebar.header("🔑 API Bağlantı Ayarları")
youtube_key = st.sidebar.text_input("YouTube API Key", type="password")
groq_key = st.sidebar.text_input("Groq API Key (Ücretsiz)", type="password")
channel_id = st.sidebar.text_input("YouTube Kanal ID")

if st.sidebar.button("Analizi Başlat"):
    if not youtube_key or not groq_key or not channel_id:
        st.error("Lütfen sol menüdeki tüm alanları doldurun!")
    else:
        try:
            # 1. YouTube API Bağlantısı (Kanal Genel)
            youtube = build('youtube', 'v3', developerKey=youtube_key)
            
            channel_req = youtube.channels().list(
                part='statistics,snippet,contentDetails',
                id=channel_id
            ).execute()

            channel = channel_req['items'][0]
            title = channel['snippet']['title']
            views = int(channel['statistics']['viewCount'])
            subscribers = int(channel['statistics']['subscriberCount'])
            videos = int(channel['statistics']['videoCount'])
            uploads_playlist_id = channel['contentDetails']['relatedPlaylists']['uploads']

            # Üst Metrik Kartları
            col1, col2, col3 = st.columns(3)
            col1.metric("Toplam İzlenme", f"{views:,}")
            col2.metric("Abone Sayısı", f"{subscribers:,}")
            col3.metric("Video Sayısı", f"{videos:,}")

            st.divider()

            # 2. Son Videoların Detaylı Verilerini Çekme
            playlist_req = youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=10
            ).execute()

            video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_req['items']]

            videos_req = youtube.videos().list(
                part='statistics,snippet',
                id=','.join(video_ids)
            ).execute()

            video_data = []
            for item in videos_req['items']:
                v_title = item['snippet']['title']
                v_views = int(item['statistics'].get('viewCount', 0))
                v_likes = int(item['statistics'].get('likeCount', 0))
                v_comments = int(item['statistics'].get('commentCount', 0))
                video_data.append({
                    "Video Başlığı": v_title[:30] + "...",
                    "İzlenme": v_views,
                    "Beğeni": v_likes,
                    "Yorum": v_comments
                })

            df = pd.DataFrame(video_data)

            # Sekmeli Arayüz
            tab1, tab2 = st.tabs(["📊 Veri & Grafikler", "🤖 AI Strateji Raporu"])

            with tab1:
                st.subheader("🎬 Son Videoların Performans Karşılaştırması")
                
                # Grafik 1: İzlenme ve Beğeni Bar Grafiği
                fig_views = px.bar(
                    df, 
                    x="Video Başlığı", 
                    y=["İzlenme", "Beğeni", "Yorum"], 
                    barmode="group",
                    title="Son 10 Videonun Etkileşim Metrikleri",
                    template="plotly_dark"
                )
                st.plotly_chart(fig_views, use_container_width=True)

                col_left, col_right = st.columns(2)
                
                with col_left:
                    # Grafik 2: Beğeni Dağılım Pasta Grafiği
                    fig_pie = px.pie(
                        df, 
                        names="Video Başlığı", 
                        values="Beğeni", 
                        title="Videoların Beğeni Payları",
                        template="plotly_dark"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col_right:
                    # Tablo Gösterimi
                    st.write("📋 **Detaylı Video Verileri**")
                    st.dataframe(df, use_container_width=True)

            with tab2:
                st.subheader("🤖 AI Stratejistinin Kanal Analizi")
                with st.spinner("AI verileri ve etkileşimleri inceliyor..."):
                    client = Groq(api_key=groq_key)
                    
                    prompt = f"""
                    Sen profesyonel bir YouTube Kripto Kanalı Stratejistisin.
                    Kanal Adı: {title}
                    Toplam İzlenme: {views} | Abone: {subscribers} | Video Sayısı: {videos}
                    Son Videoların Ortalama İzlenmesi: {df['İzlenme'].mean():.0f}
                    Son Videoların Ortalama Beğenisi: {df['Beğeni'].mean():.0f}

                    Aşağıdaki kurallara kesinlikle uyarak profesyonel Türkçe bir rapor hazırla:
                    1. Kanalın izlenme/beğeni/yorum oranlarına göre genel izleyici sadakatini değerlendir.
                    2. Kripto piyasasındaki en güncel trendlere uygun 3 yüksek potansiyelli video konusu ve tıkla-getir (clickbait olmayan) başlık öner.
                    3. İzleyici tutmayı (retention) artıracak 1 kritik altın tavsiye ver.
                    """
                    
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",
                    )

                    st.markdown(chat_completion.choices[0].message.content)

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
else:
    st.info("👈 Sol menüden API anahtarlarınızı girip 'Analizi Başlat' butonuna basın.")
