import pandas as pd

class SentimentModelMetrics:
    def __init__(self, data):
        """
            data: list containing tuples of data (observed, expected)

                The domain for each data is D = [-1, 1] where:
                    -1 = negative sentiment
                    0 = neutral sentiment
                    1 = positive sentiment

                                    Confusion Matrix Format
            ------------------------------------------------------------------------
            |              | Prediction Neutral    | Prediction Positive    | Prediction Negative
            ------------------------------------------------------------------------
            Actual Neutral |                  |                   |
            ------------------------------------------------------------------------
            Actual Positive|                  |                   |
            ------------------------------------------------------------------------
            Actual Negative|                  |                   |
        """
        self.NUM_LABELS = 3
        self.data = data

        self.micro_avg_f1_score = 0
        self.macro_avg_f1_score = 0

        self.label_metrics = {k: {'f1 score': 0, 'precision': 0, 'recall': 0} for k in range(self.NUM_LABELS)}
        self.confusion_matrix = [[0 for _ in range(self.NUM_LABELS)] for _ in range(self.NUM_LABELS)]
        self.confusion_idx_map = {0: 0, 1: 1, -1: 2} #Gets the index for the confusion matrix using the label (sentiment)

        self.process_data()

    def process_data(self):
        """
            Processes the data and computes all metrics
        """
        #Iterate over all the data and init the matrix
        for prediction, expected in self.data:
            idx_prediction = self.confusion_idx_map[prediction]
            idx_expected = self.confusion_idx_map[expected]
            self.confusion_matrix[idx_expected][idx_prediction] += 1
        
        n = self.NUM_LABELS
        #Store diagonal of matrix and map each label to its Total Positive 
        TP_map = {i: self.confusion_matrix[i][i] for i in range(n)} 
        total_TP = sum(TP_map.values())

        #Calculate the recall and precision for each label
        for label in range(n):
            TP = TP_map[label]
            #Recall is calculated by traversing by row
            recall = TP / sum(self.confusion_matrix[label])

            #Precision is calculated by traversing by col
            total = 0
            for r in range(n):
                total += self.confusion_matrix[r][label]
            precision = TP / total

            self.label_metrics[label]['recall'] = recall
            self.label_metrics[label]['precision'] = precision
            self.label_metrics[label]['f1 score'] = self.calc_f1_score(precision, recall)

        self.macro_avg_f1_score = sum(map(lambda d: d['f1 score'], list(self.label_metrics.values()))) / n
        #micro avg f1 = total TP / (total TP + 0.5 (total FP + total FN))
        #since total FP == totalFN, denominator is just entire data
        self.micro_avg_f1_score = total_TP / len(self.data)
        
    def calc_f1_score(self, precision, recall):
        return 2 * precision * recall / (precision + recall)

    def get_label_metric(self, label, metric_name):
        """
            metric_name: a string that is either: precision or recall
            return: returns the metric value
        """
        if label not in self.label_metrics:
            print('Error: Invalid label.')
            return
        
        label_metric = self.label_metrics[label]
        if metric_name not in label_metric:
            print('Error: Invalid metric name.\nMetric names: f1, precision, recall')
            return
        
        print(f"{label} {metric_name}:{label_metric[metric_name]}")
        return label_metric[metric_name]
    
    def print_all_metrics(self):
        
        sentiment_map = {0: 'neutral ', 1: 'positive', 2: 'negative'}
        n = self.NUM_LABELS
        data = []
        columns = [metric_name for metric_name in self.label_metrics[0].keys()]
        columns.insert(0, 'sentiment')

        def format_metric(metric):
            metric = str(metric)
            return metric[:min(10, len(metric))]
        
        print(f"\nTotal predictions: {len(self.data)}")
        print(f"Macro-averaged f1 score: {format_metric(self.macro_avg_f1_score)}")
        print(f"Micro-averaged f1 score: {format_metric(self.micro_avg_f1_score)}\n")

        for label in range(n):
            row = [sentiment_map[label]]
            metrics = self.label_metrics[label]
            for metric in metrics.keys():
                row.append(metrics[metric])
            data.append(row)
        df = pd.DataFrame(data)
        df.columns = columns
        print(df)
        
