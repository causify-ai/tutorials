# %%
import gspread

print(gspread.__version__)

import gspread_pandas

print(gspread_pandas.__version__)

# %%
#!sudo /bin/bash -c "(source /venv/bin/activate; pip install --upgrade google-api-python-client)"

# %%
import importlib

import helpers.hgoogle_file_api as hgofiapi

importlib.reload(hgofiapi)

# %%
creds = hgofiapi.get_credentials()

# %%
creds

# %%
sheet_id = "13hAmJ58Ois4CcxDoeP-Pwu_JR8kb11wcGHEaDQ5h_Gg"

# %%
df_signalnfx = hgofiapi.read_google_sheet(sheet_id)

# %%
df_signalnfx.head()

# %%
import ck_marketing.hunterio.hunter_api as cmhuhuap

importlib.reload(cmhuhuap)

# %%
df_signalnfx[["firstName", "lastName"]] = df_signalnfx["fullName"].str.split(
    " ", n=1, expand=True
)

# %%
hgofiapi.write_sheet(df_signalnfx, sheet_id, "cleaned_profiles")

# %%
cmhuhuap.find_bulk_emails(
    df_signalnfx, "firstName", "lastName", "companyName", incremental=False
)

# %%
# df_signalnfx = df_signalnfx.drop(columns=["hunterio_email"])


# %%
df_signalnfx.head()

# %%
hgofiapi.write_sheet(df_signalnfx, sheet_id, "hunter_email")

# %%
incremental = False
# email = "hunterio_email"
email = "hunterio_email"
cmhuhuap.verify_bulk_emails(df_signalnfx, email, incremental=incremental)

# %%
df_signalnfx.head()


# %%
hgofiapi.write_sheet(df_signalnfx, sheet_id, "email_verification")

# %%
cmhuhuap.process(
    df_signalnfx,
    "firstName",
    "lastName",
    "companyName",
    "hunterio_email",
    "hunterio_verification",
    is_company=True,
)

# %%
df_signalnfx.head()
