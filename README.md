# Charity Donation Tracker

A command-line Python application that lets a non-profit administrator
register donors, record donations against campaigns, and produce reports.
Backed by Behaviour-Driven Development (BDD) scenarios written in Gherkin
and executed with `behave`.

Built for **SWE6301 Agile Programming – Assessment 1, Task 2**.

## Features

- Register donors with a unique email and validated name
- Create fundraising campaigns with positive numeric goals
- Record donations with a full validation chain (donor exists, campaign open,
  amount in range)
- Reports: total donations, top 3 donors, campaign progress bars
- CSV export of every donation
- Persistent storage in a single `data.json` file
- Friendly text menu that never crashes on bad input

## Requirements

- Python 3.10 or newer
- `behave` (BDD test runner)
- Standard library only otherwise: `json`, `csv`, `re`, `uuid`, `os`, `datetime`

## Setup

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

## Running the program

```bash
python main.py
```

The main menu offers six options:

```
1. Donor Management
2. Campaign Management
3. Record a Donation
4. Reports
5. Export Donations to CSV
6. Save and Exit
```

## Running BDD tests

```bash
# Run every feature
behave

# Run a specific feature
behave features/donation.feature

# Pretty, uncaptured output (good for screenshots)
behave --no-capture --format=pretty
```

## Running optional unit tests

```bash
pip install pytest
pytest tests/
```

## Project layout

```
charity-donation-tracker/
├── features/                  # BDD: Gherkin scenarios + step definitions
│   ├── donor.feature
│   ├── campaign.feature
│   ├── donation.feature
│   ├── environment.py
│   └── steps/
├── src/                       # Application source code
│   ├── donor.py
│   ├── campaign.py
│   ├── donation.py
│   ├── donation_service.py
│   ├── storage.py
│   ├── validators.py
│   └── reports.py
├── tests/                     # Optional unit tests (pytest)
├── main.py                    # Entry point
├── requirements.txt
└── README.md
```

## Data persistence

State is saved automatically when you choose **Save and Exit** (option 6) and
loaded on the next launch. The file is `data.json` in the project root. If
the file is corrupted on startup, it is renamed to
`data.json.broken.<timestamp>` and the program starts with empty state.
