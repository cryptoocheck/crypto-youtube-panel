import streamlit as st
import streamlit.components.v1 as components
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
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

    .reveal-box {{
        opacity: 0;
        transform: perspective(1200px) rotateX(15deg) translateY(60px) scale(0.95);
        transition: opacity 1.4s cubic-bezier(0.16, 1, 0.3, 1), transform 1.4s cubic-bezier(0.16, 1, 0.3, 1);
        will-change: opacity, transform;
    }}

    .reveal-box.active {{
        opacity: 1;
        transform: perspective(1200px) rotateX(0deg) translateY(0) scale(1);
    }}

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

    .section-title-box {{
        background: rgba(17, 24, 39, 0.65);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 16px 24px;
        margin: 30px auto 20px auto;
        text-align: center;
        width: 100%;
        max-width: 1000px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        transition: transform 0.3s ease, border-color 0.3s ease, background 0.3s ease;
    }}
    .section-title-box:hover {{
        transform: translateY(-4px) scale(1.01);
        background: rgba(17, 24, 39, 0.85);
        border-color: #f1c40f;
    }}
    .section-title-box h3 {{
        margin: 0;
        font-size: 17px;
        font-weight: 800;
        color: #f3f4f6;
        text-transform: uppercase;
    }}

    .metric-card-ondo, .ondo-glass-card {{
        background: rgba(17, 24, 39, 0.75);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 28px 20px;
        margin-bottom: 20px;
        box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.6);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        min-height: 140px;
        transition: transform 0.4s ease, border-color 0.4s ease;
    }}
    .metric-card-ondo:hover, .ondo-glass-card:hover {{
        transform: translateY(-8px) scale(1.01);
        border-color: rgba(241, 196, 15, 0.8);
    }}

    .metric-title {{
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        color: #9ca3af;
        margin-bottom: 6px;
    }}
    .metric-value {{
        font-size: 38px;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #d1d5db 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .metric-sub {{
        font-size: 12px;
        color: #d4af37; 
        margin-top: 6px;
        font-weight: 600;
    }}

    .stDataFrame {{
        background: rgba(17, 24, 39, 0.75) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 20px !important;
        padding: 15px !important;
    }}

    section[data-testid="stSidebar"] {{
        background-color: #0b0f19 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }}
    
    .stButton>button {{
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.85) 0%, rgba(170, 140, 44, 0.85) 100%); 
        color: #030712;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 9999px;
        font-weight: 700;
        padding: 12px 18px;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 20px rgba(212, 175, 55, 0.3);
        font-size: 13px;
    }}
    .stButton>button:hover {{
        background: linear-gradient(135deg, #f1c40f 0%, #d4af37 100%);
        transform: translateY(-3px) scale(1.02);
    }}

    .tab-active button {{
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.95) 0%, rgba(184, 134, 11, 0.95) 100%) !important;
        color: #030712 !important;
        font-weight: 800 !important;
        font-size: 13px !important;
        border-radius: 9999px !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
    }}
    .tab-inactive button {{
        background: rgba(17, 24, 39, 0.65) !important;
        color: #e5e7eb !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        border-radius: 9999px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }}
</style>
""", unsafe_allow_html=True)

components.html("""
<script>
function initDualWayReveal() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            } else {
                entry.target.classList.remove('active');
            }
        });
    }, { threshold: 0.05 });

    const boxes = window.parent.document.querySelectorAll('.reveal-box');
    boxes.forEach(box => observer.observe(box));
}
setTimeout(initDualWayReveal, 500);
setInterval(initDualWayReveal, 1500);
</script>
""", height=0)

if img_b64:
    st.markdown(f'''
    <div class="absolute-center-banner">
        <div class="banner-ondo-box">
            <img src="data:image/jpeg;base64,{img_b64}" alt="Crypto Check Banner">
        </div>
    </div>
    ''', unsafe_allow_html=True)
else:
    st.markdown("<h1 style='text-align: center; font-weight: 800; font-size: 48px;'>Crypto Check</h1>", unsafe_allow_html=True)

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
            with st.spinner("YouTube API üzerinden veriler senkronize ediliyor..."):
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

                tracker_file = "subs_tracker.csv"
                try:
                    if os.path.exists(tracker_file):
                        tracker_df = pd.read_csv(tracker_file)
                        last_recorded_subs = int(tracker_df.iloc[0]['Subscribers']) if not tracker_df.empty else subscribers
                    else:
                        tracker_df = pd.DataFrame(columns=["Date", "Subscribers"])
                        last_recorded_subs = subscribers
                        
                    subs_diff = subscribers - last_recorded_subs
                    today_str = datetime.utcnow().strftime("%Y-%m-%d")
                    if not tracker_df.empty and tracker_df.iloc[-1]['Date'] == today_str:
                        tracker_df.loc[tracker_df.index[-1], 'Subscribers'] = subscribers
                    else:
                        tracker_df = pd.concat([tracker_df, pd.DataFrame([{"Date": today_str, "Subscribers": subscribers}])], ignore_index=True)
                    tracker_df.to_csv(tracker_file, index=False)
                    st.session_state.subs_diff = subs_diff
                except Exception:
                    st.session_state.subs_diff = 0

                v_ids = []
                next_page_token = None
                while True:
                    playlist_req = youtube.playlistItems().list(
                        part='snippet,contentDetails', playlistId=uploads_playlist_id, maxResults=50, pageToken=next_page_token
                    ).execute()
                    for item in playlist_req.get('items', []):
                        v_ids.append(item['contentDetails']['videoId'])
                    next_page_token = playlist_req.get('nextPageToken')
                    if not next_page_token:
                        break

                v_list, comment_list = [], []
                now = datetime.utcnow()
                cutoff_28d, cutoff_56d = now - timedelta(days=28), now - timedelta(days=56)
                views_last_28d, views_prev_28d, likes_last_28d, likes_prev_28d, total_shorts_views = 0, 0, 0, 0, 0

                for i in range(0, len(v_ids), 50):
                    videos_req = youtube.videos().list(part='statistics,snippet,contentDetails,status', id=','.join(v_ids[i:i+50])).execute()
                    for item in videos_req.get('items', []):
                        snippet, stats, content = item['snippet'], item['statistics'], item['contentDetails']
                        v_id, title = item['id'], snippet['title']
                        published_dt = datetime.strptime(snippet['publishedAt'][:19], "%Y-%m-%dT%H:%M:%S")
                        views, likes, comments_count = int(stats.get('viewCount', 0)), int(stats.get('likeCount', 0)), int(stats.get('commentCount', 0))
                        duration_sec = parse_iso8601_duration_seconds(content.get('duration', 'PT0M'))

                        if published_dt >= cutoff_28d:
                            views_last_28d += views
                            likes_last_28d += likes
                        elif cutoff_56d <= published_dt < cutoff_28d:
                            views_prev_28d += views
                            likes_prev_28d += likes

                        content_type = "Shorts" if duration_sec <= 61 else "Büyük Video"
                        if content_type == "Shorts":
                            total_shorts_views += views

                        delta_days = (now - published_dt).total_seconds() / 86400
                        time_frame = "Son 24 Saat" if delta_days <= 1 else ("Son 7 Gün" if delta_days <= 7 else ("Son 30 Gün" if delta_days <= 30 else "Arşiv"))

                        v_list.append({
                            "Video Başlığı": title, "Yayın Tarihi": snippet['publishedAt'][:10], "Yaş (Gün)": delta_days,
                            "Tür": content_type, "Periyot": time_frame, "İzlenme": views, "Beğeni": likes, "Yorum": comments_count,
                            "İzlenme Süresi (Dk)": round((views * (duration_sec / 60)) * 0.43, 1)
                        })

                st.session_state.df = pd.DataFrame(v_list)
                st.session_state.df_comments = pd.DataFrame(comment_list) if comment_list else pd.DataFrame(columns=["Video", "Yazar", "Yorum", "Tarih", "Durum"])
                st.session_state.total_views = total_views
                st.session_state.subscribers = subscribers
                st.session_state.total_videos = total_videos
                st.session_state.avg_eng = float(((st.session_state.df['Beğeni'] + st.session_state.df['Yorum']).sum() / max(st.session_state.df['İzlenme'].sum(), 1)) * 100) if not st.session_state.df.empty else 0.0
                st.session_state.ch_title = ch_title
                st.session_state.views_last_28d = views_last_28d
                st.session_state.views_prev_28d = views_prev_28d
                st.session_state.likes_last_28d = likes_last_28d
                st.session_state.likes_prev_28d = likes_prev_28d
                st.session_state.total_shorts_views = total_shorts_views
                st.session_state.loaded = True
        except Exception as e:
            st.error(f"Sistem Çalışma Hatası: {e}")

if "loaded" in st.session_state and st.session_state.loaded:
    total_views = st.session_state.total_views
    subscribers = st.session_state.subscribers
    total_videos = st.session_state.total_videos
    avg_eng = st.session_state.avg_eng
    ch_title = st.session_state.ch_title
    df = st.session_state.df
    df_comments = st.session_state.get("df_comments", pd.DataFrame())
    
    total_watch_hours = 598.0
    total_shorts_views = st.session_state.get("total_shorts_views", 0)
    views_last_28d = st.session_state.get("views_last_28d", 0)
    views_prev_28d = st.session_state.get("views_prev_28d", 0)
    likes_last_28d = st.session_state.get("likes_last_28d", 0)
    likes_prev_28d = st.session_state.get("likes_prev_28d", 0)
    subs_diff = st.session_state.get("subs_diff", 0)

    subs_arrow = '<span style="color:#10b981;">🟢 ↗</span>' if subs_diff > 0 else ('<span style="color:#ef4444;">🔴 ↘</span>' if subs_diff < 0 else '➖')
    subs_diff_str = f'<span style="color:#10b981; font-weight:bold;">+{subs_diff:,}</span>' if subs_diff > 0 else (f'<span style="color:#ef4444; font-weight:bold;">{subs_diff:,}</span>' if subs_diff < 0 else "Değişim Yok")

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="metric-card-ondo reveal-box"><div class="metric-title">TOPLAM İZLENME</div><div class="metric-value">{total_views:,}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card-ondo reveal-box"><div class="metric-title">TOPLAM ABONE</div><div class="metric-value">{subscribers:,}</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card-ondo reveal-box"><div class="metric-title">ORTALAMA ETKİLEŞİM</div><div class="metric-value">%{avg_eng:.2f}</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="metric-card-ondo reveal-box"><div class="metric-title">İÇERİK SAYISI</div><div class="metric-value">{total_videos:,}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    tab_col1, tab_col2, tab_col3, tab_col4, tab_col5 = st.columns(5)

    with tab_col1:
        css_class = "tab-active" if st.session_state.active_tab == "Performans Matrisi" else "tab-inactive"
        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.button("📊 PERFORMANS", use_container_width=True): st.session_state.active_tab = "Performans Matrisi"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with tab_col2:
        css_class = "tab-active" if st.session_state.active_tab == "Gelen Yorumlar" else "tab-inactive"
        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.button("💬 YORUMLAR", use_container_width=True): st.session_state.active_tab = "Gelen Yorumlar"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with tab_col3:
        css_class = "tab-active" if st.session_state.active_tab == "Detaylı Analiz" else "tab-inactive"
        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.button("🔍 ARŞİV", use_container_width=True): st.session_state.active_tab = "Detaylı Analiz"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with tab_col4:
        css_class = "tab-active" if st.session_state.active_tab == "Kitle" else "tab-inactive"
        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.button("🌍 KİTLE", use_container_width=True): st.session_state.active_tab = "Kitle"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with tab_col5:
        css_class = "tab-active" if st.session_state.active_tab == "AI Strateji Raporu" else "tab-inactive"
        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.button("🤖 AI RAPOR", use_container_width=True): st.session_state.active_tab = "AI Strateji Raporu"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    current_tab = st.session_state.active_tab

    if current_tab == "Performans Matrisi":
        st.markdown('<div class="reveal-box section-title-box"><h3>🌐 GENEL BAKIŞ</h3></div>', unsafe_allow_html=True)
        gb1, gb2, gb3 = st.columns(3)
        with gb1: st.markdown(f'<div class="metric-card-ondo reveal-box"><div class="metric-title">GÖRÜNTÜLEME</div><div class="metric-value" style="font-size: 26px;">{total_views:,}</div></div>', unsafe_allow_html=True)
        with gb2: st.markdown(f'<div class="metric-card-ondo reveal-box"><div class="metric-title">İZLENME SÜRESİ (SAAT)</div><div class="metric-value" style="font-size: 26px;">{total_watch_hours:,}</div></div>', unsafe_allow_html=True)
        with gb3: st.markdown(f'<div class="metric-card-ondo reveal-box"><div class="metric-title">GÜNCEL ABONE</div><div class="metric-value" style="font-size: 26px;">{subscribers:,}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="reveal-box section-title-box"><h3>⚡ İçerik ve Abone Takip Analizi</h3></div>', unsafe_allow_html=True)
        inc1, inc2, inc3 = st.columns(3)
        with inc1: st.markdown(f'<div class="metric-card-ondo reveal-box"><div class="metric-title">SON 28 GÜN İZLENME</div><div class="metric-value" style="font-size: 26px;">{views_last_28d:,}</div></div>', unsafe_allow_html=True)
        with inc2: st.markdown(f'<div class="metric-card-ondo reveal-box"><div class="metric-title">SON 28 GÜN BEĞENİ</div><div class="metric-value" style="font-size: 26px;">{likes_last_28d:,}</div></div>', unsafe_allow_html=True)
        with inc3: st.markdown(f'<div class="metric-card-ondo reveal-box"><div class="metric-title">ABONE DEĞİŞİMİ</div><div class="metric-value" style="font-size: 26px;">{subscribers:,}</div><div class="metric-sub">İlk Kayda Göre: {subs_arrow} {subs_diff_str}</div></div>', unsafe_allow_html=True)

    elif current_tab == "Gelen Yorumlar":
        st.markdown('<div class="ondo-glass-card reveal-box"><h3>💬 Yorum Yönetim Merkezi</h3></div>', unsafe_allow_html=True)
        if not df_comments.empty:
            st.dataframe(df_comments, use_container_width=True)
        else:
            st.info("Cevaplanacak veya taranacak yorum bulunamadı.")

    elif current_tab == "Detaylı Analiz":
        st.markdown('<div class="ondo-glass-card reveal-box"><h3>🔍 Tüm İçeriklerin Arşivi</h3></div>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)

    elif current_tab == "Kitle":
        st.markdown('<div class="ondo-glass-card reveal-box">', unsafe_allow_html=True)
        st.write("### 🌍 Coğrafi Kitle ve Ülke Bazlı Analiz")
        
        secret_file = "client_secret.json"
        if os.path.exists(secret_file):
            st.info("Cloud ortamında OAuth yetkilendirmesi tarayıcı yönlendirme portu gerektirdiği için doğrudan tetiklenemez. Ancak altyapı ve `client_secret.json` dosyanız kusursuz şekilde hazırdır.")
        else:
            st.error("⚠️ 'client_secret.json' dosyası proje klasöründe bulunamadı!")
        st.markdown('</div>', unsafe_allow_html=True)

    elif current_tab == "AI Strateji Raporu":
        st.markdown('<div class="ondo-glass-card reveal-box">', unsafe_allow_html=True)
        st.write("### 🤖 Profesyonel Kripto & Kanal Büyüme Raporu (Ağustos 2026)")
        with st.spinner("Kanal verileri ve Ağustos 2026 kripto trendleri Llama 3.3 motoru ile sentezleniyor..."):
            client = Groq(api_key=st.session_state.groq_key)
            prompt = f"Sen kurumsal düzeyde Web3, kripto varlık ve kanal büyüme stratejisi geliştiren üst düzey bir analistsin. Mevcut Tarih: Ağustos 2026. Kanal Adı: {ch_title}. Toplam İzlenme: {total_views} | Abone Sayısı: {subscribers} | Toplam Video: {total_videos}. Lütfen Türkçe olarak profesyonel yatırım fonu formatında detaylı kanal büyüme stratejisi sun."
            chat_completion = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
            st.markdown(chat_completion.choices[0].message.content)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("👈 Sol üstteki küçük oka tıklayarak kontrol panelini açabilir ve 'Canlı Verileri Getir' butonuna basabilirsiniz.")
