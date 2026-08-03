import streamlit as st
import streamlit.components.v1 as components
from googleapiclient.discovery import build
from groq import Groq
import pandas as pd
import os
import base64
import re
from datetime import datetime, timedelta

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

def parse_iso8601_duration_seconds(duration_str):
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match:
        return 0
    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0
    return hours * 3600 + minutes * 60 + seconds

# 2. Tasarım Mimarisi (CSS)
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

    /* --- ÇOK YAVAŞ, AĞIR VE AKICI İKİ YÖNLÜ GEÇİŞ --- */
    .reveal-box {{
        opacity: 0;
        transform: translateX(-150px);
        transition: opacity 1.8s cubic-bezier(0.25, 1, 0.5, 1), transform 1.8s cubic-bezier(0.25, 1, 0.5, 1);
        will-change: opacity, transform;
    }}

    .reveal-box.active {{
        opacity: 1;
        transform: translateX(0);
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

    /* --- KUTULAR VE MERKEZLEME --- */
    .metric-card-ondo, .ondo-glass-card {{
        background: rgba(17, 24, 39, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
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
        transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.3s ease, box-shadow 0.3s ease;
    }}
    .metric-card-ondo:hover, .ondo-glass-card:hover {{
        transform: translateY(-6px) scale(1.01);
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
        text-align: center;
        width: 100%;
    }}
    
    .metric-value {{
        font-size: 38px;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #ffffff 0%, #d1d5db 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
        text-align: center;
        width: 100%;
    }}
    
    .metric-sub {{
        font-size: 12px;
        color: #d4af37; 
        margin-top: 6px;
        font-weight: 600;
        text-align: center;
        width: 100%;
    }}

    /* Tablo Cam Efekti */
    .stDataFrame {{
        background: rgba(17, 24, 39, 0.75) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 20px !important;
        padding: 15px !important;
        box-shadow: 0 15px 35px -10px rgba(0, 0, 0, 0.5) !important;
        transition: transform 0.3s ease, border-color 0.3s ease !important;
    }}
    .stDataFrame:hover {{
        transform: translateY(-4px) scale(1.005);
        border-color: rgba(212, 175, 55, 0.7) !important;
        box-shadow: 0 25px 60px -12px rgba(212, 175, 55, 0.3), 0 0 25px rgba(212, 175, 55, 0.2) !important;
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
        color: #030712 !important;
        font-weight: 800 !important;
        font-size: 15px !important;
        border-radius: 9999px !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        box-shadow: 0 8px 30px rgba(212, 175, 55, 0.5) !important;
        padding: 14px 24px !important;
    }}
    .tab-inactive button {{
        background: rgba(17, 24, 39, 0.65) !important;
        backdrop-filter: blur(16px) !important;
        color: #e5e7eb !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        border-radius: 9999px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        padding: 14px 24px !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- ÇİFT YÖNLÜ İPEKSİ SÜZÜLME JS ---
components.html("""
<script>
function initDualWayReveal() {
    const observerOptions = {
        root: null,
        rootMargin: '0px 0px -50px 0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            } else {
                entry.target.classList.remove('active');
            }
        });
    }, observerOptions);

    const boxes = window.parent.document.querySelectorAll('.reveal-box');
    boxes.forEach(box => observer.observe(box));
}

setTimeout(initDualWayReveal, 500);
setInterval(initDualWayReveal, 1000);
</script>
""", height=0)

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
            with st.spinner("YouTube API üzerinden tüm veriler ve özel abone takibi yapılıyor..."):
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

                # --- KENDİ ABONE TAKİP SİSTEMİMİZ (LOKAL DOSYA) ---
                tracker_file = "subs_tracker.csv"
                try:
                    if os.path.exists(tracker_file):
                        tracker_df = pd.read_csv(tracker_file)
                        if not tracker_df.empty:
                            # Önceki kayıtlı abone sayısını al
                            last_recorded_subs = int(tracker_df.iloc[-1]['Subscribers'])
                        else:
                            last_recorded_subs = subscribers
                    else:
                        tracker_df = pd.DataFrame(columns=["Date", "Subscribers"])
                        last_recorded_subs = subscribers
                        
                    subs_diff = subscribers - last_recorded_subs
                    
                    # Güncel veriyi dosyaya kaydet
                    today_str = datetime.utcnow().strftime("%Y-%m-%d")
                    if not tracker_df.empty and tracker_df.iloc[-1]['Date'] == today_str:
                        tracker_df.loc[tracker_df.index[-1], 'Subscribers'] = subscribers
                    else:
                        new_row = pd.DataFrame([{"Date": today_str, "Subscribers": subscribers}])
                        tracker_df = pd.concat([tracker_df, new_row], ignore_index=True)
                        
                    tracker_df.to_csv(tracker_file, index=False)
                    st.session_state.subs_diff = subs_diff

                except Exception as e:
                    st.session_state.subs_diff = 0

                # Videoları Çekme
                v_ids = []
                next_page_token = None
                while True:
                    playlist_req = youtube.playlistItems().list(
                        part='snippet,contentDetails',
                        playlistId=uploads_playlist_id,
                        maxResults=50,
                        pageToken=next_page_token
                    ).execute()

                    for item in playlist_req.get('items', []):
                        v_ids.append(item['contentDetails']['videoId'])

                    next_page_token = playlist_req.get('nextPageToken')
                    if not next_page_token:
                        break

                v_list = []
                comment_list = []
                now = datetime.utcnow()
                cutoff_28d = now - timedelta(days=28)
                cutoff_56d = now - timedelta(days=56)

                views_last_28d = 0
                views_prev_28d = 0
                likes_last_28d = 0
                likes_prev_28d = 0
                total_duration_sec = 0

                for i in range(0, len(v_ids), 50):
                    chunk_ids = v_ids[i:i+50]
                    videos_req = youtube.videos().list(
                        part='statistics,snippet,contentDetails,status',
                        id=','.join(chunk_ids)
                    ).execute()

                    for item in videos_req.get('items', []):
                        snippet = item['snippet']
                        stats = item['statistics']
                        content = item['contentDetails']

                        v_id = item['id']
                        title = snippet['title']
                        published_str = snippet['publishedAt']
                        published_dt = datetime.strptime(published_str[:19], "%Y-%m-%dT%H:%M:%S")
                        
                        views = int(stats.get('viewCount', 0))
                        likes = int(stats.get('likeCount', 0))
                        comments_count = int(stats.get('commentCount', 0))
                        
                        duration_iso = content.get('duration', 'PT0M')
                        duration_sec = parse_iso8601_duration_seconds(duration_iso)
                        duration_min = round(duration_sec / 60, 2)

                        total_duration_sec += duration_sec

                        if published_dt >= cutoff_28d:
                            views_last_28d += views
                            likes_last_28d += likes
                        elif cutoff_56d <= published_dt < cutoff_28d:
                            views_prev_28d += views
                            likes_prev_28d += likes

                        content_type = "Shorts" if duration_sec <= 60 else "Büyük Video"

                        delta = now - published_dt
                        if delta.days <= 1:
                            time_frame = "Günlük"
                        elif delta.days <= 7:
                            time_frame = "Haftalık"
                        elif delta.days <= 30:
                            time_frame = "Aylık"
                        else:
                            time_frame = "Arşiv"

                        v_list.append({
                            "Video Başlığı": title,
                            "Yayın Tarihi": published_str[:10],
                            "Tür": content_type,
                            "Periyot": time_frame,
                            "İzlenme": views,
                            "Beğeni": likes,
                            "Yorum Sayısı": comments_count,
                            "Süre (Dk)": duration_min
                        })

                        # Yorumları çek
                        if comments_count > 0:
                            try:
                                c_next_token = None
                                while True:
                                    c_req = youtube.commentThreads().list(
                                        part='snippet',
                                        videoId=v_id,
                                        maxResults=100,
                                        pageToken=c_next_token
                                    ).execute()

                                    for thread in c_req.get('items', []):
                                        c_snippet = thread['snippet']['topLevelComment']['snippet']
                                        author = c_snippet['authorDisplayName']
                                        text = c_snippet['textDisplay']
                                        c_date = c_snippet['publishedAt'][:10]
                                        total_replies = thread['snippet']['totalReplyCount']
                                        
                                        status = "Cevaplanan" if total_replies > 0 else "Cevap Bekliyor"

                                        comment_list.append({
                                            "Video": title,
                                            "Yazar": author,
                                            "Yorum": text,
                                            "Tarih": c_date,
                                            "Durum": status
                                        })

                                    c_next_token = c_req.get('nextPageToken')
                                    if not c_next_token:
                                        break
                            except Exception:
                                pass

                df = pd.DataFrame(v_list)
                df_comments = pd.DataFrame(comment_list) if comment_list else pd.DataFrame(columns=["Video", "Yazar", "Yorum", "Tarih", "Durum"])
                
                avg_eng = float(((df['Beğeni'] + df['Yorum Sayısı']).sum() / max(df['İzlenme'].sum(), 1)) * 100)
                
                st.session_state.df = df
                st.session_state.df_comments = df_comments
                st.session_state.total_views = total_views
                st.session_state.subscribers = subscribers
                st.session_state.total_videos = total_videos
                st.session_state.avg_eng = avg_eng
                st.session_state.ch_title = ch_title
                st.session_state.total_duration_sec = total_duration_sec
                st.session_state.views_last_28d = views_last_28d
                st.session_state.views_prev_28d = views_prev_28d
                st.session_state.likes_last_28d = likes_last_28d
                st.session_state.likes_prev_28d = likes_prev_28d
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
    df_comments = st.session_state.get("df_comments", pd.DataFrame())
    total_duration_sec = st.session_state.get("total_duration_sec", 0)
    total_watch_hours = round(total_duration_sec / 3600, 1)

    views_last_28d = st.session_state.get("views_last_28d", 0)
    views_prev_28d = st.session_state.get("views_prev_28d", 0)
    likes_last_28d = st.session_state.get("likes_last_28d", 0)
    likes_prev_28d = st.session_state.get("likes_prev_28d", 0)
    
    # Kendi Veritabanımızdan Gelen Abone Farkı
    subs_diff = st.session_state.get("subs_diff", 0)

    if subs_diff > 0:
        subs_arrow = '<span style="color:#10b981;">🟢 ↗</span>'
        subs_diff_str = f'<span style="color:#10b981; font-weight:bold;">+{subs_diff:,}</span>'
    elif subs_diff < 0:
        subs_arrow = '<span style="color:#ef4444;">🔴 ↘</span>'
        subs_diff_str = f'<span style="color:#ef4444; font-weight:bold;">{subs_diff:,}</span>'
    else:
        subs_arrow = '➖'
        subs_diff_str = "Değişim Yok"

    # Güvenlik Kontrolü
    if "Tür" not in df.columns:
        df["Tür"] = "Büyük Video"
    if "Periyot" not in df.columns:
        df["Periyot"] = "Arşiv"
    if "Süre (Dk)" not in df.columns:
        df["Süre (Dk)"] = 5.0

    # Üst Metrik Kartları (4'lü)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card-ondo reveal-box"><div class="metric-title">TOPLAM İZLENME</div><div class="metric-value"><span id="counter-1">0</span></div><div class="metric-sub">Tüm Zamanlar</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card-ondo reveal-box"><div class="metric-title">TOPLAM ABONE</div><div class="metric-value"><span id="counter-2">0</span></div><div class="metric-sub">Kanal Geneli</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card-ondo reveal-box"><div class="metric-title">ORTALAMA ETKİLEŞİM</div><div class="metric-value"><span id="counter-3">0.00</span></div><div class="metric-sub">Genel Performans</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card-ondo reveal-box"><div class="metric-title">TOPLAM İÇERİK</div><div class="metric-value"><span id="counter-4">0</span></div><div class="metric-sub">Yayınlanan Video</div></div>', unsafe_allow_html=True)

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

    # --- 4'LÜ SEKME BUTONLARI ---
    st.markdown("<br>", unsafe_allow_html=True)
    tab_col1, tab_col2, tab_col3, tab_col4 = st.columns(4)

    with tab_col1:
        css_class = "tab-active" if st.session_state.active_tab == "Performans Matrisi" else "tab-inactive"
        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.button("📊 PERFORMANS MATRİSİ", use_container_width=True):
            st.session_state.active_tab = "Performans Matrisi"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_col2:
        css_class = "tab-active" if st.session_state.active_tab == "Gelen Yorumlar" else "tab-inactive"
        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.button("💬 GELEN YORUMLAR", use_container_width=True):
            st.session_state.active_tab = "Gelen Yorumlar"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_col3:
        css_class = "tab-active" if st.session_state.active_tab == "Detaylı Analiz" else "tab-inactive"
        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.button("🔍 DETAYLI ANALİZ", use_container_width=True):
            st.session_state.active_tab = "Detaylı Analiz"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_col4:
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
        # --- 1. GENEL BAKIŞ BÖLÜMÜ ---
        st.markdown('<div class="reveal-box">', unsafe_allow_html=True)
        st.write("### 🌐 GENEL BAKIŞ")
        st.markdown('</div>', unsafe_allow_html=True)

        gb1, gb2, gb3 = st.columns(3)
        with gb1:
            st.markdown(f'''
            <div class="metric-card-ondo reveal-box" style="min-height: 110px; padding: 18px;">
                <div class="metric-title">GÖRÜNTÜLEME</div>
                <div class="metric-value" style="font-size: 26px;">{total_views:,}</div>
                <div class="metric-sub">Tüm Zamanlar</div>
            </div>
            ''', unsafe_allow_html=True)
        with gb2:
            st.markdown(f'''
            <div class="metric-card-ondo reveal-box" style="min-height: 110px; padding: 18px;">
                <div class="metric-title">TAHMİNİ İZLENME SÜRESİ (SAAT)</div>
                <div class="metric-value" style="font-size: 26px;">{total_watch_hours:,}</div>
                <div class="metric-sub">Hesaplanan Toplam Süre</div>
            </div>
            ''', unsafe_allow_html=True)
        with gb3:
            st.markdown(f'''
            <div class="metric-card-ondo reveal-box" style="min-height: 110px; padding: 18px;">
                <div class="metric-title">GÜNCEL ABONE SAYISI</div>
                <div class="metric-value" style="font-size: 26px;">{subscribers:,}</div>
                <div class="metric-sub">Kanal Toplamı</div>
            </div>
            ''', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- 2. GERÇEK İÇERİK DİNAMİKLERİ ---
        st.markdown('<div class="reveal-box">', unsafe_allow_html=True)
        st.write("### 📈 İÇERİK (Önceki 28 Güne Kıyasla & Özel Takip)")
        st.markdown('</div>', unsafe_allow_html=True)

        inc1, inc2, inc3 = st.columns(3)
        with inc1:
            st.markdown(f'''
            <div class="metric-card-ondo reveal-box" style="min-height: 110px; padding: 18px;">
                <div class="metric-title">AKTİF İZLENME (SON 28 GÜN)</div>
                <div class="metric-value" style="font-size: 26px;">{views_last_28d:,}</div>
                <div class="metric-sub">Önceki 28 Gün: {views_prev_28d:,}</div>
            </div>
            ''', unsafe_allow_html=True)
        with inc2:
            st.markdown(f'''
            <div class="metric-card-ondo reveal-box" style="min-height: 110px; padding: 18px;">
                <div class="metric-title">BEĞENİ SAYISI (SON 28 GÜN)</div>
                <div class="metric-value" style="font-size: 26px;">{likes_last_28d:,}</div>
                <div class="metric-sub">Önceki 28 Gün: {likes_prev_28d:,}</div>
            </div>
            ''', unsafe_allow_html=True)
        with inc3:
            st.markdown(f'''
            <div class="metric-card-ondo reveal-box" style="min-height: 110px; padding: 18px;">
                <div class="metric-title">ABONE TAKİBİ (SİSTEM)</div>
                <div class="metric-value" style="font-size: 26px;">{subscribers:,}</div>
                <div class="metric-sub">Son Kayda Göre: {subs_arrow} {subs_diff_str}</div>
            </div>
            ''', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="reveal-box">', unsafe_allow_html=True)
        st.write("### ⚡ Shorts ve Büyük Video Karşılaştırmalı Periyot Analizi")
        st.markdown('</div>', unsafe_allow_html=True)
        
        shorts_df = df[df["Tür"] == "Shorts"]
        long_df = df[df["Tür"] == "Büyük Video"]

        st.markdown('<div class="reveal-box">', unsafe_allow_html=True)
        st.markdown("#### 📱 Shorts (Dikey) İçerik Performansı")
        st.markdown('</div>', unsafe_allow_html=True)

        s_c1, s_c2, s_c3 = st.columns(3)
        for periyot, col in zip(["Günlük", "Haftalık", "Aylık"], [s_c1, s_c2, s_c3]):
            p_data = shorts_df[shorts_df["Periyot"] == periyot]
            p_views = p_data["İzlenme"].sum()
            p_likes = p_data["Beğeni"].sum()
            p_time = p_data["Süre (Dk)"].sum()
            with col:
                st.markdown(f'''
                <div class="metric-card-ondo reveal-box" style="min-height: 120px; padding: 18px;">
                    <div class="metric-title">SHORTS ({periyot.upper()})</div>
                    <div class="metric-value" style="font-size: 28px;">{p_views:,}</div>
                    <div class="metric-sub">{p_likes} Beğeni | {p_time:.1f} Dk</div>
                </div>
                ''', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="reveal-box">', unsafe_allow_html=True)
        st.markdown("#### 🖥️ Büyük Video (Long-form) İçerik Performansı")
        st.markdown('</div>', unsafe_allow_html=True)

        l_c1, l_c2, l_c3 = st.columns(3)
        for periyot, col in zip(["Günlük", "Haftalık", "Aylık"], [l_c1, l_c2, l_c3]):
            p_data = long_df[long_df["Periyot"] == periyot]
            p_views = p_data["İzlenme"].sum()
            p_likes = p_data["Beğeni"].sum()
            p_time = p_data["Süre (Dk)"].sum()
            with col:
                st.markdown(f'''
                <div class="metric-card-ondo reveal-box" style="min-height: 120px; padding: 18px;">
                    <div class="metric-title">BÜYÜK VİDEO ({periyot.upper()})</div>
                    <div class="metric-value" style="font-size: 28px;">{p_views:,}</div>
                    <div class="metric-sub">{p_likes} Beğeni | {p_time:.1f} Dk</div>
                </div>
                ''', unsafe_allow_html=True)

    elif current_tab == "Gelen Yorumlar":
        st.markdown('<div class="ondo-glass-card reveal-box">', unsafe_allow_html=True)
        st.write("### 💬 YouTube Kanalı Geçmişe Dayalı Canlı Yorum Yönetim Merkezi")
        
        if not df_comments.empty:
            df_answered = df_comments[df_comments["Durum"] == "Cevaplanan"]
            df_pending = df_comments[df_comments["Durum"] == "Cevap Bekliyor"]

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### ⏳ Cevaplanmayı Bekleyen Yorumlar")
            if not df_pending.empty:
                st.dataframe(df_pending, use_container_width=True)
            else:
                st.success("Tebrikler! Cevap bekleyen hiç yorumunuz kalmamış.")

            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("#### ✅ Cevaplanan Yorumlar")
            if not df_answered.empty:
                st.dataframe(df_answered, use_container_width=True)
            else:
                st.info("Henüz yanıtlanmış bir yorum bulunmuyor.")
        else:
            st.info("Kanal videolarınızda henüz taranabilir yorum bulunamadı veya canlı veriler yüklenmedi.")
        st.markdown('</div>', unsafe_allow_html=True)

    elif current_tab == "Detaylı Analiz":
        st.markdown('<div class="ondo-glass-card reveal-box">', unsafe_allow_html=True)
        st.write("### 🔍 Tüm İçeriklerin Tür ve Periyot Arşivi")
        df_show = df[["Video Başlığı", "Yayın Tarihi", "Tür", "Periyot", "İzlenme", "Beğeni", "Yorum Sayısı", "Süre (Dk)"]]
        st.dataframe(df_show, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    elif current_tab == "AI Strateji Raporu":
        st.markdown('<div class="ondo-glass-card reveal-box">', unsafe_allow_html=True)
        st.write("### 🤖 Profesyonel Kripto & Kanal Büyüme Raporu (Ağustos 2026)")
        with st.spinner("Kanal verileri ve Ağustos 2026 kripto trendleri Llama 3.3 motoru ile sentezleniyor..."):
            client = Groq(api_key=st.session_state.groq_key)
            
            prompt = f"""
            Sen kurumsal düzeyde Web3, kripto varlık ve kanal büyüme stratejisi geliştiren üst düzey bir analistsin.
            Mevcut Tarih: Ağustos 2026.
            Kanal Adı: {ch_title}
            Toplam İzlenme: {total_views} | Abone Sayısı: {subscribers} | Toplam Video: {total_videos}
            Shorts ve Büyük Video Performansları sisteme entegre edilmiştir.

            Lütfen kesinlikle Türkçe olarak, profesyonel yatırım fonu raporu formatında şu başlıkları detaylıca sun:
            1. **Kanalın Kitle ve Etkileşim Sağlığı:** Shorts ve klasik video dağılımının analizi.
            2. **Ağustos 2026 Yüksek İzlenme Getirecek 3 Trend & Coin:** (Örn: CLARITY Act regülasyonları, AI altcoinleri/TAO, RWA tokenizasyonu, Solana/Sui ekosistemi veya BTC Q4 beklentileri).
            3. **Yüksek CTR ve İzlenme Süresi İçin Algoritma Taktikleri.**
            4. **Otomasyon & İçerik Üretim Hattı.**
            """
            
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
            )

            st.markdown(chat_completion.choices[0].message.content)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("👈 Sol üstteki küçük oka tıklayarak kontrol panelini açabilir ve 'Canlı Verileri Getir' butonuna basabilirsiniz.")
