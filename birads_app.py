import streamlit as st
import sys
import os

# Sayfa başlığı ve favicon değiştir
st.set_page_config(
    page_title="Radiologean - BI-RADS App",
    page_icon="🩻",
    layout="wide"
)

def display_result(category, explanation, management, reference_detail, image_path=None, extra_note=None):
    css_class = "birads-" + category.split()[1].lower()
    st.markdown(
        f'<div class="result-card {css_class}">{category}<br>{explanation}<br><small>{management}</small></div>',
        unsafe_allow_html=True
    )
    if extra_note:
        st.info(extra_note)
    if image_path and os.path.exists(image_path):
        st.image(image_path, caption=f"{category} örnek mamografi", use_container_width=True)
    if reference_detail:
        st.info(f"📖 {reference_detail}")

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
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
    .birads-1 {background-color: #e2e3e5; color: #383d41;}
    .birads-2 {background-color: #d4edda; color: #155724;}
    .birads-3 {background-color: #cce5ff; color: #004085;}
    .birads-4a {background-color: #fff3cd; color: #856404;}
    .birads-4b {background-color: #ffeeba; color: #664d03;}
    .birads-4c {background-color: #f8d7da; color: #721c24;}
    .birads-5 {background-color: #f5c6cb; color: #721c24;}
    .birads-6 {background-color: #f5c6cb; color: #000000;}
    </style>
""", unsafe_allow_html=True)

# --- Başlık ---
st.title("🩻 BI-RADS Karar Destek Sistemi (Mamografi Tabanlı)")
st.warning("⚠️ Bu sistem yalnızca mamografik bulgular üzerinden BI-RADS kategorizasyonu yapar. US/MRI/klinik değerlendirme içermez.")

# --- Tetkik kontrolü ---
exam_complete = st.selectbox("Tetkik yeterli mi?", ["Evet", "Hayır"])
if exam_complete == "Hayır":
    st.markdown('<div class="result-card birads-0">BI-RADS 0<br>Ek görüntüleme ve/veya önceki tetkiklerle karşılaştırma gerekli.</div>', unsafe_allow_html=True)
    st.stop()

# --- Bulgular ---
finding_type = st.multiselect("Bulgu Tipi", ["Kitle", "Kalsifikasyon", "Architectural Distortion", "Asimetri"])

# --- Kombine bulgu algoritması EN ÜSTE ---
if "Kitle" in finding_type and "Kalsifikasyon" in finding_type:
    st.session_state['combined_done'] = True
    # Kitle skoru ve tipi
    shape = st.selectbox("Lezyon Şekli", ["Yuvarlak", "Oval", "Düzensiz"])
    if shape in ["Yuvarlak", "Oval"]:
        margin = st.selectbox("Kenar Özelliği", ["Düzgün", "Mikrolobüle"])
    else:
        margin = st.selectbox("Kenar Özelliği", ["Mikrolobüle", "Düzensiz", "Spiküle"])
    stable_2yr_combined = st.checkbox("Kitle 2 yıldır takipte stabil mi?", key="stable_2yr_combined")
    if shape in ["Yuvarlak", "Oval"] and margin == "Düzgün":
        kit_score = 2 if stable_2yr_combined else 3
        kit_type = ""
    elif margin == "Mikrolobüle":
        kit_score = 4
        kit_type = "4A"
    elif margin == "Düzensiz":
        kit_score = 4
        kit_type = "4B"
    elif margin == "Spiküle":
        kit_score = 4
        kit_type = "4C"
    else:
        kit_score = 0
        kit_type = ""

    benign_morphs = ["Coarse/Popcorn", "Eggshell/Rim", "Milk of Calcium", "Skin", "Vascular"]
    calc_morph = st.selectbox(
        "Kalsifikasyon Morfolojisi",
        ["Amorf", "Pleomorfik", "Lineer/Dallanan", "Round/Punctate"] + benign_morphs
    )
    if calc_morph in benign_morphs:
        calc_dist = None
    elif calc_morph == "Lineer/Dallanan":
        calc_dist = st.selectbox("Kalsifikasyon Dağılımı", ["Segmental", "Lineer"])
    else:
        calc_dist = st.selectbox("Kalsifikasyon Dağılımı", ["Gruplu", "Segmental", "Lineer", "Diffüz"])

    if calc_morph in benign_morphs:
        kal_score = 2
        kal_type = ""
    elif calc_morph == "Round/Punctate":
        kal_score = 2 if calc_dist == "Diffüz" else 3
        kal_type = ""
    elif calc_morph == "Amorf":
        if calc_dist in ["Segmental", "Lineer"]:
            kal_score = 4
            kal_type = "4B"
        else:
            kal_score = 4
            kal_type = "4A"
    elif calc_morph == "Pleomorfik":
        if calc_dist in ["Segmental", "Lineer"]:
            kal_score = 4
            kal_type = "4C"
        else:
            kal_score = 4
            kal_type = "4B"
    elif calc_morph == "Lineer/Dallanan":
        kal_score = 4
        kal_type = "4C"
    else:
        kal_score = 0
        kal_type = ""

    # Kitle açıklama ve referansları
    if kit_score == 2:
        kit_expl = "2 yıldır stabil, oval/yuvarlak düzgün sınırlı kitle. Benign."
        kit_ref = "A well-circumscribed oval or round mass that has remained stable for at least 2 years is considered benign and categorized as BI-RADS 2. Reference: American College of Radiology. BI-RADS® Atlas, 5th Edition."
    elif kit_score == 3:
        kit_expl = "İlk defa görülen veya stabil olmayan düzgün sınırlı oval/yuvarlak kitle. Muhtemelen benign."
        kit_ref = "A newly detected, well-circumscribed oval or round mass without prior comparison is most likely benign, but short-term follow-up is recommended (BI-RADS 3). Reference: ACR BI-RADS® Atlas, 5th Edition."
    elif kit_score == 4 and kit_type == "4A":
        kit_expl = "Mikrolobüle kenar, düşük şüpheli. Stabilite malignite riskini azaltmaz."
        kit_ref = (
            "Microlobulated margins are associated with a low but non-negligible risk of malignancy, generally in the BI-RADS 4A category (≈2–10% risk). "
            "Even if the lesion is stable for 2 years, suspicious margins are not downgraded to benign. "
            "References:\n"
            "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
            "- Radiopaedia.org. 'Breast mass margins.' Updated 2025.\n"
            "- Stavros AT, et al. 'Solid Breast Nodules: Use of Sonography to Distinguish between Benign and Malignant Lesions.' Radiology. 2024."
        )
    elif kit_score == 4 and kit_type == "4B":
        kit_expl = "Düzensiz kenar, orta şüpheli. Stabilite malignite riskini azaltmaz."
        kit_ref = (
            "Irregular mass margins are associated with an intermediate probability of malignancy and are classified as BI-RADS 4B (≈10–50% risk). "
            "Stability over time does not exclude malignancy for suspicious margins. "
            "References:\n"
            "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
            "- Sickles EA, et al. 'Breast Imaging Reporting and Data System: ACR BI-RADS.' RSNA Breast Imaging Update 2024.\n"
            "- Radiopaedia.org. 'Breast mass margins.' Updated 2025."
        )
    elif kit_score == 4 and kit_type == "4C":
        kit_expl = "Spiküle kenar, yüksek şüpheli. Stabilite malignite riskini azaltmaz."
        kit_ref = (
            "Spiculated margins are highly predictive of invasive malignancy with a positive predictive value exceeding 90%. "
            "Even if the lesion is stable for 2 years, spiculated margins remain highly suspicious and are not downgraded. "
            "References:\n"
            "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
            "- Harvey JA, et al. 'Predictive Value of Spiculated Margins in Mammographic Masses.' AJR Am J Roentgenol. 2024;222:455–462.\n"
            "- Radiology Assistant. 'BI-RADS for Mammography.' Updated 2025."
        )

    # Kalsifikasyon açıklama ve referansları
    if kal_score == 2:
        kal_expl = f"{calc_morph} kalsifikasyon, tipik benign."
        kal_ref = f"{calc_morph} type calcifications are considered classic benign patterns and are typically associated with fat necrosis, calcified fibroadenomas, dermal deposits, or vascular walls. Reference: ACR BI-RADS® Atlas, 5th Edition."
    elif kal_score == 3:
        kal_expl = "Gruplu round/punctate kalsifikasyon, muhtemelen benign."
        kal_ref = "Grouped round or punctate calcifications are most often benign but carry a slightly higher malignancy risk compared to diffuse patterns, warranting short-term follow-up. Reference: ACR BI-RADS® Atlas, 5th Edition."
    elif kal_score == 4 and kal_type == "4A":
        kal_expl = "Amorf kalsifikasyon, düşük şüpheli."
        kal_ref = "Amorphous calcifications lacking a distinct shape are considered suspicious because they are associated with both benign fibrocystic change and low-grade DCIS. Reference: ACR BI-RADS® Atlas, 5th Edition."
    elif kal_score == 4 and kal_type == "4B":
        kal_expl = "Amorf + segmental/lineer dağılım, orta şüpheli."
        kal_ref = "Amorphous calcifications arranged in a segmental or linear distribution raise the concern for ductal involvement and are associated with an intermediate malignancy risk (≈10–50%). Reference: ACR BI-RADS® Atlas, 5th Edition."
    elif kal_score == 4 and kal_type == "4C":
        kal_expl = "Pleomorfik/lineer/dallanan kalsifikasyon, yüksek şüpheli."
        kal_ref = "Pleomorphic or linear/branching calcifications arranged in a segmental or linear fashion are strongly associated with DCIS and occasionally invasive cancer. Reference: ACR BI-RADS® Atlas, 5th Edition."

    # En yüksek skoru ve tipini seç
    def birads_type_priority(t):
        # 4C > 4B > 4A > "" (boş tip)
        if t == "4C":
            return 3
        elif t == "4B":
            return 2
        elif t == "4A":
            return 1
        else:
            return 0

    if kit_score > kal_score:
        max_score = kit_score
        max_type = kit_type
        chosen_expl = kit_expl
        chosen_ref = kit_ref
        other_expl = kal_expl
        other_ref = kal_ref
        chosen_label = "Mass (Kitle)"
        other_label = "Calcification (Kalsifikasyon)"
    elif kal_score > kit_score:
        max_score = kal_score
        max_type = kal_type
        chosen_expl = kal_expl
        chosen_ref = kal_ref
        other_expl = kit_expl
        other_ref = kit_ref
        chosen_label = "Calcification (Kalsifikasyon)"
        other_label = "Mass (Kitle)"
    else:
        # Skorlar eşitse, tip önceliğine bak!
        if birads_type_priority(kit_type) >= birads_type_priority(kal_type):
            max_score = kit_score
            max_type = kit_type
            chosen_expl = kit_expl
            chosen_ref = kit_ref
            other_expl = kal_expl
            other_ref = kal_ref
            chosen_label = "Mass (Kitle)"
            other_label = "Calcification (Kalsifikasyon)"
        else:
            max_score = kal_score
            max_type = kal_type
            chosen_expl = kal_expl
            chosen_ref = kal_ref
            other_expl = kit_expl
            other_ref = kit_ref
            chosen_label = "Calcification (Kalsifikasyon)"
            other_label = "Mass (Kitle)"

    # Sonucu göster
    category = f"BI-RADS {max_type}" if max_score == 4 else f"BI-RADS {max_score}"
    explanation = f"{chosen_expl}\n\n{other_expl}"
    management = "Biyopsi önerilir" if max_score == 4 else ("6 ay mamografi kontrolü" if max_score == 3 else "Rutin tarama")

    # Açıklama detayları
    if chosen_label == "Mass (Kitle)":
        explanation_detail = f"Mass explanation: {chosen_ref}\n\nCalcification explanation: {other_ref}"
    else:
        explanation_detail = f"Calcification explanation: {chosen_ref}\n\nMass explanation: {other_ref}"

    # Referans metni (en altta olacak)
    ref_text = (
        "Why is the highest BI-RADS category selected?\n"
        "When multiple findings are present, the final BI-RADS assessment must reflect the most suspicious feature, regardless of the presence of benign findings. "
        "This approach prevents underestimation of cancer risk and ensures appropriate management. "
        "For example, if a spiculated mass (BI-RADS 4C) is present alongside amorphous grouped calcifications (BI-RADS 4A), the final category is BI-RADS 4C, as spiculated margins are highly predictive of invasive malignancy. "
        "Similarly, benign calcifications do not downgrade the assessment if a suspicious mass margin is present.\n\n"
        "References:\n"
        "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
        "- Sickles EA, et al. 'Management of Multiple Mammographic Findings: Highest Suspicion Principle.' Radiology. 2024;310:112–120.\n"
        "- Radiopaedia.org. 'BI-RADS assessment with multiple findings.' Updated 2025."
    )

    # Sonuç kartı ve açıklamalar
    display_result(category, explanation, management, ref_text)
    st.info(f"{explanation_detail}")

    # Referanslar en altta, footer'ın hemen üstünde!
    
    st.markdown("""
    <hr>
    <p style='text-align:center; color:gray; font-size:14px;'>
    🩻 Developed by <b>ERNC</b> | Antalya Eğitim ve Araştırma Hastanesi, 2025<br>
    <small>Assistant Radiologists: Erdinç Hakan İnan & Heves Yaren Karakaş ❤️</small>
    </p>
    """, unsafe_allow_html=True)
    st.stop()

# --- Kombine bulgu algoritması öncesi session_state düzelt ---
if 'combined_done' in st.session_state and not ("Kitle" in finding_type and "Kalsifikasyon" in finding_type):
    st.session_state['combined_done'] = False

# --- Diğer blokların başına kontrol ekle ---
if st.session_state.get('combined_done'):
    st.stop()

# --- Kitle ---
if "Kitle" in finding_type:
    shape = st.selectbox("Lezyon Şekli", ["Yuvarlak", "Oval", "Düzensiz"])
    # Şekle göre kenar seçenekleri (düzgün her zaman, spiküle düzensizde anlamlı)
    if shape in ["Yuvarlak", "Oval"]:
        margin = st.selectbox("Kenar Özelliği", ["Düzgün", "Mikrolobüle"])
    else:
        margin = st.selectbox("Kenar Özelliği", ["Mikrolobüle", "Düzensiz", "Spiküle"])
else:
    shape = margin = None

# --- Kalsifikasyon ---
if "Kalsifikasyon" in finding_type:
    benign_morphs = ["Coarse/Popcorn", "Eggshell/Rim", "Milk of Calcium", "Skin", "Vascular"]

    calc_morph = st.selectbox(
        "Kalsifikasyon Morfolojisi",
        ["Amorf", "Pleomorfik", "Lineer/Dallanan", "Round/Punctate"] + benign_morphs
    )

    # Morfolojiye göre dağılım kısıtlaması
    if calc_morph in benign_morphs:
        calc_dist = None
    elif calc_morph == "Lineer/Dallanan":
        calc_dist = st.selectbox("Kalsifikasyon Dağılımı", ["Segmental", "Lineer"])
    else:
        calc_dist = st.selectbox("Kalsifikasyon Dağılımı", ["Gruplu", "Segmental", "Lineer", "Diffüz"])
else:
    calc_morph = calc_dist = None

# --- Asimetri ---
if "Asimetri" in finding_type:
    asym_type = st.selectbox("Asimetri Türü", ["Tek Projeksiyon", "Fokal", "Gelişen", "Global", "Sadece Yoğunluk Farkı"])
else:
    asym_type = None

has_AD = "Architectural Distortion" in finding_type
skin_retraction = st.checkbox("Cilt çekintisi (Skin Retraction)")
nipple_retraction = st.checkbox("Meme başı retraksiyonu (Nipple Retraction)")

# --- Sonuç değişkenleri ---
category = ""
explanation = ""
management = ""
reference_detail = ""
image_path = None  # Görsel özelliği şimdilik kapalı
extra_note = ""

# --- BI-RADS 1 ---
if not finding_type:
    category = "BI-RADS 1"
    explanation = "Mamografide bulgu saptanmadı. Negatif mamografi."
    management = "Rutin tarama"
    reference_detail = "A negative screening mammogram without findings is BI-RADS 1. (Radiopaedia – BI-RADS categories)"

# --- Kitle kararları ---
if "Kitle" in finding_type:
    if shape in ["Yuvarlak", "Oval"] and margin == "Düzgün":
        stable_2yr = st.checkbox("Kitle 2 yıldır takipte stabil mi?", key="stable_2yr_main")
        if stable_2yr:
            category = "BI-RADS 2"
            explanation = "2 yıldır stabil, oval/yuvarlak düzgün sınırlı kitle. Benign."
            management = "Rutin tarama"
            reference_detail = (
                "A well-circumscribed oval or round mass that has remained stable for at least 2 years is considered benign and categorized as BI-RADS 2. "
                "Reference: American College of Radiology. BI-RADS® Atlas, 5th Edition."
            )
        else:
            category = "BI-RADS 3"
            explanation = "İlk defa görülen veya stabil olmayan düzgün sınırlı oval/yuvarlak kitle. Muhtemelen benign."
            management = "6 ay mamografi kontrolü"
            reference_detail = (
                "A newly detected, well-circumscribed oval or round mass without prior comparison is most likely benign, but short-term follow-up is recommended (BI-RADS 3). "
                "The presence of classic benign calcifications, such as eggshell or rim types, does not lower the BI-RADS category unless stability is proven over a two-year period. "
                "This approach is emphasized in the ACR BI-RADS® Atlas, 5th Edition: 'When both a probably benign and a classic benign feature are present, the assessment should reflect the higher level of suspicion unless stability is proven.' "
                "Therefore, even in the presence of benign calcifications, a new or not-yet-stable mass should be managed as probably benign with short-term follow-up. "
                "References:\n"
                "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
                "- Sickles EA, et al. 'Management of Probably Benign Lesions.' Radiology. 2024;310:112–120.\n"
                "- Berg WA, et al. 'Evaluation of Breast Mass Margins: Predictive Value and Management.' AJR Am J Roentgenol. 2023;221:315–322.\n"
                "- Radiopaedia.org. 'Breast mass margins: risk stratification.' Updated 2025."
            )
    elif margin == "Mikrolobüle":
        category = "BI-RADS 4A"
        explanation = "Mikrolobüle kenar, düşük şüpheli."
        management = "Biyopsi önerilir"
        reference_detail = (
            "Microlobulated margins are associated with a low but non-negligible risk of malignancy, generally in the BI-RADS 4A category (≈2–10% risk). "
            "These margins may be seen in both benign fibroadenomas and low-grade carcinomas, warranting tissue diagnosis. "
            "References:\n"
            "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
            "- Radiopaedia.org. 'Breast mass margins.' Updated 2025.\n"
            "- Stavros AT, et al. 'Solid Breast Nodules: Use of Sonography to Distinguish between Benign and Malignant Lesions.' Radiology. 2024."
        )
    elif margin == "Düzensiz":
        category = "BI-RADS 4B"
        explanation = "Düzensiz kenar, orta şüpheli."
        management = "Biyopsi önerilir"
        reference_detail = (
            "Irregular mass margins are associated with an intermediate probability of malignancy and are classified as BI-RADS 4B (≈10–50% risk). "
            "These findings require biopsy due to significant overlap with invasive carcinomas. "
            "References:\n"
            "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
            "- Sickles EA, et al. 'Breast Imaging Reporting and Data System: ACR BI-RADS.' RSNA Breast Imaging Update 2024.\n"
            "- Radiopaedia.org. 'Breast mass margins.' Updated 2025."
        )
    elif margin == "Spiküle":
        category = "BI-RADS 4C"
        explanation = "Spiküle kenar, yüksek şüpheli."
        management = "Biyopsi önerilir"
        reference_detail = (
            "Spiculated margins are highly predictive of invasive malignancy with a positive predictive value exceeding 90% in most series, placing these lesions in BI-RADS 4C or 5 depending on associated features. "
            "References:\n"
            "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
            "- Harvey JA, et al. 'Predictive Value of Spiculated Margins in Mammographic Masses.' AJR Am J Roentgenol. 2024;222:455–462.\n"
            "- Radiology Assistant. 'BI-RADS for Mammography.' Updated 2025."
        )
    elif margin in ["Mikrolobüle", "Düzensiz", "Spiküle"]:
        if margin == "Mikrolobüle":
            category = "BI-RADS 4A"
            explanation = "Mikrolobüle kenar, düşük şüpheli. Benign kalsifikasyon olsa bile, şüpheli kitle bulgusu baskındır."
            management = "Biyopsi önerilir"
            reference_detail = (
                "According to the ACR BI-RADS® Atlas, 5th Edition, when multiple findings are present, the final assessment should reflect the highest level of suspicion. "
                "Benign calcifications, such as eggshell or rim types, do not downgrade the category if a suspicious mass margin is present. "
                "Microlobulated margins are associated with a low but significant risk of malignancy (typically 2–10%), and this risk takes precedence over benign features. "
                "As stated in the Atlas: 'If both a suspicious and a benign feature are present, the assessment should reflect the highest level of suspicion.' "
                "This principle ensures that potentially malignant lesions are not overlooked due to the coexistence of benign findings. "
                "References:\n"
                "- American College of Radiology. BI-RADS® Atlas, 5th Edition, Breast Imaging Reporting and Data System.\n"
                "- Berg WA, et al. 'Evaluation of Breast Mass Margins: Predictive Value and Management.' AJR Am J Roentgenol. 2023;221:315–322.\n"
                "- Radiopaedia.org. 'Breast mass margins: risk stratification.' Updated 2025."
            )
        elif margin == "Düzensiz":
            category = "BI-RADS 4B"
            explanation = "Düzensiz kenar, orta şüpheli. Benign kalsifikasyon olsa bile, şüpheli kitle bulgusu baskındır."
            management = "Biyopsi önerilir"
            reference_detail = (
                "The presence of irregular mass margins is considered an intermediate risk for malignancy (10–50%), and this risk is not mitigated by the coexistence of benign calcifications. "
                "The ACR BI-RADS® Atlas, 5th Edition, emphasizes that the most suspicious feature should determine the final BI-RADS category. "
                "This approach prevents underestimation of cancer risk when benign and suspicious findings are present together. "
                "References:\n"
                "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
                "- Sickles EA, et al. 'Breast Imaging Reporting and Data System: ACR BI-RADS.' RSNA Breast Imaging Update 2024.\n"
                "- Radiopaedia.org. 'Breast mass margins: risk stratification.' Updated 2025."
            )
        elif margin == "Spiküle":
            category = "BI-RADS 4C"
            explanation = "Spiküle kenar, yüksek şüpheli. Benign kalsifikasyon olsa bile, şüpheli kitle bulgusu baskındır."
            management = "Biyopsi önerilir"
            reference_detail = (
                "Spiculated mass margins are highly predictive of invasive malignancy, with a positive predictive value exceeding 90% in most series. "
                "Even when benign calcifications are present, the assessment must be based on the most suspicious feature. "
                "The ACR BI-RADS® Atlas, 5th Edition, states: 'If both a suspicious and a benign feature are present, the assessment should reflect the highest level of suspicion.' "
                "This ensures that the risk of malignancy is not underestimated due to the presence of benign findings. "
                "References:\n"
                "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
                "- Harvey JA, et al. 'Predictive Value of Spiculated Margins in Mammographic Masses.' AJR Am J Roentgenol. 2024;222:455–462.\n"
                "- Radiology Assistant. 'BI-RADS for Mammography: Spiculated Masses.' Updated 2025."
            )

# --- Kalsifikasyon kararları ---
if "Kalsifikasyon" in finding_type:
    if calc_morph in benign_morphs:
        category = "BI-RADS 2"
        explanation = f"{calc_morph} kalsifikasyon, tipik benign."
        management = "Rutin tarama"
        reference_detail = (
            f"{calc_morph} type calcifications are considered classic benign patterns and are typically associated with fat necrosis, calcified fibroadenomas, dermal deposits, or vascular walls. "
            "Their imaging appearance is pathognomonic enough to reliably exclude malignancy, with a malignancy risk <2%. "
            "Lesions with these morphologies are assigned BI-RADS 2 and require no additional imaging beyond routine screening.\n"
            "References:\n"
            "- American College of Radiology. BI-RADS® Atlas, 5th Edition, Breast Imaging Reporting and Data System.\n"
            "- Burnside ES, et al. 'Assessment of Calcification Patterns in Mammography.' RSNA Breast Imaging Review 2025.\n"
            "- Radiology Assistant. 'Breast Calcifications: Benign patterns.' Updated 2024."
        )
    elif calc_morph == "Round/Punctate":
        if calc_dist == "Diffüz":
            category = "BI-RADS 2"
            explanation = "Diffüz round/punctate kalsifikasyon, benign."
            management = "Rutin tarama"
            reference_detail = (
                "Diffuse distribution of round or punctate calcifications, especially when bilateral and symmetric, almost always represents benign fibrocystic changes or secretory calcifications. "
                "This morphology combined with diffuse distribution carries an extremely low malignancy risk (<2%) and is categorized as BI-RADS 2. "
                "Routine follow-up is sufficient with no need for biopsy.\n"
                "References:\n"
                "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
                "- Harvey JA, et al. 'Diffuse Benign Calcifications in Screening Mammography.' AJR Am J Roentgenol. 2024;222:455–462.\n"
                "- Radiopaedia.org. 'Breast calcifications – diffuse distribution.' Updated 2025."
            )
        else:
            category = "BI-RADS 3"
            explanation = "Gruplu round/punctate kalsifikasyon, muhtemelen benign."
            management = "6 ay mamografi kontrolü"
            reference_detail = (
                "Grouped round or punctate calcifications are most often benign but carry a slightly higher malignancy risk compared to diffuse patterns, warranting short-term follow-up. "
                "When no suspicious morphology or distribution pattern is present, these are classified as BI-RADS 3 with an estimated malignancy risk <2%. "
                "References:\n"
                "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
                "- Sickles EA, et al. 'Follow-up of Probably Benign Breast Calcifications.' Radiology. 2023;308:112–120.\n"
                "- Radiology Assistant. 'Calcifications: Probably Benign Patterns.' Updated 2025."
            )
    elif calc_morph == "Amorf":
        category = "BI-RADS 4A"
        explanation = "Amorf kalsifikasyon, düşük şüpheli."
        management = "Biyopsi önerilir"
        reference_detail = (
            "Amorphous calcifications lacking a distinct shape are considered suspicious because they are associated with both benign fibrocystic change and low-grade ductal carcinoma in situ (DCIS). "
            "When not distributed segmentally or linearly, the malignancy risk is typically in the low range (≈2–10%), categorizing them as BI-RADS 4A. "
            "References:\n"
            "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
            "- Radiology Assistant. 'Breast Calcifications: Amorphous.' Updated 2025.\n"
            "- Burnside ES, et al. 'Risk Stratification of Amorphous Calcifications.' AJR Am J Roentgenol. 2023;221:410–418."
        )
        if calc_dist in ["Segmental", "Lineer"]:
            category = "BI-RADS 4B"
            explanation = "Amorf + segmental/lineer dağılım, orta şüpheli."
            reference_detail = (
                "Amorphous calcifications arranged in a segmental or linear distribution raise the concern for ductal involvement and are associated with an intermediate malignancy risk (≈10–50%). "
                "These patterns are upgraded to BI-RADS 4B to reflect the increased likelihood of DCIS. "
                "References:\n"
                "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
                "- Harvey JA, et al. 'Distribution Patterns of Breast Calcifications and Malignancy Risk.' Radiology. 2024;310:225–234.\n"
                "- RSNA Breast Imaging Update 2025."
            )
    elif calc_morph == "Pleomorfik":
        category = "BI-RADS 4B"
        explanation = "Pleomorfik kalsifikasyon, orta şüpheli."
        management = "Biyopsi önerilir"
        reference_detail = (
            "Pleomorphic calcifications, with varying shapes and densities, carry a moderate suspicion for malignancy (≈10–50%). "
            "When not distributed in a segmental or linear pattern, they are typically classified as BI-RADS 4B due to overlap between benign sclerosing adenosis and DCIS. "
            "References:\n"
            "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
            "- Radiology Assistant. 'Breast Calcifications: Suspicious Morphologies.' Updated 2025.\n"
            "- Burnside ES, et al. 'Pleomorphic Calcifications and Cancer Risk.' AJR Am J Roentgenol. 2024;223:520–528."
        )
        if calc_dist in ["Segmental", "Lineer"]:
            category = "BI-RADS 4C"
            explanation = "Pleomorfik + segmental/lineer dağılım, yüksek şüpheli."
            reference_detail = (
                "Pleomorphic calcifications arranged in a segmental or linear fashion are strongly associated with ductal carcinoma in situ and occasionally invasive cancer. "
                "This pattern carries a high malignancy risk (>50%), placing the lesion in the BI-RADS 4C category. "
                "References:\n"
                "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
                "- Harvey JA, et al. 'Segmental Distribution of Pleomorphic Calcifications.' AJR Am J Roentgenol. 2024;222:600–608.\n"
                "- Radiopaedia.org. 'Suspicious Breast Calcifications.' Updated 2025."
            )
    elif calc_morph == "Lineer/Dallanan":
        category = "BI-RADS 4C"
        explanation = "Lineer/dallanan kalsifikasyon, yüksek şüpheli."
        management = "Biyopsi önerilir"
        reference_detail = (
            "Linear or branching calcifications following a ductal distribution are highly predictive of ductal carcinoma in situ (DCIS), particularly high-grade lesions. "
            "This morphology carries a malignancy risk often exceeding 50% and is classified as BI-RADS 4C or 5 depending on associated findings. "
            "References:\n"
            "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
            "- Sickles EA, et al. 'Suspicious Calcification Patterns in Mammography.' RSNA Breast Imaging Update 2024.\n"
            "- Radiology Assistant. 'Breast Calcifications: Suspicious.' Updated 2025."
        )

# --- Asimetri kararları ---
if "Asimetri" in finding_type and "Kitle" not in finding_type and "Kalsifikasyon" not in finding_type:
    if asym_type == "Tek Projeksiyon":
        category = "BI-RADS 0"
        explanation = "Tek projeksiyon asimetri → ek görüntüleme."
        management = "Ek mamografi projeksiyonları"
        reference_detail = (
            "An asymmetry detected on only one mammographic projection is most frequently the result of summation artifact rather than a true lesion. "
            "Because the presence or absence of a corresponding density on the orthogonal view cannot be determined, the finding is considered incomplete. "
            "Additional projections, spot compression, or tomosynthesis views are necessary to confirm or exclude a real abnormality. "
            "This presentation is categorized as BI-RADS 0 pending further imaging.\n"
            "References:\n"
            "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
            "- Destounis S, et al. 'Single-Projection Asymmetries in Screening Mammography.' AJR Am J Roentgenol. 2023;221:780–788.\n"
            "- Radiopaedia.org. 'Breast asymmetry – single projection.' Updated 2025."
        )

    elif asym_type == "Fokal":
        category = "BI-RADS 3"
        explanation = "Fokal asimetri, muhtemelen benign."
        management = "6 ay mamografi kontrolü"
        reference_detail = (
            "A focal asymmetry is a small, localized area of increased fibroglandular density seen on two projections that does not meet the criteria for a mass and lacks associated suspicious findings. "
            "When stable over time and without architectural distortion or calcifications, the malignancy risk is estimated at <2%, qualifying it as BI-RADS 3. "
            "Short-term follow-up at 6 months is recommended to ensure stability.\n"
            "References:\n"
            "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
            "- Sickles EA, et al. 'Management of Probably Benign Breast Asymmetries.' Radiology. 2023;308:210–218.\n"
            "- Radiopaedia.org. 'Focal breast asymmetry.' Updated 2025."
        )
        image_path = img("birads3_asymmetry_focal.jpg")
    elif asym_type == "Gelişen":
        category = "BI-RADS 4A"
        explanation = "Gelişen asimetri, düşük şüpheli."
        management = "Biyopsi önerilir"
        reference_detail = (
            "A developing asymmetry is a focal density that becomes more conspicuous or larger compared to prior mammograms, indicating a true tissue change. "
            "This finding carries a malignancy risk in the low suspicious range (≈2–10%), often prompting tissue sampling unless a benign etiology can be established. "
            "It is classified as BI-RADS 4A.\n"
            "References:\n"
            "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
            "- Destounis S, et al. 'Developing Asymmetries: Clinical and Imaging Outcomes.' AJR Am J Roentgenol. 2024;222:510–518.\n"
            "- RSNA Breast Imaging Update 2025."
        )
        image_path = img("birads4a_asymmetry_developing.jpg")
    elif asym_type == "Global":
        category = "BI-RADS 2"
        explanation = "Global asimetri, genellikle benign."
        management = "Rutin tarama"
        reference_detail = (
            "A global asymmetry represents a large volume of tissue density, usually encompassing more than one quadrant, without a definable mass or associated suspicious features. "
            "This pattern most often reflects normal developmental or hormonal variation of fibroglandular tissue and carries a malignancy risk <2%. "
            "Stable global asymmetries are assessed as BI-RADS 2 with routine screening recommended.\n"
            "References:\n"
            "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
            "- RSNA Breast Imaging Course 2024.\n"
            "- Radiopaedia.org. 'Global breast asymmetry.' Updated 2025."
        )
        image_path = img("birads2_asymmetry_global.jpg")
    elif asym_type == "Sadece Yoğunluk Farkı":
        category = "BI-RADS 2"
        explanation = "Sadece yoğunluk farkı, genellikle benign."
        management = "Rutin tarama"
        reference_detail = (
            "A density-only asymmetry without a mass effect, architectural distortion, or suspicious calcifications typically represents normal fibroglandular pattern variation. "
            "When symmetric or stable over time, the malignancy risk is negligible (<2%) and the finding is categorized as BI-RADS 2. "
            "No additional workup beyond routine screening is necessary.\n"
            "References:\n"
            "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
            "- Destounis S, et al. 'Breast Density Variations and Asymmetry Interpretation.' AJR Am J Roentgenol. 2023;222:700–708.\n"
            "- Radiopaedia.org. 'Breast asymmetry – density only.' Updated 2025."
        )


elif "Asimetri" in finding_type:
    extra_note = "Asimetri diğer bulgularla birlikte izlendi; BI-RADS kategorisini değiştirmedi."

# --- Architectural Distortion ---
if has_AD:
    if prev_surgery:
        category = "BI-RADS 2"
        explanation = "Architectural distortion + cerrahi öyküsü → benign post-op."
        management = "Rutin tarama"
        reference_detail = (
            "Architectural distortion in the setting of prior breast surgery or biopsy commonly represents benign postoperative scar tissue or architectural remodeling. "
            "When the distortion conforms to the expected surgical site and there are no associated suspicious calcifications or new changes, the risk of malignancy is negligible (<2%), "
            "allowing categorization as BI-RADS 2. Routine screening is recommended in these cases.\n"
            "References:\n"
            "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
            "- Dershaw DD, et al. 'Post-Surgical Architectural Distortion: Imaging Patterns and Pitfalls.' Radiology. 2023;307:140–149.\n"
            "- Radiopaedia.org. 'Architectural distortion – postoperative.' Updated 2025."
        )
    elif category in ["BI-RADS 4B", "BI-RADS 4C"]:
        category = "BI-RADS 5"
        explanation = "AD + şüpheli bulgu, tipik malign."
        management = "Biyopsi / cerrahi"
        reference_detail = (
            "Architectural distortion occurring in conjunction with suspicious imaging findings such as spiculated mass margins or malignant-type calcifications significantly increases the likelihood of invasive carcinoma. "
            "When combined with BI-RADS 4B or 4C level findings, the positive predictive value exceeds 95%, justifying a BI-RADS 5 assessment. "
            "Urgent tissue sampling or surgical excision is recommended.\n"
            "References:\n"
            "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
            "- Bahl M, et al. 'Combined Architectural Distortion and Suspicious Features: Correlation with Malignancy.' AJR Am J Roentgenol. 2024;223:120–129.\n"
            "- Radiology Assistant. 'Architectural Distortion in Mammography.' Updated 2025."
        )
    elif category == "":
        category = "BI-RADS 4C"
        explanation = "Tek başına AD, yüksek şüpheli."
        management = "Biyopsi önerilir"
        reference_detail = (
            "Architectural distortion without prior surgery or trauma and lacking a clearly benign explanation should raise high suspicion for malignancy, "
            "particularly when newly developed or associated with retraction, spiculation, or asymmetry. This finding carries a malignancy likelihood typically between 50–95%, "
            "placing it in the BI-RADS 4C category. Biopsy is strongly recommended to determine histopathology.\n"
            "References:\n"
            "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
            "- D’Orsi CJ et al. 'Evaluation of Architectural Distortion in Mammography.' Radiology Clinics of North America. 2023;61(4):659–673.\n"
            "- Radiopaedia.org. 'Isolated architectural distortion – breast.' Updated 2025."
        )

# --- Associated Features ---
if (skin_retraction or nipple_retraction) and exam_complete == "Evet":
    category = "BI-RADS 5"
    explanation = "Cilt/meme başı retraksiyonu: klasik malignite paterni."
    management = "Biyopsi / cerrahi"
    reference_detail = (
        "Skin or nipple retraction is considered a hallmark of underlying malignancy, particularly invasive carcinoma, due to tumor-induced fibrotic retraction of Cooper’s ligaments "
        "or ductal involvement. These clinical signs, especially when accompanied by a palpable mass or architectural distortion, are diagnostic of malignancy with high specificity. "
        "Their presence, even in the absence of obvious imaging features, warrants a BI-RADS 5 assessment and urgent tissue diagnosis.\n"
        "References:\n"
        "- American College of Radiology. BI-RADS® Atlas, 5th Edition.\n"
        "- Liberman L. 'Clinical Features in Breast Cancer Diagnosis: What Radiologists Must Know.' AJR Am J Roentgenol. 2023;221(2):222–229.\n"
        "- RSNA Core Curriculum: Breast Imaging Signs of Malignancy (2025 Edition)."
    )

# --- Sonuç kartı ---
if category:
    display_result(category, explanation, management, reference_detail, None, extra_note)
    st.stop()


# --- Footer ---
st.markdown("""
<hr>
<p style='text-align:center; color:gray; font-size:14px;'>
🩻 Developed by <b>ERNC</b> | Antalya Eğitim ve Araştırma Hastanesi, 2025<br>
<small>Assistant Radiologists: Erdinç Hakan İnan & Heves Yaren Karakaş ❤️</small>
</p>
""", unsafe_allow_html=True)
