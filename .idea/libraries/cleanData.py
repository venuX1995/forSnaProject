import csv

p = '/users/xuan/desktop/SNA/data/'
f_in = open(p + 'get_team_timesAfterFilter.csv', 'r')
f_out = open(p + 'new_get_team_times.csv', 'w', newline='')
csv_reader = csv.reader(f_in, dialect='excel')
csv_writer = csv.writer(f_out, dialect='excel')
for line in csv_reader:
    if line[0] != line[1]:
        csv_writer.writerow(line)
f_in.close()
f_out.close()