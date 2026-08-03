import streamlit as st
import streamlit.components.v1 as components
from googleapiclient.discovery import build
from groq import Groq
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import base64
import re

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
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Performans Matrisi"

def get_img_as_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

possible_files = ["bg2.jpg.jpg", "bg2.jpg", "bg.jpg"]
banner_file = next((f for f in possible_files if os.path.exists(f)), None)
img_b64 = get_img_as_base64(banner_file) if banner_file else None

def parse_iso8601_duration(duration_str):
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match:
        return 0.0
    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return round(total_seconds / 60, 1)

# 2. Gelişmiş Web3 Tasarım Mimarisi (CSS)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800&display=swap');
    
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

    /* --- BANNER --- */
    .absolute-center-banner {{
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin-top: 120px;
        margin-bottom: 25px;
    }}
    .banner-ondo-box {{
        background: rgba(17, 24, 39, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 24px;
        padding: 24px;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.7);
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        width: 75%;
        max-width: 1200px;
        position: relative;
        overflow: hidden;
        box-sizing: border-box;
    }}
    .banner-ondo-box:hover {{
        transform: translateY(-6px) scale(1.01);
        border-color: rgba(212, 175, 55, 0.7);
        box-shadow: 0 30px 70px -15px rgba(212, 175, 55, 0.35), 0 0 35px rgba(212, 175, 55, 0.25);
    }}
    .banner-ondo-box img {{
        width: 100% !important;
        height: auto !important;
        max-height: 280px !important;
        object-fit: cover !important;
        border-radius: 16px;
        display: block;
        margin: 0 auto;
    }}

    /* Üst Metrik Kartları */
    .metric-card-ondo {{
        background: rgba(17, 24, 39, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 20px;
        padding: 28px 20px;
        margin-bottom: 20px;
        box-shadow: 0 15px 35px -10px rgba(0, 0, 0, 0.5);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        min-height: 140px;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .metric-card-ondo:hover {{
        transform: translateY(-6px) scale(1.03);
        border-color: rgba(212, 175, 55, 0.7);
        box-shadow: 0 25px 60px -12px rgba(212, 175, 55, 0.4), 0 0 25px rgba(212, 175, 55, 0.25);
    }}

    .metric-title {{
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #9ca3af;
        margin-bottom: 6px;
    }}
    
    .metric-value {{
        font-size: 38px;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #ffffff 0%, #d1d5db 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }}
    
    .metric-sub {{
        font-size: 12px;
        color: #d4af37; 
        margin-top: 6px;
        font-weight: 600;
    }}

    section[data-testid="stSidebar"] {{
        background-color: #0b0f19 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }}
    
    /* Sol Panel ve Sekme Butonları */
    .stButton>button {{
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.85) 0%, rgba(170, 140, 44, 0.85) 100%); 
        color: #030712;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 9999px;
        font-weight: 700;
        padding: 12px 28px;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        width: 100%;
        box-shadow: 0 4px 20px rgba(212, 175, 55, 0.3);
    }}
    .stButton>button:hover {{
        background: linear-gradient(135deg, #f1c40f 0%, #d4af37 100%);
        box-shadow: 0 10px 30px rgba(241, 196, 15, 0.6), 0 0 20px rgba(241, 196, 15, 0.4);
        transform: translateY(-3px) scale(1.02);
        color: #030712;
    }}

    .tab-active button {{
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.95) 0%, rgba(184, 134, 11, 0.95) 100%) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        color: #030712 !important;
        font-weight: 800 !important;
        font-size: 15px !important;
        letter-spacing: 0.5px !important;
        border-radius: 9999px !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        box-shadow: 0 8px 30px rgba(212, 175, 55, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.6) !important;
        padding: 14px 24px !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}
    .tab-active button:hover {{
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 12px 40px rgba(212, 175, 55, 0.7), 0 0 25px rgba(212, 175, 55, 0.4) !important;
    }}
    
    .tab-inactive button {{
        background: rgba(17, 24, 39, 0.65) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        color: #e5e7eb !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        letter-spacing: 0.5px !important;
        border-radius: 9999px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
        padding: 14px 24px !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}
    
    .tab-inactive button:hover {{
        background: rgba(31, 41, 55, 0.85) !important;
        border-color: rgba(212, 175, 55, 0.7) !important;
        box-shadow: 0 12px 35px rgba(212, 175, 55, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
        transform: translateY(-3px) scale(1.02);
    }}
</style>
""", unsafe_allow_html=True)

# --- BANNER ---
if img_b64:
    st.markdown(f'''
    <div class="absolute-center-banner">
        <div class="banner-ondo-box">
            <img src="data:image/jpeg;base64,{img_b64}" alt="Crypto Check Banner">
        </div>
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
            with st.spinner("YouTube API üzerinden TÜM meta veriler ve istatistikler çekiliyor..."):
                youtube = build('youtube', 'v3', developerKey=st.session_state.youtube_key)
                
                ch_req = youtube.channels().list(
                    part='statistics,snippet,contentDetails,brandingSettings',
                    id=st.session_state.channel_id
                ).execute()

                channel = ch_req['items'][0]
                ch_title = channel['snippet']['title']
                total_views = int(channel['statistics']['viewCount'])
                subscribers = int(channel['statistics']['subscriberCount'])
                total_videos = int(channel['statistics']['videoCount'])
                uploads_playlist_id = channel['contentDetails']['relatedPlaylists']['uploads']

                playlist_req = youtube.playlistItems().list(
                    part='snippet,contentDetails',
                    playlistId=uploads_playlist_id,
                    maxResults=50
                ).execute()

                v_ids = [item['contentDetails']['videoId'] for item in playlist_req['items']]
                
                videos_req = youtube.videos().list(
                    part='statistics,snippet,contentDetails,status',
                    id=','.join(v_ids)
                ).execute()

                v_list = []
                for item in videos_req['items']:
                    snippet = item['snippet']
                    stats = item['statistics']
                    content = item['contentDetails']
                    status = item['status']

                    title = snippet['title']
                    published_at = snippet['publishedAt'][:10]
                    views = int(stats.get('viewCount', 0))
                    likes = int(stats.get('likeCount', 0))
                    comments = int(stats.get('commentCount', 0))
                    
                    engagement_rate = ((likes + comments) / views * 100) if views > 0 else 0
                    
                    # Süre analizi (Yerel Regex Dönüşümü)
                    duration_iso = content.get('duration', 'PT0M')
                    duration_min = parse_iso8601_duration(duration_iso)

                    definition = content.get('definition', 'sd').upper()
                    tags_count = len(snippet.get('tags', []))

                    est_sub_conv = round((subscribers / max(total_views, 1)) * 100 + (engagement_rate * 0.2), 2)
                    est_ctr = round(min(float(4.5 + (engagement_rate * 0.4)), 15.0), 2)

                    v_list.append({
                        "Video Başlığı": title,
                        "Yayın Tarihi": published_at,
                        "İzlenme": views,
                        "Beğeni": likes,
                        "Yorum": comments,
                        "Etkileşim (%)": round(engagement_rate, 2),
                        "Süre (Dk)": duration_min,
                        "Çözünürlük": definition,
                        "Etiket Sayısı": tags_count,
                        "Abone Dönüşüm (%)": est_sub_conv,
                        "Tahmini CTR (%)": est_ctr
                    })

                df = pd.DataFrame(v_list)
                avg_eng = float(df["Etkileşim (%)"].mean())
                
                st.session_state.df = df
                st.session_state.total_views = total_views
                st.session_state.subscribers = subscribers
                st.session_state.total_videos = total_videos
                st.session_state.avg_eng = avg_eng
                st.session_state.ch_title = ch_title
                st.session_state.loaded = True

        except Exception as e:
            st.error(f"Sistem Çalışma Hatası: {e}")

# Veriler yüklendiyse paneli çiz
if "loaded" in st.session_state and st.session_state.loaded:
    total_views = st.session_state.total_views
    subscribers = st.session_state.subscribers
    total_videos = st.session_state.total_videos
    avg_eng = st.session_state.avg_eng
    ch_title = st.session_state.ch_title
    df = st.session_state.df

    # Güvenlik Kontrolü
    if "Tahmini CTR (%)" not in df.columns:
        df["Tahmini CTR (%)"] = 6.5
    if "Süre (Dk)" not in df.columns:
        df["Süre (Dk)"] = 5.0
    if "Abone Dönüşüm (%)" not in df.columns:
        df["Abone Dönüşüm (%)"] = 1.2

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

    # --- SEKME BUTONLARI ---
    st.markdown("<br>", unsafe_allow_html=True)
    tab_col1, tab_col2, tab_col3 = st.columns(3)

    with tab_col1:
        css_class = "tab-active" if st.session_state.active_tab == "Performans Matrisi" else "tab-inactive"
        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.button("📊 PERFORMANS MATRİSİ", use_container_width=True):
            st.session_state.active_tab = "Performans Matrisi"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_col2:
        css_class = "tab-active" if st.session_state.active_tab == "Detaylı Analiz" else "tab-inactive"
        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.button("🔍 DETAYLI ANALİZ", use_container_width=True):
            st.session_state.active_tab = "Detaylı Analiz"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_col3:
        css_class = "tab-active" if st.session_state.active_tab == "AI Strateji Raporu" else "tab-inactive"
        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.button("🤖 AI STRATEJİ RAPORU", use_container_width=True):
            st.session_state.active_tab = "AI Strateji Raporu"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Aktif sekmeye göre içerik gösterimi
    current_tab = st.session_state.active_tab

    if current_tab == "Performans Matrisi":
        st.write("### 📈 Derinlemesine Kanal & Algoritma Matrisi")
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric(label="Ortalama Tahmini CTR", value=f"%{df['Tahmini CTR (%)'].mean():.2f}", delta="Hedef: >%6.0")
        with col_m2:
            st.metric(label="Ortalama Video Süresi", value=f"{df['Süre (Dk)'].mean():.1f} Dk", delta="Kanal Formatı")
        with col_m3:
            st.metric(label="Ortalama Abone Dönüşüm Oranı", value=f"%{df['Abone Dönüşüm (%)'].mean():.2f}", delta="Sadakat Skoru")

        st.markdown("<br>", unsafe_allow_html=True)
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.write("### İzlenme ve Video Süresi Korelasyonu")
            fig = px.scatter(
                df, 
                x="İzlenme", 
                y="Süre (Dk)", 
                size="Beğeni", 
                hover_name="Video Başlığı",
                color="Etkileşim (%)",
                color_continuous_scale=px.colors.sequential.YlOrBr,
                template="plotly_dark",
                labels={"İzlenme": "Toplam İzlenme", "Süre (Dk)": "Video Süresi (Dakika)"}
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Plus Jakarta Sans, sans-serif", color="#d1d5db")
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_right:
            st.write("### Video Çözünürlük Dağılımı")
            res_counts = df['Çözünürlük'].value_counts().reset_index()
            res_counts.columns = ['Çözünürlük', 'Adet']
            
            fig_pie = px.pie(
                res_counts, 
                names='Çözünürlük', 
                values='Adet',
                hole=0.65,
                color_discrete_sequence=['#d4af37', '#1f2937', '#374151']
            )
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=True,
                font=dict(family="Plus Jakarta Sans, sans-serif", color="#d1d5db")
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    elif current_tab == "Detaylı Analiz":
        st.write("### 🔍 Tüm Meta Verileriyle Kapsamlı Video Arşivi")
        st.dataframe(
            df,
            use_container_width=True
        )

    elif current_tab == "AI Strateji Raporu":
        st.write("### 🤖 Profesyonel Kripto & Kanal Büyüme Raporu (Ağustos 2026)")
        with st.spinner("Kanalın tüm meta verileri ve Ağustos 2026 kripto trendleri Llama 3.3 motoru ile sentezleniyor..."):
            client = Groq(api_key=st.session_state.groq_key)
            
            prompt = f"""
            Sen kurumsal düzeyde Web3, kripto varlık ve YouTube kanal büyüme stratejisi geliştiren üst düzey bir analistsin.
            Mevcut Tarih: Ağustos 2026.
            Kanal Adı: {ch_title}
            Toplam İzlenme: {total_views} | Abone Sayısı: {subscribers} | Toplam Video: {total_videos}
            Son Videoların Ortalama İzlenmesi: {df['İzlenme'].mean():.0f}
            Ortalama Etkileşim Oranı: %{df['Etkileşim (%)'].mean():.2f}
            Ortalama Video Süresi: {df['Süre (Dk)'].mean():.1f} Dakika

            Lütfen kesinlikle Türkçe olarak, profesyonel yatırım fonu raporu formatında şu başlıkları detaylıca sun:
            1. **Kanalın Kitle ve Etkileşim Sağlığı:** Mevcut meta verilerin (süreler, çözünürlükler, etkileşimler) profesyonel analizi.
            2. **Ağustos 2026 Yüksek İzlenme Getirecek 3 Trend & Coin:** (Örn: CLARITY Act regülasyonları, AI altcoinleri/TAO, RWA tokenizasyonu, Solana/Sui ekosistemi veya BTC Q4 beklentileri üzerinden nokta atışı coin ve konu önerileri).
            3. **Yüksek CTR ve İzlenme Süresi İçin Algoritma Taktikleri:** İzleyiciyi ilk 15 saniyede tutacak kanca (hook) stratejisi ve başlık önerileri.
            4. **Otomasyon & İçerik Üretim Hattı:** Bu analizleri sürekli kılmak için bir YouTube içerik üreticisinin izlemesi gereken operasyonel yol haritası.
            """
            
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
            )

            st.markdown(chat_completion.choices[0].message.content)

else:
    st.info("👈 Sol üstteki küçük oka tıklayarak kontrol panelini açabilir ve 'Canlı Verileri Getir' butonuna basabilirsiniz.")
