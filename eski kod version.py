import streamlit as st
import os

# --- Yol sabitleme ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def img(file):
    return os.path.join(BASE_DIR, "images", file)

# --- Custom CSS ---
st.markdown("""
    <style>
    .result-card {
        padding: 20px;
        border-radius: 15px;
        margin-top: 20px;
        text-align: center;
        font-weight: bold;
        font-size: 20px;
    }
    .birads-2 {background-color: #d4edda; color: #155724;}
    .birads-3 {background-color: #cce5ff; color: #004085;}
    .birads-4a {background-color: #fff3cd; color: #856404;}
    .birads-4b {background-color: #ffeeba; color: #664d03;}
    .birads-4c {background-color: #f8d7da; color: #721c24;}
    .birads-5 {background-color: #f5c6cb; color: #721c24;}
    div[data-baseweb="tag"] {
        background-color: #28a745 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Başlık + Uyarı ---
st.title("🩻 BI-RADS Karar Destek Sistemi (Mamografi Tabanlı)")
st.warning("⚠️ Bu karar destek sistemi yalnızca mamografik bulgular üzerinden BI-RADS kategorizasyonu yapar. Ultrasonografi ve klinik değerlendirme içermez.")

# --- Tetkik kontrolü ---
exam_complete = st.selectbox("Tetkik yeterli mi?", ["Evet", "Hayır"])
if exam_complete == "Hayır":
    st.markdown('<div class="result-card birads-0">BI-RADS 0<br>Ek görüntüleme gerekli</div>', unsafe_allow_html=True)
    st.stop()

# --- Bulgular ---
finding_type = st.multiselect("Bulgu Tipi", ["Kitle", "Kalsifikasyon", "Architectural Distortion", "Asimetri"])

# --- Kitle ---
if "Kitle" in finding_type:
    shape = st.selectbox("Lezyon Şekli", ["Yuvarlak", "Oval", "Düzensiz"])
    margin = st.selectbox("Kenar Özelliği", ["Düzgün", "Mikrolobüle", "Düzensiz", "Spiküle"])
else:
    shape = margin = None

# --- Kalsifikasyon ---
if "Kalsifikasyon" in finding_type:
    calc_morph = st.selectbox(
        "Kalsifikasyon Morfolojisi",
        ["Amorf", "Pleomorfik", "Lineer/Dallanan", "Round/Punctate",
         "Coarse/Popcorn", "Eggshell/Rim", "Milk of Calcium", "Skin", "Vascular"]
    )
    calc_dist = st.selectbox("Kalsifikasyon Dağılımı", ["Gruplu", "Segmental", "Lineer", "Diffüz"])
else:
    calc_morph = calc_dist = None

# --- Asimetri ---
if "Asimetri" in finding_type and "Kitle" not in finding_type:
    asym_type = st.selectbox("Asimetri Türü", ["Fokal", "Gelişen", "Global", "Sadece Yoğunluk Farkı"])
else:
    asym_type = None

has_AD = "Architectural Distortion" in finding_type

# --- Associated Features ---
st.subheader("Eşlik Eden Bulgular (Associated Features)")
skin_retraction = st.checkbox("Cilt çekintisi (Skin Retraction)")
nipple_retraction = st.checkbox("Meme başı retraksiyonu (Nipple Retraction)")

category = ""
explanation = ""
management = ""
reference = ""
image_path = ""

# --- Kitle kararları ---
if "Kitle" in finding_type:
    if shape in ["Yuvarlak", "Oval"] and margin == "Düzgün":
        category = "BI-RADS 2"
        explanation = "Benign patern. Oval/yuvarlak düzgün sınırlı kitle."
        management = "Rutin tarama"
        reference = "ACR BI-RADS Atlas 5th Ed. – Mass Shape/Margin"
        image_path = img("birads2.jpg")
    elif margin == "Mikrolobüle":
        category = "BI-RADS 4A"
        explanation = "Mikrolobüle kenar, düşük şüpheli."
        management = "Biyopsi önerilir"
        reference = "ACR BI-RADS Atlas 5th Ed. – Mass Margin"
        image_path = img("birads4a.jpg")
    elif margin == "Düzensiz":
        category = "BI-RADS 4B"
        explanation = "Düzensiz kenar, orta şüpheli."
        management = "Biyopsi önerilir"
        reference = "ACR BI-RADS Atlas 5th Ed. – Mass Margin"
        image_path = img("birads4b.jpg")
    elif margin == "Spiküle":
        category = "BI-RADS 4C"
        explanation = "Spiküle kenar, yüksek şüpheli."
        management = "Biyopsi önerilir"
        reference = "ACR BI-RADS Atlas 5th Ed. – Mass Margin"
        image_path = img("birads4c.jpg")

# --- Kalsifikasyon kararları ---
if "Kalsifikasyon" in finding_type:
    if calc_morph == "Coarse/Popcorn":
        category = "BI-RADS 2"
        explanation = "Coarse/popcorn kalsifikasyon, tipik benign."
        management = "Rutin tarama"
        reference = "ACR BI-RADS Atlas 5th Ed. – Typically Benign Calcifications"
        image_path = img("birads2.jpg")
    elif calc_morph in ["Eggshell/Rim", "Milk of Calcium", "Skin", "Vascular"]:
        category = "BI-RADS 2"
        explanation = f"{calc_morph} kalsifikasyon, tipik benign."
        management = "Rutin tarama"
        reference = "ACR BI-RADS Atlas 5th Ed. – Typically Benign Calcifications"
        image_path = img("birads2.jpg")
    elif calc_morph == "Round/Punctate":
        if calc_dist == "Diffüz":
            category = "BI-RADS 2"
            explanation = "Diffüz round/punctate kalsifikasyon, benign."
            management = "Rutin tarama"
            reference = "ACR BI-RADS Atlas 5th Ed. – Typically Benign Calcifications"
            image_path = img("birads2.jpg")
        else:
            category = "BI-RADS 3"
            explanation = "Gruplu round/punctate kalsifikasyon, muhtemelen benign."
            management = "6 ay mamografi kontrolü"
            reference = "ACR BI-RADS Atlas 5th Ed. – Probably Benign Calcifications"
            image_path = img("birads3_asymmetry.jpg")
    elif calc_morph == "Amorf":
        category = "BI-RADS 4A"
        explanation = "Amorf kalsifikasyon, düşük şüpheli."
        management = "Biyopsi önerilir"
        reference = "ACR BI-RADS Atlas 5th Ed. – Calcifications"
        image_path = img("birads4a_calcification.jpg")
        if calc_dist in ["Segmental", "Lineer"]:
            category = "BI-RADS 4B"
            explanation = "Amorf + segmental/lineer dağılım, orta şüpheli."
            management = "Biyopsi önerilir"
            reference = "ACR BI-RADS Atlas 5th Ed. – Calcifications Distribution"
            image_path = img("birads4b_calcification.jpg")
    elif calc_morph == "Pleomorfik":
        category = "BI-RADS 4B"
        explanation = "Pleomorfik kalsifikasyon, orta şüpheli."
        management = "Biyopsi önerilir"
        reference = "ACR BI-RADS Atlas 5th Ed. – Calcifications"
        image_path = img("birads4b_calcification.jpg")
        if calc_dist in ["Segmental", "Lineer"]:
            category = "BI-RADS 4C"
            explanation = "Pleomorfik + segmental/lineer dağılım, yüksek şüpheli."
            management = "Biyopsi önerilir"
            reference = "ACR BI-RADS Atlas 5th Ed. – Calcifications Distribution"
            image_path = img("birads4c_calcification.jpg")
    elif calc_morph == "Lineer/Dallanan":
        category = "BI-RADS 4C"
        explanation = "Lineer/dallanan kalsifikasyon, yüksek şüpheli."
        management = "Biyopsi önerilir"
        reference = "ACR BI-RADS Atlas 5th Ed. – Calcifications"
        image_path = img("birads4c_calcification.jpg")

# --- Asimetri kararları ---
if "Asimetri" in finding_type and "Kitle" not in finding_type:
    if asym_type == "Gelişen":
        category = "BI-RADS 4A"
        explanation = "Gelişen asimetri, düşük şüpheli."
        management = "Biyopsi önerilir"
        reference = "ACR BI-RADS Atlas 5th Ed. – Developing Asymmetry"
        image_path = img("birads4a.jpg")
    elif asym_type == "Fokal":
        category = "BI-RADS 3"
        explanation = "Fokal asimetri, muhtemelen benign."
        management = "6 ay mamografi kontrolü"
        reference = "ACR BI-RADS Atlas 5th Ed. – Asymmetry"
        image_path = img("birads3_asymmetry.jpg")
    elif asym_type == "Global":
        category = "BI-RADS 2"
        explanation = "Global asimetri, genellikle benign."
        management = "Rutin tarama"
        reference = "ACR BI-RADS Atlas 5th Ed. – Global Asymmetry"
        image_path = img("birads2.jpg")
    elif asym_type == "Sadece Yoğunluk Farkı":
        category = "BI-RADS 2"
        explanation = "Sadece yoğunluk farkı, genellikle benign."
        management = "Rutin tarama"
        reference = "ACR BI-RADS Atlas 5th Ed. – Density Only Asymmetry"
        image_path = img("birads2.jpg")

# --- Architectural Distortion ---
if has_AD:
    if category in ["BI-RADS 4B", "BI-RADS 4C"]:
        category = "BI-RADS 5"
        explanation = "Architectural distortion şüpheli bulguya eşlik ediyor, tipik malign."
        management = "Biyopsi / cerrahi"
        reference = "ACR BI-RADS Atlas 5th Ed. – Architectural Distortion"
        image_path = img("birads5.jpg")
    elif category == "":
        category = "BI-RADS 4C"
        explanation = "Tek başına architectural distortion, yüksek şüpheli."
        management = "Biyopsi önerilir"
        reference = "ACR BI-RADS Atlas 5th Ed. – Architectural Distortion"
        image_path = img("birads4c_architectural_distortion.jpg")

# --- Associated feature algoritması ---
if skin_retraction or nipple_retraction:
    category = "BI-RADS 5"
    explanation = "Cilt/meme başı retraksiyonu: klasik malignite paterni."
    management = "Biyopsi / cerrahi"
    reference = "ACR BI-RADS Atlas 5th Ed. – Associated Features"
    image_path = img("birads5.jpg")

# --- Kitle + Kalsifikasyon kombinasyonu ---
if "Kitle" in finding_type and "Kalsifikasyon" in finding_type:
    if margin == "Spiküle" and calc_morph == "Pleomorfik" and calc_dist in ["Segmental", "Lineer"]:
        category = "BI-RADS 5"
        explanation = "Spiküle kitle + segmental pleomorfik kalsifikasyon: tipik malign."
        management = "Biyopsi / cerrahi"
        reference = "ACR BI-RADS Atlas 5th Ed. – Combined Findings"
        image_path = img("birads5.jpg")

# --- Fallback (Atlas'a uygun) ---
if not category and finding_type:
    category = "BI-RADS 3"
    explanation = "Belirsiz bulgu, muhtemelen benign."
    management = "6 ay mamografi kontrolü"
    reference = "ACR BI-RADS Atlas 5th Ed. – Assessment Category Selection"

# --- Sonuç kartı ---
if category:
    css_class = "birads-" + category.split()[1].lower()
    st.markdown(f'<div class="result-card {css_class}">{category}<br>{explanation}<br><small>{management}</small></div>', unsafe_allow_html=True)
    st.caption("Not: Değerlendirme mamografiye dayanmaktadır, eşlik eden US/klinik bulgular hesaba katılmamıştır.")

    if image_path and os.path.exists(image_path):
        st.image(image_path, caption=f"{category} örnek mamografi", use_container_width=True)
    else:
        st.warning("📷 Örnek görsel bulunamadı veya yüklenemedi.")

    if reference:
        st.info(f"📌 Referans: {reference}")

# --- Footer / İmza ---
st.markdown("""
<hr>
<p style='text-align:center; color:gray; font-size:14px;'>
🩻 Developed by <b>ERNC</b> | Antalya Eğitim ve Araştırma Hastanesi, 2025<br>
<small>Assistant Radiologist: Erdinç Hakan İnan</small>
</p>
""", unsafe_allow_html=True)
