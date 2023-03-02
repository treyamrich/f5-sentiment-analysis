from simple_salesforce import Salesforce
import pandas as pd
from model_metrics import SentimentModelMetrics

class SFDataManager:

    def __init__(self, username, password, security_token, isSandbox=False):
        self.username = username
        self.password = password
        self.token = security_token
        self.isSandbox = isSandbox
        self.sf = None

        self.login()

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

        df = pd.DataFrame(self.sf.query('SELECT Id, Subject FROM Case'))
        return df
    
    def customQuery(self, query):
        return self.sf.query(query)
    
    def getEmails(self, caseIds):
        """
            Returns a datafrom of sObjects of type EmailMessage with the sentiment analysis and expected sentiment.
        """
        ids = tuple(caseIds)
        query = self.sf.query(
            'SELECT Sentiment__c, SentimentActual__c FROM EmailMessage WHERE ParentId IN ' + str(ids)
        )
        df = pd.DataFrame(query)
        return df
    def addEmailToCases(self, dataFile, rowRange, caseIds, textColName, sentimentColName):
        """
        dataFile: string - Relative file path to CSV file
        rowRange: tuple (start, end) - Inclusive row range in the CSV. Subtract 1 from line length if there are headers in the file.
        caseIds: List of Salesforce ids of the case objects
        textColName: str - Name of the column that contains the textual data

        returns: query result
        """

        #Create emails using the data, assigning a partial-random id
        sentimentMap = {'negative': -1, 'neutral': 0, 'positive': 1}
        emails = []

        df = pd.read_csv(dataFile)
        start, end = rowRange
        end = min(end+1, len(df))
        actualRequested = 0
        
        print(f"Attempting to add {end - start} emails to cases")
        for i in range(start, min(end+1, len(df))):
            if df[sentimentColName][i] not in sentimentMap: continue

            emails.append({
                'Subject': 'Test: Einstein Community Model Performance', 
                'TextBody': df[textColName][i], 
                'ParentId': caseIds[i % len(caseIds)],
                'Incoming': True,
                'SentimentActual__c': sentimentMap[df[sentimentColName][i]]
            })
            actualRequested += 1
        
        print(f"Actual # of emails sent to salesforce {actualRequested}")
        res = self.sf.bulk.EmailMessage.insert(emails)
        print("\nResult:\n")
        print(res)
        return res
    
    def delEmails(self, caseIds):
        """
        Deletes EmailMessage sObjects given a list of ParentIds of Cases.

        caseIds: list of parent id cases

        returns: query result
        """

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
        return res
    
    def getF1Score(self, caseIds):

        emails = self.getEmails(caseIds)

        data = []
        records = emails['records']
        for rec in records:
            prediction = float(rec['Sentiment__c'])
            actual = float(rec['SentimentActual__c'])

            data.append((prediction, actual))
        
        return SentimentModelMetrics(data)
    
    def getF1ScoreFromFile(self, file):
        data = []
        with open(file, 'r') as f:
            for line in f:
                line = line.strip()
                tup = line.split(', ')
                tup[0] = tup[0][1:]
                tup[1] = tup[1][0:len(tup[1])-1]
                data.append((float(tup[0]), float(tup[1])))
        
        return SentimentModelMetrics(data)
        