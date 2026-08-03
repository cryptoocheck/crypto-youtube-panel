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
    page_title="Crypto Check — Profesyonel Web3 Finans Paneli",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "youtube_key" not in st.session_state:
    st.session_state.youtube_key = ""
if "groq_key" not in st.session_state:
    st.session_state.groq_key = ""
if "channel_id" not in st.session_state:
    st.session_state.channel_id = ""

def get_img_as_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

img_path = "bg2.jpg" if os.path.exists("bg2.jpg") else "bg.jpg" if os.path.exists("bg.jpg") else "bg.jpg.jpg" if os.path.exists("bg.jpg.jpg") else "photo_6014965432080600852_y (1).jpg" if os.path.exists("photo_6014965432080600852_y (1).jpg") else ""
img_b64 = get_img_as_base64(img_path)

# 2. İşaretlediğin Alanlara Tam Oturan Profesyonel Sekme Mimarisi (CSS)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #f3f4f6;
    }}

    .stApp {{
        background-color: #030712;
        background-image: 
            radial-gradient(at 0% 0%, rgba(212, 175, 55, 0.08) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(30, 58, 138, 0.15) 0px, transparent 50%),
            radial-gradient(at 50% 100%, rgba(15, 23, 42, 1) 0px, transparent 50%);
        background-attachment: fixed;
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    .block-container {{
        padding-top: 0rem !important;
        padding-bottom: 3rem !important;
        max-width: 100% !important;
    }}

    .absolute-center-banner {{
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin-top: 15px;
        margin-bottom: 25px;
    }}
    .absolute-center-banner img {{
        width: 75% !important;
        max-width: 1200px !important;
        height: auto;
        border-radius: 20px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8), 0 0 40px rgba(212, 175, 55, 0.15);
        display: block;
    }}

    .ondo-glass-card {{
        background: rgba(17, 24, 39, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 24px;
        padding: 30px;
        margin-bottom: 24px;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.7);
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
        overflow: hidden;
    }}
    .ondo-glass-card:hover {{
        transform: translateY(-6px);
        border-color: rgba(212, 175, 55, 0.3);
        box-shadow: 0 30px 60px -20px rgba(212, 175, 55, 0.15);
    }}

    .metric-card-ondo {{
        background: rgba(17, 24, 39, 0.75);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 20px;
        padding: 26px;
        margin-bottom: 20px;
        box-shadow: 0 15px 35px -10px rgba(0, 0, 0, 0.5);
    }}

    .metric-title {{
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #9ca3af;
        margin-bottom: 10px;
    }}
    
    .metric-value {{
        font-size: 38px;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #ffffff 0%, #d1d5db 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    .metric-sub {{
        font-size: 12px;
        color: #d4af37; 
        margin-top: 8px;
        font-weight: 600;
    }}

    section[data-testid="stSidebar"] {{
        background-color: #0b0f19 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }}
    
    .stButton>button {{
        background: linear-gradient(135deg, #d4af37 0%, #aa8c2c 100%); 
        color: #030712;
        border: none;
        border-radius: 9999px;
        font-weight: 700;
        padding: 12px 28px;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 20px rgba(212, 175, 55, 0.3);
    }}
    .stButton>button:hover {{
        background: linear-gradient(135deg, #f1c40f 0%, #d4af37 100%);
        transform: translateY(-2px);
    }}

    /* --- İŞARETLEDİĞİN 3 ALANA TAM OTURAN BUTONÇUK SEKME MİMARİSİ --- */
    div[data-baseweb="tab-list"] {{
        display: grid !important;
        grid-template-columns: repeat(3, 1fr) !important;
        width: 100% !important;
        max-width: 950px !important;
        margin: 10px auto 30px auto !important;
        background-color: rgba(17, 24, 39, 0.85) !important;
        padding: 8px !important;
        border-radius: 18px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(12px) !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6) !important;
        gap: 8px !important;
    }}

    div[data-baseweb="tab"] {{
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        border-radius: 14px !important;
        color: #9ca3af !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        padding: 12px 16px !important;
        background: transparent !important;
        border: none !important;
        transition: all 0.3s ease !important;
        text-align: center !important;
    }}

    div[data-baseweb="tab"]:hover {{
        color: #ffffff !important;
        background: rgba(255, 255, 255, 0.05) !important;
    }}

    div[aria-selected="true"] {{
        background: linear-gradient(135deg, #d4af37 0%, #aa8c2c 100%) !important;
        color: #030712 !important;
        box-shadow: 0 4px 20px rgba(212, 175, 55, 0.4) !important;
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
    st.markdown("<h1 style='text-align: center; font-weight: 800; font-size: 48px; letter-spacing: -1px;'>Crypto Check</h1>", unsafe_allow_html=True)

# Sidebar (Kontrol Paneli)
st.sidebar.markdown("### 🌐 Web3 Kontrol Paneli")
st.session_state.youtube_key = st.sidebar.text_input("YouTube Data API Anahtarı", value=st.session_state.youtube_key, type="password")
st.session_state.groq_key = st.sidebar.text_input("Groq AI Anahtarı", value=st.session_state.groq_key, type="password")
st.session_state.channel_id = st.sidebar.text_input("Kanal ID", value=st.session_state.channel_id)

analyze_btn = st.sidebar.button("Canlı Verileri Getir")

if analyze_btn:
    if not st.session_state.youtube_key or not st.session_state.groq_key or not st.session_state.channel_id:
        st.error("Lütfen sol paneldeki tüm erişim anahtarlarını eksiksiz girin.")
    else:
        try:
            with st.spinner("Onchain ve YouTube verileri senkronize ediliyor..."):
                youtube = build('youtube', 'v3', developerKey=st.session_state.youtube_key)
                
                ch_req = youtube.channels().list(
                    part='statistics,snippet,contentDetails',
                    id=st.session_state.channel_id
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
            
            # Üst Metrik Kartları
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f'<div class="metric-card-ondo"><div class="metric-title">TOPLAM İZLENME</div><div class="metric-value"><span id="counter-1">0</span></div><div class="metric-sub">Canlı Veri</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="metric-card-ondo"><div class="metric-title">ABONE SAYISI</div><div class="metric-value"><span id="counter-2">0</span></div><div class="metric-sub">Aktif İzleyici</div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="metric-card-ondo"><div class="metric-title">ORTALAMA ETKİLEŞİM</div><div class="metric-value"><span id="counter-3">0.00</span></div><div class="metric-sub">Kanal Performansı</div></div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<div class="metric-card-ondo"><div class="metric-title">İÇERİK SAYISI</div><div class="metric-value"><span id="counter-4">0</span></div><div class="metric-sub">Yayınlanan Video</div></div>', unsafe_allow_html=True)

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

            # --- İŞARETLEDİĞİN 3 ALANA TAM YAYILAN SEKME MİMARİSİ ---
            t1, t2, t3 = st.tabs(["📊 Performans Matrisi", "🔍 Detaylı Analiz", "🤖 AI Strateji Raporu"])

            with t1:
                col_left, col_right = st.columns([2, 1])
                
                with col_left:
                    st.markdown('<div class="ondo-glass-card">', unsafe_allow_html=True)
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
                        font=dict(family="Plus Jakarta Sans, sans-serif", color="#d1d5db")
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                with col_right:
                    st.markdown('<div class="ondo-glass-card">', unsafe_allow_html=True)
                    st.write("### İzleyici Etkileşim Oranı")
                    avg_likes = df['Beğeni'].mean()
                    avg_comments = df['Yorum'].mean()
                    
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=['Beğeniler', 'Yorumlar'],
                        values=[avg_likes, avg_comments],
                        hole=.65,
                        marker_colors=['#d4af37', '#1f2937'] 
                    )])
                    fig_pie.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        showlegend=True,
                        font=dict(family="Plus Jakarta Sans, sans-serif", color="#d1d5db")
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            with t2:
                st.markdown('<div class="ondo-glass-card">', unsafe_allow_html=True)
                st.write("### Video Performans Kayıtları")
                st.dataframe(
                    df,
                    use_container_width=True
                )
                st.markdown('</div>', unsafe_allow_html=True)

            with t3:
                st.markdown('<div class="ondo-glass-card">', unsafe_allow_html=True)
                st.write("### 🤖 Stratejik Yönetici Özeti")
                with st.spinner("Web3 finans modelleri Llama 3.3 Motoru ile analiz ediliyor..."):
                    client = Groq(api_key=st.session_state.groq_key)
                    
                    prompt = f"""
                    Sen kurumsal düzeyde Web3 ve kripto varlık stratejisi geliştiren lider bir finansal analistsin.
                    Kanal Adı: {ch_title}
                    Toplam İzlenme: {total_views} | Abone Sayısı: {subscribers}
                    Son 15 Videonun Ortalama İzlenmesi: {df['İzlenme'].mean():.0f}
                    Ortalama Etkileşim Oranı: %{df['Etkileşim (%)'].mean():.2f}

                    Lütfen kesinlikle Türkçe olarak, üst düzey kurumsal DeFi formatında:
                    1. **Kanalın Likidite & Kitle Vektörü:** Mevcut kitle sadakatini ve etkileşim gücünü analiz et.
                    2. **3 Kurumsal İçerik Fikri:** Güncel kripto ekosistemine uygun 3 spesifik, yüksek CTR potansiyelli video konusu sun.
                    3. **Kitle Tutma Mimarisi:** İzleyici kaybını engelleyecek 1 stratejik altın kural sun.
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
