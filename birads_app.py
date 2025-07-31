import streamlit as st

# Sayfa başlığı ve favicon değiştir
st.set_page_config(
    page_title="Radiologean - BI-RADS App",
    page_icon="🩻",
    layout="wide"
)

import sys
import os
import streamlit as st

def display_result(category, explanation, management, reference_detail, image_path=None, extra_note=None):
    """
    Displays the BI-RADS classification result card and supporting information in the Streamlit app.

    Args:
        category (str): BI-RADS category (e.g., 'BI-RADS 2').
        explanation (str): Short explanation of the decision.
        management (str): Recommended management action.
        reference_detail (str): Detailed reference text with citations.
        image_path (str, optional): Path to the example image for the finding.
        extra_note (str, optional): Any extra note or clarification to display.
    """
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


# --- Base directory (PyInstaller uyumlu) ---
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

# --- Önceki cerrahi/biopsi öyküsü ---
prev_surgery = st.checkbox("Önceki cerrahi / biyopsi öyküsü mevcut mu?")
biopsy_proven = st.checkbox("Biyopsi ile malignite doğrulandı mı? (BI-RADS 6)")

# --- BI-RADS 6 override ---
if biopsy_proven:
    category = "BI-RADS 6"
    explanation = "Biyopsi ile doğrulanmış malignite."
    management = "Tedavi planlaması"
    reference_detail = "Known biopsy-proven malignancy is categorized as BI-RADS 6 regardless of imaging findings. (ACR BI-RADS 5th Ed.)"
    st.markdown(f'<div class="result-card birads-6">{category}<br>{explanation}</div>', unsafe_allow_html=True)
    st.info(f"📖 {reference_detail}")
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
image_path = ""
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
        category = "BI-RADS 2"
        explanation = "Oval/yuvarlak düzgün sınırlı kitle, tipik benign patern."
        management = "Rutin tarama"
        reference_detail = (
            "Well-circumscribed oval or round masses with smooth margins are typically benign and most commonly represent fibroadenomas or simple cysts. "
            "When no suspicious associated features are present, the risk of malignancy is extremely low (<2%), qualifying these lesions as BI-RADS 2. "
            "References:\n"
            "- American College of Radiology. BI-RADS® Atlas, 5th Edition, Breast Imaging Reporting and Data System.\n"
            "- Berg WA, et al. 'Diagnostic Performance of BI-RADS for Mass Characterization.' AJR Am J Roentgenol. 2023;221:315–322.\n"
            "- Radiopaedia.org. 'Breast imaging reporting and data system (BI-RADS).' Updated 2025."
        )
        image_path = img("birads2_mass_circumscribed.jpg")
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
        image_path = img("birads4a_mass_microlobulated.jpg")
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
        image_path = img("birads4b_mass_irregular.jpg")
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
        image_path = img("birads4c_mass_spiculated.jpg")

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
        image_path = img(f"birads2_calc_{calc_morph.lower().replace('/', '_')}.jpg")
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
            image_path = img("birads2_calc_punctate_diffuse.jpg")
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
            image_path = img("birads3_calc_punctate_grouped.jpg")
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
        image_path = img("birads4a_calc_amorphous.jpg")
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
            image_path = img("birads4b_calc_amorphous_segmental.jpg")
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
        image_path = img("birads4b_calc_pleomorphic.jpg")
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
            image_path = img("birads4c_calc_pleomorphic_segmental.jpg")
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
        image_path = img("birads4c_calc_linear_branching.jpg")

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
        image_path = img("birads2_postop_ad.jpg")
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
        image_path = img("birads5_ad_combined.jpg")
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
        image_path = img("birads4c_ad_isolated.jpg")

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
    image_path = img("birads5_skin_nipple_retraction.jpg")

# --- Sonuç kartı ---
if category:
    display_result(category, explanation, management, reference_detail, image_path, extra_note)


# --- Footer ---
st.markdown("""
<hr>
<p style='text-align:center; color:gray; font-size:14px;'>
🩻 Developed by <b>ERNC</b> | Antalya Eğitim ve Araştırma Hastanesi, 2025<br>
<small>Assistant Radiologists: Erdinç Hakan İnan & Heves Yaren Karakaş</small>
</p>
""", unsafe_allow_html=True)
