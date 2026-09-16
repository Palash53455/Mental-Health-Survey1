"""
Mental Health in Tech Survey — Interactive EDA Dashboard
Run locally with: streamlit run app.py
"""
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Mental Health in Tech Survey", layout="wide", page_icon="🧠")
sns.set_style("whitegrid")

ORDER_LEAVE = ['Very difficult', 'Somewhat difficult', "Don't know", 'Somewhat easy', 'Very easy']
ORDER_INTERFERE = ['Never', 'Rarely', 'Sometimes', 'Often', 'Not applicable']
ORDER_SIZE = ['1-5', '6-25', '26-100', '100-500', '500-1000', 'More than 1000']


@st.cache_data
def load_and_clean(path="survey.csv"):
    df = pd.read_csv(path)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    # Age cleaning
    df.loc[(df["Age"] < 15) | (df["Age"] > 80), "Age"] = np.nan
    df["Age"] = df["Age"].fillna(df["Age"].median()).astype(int)

    # Gender cleaning
    def clean_gender(g):
        g = str(g).strip().lower()
        male_set = {'male', 'm', 'man', 'cis male', 'cis man', 'male (cis)', 'make', 'maile', 'mal', 'malr',
                    'mail', 'msle', 'male-ish', 'guy (-ish) ^_^', 'male leaning androgynous',
                    'ostensibly male, unsure what that really means', 'cis-female/femme'}
        female_set = {'female', 'f', 'woman', 'cis female', 'femake', 'femail',
                      'female (cis)', 'trans-female', 'female (trans)', 'trans woman'}
        if g in male_set:
            return 'Male'
        if g in female_set:
            return 'Female'
        return 'Other'

    df["Gender"] = df["Gender"].apply(clean_gender)
    df["self_employed"] = df["self_employed"].fillna(df["self_employed"].mode()[0])
    df["work_interfere"] = df["work_interfere"].fillna("Not applicable")
    df = df.drop(columns=["comments", "state", "Timestamp"])

    top_countries = df["Country"].value_counts().nlargest(10).index
    df["Country_grouped"] = np.where(df["Country"].isin(top_countries), df["Country"], "Other")
    df = df.drop_duplicates().reset_index(drop=True)
    return df


def treatment_rate_chart(df, col, order=None, title="", horizontal=False):
    rates = df.groupby(col)["treatment"].apply(lambda s: (s == "Yes").mean() * 100)
    if order:
        rates = rates.reindex([o for o in order if o in rates.index])
    fig, ax = plt.subplots(figsize=(7, 4.5))
    if horizontal:
        rates.sort_values().plot(kind="barh", ax=ax, color=sns.color_palette("viridis", len(rates)))
        ax.set_xlabel("% Sought Treatment")
    else:
        rates.plot(kind="bar", ax=ax, color=sns.color_palette("viridis", len(rates)))
        ax.set_ylabel("% Sought Treatment")
        plt.xticks(rotation=30, ha="right")
    ax.set_title(title)
    fig.tight_layout()
    return fig


def main():
    st.title("🧠 Mental Health in Tech Survey — Interactive EDA")
    st.caption(
        "OSMI 2014 survey of tech-industry employees. Explore how demographics and workplace "
        "policies relate to mental-health treatment-seeking and perceived stigma."
    )

    df_full = load_and_clean()

    # ---------------- Sidebar filters ----------------
    st.sidebar.header("Filters")
    genders = st.sidebar.multiselect("Gender", sorted(df_full["Gender"].unique()), default=list(sorted(df_full["Gender"].unique())))
    countries = st.sidebar.multiselect(
        "Country (top 10 + Other)",
        sorted(df_full["Country_grouped"].unique()),
        default=list(sorted(df_full["Country_grouped"].unique())),
    )
    age_min, age_max = int(df_full["Age"].min()), int(df_full["Age"].max())
    age_range = st.sidebar.slider("Age range", age_min, age_max, (age_min, age_max))
    company_sizes = st.sidebar.multiselect(
        "Company size", [s for s in ORDER_SIZE if s in df_full["no_employees"].unique()],
        default=[s for s in ORDER_SIZE if s in df_full["no_employees"].unique()],
    )
    remote_filter = st.sidebar.multiselect("Remote work", sorted(df_full["remote_work"].unique()), default=list(sorted(df_full["remote_work"].unique())))

    df = df_full[
        df_full["Gender"].isin(genders)
        & df_full["Country_grouped"].isin(countries)
        & df_full["Age"].between(age_range[0], age_range[1])
        & df_full["no_employees"].isin(company_sizes)
        & df_full["remote_work"].isin(remote_filter)
    ]

    st.sidebar.markdown(f"**{len(df)} / {len(df_full)}** respondents match the current filters.")

    if len(df) == 0:
        st.warning("No respondents match the current filters. Please broaden your selection.")
        return

    # ---------------- KPI row ----------------
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Respondents", len(df))
    c2.metric("Sought Treatment", f"{(df['treatment']=='Yes').mean()*100:.1f}%")
    c3.metric("Family History", f"{(df['family_history']=='Yes').mean()*100:.1f}%")
    c4.metric("Median Age", int(df["Age"].median()))

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🔍 Treatment Drivers", "🏢 Workplace Factors", "🗃️ Raw Data"])

    # ---------------- Tab 1: Overview ----------------
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.histplot(df["Age"], bins=25, kde=True, color="steelblue", ax=ax)
            ax.set_title("Age Distribution")
            st.pyplot(fig)
        with col2:
            fig, ax = plt.subplots(figsize=(6, 4))
            order = df["Gender"].value_counts().index
            sns.countplot(x="Gender", data=df, order=order, palette="mako", ax=ax)
            ax.set_title("Gender Distribution")
            st.pyplot(fig)

        col3, col4 = st.columns(2)
        with col3:
            fig, ax = plt.subplots(figsize=(6, 4))
            df["treatment"].value_counts().plot(
                kind="pie", autopct="%1.1f%%", colors=["#4c72b0", "#dd8452"], ax=ax, ylabel=""
            )
            ax.set_title("Sought Treatment?")
            st.pyplot(fig)
        with col4:
            fig, ax = plt.subplots(figsize=(6, 4))
            top = df["Country"].value_counts().nlargest(10)
            sns.barplot(x=top.values, y=top.index, palette="viridis", ax=ax)
            ax.set_title("Top Countries")
            ax.set_xlabel("Respondents")
            st.pyplot(fig)

    # ---------------- Tab 2: Treatment Drivers ----------------
    with tab2:
        st.subheader("What relates to treatment-seeking?")
        col1, col2 = st.columns(2)
        with col1:
            st.pyplot(treatment_rate_chart(df, "family_history", title="Treatment Rate by Family History"))
        with col2:
            st.pyplot(treatment_rate_chart(df, "Gender", title="Treatment Rate by Gender"))

        st.pyplot(treatment_rate_chart(df, "work_interfere", order=ORDER_INTERFERE, title="Treatment Rate by Work Interference Level"))

        col3, col4 = st.columns(2)
        with col3:
            fig, ax = plt.subplots(figsize=(6, 4.5))
            sns.violinplot(x="treatment", y="Age", data=df, palette="Set2", ax=ax)
            ax.set_title("Age Distribution by Treatment-Seeking")
            st.pyplot(fig)
        with col4:
            fig, ax = plt.subplots(figsize=(7, 5))
            enc_cols = ["Gender", "family_history", "treatment", "work_interfere", "no_employees",
                        "remote_work", "tech_company", "benefits", "care_options", "wellness_program",
                        "seek_help", "anonymity", "leave", "mental_health_consequence",
                        "phys_health_consequence", "obs_consequence"]
            from sklearn.preprocessing import LabelEncoder
            df_enc = df[enc_cols + ["Age"]].copy()
            for c in enc_cols:
                df_enc[c] = LabelEncoder().fit_transform(df_enc[c])
            sns.heatmap(df_enc.corr(), cmap="coolwarm", center=0, ax=ax)
            ax.set_title("Correlation Heatmap")
            st.pyplot(fig)

    # ---------------- Tab 3: Workplace Factors ----------------
    with tab3:
        st.subheader("Employer policy and perceived stigma")
        col1, col2 = st.columns(2)
        with col1:
            st.pyplot(treatment_rate_chart(df, "benefits", title="Treatment Rate by Mental Health Benefits"))
        with col2:
            st.pyplot(treatment_rate_chart(df, "care_options", title="Treatment Rate by Awareness of Care Options"))

        col3, col4 = st.columns(2)
        with col3:
            st.pyplot(treatment_rate_chart(df, "anonymity", title="Treatment Rate by Anonymity Protection"))
        with col4:
            st.pyplot(treatment_rate_chart(df, "leave", order=ORDER_LEAVE, title="Treatment Rate by Ease of Leave"))

        st.pyplot(treatment_rate_chart(df, "no_employees", order=ORDER_SIZE, title="Treatment Rate by Company Size"))

        fig, ax = plt.subplots(figsize=(8, 4.5))
        mh = df["mental_health_consequence"].value_counts(normalize=True) * 100
        ph = df["phys_health_consequence"].value_counts(normalize=True) * 100
        comp = pd.DataFrame({"Mental Health": mh, "Physical Health": ph}).reindex(["Yes", "Maybe", "No"])
        comp.plot(kind="bar", ax=ax, color=["#c44e52", "#4c72b0"])
        ax.set_title("Perceived Negative Consequences: Mental vs Physical Health Disclosure")
        ax.set_ylabel("% of Respondents")
        plt.xticks(rotation=0)
        st.pyplot(fig)

    # ---------------- Tab 4: Raw Data ----------------
    with tab4:
        st.subheader("Filtered dataset")
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "Download filtered data as CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="filtered_mental_health_survey.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()
