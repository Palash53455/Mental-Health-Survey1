# Mental Health in Tech Survey — Streamlit Dashboard

Interactive EDA dashboard for the OSMI 2014 Mental Health in Tech Survey.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Make sure `survey.csv` is in the same folder as `app.py` (already included here).

## Deploy for free on Streamlit Community Cloud

1. Create a new GitHub repo and push these three files: `app.py`, `requirements.txt`, `survey.csv`.
2. Go to https://share.streamlit.io, sign in with GitHub.
3. Click **New app**, select your repo/branch, and set the main file path to `app.py`.
4. Click **Deploy**. Your app will be live at `https://<your-app-name>.streamlit.app`.

## What it does

- **Sidebar filters**: gender, country, age range, company size, remote-work status.
- **Overview tab**: age/gender distributions, treatment split, top countries.
- **Treatment Drivers tab**: treatment rate by family history, gender, work interference, age, plus a correlation heatmap — all recompute live as filters change.
- **Workplace Factors tab**: treatment rate by benefits, care options, anonymity, leave ease, company size, and the mental-vs-physical stigma comparison.
- **Raw Data tab**: view and download the currently filtered data as CSV.

The cleaning logic (Age outlier handling, Gender text consolidation, missing-value handling) matches the companion Jupyter notebook exactly, so results are consistent between the two deliverables.
