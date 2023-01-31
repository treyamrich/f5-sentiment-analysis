import os
from dotenv import load_dotenv
from sfdatamanager import SFDataManager

#Load environment variables
load_dotenv()
UNAME = os.getenv("USERNAME")
PW = os.getenv("PASSWORD")
TOK = os.getenv("TOKEN")

TEST_DATA = "sentiment_data/test.csv"

#Get case ids
with open("aux_data/case-ids.txt", "r") as f:
    caseIds = [id.strip() for id in f]


sfdm = SFDataManager(UNAME, PW, TOK, True)
sfdm.login()

sfdm.addEmailToCases(TEST_DATA, (0, 200), caseIds, "text")