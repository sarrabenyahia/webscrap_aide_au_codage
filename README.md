# ICD-10 Synonyms Scraper

A Python tool to automatically extract all synonyms for ICD-10 codes from [aideaucodage.fr](https://www.aideaucodage.fr/cim).

## 📋 Description

This script allows you to:
- Read a list of ICD-10 codes from a CSV file
- Automatically scrape synonyms associated with each code
- Process complex synonyms with parentheses (e.g., `Cholera(Asian)(epidemic)classic`)
- Export results to an Excel file
- Automatically resume in case of interruption

## 🚀 Installation

### Prerequisites
- Python 3.7+
- pip

### Dependencies
```bash
pip install requests beautifulsoup4 pandas openpyxl
```

## 🏃‍♂️ Usage

### Simple Launch
```bash
python scraper.py
```

### Main Features

#### 1. Automatic Scraping
- Automatically reads all codes from CSV
- Visits `https://www.aideaucodage.fr/cim-{code}` for each code
- Extracts all `<li class="synonyme">` elements

#### 2. Complex Synonym Processing
The script automatically processes synonyms with parentheses:

**Input:**
```
Cholera(Asian)(epidemic)(malignant)classic
```

**Output:**
```
Cholera classic
Cholera Asian classic
Cholera epidemic classic
Cholera malignant classic
```

#### 3. Automatic Resume System
- **Intermediate saves**: Every 50 processed codes
- **Checkpoint**: `checkpoint.json` file created automatically
- **Smart resume**: Continues where it left off
- **Safe interruption**: Ctrl+C saves before stopping

#### 4. Error Handling
- Configurable delay between requests (prevents server overload)
- Continues even if some codes fail
- Handles timeouts and network errors

## 📊 Output Format

The generated Excel file contains 2 columns:

| Code | Synonym |
|------|---------|
| A00  | Cholera classic |
| A00  | Cholera Asian classic |
| A00  | Cholera epidemic classic |
| A00  | Cholera malignant classic |

## ⏱️ Performance

### Time Estimation
- **16,880 codes** with **1 second delay** = ~4-5 hours
- **Save** every 50 codes (quick recovery)
- **Automatic resume** in case of interruption

## 📜 License

This project is intended for educational and research use. Please respect the terms of use of aideaucodage.fr.

## 🤝 Contributing

1. Fork the project
2. Create a branch (`git checkout -b feature/improvement`)
3. Commit (`git commit -am 'Add feature'`)
4. Push (`git push origin feature/improvement`)
5. Open a Pull Request

## ⚠️ Warnings

- **Respect delays** between requests to avoid overloading the server
- **Responsible use**: This script is for personal/research use
- **Backup** your data before running a complete scraping
---

**Developed for automated ICD-10 synonym extraction** 🏥