import csv
import io

RAW = """station,date,pm25
Adyar,2026-10-01,48
Adyar,2026-10-02,NA
Adyar,2026-10-03,
Guindy,2026-10-01,95
Guindy,2026-10-02,-5
Guindy,2026-10-03,121
Guindy,2026-10-04,1200
"""

def load_clean(text):
    rows = []

    reader = csv.DictReader(io.StringIO(text))

    for row in reader:
        value = row["pm25"]

        if value == "" or value == "NA":
            continue

        pm25 = float(value)

        if pm25 < 0 or pm25 > 999:
            continue

        rows.append((row["station"], row["date"], pm25))

    return rows


def min_max(values):
    minimum = min(values)
    maximum = max(values)

    return [
        round((v - minimum) / (maximum - minimum), 3)
        for v in values
    ]


clean = load_clean(RAW)

print("Cleaned Data:")
print(clean)

print("Normalised Data:")
print(min_max([pm for _, _, pm in clean]))
