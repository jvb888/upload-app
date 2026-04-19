import streamlit as st
import pandas as pd
import io

st.set_page_config(
    page_title="Patiëntgegevens",
    page_icon="🏥",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #0a1628 0%, #1a3a5c 100%);
        color: white;
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
    }

    .main-header h1 {
        font-size: 1.8rem;
        font-weight: 600;
        margin: 0 0 0.25rem 0;
        letter-spacing: -0.02em;
    }

    .main-header p {
        font-size: 0.9rem;
        opacity: 0.7;
        margin: 0;
        font-weight: 300;
    }

    .upload-zone {
        border: 2px dashed #378ADD;
        border-radius: 12px;
        padding: 3rem;
        text-align: center;
        background: #E6F1FB22;
        margin-bottom: 1.5rem;
    }

    .stat-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.25rem 1.5rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }

    .stat-card .number {
        font-size: 2rem;
        font-weight: 600;
        color: #185FA5;
        line-height: 1;
        margin-bottom: 0.25rem;
    }

    .stat-card .label {
        font-size: 0.8rem;
        color: #888780;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
    }

    .badge-valid {
        background: #EAF3DE;
        color: #3B6D11;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 500;
    }

    .badge-warning {
        background: #FAEEDA;
        color: #854F0B;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 500;
    }

    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }

    .section-title {
        font-size: 1rem;
        font-weight: 600;
        color: #2C2C2A;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #378ADD;
        display: inline-block;
    }

    div[data-testid="stFileUploader"] {
        border: none !important;
    }

    .error-box {
        background: #FCEBEB;
        border: 1px solid #F09595;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        color: #791F1F;
        font-size: 0.9rem;
    }

    .success-box {
        background: #EAF3DE;
        border: 1px solid #97C459;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        color: #27500A;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

EXPECTED_COLUMNS = {
    "Burgerservicenummer": str,
    "Patiënt ID": str,
    "Voornaam": str,
    "Tussenvoegsel": str,
    "Achternaam": str,
    "Geboortedatum": str,
    "Telefoonnummer": str,
}

COLUMN_ALIASES = {
    "burgerservicenummer": "Burgerservicenummer",
    "bsn": "Burgerservicenummer",
    "patiënt id": "Patiënt ID",
    "patient id": "Patiënt ID",
    "patientid": "Patiënt ID",
    "voornaam": "Voornaam",
    "tussenvoegsel": "Tussenvoegsel",
    "achternaam": "Achternaam",
    "geboortedatum": "Geboortedatum",
    "telefoonnummer": "Telefoonnummer",
    "telefoon": "Telefoonnummer",
    "phone": "Telefoonnummer",
}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    for col in df.columns:
        normalized = col.strip().lower()
        if normalized in COLUMN_ALIASES:
            rename_map[col] = COLUMN_ALIASES[normalized]
    return df.rename(columns=rename_map)


def validate_bsn(bsn: str) -> bool:
    """Elfproef voor BSN-validatie."""
    bsn = str(bsn).strip().zfill(9)
    if not bsn.isdigit() or len(bsn) != 9:
        return False
    total = sum(int(bsn[i]) * (9 - i) for i in range(8))
    total -= int(bsn[8])
    return total % 11 == 0


def load_csv(file) -> tuple[pd.DataFrame | None, list[str]]:
    errors = []
    try:
        content = file.read()
        for sep in [";", ",", "\t"]:
            try:
                df = pd.read_csv(io.BytesIO(content), sep=sep, dtype=str)
                if len(df.columns) > 1:
                    break
            except Exception:
                continue

        df = normalize_columns(df)
        df = df.fillna("")

        missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
        if missing:
            errors.append(f"Ontbrekende kolommen: {', '.join(missing)}")

        return df, errors
    except Exception as e:
        return None, [f"Fout bij inlezen: {str(e)}"]


st.markdown("""
<div class="main-header">
    <h1>🏥 Patiëntgegevens Viewer</h1>
    <p>Upload een CSV-bestand met fictieve patiëntgegevens om ze te bekijken en te valideren.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<p class="section-title">CSV-bestand uploaden</p>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Sleep een CSV-bestand hierheen of klik om te uploaden",
    type=["csv"],
    help="Ondersteunde kolommen: Burgerservicenummer, Patiënt ID, Voornaam, Tussenvoegsel, Achternaam, Geboortedatum, Telefoonnummer",
)

with st.expander("📋 Verwacht kolomformaat"):
    st.markdown("""
    | Kolom | Type | Opmerking |
    |-------|------|-----------|
    | `Burgerservicenummer` | Tekst | 9 cijfers, elfproef wordt uitgevoerd |
    | `Patiënt ID` | Tekst | Uniek ID per patiënt |
    | `Voornaam` | Tekst | |
    | `Tussenvoegsel` | Tekst | Mag leeg zijn |
    | `Achternaam` | Tekst | |
    | `Geboortedatum` | Tekst | Bijv. DD-MM-YYYY |
    | `Telefoonnummer` | Tekst | |

    > Scheidingsteken: komma (`,`) of puntkomma (`;`) worden automatisch herkend.
    """)

if uploaded_file is not None:
    df, errors = load_csv(uploaded_file)

    if errors:
        for err in errors:
            st.markdown(f'<div class="error-box">⚠️ {err}</div>', unsafe_allow_html=True)

    if df is not None:
        st.markdown("---")
        st.markdown('<p class="section-title">Overzicht</p>', unsafe_allow_html=True)

        total = len(df)
        valid_bsn = 0
        invalid_bsn = 0

        if "Burgerservicenummer" in df.columns:
            bsn_results = df["Burgerservicenummer"].apply(validate_bsn)
            valid_bsn = bsn_results.sum()
            invalid_bsn = total - valid_bsn

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(
                f'<div class="stat-card"><div class="number">{total}</div><div class="label">Patiënten</div></div>',
                unsafe_allow_html=True)
        with col2:
            st.markdown(
                f'<div class="stat-card"><div class="number">{len(df.columns)}</div><div class="label">Kolommen</div></div>',
                unsafe_allow_html=True)
        with col3:
            st.markdown(
                f'<div class="stat-card"><div class="number">{valid_bsn}</div><div class="label">Geldig BSN</div></div>',
                unsafe_allow_html=True)
        with col4:
            st.markdown(
                f'<div class="stat-card"><div class="number">{invalid_bsn}</div><div class="label">Ongeldig BSN</div></div>',
                unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if "Burgerservicenummer" in df.columns:
            df_display = df.copy()
            df_display["BSN Geldig"] = df["Burgerservicenummer"].apply(
                lambda x: "✓ Geldig" if validate_bsn(x) else "✗ Ongeldig"
            )

        st.markdown('<p class="section-title">Patiëntgegevens</p>', unsafe_allow_html=True)

        search = st.text_input("🔍 Zoeken op naam of ID", placeholder="Typ een naam of patiënt-ID...")

        df_filtered = df_display.copy() if "Burgerservicenummer" in df.columns else df.copy()

        if search:
            mask = df_filtered.apply(
                lambda row: row.astype(str).str.contains(search, case=False, na=False).any(),
                axis=1
            )
            df_filtered = df_filtered[mask]
            st.caption(f"{len(df_filtered)} resultaten gevonden voor '{search}'")

        st.dataframe(
            df_filtered,
            use_container_width=True,
            height=min(600, 80 + len(df_filtered) * 35),
            hide_index=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        csv_export = df.to_csv(index=False, sep=";").encode("utf-8")
        st.download_button(
            label="⬇️ Download gefilterde data als CSV",
            data=csv_export,
            file_name="patiëntgegevens_export.csv",
            mime="text/csv",
        )

else:
    st.markdown("""
    <div class="upload-zone">
        <div style="font-size: 2.5rem; margin-bottom: 0.75rem">📂</div>
        <div style="font-size: 1rem; font-weight: 500; color: #185FA5; margin-bottom: 0.25rem">Sleep een CSV-bestand hierheen</div>
        <div style="font-size: 0.85rem; color: #888780">of gebruik de knop hierboven om een bestand te selecteren</div>
    </div>
    """, unsafe_allow_html=True)

