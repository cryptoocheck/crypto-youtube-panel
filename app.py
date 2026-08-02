import streamlit as st
import streamlit.components.v1 as components
from googleapiclient.discovery import build
from groq import Groq
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import base64

# 1. Streamlit Sayfa Yapılandırması
st.set_page_config(
    page_title="Crypto Check — Profesyonel Analiz Paneli",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def get_img_as_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

img_path = "bg2.jpg" if os.path.exists("bg2.jpg") else "bg.jpg" if os.path.exists("bg.jpg") else "bg.jpg.jpg" if os.path.exists("bg.jpg.jpg") else "photo_6014965432080600852_y (1).jpg" if os.path.exists("photo_6014965432080600852_y (1).jpg") else ""
img_b64 = get_img_as_base64(img_path)

# 2. Apple Tipografi ve 3D Kart Mimarisi (CSS)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif;
        color: #f5f5f7;
        letter-spacing: -0.01em;
    }}

    .stApp {{
        background-color: #000000;
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    .block-container {{
        padding-top: 0rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }}

    .absolute-center-banner {{
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin-top: 10px;
        margin-bottom: 15px;
    }}
    .absolute-center-banner img {{
        width: 75% !important;
        max-width: 1200px !important;
        height: auto;
        border-radius: 16px;
        display: block;
    }}

    .apple-card-3d {{
        background: linear-gradient(145deg, #121214, #1b1b1e);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 22px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 16px 48px 0 rgba(0, 0, 0, 0.7), inset 0 1px 0 0 rgba(255, 255, 255, 0.12);
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
    }}
    .apple-card-3d:hover {{
        transform: translateY(-5px);
        box-shadow: 0 24px 60px 0 rgba(0, 0, 0, 0.85), inset 0 1px 0 0 rgba(255, 255, 255, 0.2);
        border-color: rgba(212, 175, 55, 0.3);
    }}

    .metric-card-apple {{
        background: linear-gradient(145deg, #161618, #1c1c1e);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 26px;
        margin-bottom: 20px;
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.6), inset 0 1px 0 0 rgba(255, 255, 255, 0.1);
    }}

    .metric-title {{
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #86868b;
        margin-bottom: 8px;
    }}
    
    .metric-value {{
        font-size: 38px;
        font-weight: 700;
        letter-spacing: -0.02em;
        background: linear-gradient(180deg, #ffffff 0%, #a1a1a6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    .metric-sub {{
        font-size: 12px;
        color: #d4af37; 
        margin-top: 6px;
        font-weight: 500;
    }}

    section[data-testid="stSidebar"] {{
        background-color: #09090b !important;
        border-right: 1px solid #27272a;
    }}
    
    .stButton>button {{
        background: #d4af37; 
        color: #000000;
        border: none;
        border-radius: 980px;
        font-weight: 600;
        padding: 10px 24px;
        transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
        width: 100%;
    }}
    .stButton>button:hover {{
        background: #f1c40f;
        box-shadow: 0 0 20px rgba(241, 196, 15, 0.5);
        color: #000000;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: #1c1c1e;
        padding: 6px;
        border-radius: 980px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 980px;
        color: #86868b;
        font-weight: 500;
        padding: 8px 20px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: #d4af37 !important;
        color: #000000 !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- BANNER ---
if img_b64:
    st.markdown(f'''
    <div class="absolute-center-banner">
        <img src="data:image/jpeg;base64,{img_b64}" alt="Crypto Check Logo">
    </div>
    ''', unsafe_allow_html=True)
else:
    st.markdown("<h1 style='text-align: center; font-weight: 700; font-size: 48px;'>Crypto Check</h1>", unsafe_allow_html=True)

# Sidebar (Kontrol Paneli)
st.sidebar.markdown("### ⚙️ Kontrol Paneli")
youtube_key = st.sidebar.text_input("YouTube Data API Anahtarı", type="password")
groq_key = st.sidebar.text_input("Groq AI Anahtarı", type="password")
channel_id = st.sidebar.text_input("Kanal ID")

analyze_btn = st.sidebar.button("Canlı Verileri Getir")

if analyze_btn:
    if not youtube_key or not groq_key or not channel_id:
        st.error("Lütfen sol paneldeki tüm erişim anahtarlarını eksiksiz girin.")
    else:
        try:
            with st.spinner("YouTube sunucularından canlı veriler yükleniyor..."):
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
                avg_eng = float(df["Etkileşim (%)"].mean())
            
            # Üst Metrik Kartları ve 2 Saniyelik Sayaç Motoru (Bileşen Entegrasyonu)
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f'<div class="metric-card-apple"><div class="metric-title">TOPLAM İZLENME</div><div class="metric-value"><span id="counter-1">0</span></div><div class="metric-sub">Canlı Veri</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="metric-card-apple"><div class="metric-title">ABONE SAYISI</div><div class="metric-value"><span id="counter-2">0</span></div><div class="metric-sub">Aktif İzleyici</div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="metric-card-apple"><div class="metric-title">ORTALAMA ETKİLEŞİM</div><div class="metric-value"><span id="counter-3">0.00</span></div><div class="metric-sub">Kanal Performansı</div></div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<div class="metric-card-apple"><div class="metric-title">İÇERİK SAYISI</div><div class="metric-value"><span id="counter-4">0</span></div><div class="metric-sub">Yayınlanan Video</div></div>', unsafe_allow_html=True)

            # Sayaç animasyonunu çalıştıran güvenli JavaScript bileşeni
            components.html(f"""
            <script>
            function runCounter(id, target, isFloat) {{
                const el = window.parent.document.getElementById(id);
                if (!el) return;
                const duration = 2000;
                let startTime = null;

                function update(currentTime) {{
                    if (!startTime) startTime = currentTime;
                    const progress = currentTime - startTime;
                    const percentage = Math.min(progress / duration, 1);
                    const ease = percentage === 1 ? 1 : 1 - Math.pow(2, -10 * percentage);
                    const currentVal = target * ease;

                    if (isFloat) {{
                        el.innerText = '%' + currentVal.toFixed(2);
                    }} else {{
                        el.innerText = Math.floor(currentVal).toLocaleString('en-US');
                    }}

                    if (percentage < 1) {{
                        requestAnimationFrame(update);
                    }} else {{
                        if (isFloat) {{
                            el.innerText = '%' + target.toFixed(2);
                        }} else {{
                            el.innerText = target.toLocaleString('en-US');
                        }}
                    }}
                }}
                requestAnimationFrame(update);
            }}

            runCounter('counter-1', {total_views}, false);
            runCounter('counter-2', {subscribers}, false);
            runCounter('counter-3', {avg_eng}, true);
            runCounter('counter-4', {total_videos}, false);
            </script>
            """, height=0)

            # Sekmeli Panel Yapısı
            t1, t2, t3 = st.tabs(["📊 Performans Matrisi", "🔍 Detaylı Analiz", "🤖 AI Strateji Raporu"])

            with t1:
                col_left, col_right = st.columns([2, 1])
                
                with col_left:
                    st.markdown('<div class="apple-card-3d">', unsafe_allow_html=True)
                    st.write("### İzlenme ve Etkileşim Dağılımı")
                    fig = px.scatter(
                        df, 
                        x="İzlenme", 
                        y="Etkileşim (%)", 
                        size="Beğeni", 
                        hover_name="Video Başlığı",
                        color="Etkileşim (%)",
                        color_continuous_scale=px.colors.sequential.YlOrBr,
                        template="plotly_dark",
                        labels={"İzlenme": "İzlenme Sayısı", "Etkileşim (%)": "Etkileşim Oranı (%)"}
                    )
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="SF Pro Display, -apple-system", color="#d1d1d6")
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                with col_right:
                    st.markdown('<div class="apple-card-3d">', unsafe_allow_html=True)
                    st.write("### İzleyici Etkileşim Oranı")
                    avg_likes = df['Beğeni'].mean()
                    avg_comments = df['Yorum'].mean()
                    
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=['Beğeniler', 'Yorumlar'],
                        values=[avg_likes, avg_comments],
                        hole=.6,
                        marker_colors=['#d4af37', '#48484a'] 
                    )])
                    fig_pie.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        showlegend=True,
                        font=dict(family="SF Pro Display, -apple-system", color="#d1d1d6")
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            with t2:
                st.markdown('<div class="apple-card-3d">', unsafe_allow_html=True)
                st.write("### Video Performans Kayıtları")
                st.dataframe(
                    df,
                    use_container_width=True
                )
                st.markdown('</div>', unsafe_allow_html=True)

            with t3:
                st.markdown('<div class="apple-card-3d">', unsafe_allow_html=True)
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
    st.info("👈 Sol üstteki küçük oka tıklayarak kontrol panelini açabilir ve 'Canlı Verileri Getir' butonuna basabilirsiniz.")
