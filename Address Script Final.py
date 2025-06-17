import re
import csv
import pandas as pd

# === FILE PATHS ===
input_file = r'C:\Users\jbarber\Desktop\addresses.csv'
shortened_output = r'C:\Users\jbarber\Desktop\addresses_shortened.csv'
alert_output = r'C:\Users\jbarber\Desktop\addresses_alerts.csv'
duplicate_output = r'C:\Users\jbarber\Desktop\duplicates.csv'

# === REPLACEMENT RULES ===
abbrev_replacements = {
    "north": "N", "n": "N", "south": "S", "s": "S",
    "east": "E", "e": "E", "west": "W", "w": "W",
    "street": "St", "st": "St", "avenue": "Ave", "ave": "Ave",
    "boulevard": "Blvd", "blvd": "Blvd", "road": "Rd", "rd": "Rd",
    "drive": "Dr", "dr": "Dr", "court": "Ct", "crt": "Ct",
    "lane": "Ln", "ln": "Ln", "terrace": "Terr", "ter": "Terr",
    "place": "Pl", "pl": "Pl", "circle": "Cir", "cir": "Cir",
    "highway": "Hwy", "hwy": "Hwy", "parkway": "Pkwy", "pkwy": "Pkwy",
    "trail": "Trl", "trl": "Trl", "crossing": "Xing", "xing": "Xing",
    "esplanade": "Esp", "esp": "Esp",
}

fortwayne_replacements = {
    "st marys": "St Mary's",
    "saint joe rd": "St Joe Rd",
    "woodland ridge": "Woodland Rdg"
}

abbrev_pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in abbrev_replacements) + r')\.?(?=[,\s]|$)', re.IGNORECASE)
fortwayne_pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in fortwayne_replacements) + r')\.?(?=[,\s]|$)', re.IGNORECASE)

known_suffixes = ['Ave', 'Road', 'Rd', 'Lane', 'Ln', 'Street', 'St', 'Drive', 'Dr']

directional_checks = [
    {
        'name': 'Washington Blvd',
        'pattern': re.compile(r'(?<!\b[EW]\s)Washington Blvd\b', re.IGNORECASE),
        'required_prefix': 'E or W',
        'city': 'Fort Wayne'
    },
    {
        'name': 'Washington Center Rd',
        'pattern': re.compile(r'(?<!\b[EW]\s)Washington Center Rd\b', re.IGNORECASE),
        'required_prefix': 'E or W'
    },
    {
        'name': 'Washington Rd',
        'pattern': re.compile(r'(?<!\b[NS]\s)Washington Rd\b', re.IGNORECASE),
        'required_prefix': 'N or S'
    },
    {
        'name': 'Jefferson Blvd',
        'pattern': re.compile(r'(?<!\b[EW]\s)Jefferson Blvd\b', re.IGNORECASE),
        'required_prefix': 'E or W'
    },
    {
        'name': 'Berry St',
        'pattern': re.compile(r'(?<!\b[EW]\s)(?<![a-zA-Z])Berry St\b', re.IGNORECASE),
        'required_prefix': 'E or W'
    },
    {
        'name': 'Wayne St',
        'pattern': re.compile(r'(?<!\bE\s)(?<!\bW\s)\bWayne St\b', re.IGNORECASE),
        'required_prefix': 'E or W',
        'city': 'Fort Wayne'
    },
    {
        'name': 'Barr St',
        'pattern': re.compile(r'\bS\s+Barr St\b', re.IGNORECASE),
        'required_prefix': 'S not allowed before Barr St'
    },
    {
        'name': 'Clinton St',
        'pattern': re.compile(r'(?<!\b[NS]\s)Washington Rd\b', re.IGNORECASE),
        'required_prefix': 'N or S'
    },
    {
        'name': 'Anthony Blvd',
        'pattern': re.compile(r'(?<!\b[NS]\s)Anthony Blvd\b', re.IGNORECASE),
        'required_prefix': 'N or S'
    },
    {
        'name': 'Pontiac St',
        'pattern': re.compile(r'(?<!\b[EW]\s)Pontiac St\b', re.IGNORECASE),
        'required_prefix': 'E or W'
    },
    {
        'name': 'Rudisill Blvd',
        'pattern': re.compile(r'(?<!\b[EW]\s)Rudisill Blvd\b', re.IGNORECASE),
        'required_prefix': 'E or W'
    },
    {
        'name': 'Paulding Rd',
        'pattern': re.compile(r'(?<!\b[EW]\s)(?<![a-zA-Z])Paulding Rd\b', re.IGNORECASE),
        'required_prefix': 'E or W',
        'city': 'Fort Wayne'

    },
    {
        'name': 'Tillman Rd',
        'pattern': re.compile(r'(?<!\bE\s)Tillman Rd\b', re.IGNORECASE),
        'required_prefix': 'E',
        'city': 'Fort Wayne'
    },
    {
        'name': 'Creighton Ave',
        'pattern': re.compile(r'(?<!\b[EW]\s)Creighton Ave\b', re.IGNORECASE),
        'required_prefix': 'E or W'
    },
    {
        'name': 'Cook Rd',
        'pattern': re.compile(r'(?<!\b[EW]\s)Cook Rd\b', re.IGNORECASE),
        'required_prefix': 'E or W'
    },
    {
        'name': 'Wallen Rd',
        'pattern': re.compile(r'(?<!\b[EW]\s)Wallen Rd\b', re.IGNORECASE),
        'required_prefix': 'E or W'
    },
    {
        'name': 'State Blvd',
        'pattern': re.compile(r'(?<!\b[EW]\s)State Blvd\b', re.IGNORECASE),
        'required_prefix': 'E or W'
    },
    {
        'name': 'Lafayette St',
        'pattern': re.compile(r'\bS\s+Lafayette St\b', re.IGNORECASE),
        'required_prefix': 'S'
    },
    {
        'name': 'Dupont Rd',
        'pattern': re.compile(r'(?<!\b[EW]\s)Dupont Rd\b', re.IGNORECASE),
        'required_prefix': 'E or W'
    }
]

# === FUNCTION: Normalize Address ===
def normalize_address(addr):
    if not addr:
        return addr
    addr = abbrev_pattern.sub(lambda m: abbrev_replacements.get(m.group(1).lower(), m.group(0)), addr)
    addr = fortwayne_pattern.sub(lambda m: fortwayne_replacements.get(m.group(1).lower(), m.group(0)), addr)
    if re.search(r"\bSt Mary's\b(?!\s+(?:" + '|'.join(known_suffixes) + r")\b)", addr, re.IGNORECASE):
        addr = re.sub(r"\bSt Mary's\b(?!\s+(?:" + '|'.join(known_suffixes) + r")\b)", "St Mary's Ave", addr, flags=re.IGNORECASE)
    return addr

# === FUNCTION: Check Directional Alerts ===
def check_directional_issues(addr, city, row_num):
    issues = []
    for check in directional_checks:
        if check['pattern'].search(addr):
            if 'city' in check and city.strip().lower() != check['city'].strip().lower():
                continue
            issues.append({'row': row_num, 'issue': f"{check['name']} missing '{check['required_prefix']}' prefix", 'address': addr})
    return issues

# === PROCESSING: Shorten + Alert ===
alerts = []
try:
    with open(input_file, newline='', encoding='utf-8') as infile, \
         open(shortened_output, 'w', newline='', encoding='utf-8') as outfile, \
         open(alert_output, 'w', newline='', encoding='utf-8') as alertfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        if fieldnames[0].startswith('\ufeff'):
            fieldnames[0] = fieldnames[0].replace('\ufeff', '')
        if 'address' not in fieldnames:
            raise ValueError("CSV must contain 'address' column")

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        alert_writer = csv.DictWriter(alertfile, fieldnames=['row', 'issue', 'address'])

        writer.writeheader()
        alert_writer.writeheader()

        for idx, row in enumerate(reader, start=2):
            original = row.get('address', '')
            city = row.get('city', '')
            updated = normalize_address(original)
            row['address'] = updated
            writer.writerow(row)
            alerts.extend(check_directional_issues(updated, city, idx))

        for alert in alerts:
            alert_writer.writerow(alert)

    print(f"✔ Address normalization done. {len(alerts)} alerts written to: {alert_output}")

except Exception as e:
    print(f"❌ Error during processing: {e}")

# === DUPLICATION CHECK ===
try:
    df = pd.read_csv(shortened_output)
    if 'address' not in df.columns or 'name' not in df.columns:
        raise ValueError("CSV must contain 'name' and 'address' columns")

    df['address_normalized'] = df['address'].astype(str).str.strip().str.lower()
    df['name_normalized'] = df['name'].astype(str).str.strip().str.lower()
    duplicates = df[df.duplicated(subset=['name_normalized', 'address_normalized'], keep=False)]

    if not duplicates.empty:
        duplicates.to_csv(duplicate_output, index=False)
        print(f"✔ Found {len(duplicates)} duplicates saved to: {duplicate_output}")
    else:
        print("✅ No duplicates found.")

except Exception as e:
    print(f"❌ Duplication check error: {e}")
