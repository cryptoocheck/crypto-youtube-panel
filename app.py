import streamlit as st
from googleapiclient.discovery import build
from groq import Groq
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Streamlit Sayfa Yapılandırması
st.set_page_config(
    page_title="Crypto Check — Profesyonel Analiz Paneli",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Apple Tasarım Sistemi (Custom CSS)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: #000000;
        color: #f5f5f7;
    }
    
    .stApp {
        background: radial-gradient(circle at 50% -20%, #1a1a2e 0%, #000000 80%);
    }

    .apple-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    .metric-title {
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #86868b;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 34px;
        font-weight: 700;
        letter-spacing: -0.5px;
        background: linear-gradient(180deg, #ffffff 0%, #a1a1a6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-sub {
        font-size: 12px;
        color: #2997ff;
        margin-top: 4px;
        font-weight: 500;
    }

    section[data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.6);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .stButton>button {
        background: #0071e3;
        color: #ffffff;
        border: none;
        border-radius: 980px;
        font-weight: 500;
        padding: 10px 24px;
        transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
        width: 100%;
    }
    .stButton>button:hover {
        background: #0077ed;
        box-shadow: 0 0 18px rgba(0, 113, 227, 0.5);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(255, 255, 255, 0.03);
        padding: 6px;
        border-radius: 980px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 980px;
        color: #86868b;
        font-weight: 500;
        padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1d1d1f !important;
        color: #f5f5f7 !important;
    }
</style>
""", unsafe_allow_html=True)

# Başlık
st.markdown("<h1 style='text-align: center; font-weight: 700; font-size: 48px; letter-spacing: -1px; margin-bottom: 0px;'>Crypto Check</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #86868b; font-size: 19px; font-weight: 400; margin-bottom: 40px;'>Yapay Zeka Destekli Kanal Analiz Stüdyosu</p>", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("### ⚙️ Kontrol Paneli")
youtube_key = st.sidebar.text_input("YouTube Data API Anahtarı", type="password")
groq_key = st.sidebar.text_input("Groq AI Anahtarı", type="password")
channel_id = st.sidebar.text_input("Kanal ID")

analyze_btn = st.sidebar.button("Analiz Motorunu Çalıştır")

if analyze_btn:
    if not youtube_key or not groq_key or not channel_id:
        st.error("Lütfen sol paneldeki tüm erişim anahtarlarını eksiksiz girin.")
    else:
        try:
            # 1. API Veri Çekimi
            youtube = build('youtube', 'v3', developerKey=youtube_key)
            
            ch_req = youtube.channels().list(
                part='statistics,snippet,contentDetails',
                id=channel_id
            ).execute()

            channel = ch_req['items'][0]
            ch_title = channel['snippet']['title']
            total_views = int(channel['statistics']['viewCount'])
            subscribers = int(channel['statistics']['subscriberCount'])
            total_videos = int(channel['statistics']['videoCount'])
            uploads_playlist_id = channel['contentDetails']['relatedPlaylists']['uploads']

            # Son 15 Videonun Detay Verileri
            playlist_req = youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=15
            ).execute()

            v_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_req['items']]
            
            videos_req = youtube.videos().list(
                part='statistics,snippet,contentDetails',
                id=','.join(v_ids)
            ).execute()

            v_list = []
            for item in videos_req['items']:
                title = item['snippet']['title']
                views = int(item['statistics'].get('viewCount', 0))
                likes = int(item['statistics'].get('likeCount', 0))
                comments = int(item['statistics'].get('commentCount', 0))
                
                engagement_rate = ((likes + comments) / views * 100) if views > 0 else 0
                
                v_list.append({
                    "Video Başlığı": title,
                    "İzlenme": views,
                    "Beğeni": likes,
                    "Yorum": comments,
                    "Etkileşim (%)": round(engagement_rate, 2)
                })

            df = pd.DataFrame(v_list)
            
            # Üst Metrik Kartları
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f'<div class="apple-card"><div class="metric-title">TOPLAM İZLENME</div><div class="metric-value">{total_views:,}</div><div class="metric-sub">Tüm Zamanlar</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="apple-card"><div class="metric-title">ABONE SAYISI</div><div class="metric-value">{subscribers:,}</div><div class="metric-sub">Aktif İzleyici</div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="apple-card"><div class="metric-title">ORTALAMA ETKİLEŞİM</div><div class="metric-value">%{df["Etkileşim (%)"].mean():.2f}</div><div class="metric-sub">Kanal Performansı</div></div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<div class="apple-card"><div class="metric-title">İÇERİK SAYISI</div><div class="metric-value">{total_videos}</div><div class="metric-sub">Yayınlanan Video</div></div>', unsafe_allow_html=True)

            # Sekmeli Panel Yapısı
            t1, t2, t3 = st.tabs(["📊 Performans Matrisi", "🔍 Detaylı Analiz", "🤖 AI Strateji Raporu"])

            with t1:
                col_left, col_right = st.columns([2, 1])
                
                with col_left:
                    st.markdown('<div class="apple-card">', unsafe_allow_html=True)
                    st.write("### İzlenme ve Etkileşim Dağılımı")
                    fig = px.scatter(
                        df, 
                        x="İzlenme", 
                        y="Etkileşim (%)", 
                        size="Beğeni", 
                        hover_name="Video Başlığı",
                        color="Etkileşim (%)",
                        color_continuous_scale=px.colors.sequential.Bluered,
                        template="plotly_dark",
                        labels={"İzlenme": "İzlenme Sayısı", "Etkileşim (%)": "Etkileşim Oranı (%)"}
                    )
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="SF Pro Display", color="#86868b")
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                with col_right:
                    st.markdown('<div class="apple-card">', unsafe_allow_html=True)
                    st.write("### İzleyici Etkileşim Oranı")
                    avg_likes = df['Beğeni'].mean()
                    avg_comments = df['Yorum'].mean()
                    
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=['Beğeniler', 'Yorumlar'],
                        values=[avg_likes, avg_comments],
                        hole=.6,
                        marker_colors=['#2997ff', '#30d158']
                    )])
                    fig_pie.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        showlegend=True,
                        font=dict(family="SF Pro Display", color="#86868b")
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            with t2:
                st.markdown('<div class="apple-card">', unsafe_allow_html=True)
                st.write("### Video Performans Kayıtları")
                st.dataframe(
                    df,
                    use_container_width=True
                )
                st.markdown('</div>', unsafe_allow_html=True)

            with t3:
                st.markdown('<div class="apple-card">', unsafe_allow_html=True)
                st.write("### 🤖 Stratejik Yönetici Özeti")
                with st.spinner("Kanal modelleri Llama 3.3 Motoru ile analiz ediliyor..."):
                    client = Groq(api_key=groq_key)
                    
                    prompt = f"""
                    Sen Apple seviyesinde ürün ve içerik stratejisi geliştiren lider bir YouTube Kripto Kanalı Danışmanısın.
                    Kanal Adı: {ch_title}
                    Toplam İzlenme: {total_views} | Abone Sayısı: {subscribers}
                    Son 15 Videonun Ortalama İzlenmesi: {df['İzlenme'].mean():.0f}
                    Ortalama Etkileşim Oranı: %{df['Etkileşim (%)'].mean():.2f}

                    Lütfen kesinlikle Türkçe olarak, üst düzey yönetici formatında (Apple Tarzı Minimalist ve Derin):
                    1. **Kanalın Büyüme Vektörü:** Mevcut kitle sadakatini ve etkileşim gücünü analiz et.
                    2. **3 Fark Yaratan İçerik Fikri:** Güncel kripto ekosistemine uygun 3 spesifik, yüksek tıklama (CTR) potansiyelli video konusu ve başlık yapısı sun.
                    3. **Kitle Tutma Mimarisi:** Tıklama sonrası izleyici kaybını engelleyecek 1 stratejik altın kural sun.
                    """
                    
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",
                    )

                    st.markdown(chat_completion.choices[0].message.content)
                st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Sistem Çalışma Hatası: {e}")
else:
    st.info("👈 Analiz motorunu başlatmak için sol taraftaki kontrol panelinden erişim anahtarlarınızı girin.")
