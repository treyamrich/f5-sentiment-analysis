import os
from dotenv import load_dotenv
from sfdatamanager import SFDataManager

#Load environment variables
load_dotenv()
UNAME = os.getenv("USERNAME")
PW = os.getenv("PASSWORD")
TOK = os.getenv("TOKEN")

TEST_DATA = "sentiment_data/test.csv"
MODEL_CMP_DATA = "model_output.txt"

#Get case ids
with open("aux_data/case-ids.txt", "r") as f:
    caseIds = [id.strip() for id in f]


sfdm = SFDataManager(UNAME, PW, TOK, True)

#Recently added rows 0-200 inclusive
#sfdm.addEmailToCases(TEST_DATA, (0, 4000), caseIds, "text", "sentiment")
#sfdm.delEmails(caseIds)
model_metrics = sfdm.getF1ScoreFromFile(MODEL_CMP_DATA)
model_metrics.print_all_metrics()