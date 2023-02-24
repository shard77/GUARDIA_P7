import csv


class CSVWriter:
    def __init__(self, filename, headers):
        self.filename = filename
        self.headers = headers

    def write_csv(self, data):
        with open(f"./csv_files/{self.filename.split('_')[0]}/" + self.filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=self.headers)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
            
