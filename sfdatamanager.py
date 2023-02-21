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

    def addEmailToCases(self, dataFile, rowRange, caseIds, textColName, sentimentColName):
        """
        dataFile: string - Relative file path to CSV file
        rowRange: tuple (start, end) - Inclusive row range in the CSV. Subtract 1 from line length if there are headers in the file.
        caseIds: List of Salesforce ids of the case objects
        textColName: str - Name of the column that contains the textual data

        returns: query result
        """

        if not self.sf: return

        start, end = rowRange
        print(f"Adding {end - start} emails to cases")

        #Create emails using the data, assigning a partial-random id
        sentimentMap = {'negative': -1, 'neutral': 0, 'positive': 1}
        emails = []
        df = pd.read_csv(dataFile)
        for i in range(start, min(end+1, len(df))):
            emails.append({
                'Subject': 'Python Test Data Email', 
                'TextBody': df[textColName][i], 
                'ParentId': caseIds[i % len(caseIds)],
                'Incoming': True,
                'Sentiment__c': sentimentMap[df[sentimentColName][i]]
            })
        
        res = self.sf.bulk.EmailMessage.insert(emails)
        print(res)
        return res
    
    def delEmails(self, caseIds):
        """
        Deletes EmailMessage sObjects given a list of ParentIds of Cases.

        caseIds: list of parent id cases

        returns: query result
        """
        if not self.sf: return


        #Form a tuple of ids
        ids = tuple(caseIds)
        
        #Get emails with parentId = caseId_i
        emails = pd.DataFrame(
            self.sf.query(
                'SELECT Id, Subject, ParentId FROM EmailMessage WHERE ParentId IN ' + str(ids)
            )
        )
        emailIds = [{'Id': email['Id']} for email in emails['records']]

        #Delete emails by bulk
        print(f"Deleting {len(emailIds)} emails from the org.")
        res = self.sf.bulk.EmailMessage.delete(emailIds)
        print(res)
        return res