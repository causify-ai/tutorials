# %%
import time
import os
import pandas as pd
import ck_marketing.linkedin.phantombuster_api as cmlpapap


# %%
# Set your LinkedIn session cookie.
os.environ["Phantom_API_KEY"] = 'Q98YT6duhMEm1HgyagbbZhy6DmPMvw4q2ZXGqvfqTFU' 

linkedin_session_cookie = os.getenv('Phantom_API_KEY')

# %%
data = {
    "companyName": ["Benchmark Capital", "Greylock Partners"],
    "SnQuery": [
        "https://www.linkedin.com/sales/search/people?query=(spellCorrectionEnabled%3Atrue%2CrecentSearchParam%3A(id%3A3566053282%2CdoLogHistory%3Atrue)%2Cfilters%3AList((type%3AFUNCTION%2Cvalues%3AList((id%3A12%2Ctext%3AHuman%2520Resources%2CselectionType%3AEXCLUDED)%2C(id%3A16%2Ctext%3AMedia%2520and%2520Communication%2CselectionType%3AEXCLUDED)%2C(id%3A1%2Ctext%3AAccounting%2CselectionType%3AEXCLUDED)%2C(id%3A15%2Ctext%3AMarketing%2CselectionType%3AEXCLUDED)%2C(id%3A18%2Ctext%3AOperations%2CselectionType%3AEXCLUDED)%2C(id%3A13%2Ctext%3AInformation%2520Technology%2CselectionType%3AEXCLUDED)))%2C(type%3AREGION%2Cvalues%3AList((id%3A103644278%2Ctext%3AUnited%2520States%2CselectionType%3AINCLUDED)))%2C(type%3ASENIORITY_LEVEL%2Cvalues%3AList((id%3A320%2Ctext%3AOwner%2520%252F%2520Partner%2CselectionType%3AINCLUDED)))%2C(type%3ACURRENT_COMPANY%2Cvalues%3AList((id%3Aurn%253Ali%253Aorganization%253A18077%2Ctext%3AGreylock%2CselectionType%3AINCLUDED))))%2Ckeywords%3APartner)&sessionId=9crXfVSbSneO74cLlQLLNg%3D%3D",
        "https://www.linkedin.com/sales/search/people?query=(spellCorrectionEnabled%3Atrue%2CrecentSearchParam%3A(id%3A3566053282%2CdoLogHistory%3Atrue)%2Cfilters%3AList((type%3AFUNCTION%2Cvalues%3AList((id%3A12%2Ctext%3AHuman%2520Resources%2CselectionType%3AEXCLUDED)%2C(id%3A16%2Ctext%3AMedia%2520and%2520Communication%2CselectionType%3AEXCLUDED)%2C(id%3A1%2Ctext%3AAccounting%2CselectionType%3AEXCLUDED)%2C(id%3A15%2Ctext%3AMarketing%2CselectionType%3AEXCLUDED)%2C(id%3A18%2Ctext%3AOperations%2CselectionType%3AEXCLUDED)%2C(id%3A13%2Ctext%3AInformation%2520Technology%2CselectionType%3AEXCLUDED)))%2C(type%3AREGION%2Cvalues%3AList((id%3A103644278%2Ctext%3AUnited%2520States%2CselectionType%3AINCLUDED)))%2C(type%3ASENIORITY_LEVEL%2Cvalues%3AList((id%3A320%2Ctext%3AOwner%2520%252F%2520Partner%2CselectionType%3AINCLUDED)))%2C(type%3ACURRENT_COMPANY%2Cvalues%3AList((id%3Aurn%253Ali%253Aorganization%253A18077%2Ctext%3AGreylock%2CselectionType%3AINCLUDED))))%2Ckeywords%3APartner)&sessionId=9crXfVSbSneO74cLlQLLNg%3D%3D"
    ]
}
df = pd.DataFrame(data)

# %%
phantom = cmlpapap.Phantom()

# %%
# Iterate over the rows of the DataFrame.
for index, row in df.iterrows():
    company_name = row['companyName']
    sn_query = row['SnQuery']
    # Create a unique agent name for this company.
    agent_name = f"{company_name}_SalesNav"
    print(f"Processing: {company_name}")
    # Step 1: Create the Phantom agent.
    response = phantom.create_sales_nav_phantom(
        agent_name=agent_name,
        sales_nav_query=sn_query,
        linkedin_session_cookie=linkedin_session_cookie,
    )
    agent_id = response.get("id")
    print(f"Agent created with ID: {agent_id}")
    # Step 2: Launch the agent and wait for results.
    try:
        print(f"Launching agent: {agent_name}")
        result_df = phantom.launch_and_get_df(agent_id)
        print(f"Results fetched for: {company_name}")
        # Save the results.
        result_df.to_csv(f"{company_name}_results.csv", index=False)
        print(f"Results saved for: {company_name}")

    except Exception as e:
        print(f"Error processing {company_name}: {e}")
        continue
    # Step 3: Delete the agent after processing.
    try:
        phantom.delete_phantom(agent_id)
        print(f"Agent {agent_name} deleted.")
    except Exception as e:
        print(f"Error deleting agent {agent_name}: {e}")
    time.sleep(5)



