from simple_salesforce import Salesforce
import pandas as pd

class SFDataManager:

    def __init__(self, username, password, security_token, isSandbox=False):
        self.username = username
        self.password = password
        self.token = security_token
        self.isSandbox = isSandbox
        self.sf = None

    def login(self):
        """
        Creates a session with the salesforce rest api.
        """
        self.sf = Salesforce(
            username = self.username, 
            password = self.password, 
            security_token = self.token, 
            domain = "test" if self.isSandbox else None
        )

    def getCases(self):
        """
        Returns a dataframe of sObjects of type Case from the Salesforce database
        """
        if not self.sf: return

        df = pd.DataFrame(self.sf.query('SELECT Id, Subject FROM Case'))
        print(df)
        return df

    def addEmailToCases(self, dataFile, rowRange, caseIds, textColName):
        """
        dataFile: string - Relative file path to CSV file
        rowRange: tuple (start, end) - Inclusive row range in the CSV. Subtract 1 from line length if there are headers in the file.
        caseIds: List of Salesforce ids of the case objects
        textColName: str - Name of the column that contains the textual data
        """

        if not self.sf: return

        start, end = rowRange
        print(f"Adding {end - start} emails to cases")

        emails = []
        df = pd.read_csv(dataFile)
        
        for i in range(start, min(end+1, len(df))):
            emails.append({
                'Subject': 'Python Test Data Email', 
                'TextBody': df[textColName][i], 
                'ParentId': caseIds[i % len(caseIds)]
            })
        print(emails)
        res = self.sf.bulk.EmailMessage.insert(emails)
        print(res)