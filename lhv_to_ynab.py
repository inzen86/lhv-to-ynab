from sys import argv
from os import path
from collections import OrderedDict
from datetime  import datetime
import csv


class LhvYnabConverter(object):
    def __init__(self):
        self.in_file_path = ''
        self.in_file_data = []
        self.out_file_data = []
        self.output_columns = ('Date','Payee','Memo','Outflow','Inflow')
        self.input_date_format = '%Y-%m-%d'
        self.output_date_format = '%m/%d/%Y'
        self.out_file_name = 'tulemus.csv'

    def run(self):
        self._get_file_path()
        self._read_file_to_ordered_dict()
        self._convert_data()
        self._write_ordered_dict_to_file()

    def _get_file_path(self):
        if len(argv) < 2:
            print('No imput file!')
            exit()
        if len(argv) > 2:
            print('Too many arguments!')
            exit()
        self.in_file_path = path.join(path.dirname(path.abspath(__file__)), argv[1])

    def _read_file_to_ordered_dict(self):
        with open(self.in_file_path, mode='r', encoding='utf-8-sig') as in_file:
            csv_reader = csv.DictReader(in_file)
            for row in csv_reader:
                self.in_file_data.append(row)

    def _write_ordered_dict_to_file(self):
        with open(self.out_file_name, 'w', encoding='utf-8', newline='') as out_file:
            csv_writer = csv.DictWriter(f=out_file, fieldnames=self.output_columns, delimiter=',')
            csv_writer.writeheader()
            csv_writer.writerows(self.out_file_data)
            print('Output writen to file {}'.format(self.out_file_name))

    def _convert_data(self):
        for row in self.in_file_data:
            self._convert_row(row)

    def _convert_row(self, row):
        new_row = OrderedDict()
        for column in self.output_columns:
            new_row[column] = self._convert_column_data(column_name=column, data_row=row)
        self.out_file_data.append(new_row)

        # If fee is not 0 add fee row
        fee = row['Teenustasu']
        if fee != '0.00':
            fee_row = [('Date', new_row['Date']),
                       ('Payee', 'Pank'),
                       ('Memo', 'Teenustasu'),
                       ('Outflow', float(fee)),
                       ('Inflow', None)]
            self.out_file_data.append(OrderedDict(fee_row))

    def _convert_column_data(self, column_name, data_row):
        if column_name == 'Date':
            return (datetime.strptime(data_row['Kuupäev'], self.input_date_format)).strftime(self.output_date_format)
        elif column_name == 'Payee':
            if data_row['Saaja/maksja nimi']:
                return data_row['Saaja/maksja nimi']
            else:
                return 'Pank'
        elif column_name == 'Memo':
            return data_row['Selgitus']
        elif column_name in ('Outflow', 'Inflow'):
            return self._calculate_sum(column_name, data_row)

    def _calculate_sum(self, column_name, data_row):
        if column_name == 'Outflow' and data_row['Deebet/Kreedit (D/C)'] == 'D':
            return abs(float(data_row['Summa'])) + float(data_row['Teenustasu'])
        elif column_name == 'Inflow' and data_row['Deebet/Kreedit (D/C)'] == 'C':
            return float(data_row['Summa']) - float(data_row['Teenustasu'])


if __name__ == '__main__':
    converter = LhvYnabConverter()
    converter.run()

# input column names
# Kuupäev
# Saaja/maksja nimi
# Deebet/Kreedit (D/C)     C  raha sisse   D raha välja
# Summa
# Selgitus
# Teenustasu
# Valuuta
