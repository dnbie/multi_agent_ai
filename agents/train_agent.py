"""
Train Ticket Agent - Search and book train tickets (mock IRCTC-style dataset)
New module — no existing train agent in system.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .base_agent import BaseAgent, AgentResult


# ── Mock train dataset ────────────────────────────────────────────────────────

MOCK_TRAINS = [
    # ── Delhi ↔ Mumbai ────────────────────────────────────────────────────────
    {"train_no": "12951", "name": "Mumbai Rajdhani",          "from": "mumbai",           "to": "delhi",              "dep": "17:00", "arr": "08:35+1",  "duration": "15h 35m", "classes": ["2A","3A","1A"],       "fare": {"2A": 2120, "3A": 1450, "1A": 3590}},
    {"train_no": "12952", "name": "Mumbai Rajdhani",          "from": "delhi",            "to": "mumbai",             "dep": "16:25", "arr": "08:15+1",  "duration": "15h 50m", "classes": ["2A","3A","1A"],       "fare": {"2A": 2120, "3A": 1450, "1A": 3590}},
    {"train_no": "12137", "name": "Punjab Mail",              "from": "mumbai",           "to": "delhi",              "dep": "19:05", "arr": "11:45+1",  "duration": "16h 40m", "classes": ["SL","2A","3A","1A"],  "fare": {"SL": 520,  "2A": 1975, "3A": 1360, "1A": 3290}},
    {"train_no": "12138", "name": "Punjab Mail",              "from": "delhi",            "to": "mumbai",             "dep": "19:30", "arr": "12:30+1",  "duration": "17h 0m",  "classes": ["SL","2A","3A","1A"],  "fare": {"SL": 520,  "2A": 1975, "3A": 1360, "1A": 3290}},
    {"train_no": "12953", "name": "August Kranti Rajdhani",   "from": "mumbai",           "to": "delhi",              "dep": "17:40", "arr": "10:55+1",  "duration": "17h 15m", "classes": ["2A","3A","1A"],       "fare": {"2A": 2120, "3A": 1450, "1A": 3590}},

    # ── Delhi ↔ Kolkata ───────────────────────────────────────────────────────
    {"train_no": "12301", "name": "Howrah Rajdhani",          "from": "kolkata",          "to": "delhi",              "dep": "16:55", "arr": "10:00+1",  "duration": "17h 5m",  "classes": ["2A","3A","1A"],       "fare": {"2A": 2060, "3A": 1415, "1A": 3505}},
    {"train_no": "12302", "name": "Howrah Rajdhani",          "from": "delhi",            "to": "kolkata",            "dep": "17:00", "arr": "10:05+1",  "duration": "17h 5m",  "classes": ["2A","3A","1A"],       "fare": {"2A": 2060, "3A": 1415, "1A": 3505}},
    {"train_no": "12303", "name": "Poorva Express",           "from": "kolkata",          "to": "delhi",              "dep": "08:15", "arr": "05:45+2",  "duration": "45h 30m", "classes": ["SL","2A","3A","1A"],  "fare": {"SL": 580,  "2A": 2200, "3A": 1520, "1A": 3770}},
    {"train_no": "12304", "name": "Poorva Express",           "from": "delhi",            "to": "kolkata",            "dep": "22:30", "arr": "20:30+1",  "duration": "22h 0m",  "classes": ["SL","2A","3A","1A"],  "fare": {"SL": 580,  "2A": 2200, "3A": 1520, "1A": 3770}},

    # ── Delhi ↔ Chennai ───────────────────────────────────────────────────────
    {"train_no": "12621", "name": "Tamil Nadu Express",       "from": "delhi",            "to": "chennai",            "dep": "22:30", "arr": "07:00+2",  "duration": "32h 30m", "classes": ["SL","2A","3A","1A"],  "fare": {"SL": 755,  "2A": 2860, "3A": 1985, "1A": 4920}},
    {"train_no": "12622", "name": "Tamil Nadu Express",       "from": "chennai",          "to": "delhi",              "dep": "22:00", "arr": "07:30+2",  "duration": "33h 30m", "classes": ["SL","2A","3A","1A"],  "fare": {"SL": 755,  "2A": 2860, "3A": 1985, "1A": 4920}},
    {"train_no": "12615", "name": "Grand Trunk Express",      "from": "delhi",            "to": "chennai",            "dep": "18:30", "arr": "06:10+2",  "duration": "35h 40m", "classes": ["SL","2A","3A"],       "fare": {"SL": 755,  "2A": 2860, "3A": 1985}},
    {"train_no": "12616", "name": "Grand Trunk Express",      "from": "chennai",          "to": "delhi",              "dep": "19:35", "arr": "08:30+2",  "duration": "36h 55m", "classes": ["SL","2A","3A"],       "fare": {"SL": 755,  "2A": 2860, "3A": 1985}},

    # ── Delhi ↔ Bangalore ─────────────────────────────────────────────────────
    {"train_no": "12627", "name": "Karnataka Express",        "from": "delhi",            "to": "bangalore",          "dep": "20:30", "arr": "06:45+2",  "duration": "34h 15m", "classes": ["SL","2A","3A","1A"],  "fare": {"SL": 740,  "2A": 2810, "3A": 1950, "1A": 4830}},
    {"train_no": "12628", "name": "Karnataka Express",        "from": "bangalore",        "to": "delhi",              "dep": "20:15", "arr": "06:20+2",  "duration": "34h 5m",  "classes": ["SL","2A","3A","1A"],  "fare": {"SL": 740,  "2A": 2810, "3A": 1950, "1A": 4830}},
    {"train_no": "22691", "name": "Rajdhani Express",         "from": "delhi",            "to": "bangalore",          "dep": "20:00", "arr": "05:35+2",  "duration": "33h 35m", "classes": ["2A","3A","1A"],       "fare": {"2A": 3050, "3A": 2110, "1A": 5220}},
    {"train_no": "22692", "name": "Rajdhani Express",         "from": "bangalore",        "to": "delhi",              "dep": "20:30", "arr": "06:30+2",  "duration": "34h 0m",  "classes": ["2A","3A","1A"],       "fare": {"2A": 3050, "3A": 2110, "1A": 5220}},

    # ── Delhi ↔ Hyderabad ─────────────────────────────────────────────────────
    {"train_no": "12721", "name": "Dakshin Express",          "from": "delhi",            "to": "hyderabad",          "dep": "22:30", "arr": "20:00+1",  "duration": "21h 30m", "classes": ["SL","2A","3A","1A"],  "fare": {"SL": 560,  "2A": 2100, "3A": 1460, "1A": 3620}},
    {"train_no": "12722", "name": "Dakshin Express",          "from": "hyderabad",        "to": "delhi",              "dep": "06:20", "arr": "07:00+1",  "duration": "24h 40m", "classes": ["SL","2A","3A","1A"],  "fare": {"SL": 560,  "2A": 2100, "3A": 1460, "1A": 3620}},
    {"train_no": "12723", "name": "AP Express",               "from": "hyderabad",        "to": "delhi",              "dep": "14:55", "arr": "13:15+1",  "duration": "22h 20m", "classes": ["SL","2A","3A"],       "fare": {"SL": 560,  "2A": 2100, "3A": 1460}},

    # ── Delhi ↔ Ahmedabad ─────────────────────────────────────────────────────
    {"train_no": "12957", "name": "Rajdhani Express",         "from": "delhi",            "to": "ahmedabad",          "dep": "20:20", "arr": "08:00+1",  "duration": "11h 40m", "classes": ["2A","3A","1A"],       "fare": {"2A": 1615, "3A": 1115, "1A": 2765}},
    {"train_no": "12958", "name": "Rajdhani Express",         "from": "ahmedabad",        "to": "delhi",              "dep": "15:35", "arr": "05:40+1",  "duration": "14h 5m",  "classes": ["2A","3A","1A"],       "fare": {"2A": 1615, "3A": 1115, "1A": 2765}},
    {"train_no": "12009", "name": "Shatabdi Express",         "from": "mumbai",           "to": "ahmedabad",          "dep": "06:25", "arr": "12:45",    "duration": "6h 20m",  "classes": ["CC","EC"],            "fare": {"CC": 810,  "EC": 1590}},
    {"train_no": "12010", "name": "Shatabdi Express",         "from": "ahmedabad",        "to": "mumbai",             "dep": "14:45", "arr": "21:25",    "duration": "6h 40m",  "classes": ["CC","EC"],            "fare": {"CC": 810,  "EC": 1590}},

    # ── Delhi ↔ Jaipur ────────────────────────────────────────────────────────
    {"train_no": "12015", "name": "Ajmer Shatabdi",           "from": "delhi",            "to": "jaipur",             "dep": "06:05", "arr": "10:40",    "duration": "4h 35m",  "classes": ["CC","EC"],            "fare": {"CC": 550,  "EC": 1075}},
    {"train_no": "12016", "name": "Ajmer Shatabdi",           "from": "jaipur",           "to": "delhi",              "dep": "17:05", "arr": "21:35",    "duration": "4h 30m",  "classes": ["CC","EC"],            "fare": {"CC": 550,  "EC": 1075}},
    {"train_no": "12413", "name": "Ajmer Rajdhani",           "from": "delhi",            "to": "jaipur",             "dep": "17:50", "arr": "22:30",    "duration": "4h 40m",  "classes": ["2A","3A","1A"],       "fare": {"2A": 1145, "3A": 790,  "1A": 1970}},

    # ── Delhi ↔ Lucknow ───────────────────────────────────────────────────────
    {"train_no": "12003", "name": "Lucknow Shatabdi",         "from": "delhi",            "to": "lucknow",            "dep": "06:10", "arr": "12:30",    "duration": "6h 20m",  "classes": ["CC","EC"],            "fare": {"CC": 695,  "EC": 1360}},
    {"train_no": "12004", "name": "Lucknow Shatabdi",         "from": "lucknow",          "to": "delhi",              "dep": "15:05", "arr": "22:00",    "duration": "6h 55m",  "classes": ["CC","EC"],            "fare": {"CC": 695,  "EC": 1360}},
    {"train_no": "14005", "name": "Lichchhavi Express",       "from": "delhi",            "to": "lucknow",            "dep": "22:45", "arr": "07:20+1",  "duration": "8h 35m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 215,  "2A": 810,  "3A": 565}},

    # ── Delhi ↔ Amritsar ──────────────────────────────────────────────────────
    {"train_no": "12013", "name": "Amritsar Shatabdi",        "from": "delhi",            "to": "amritsar",           "dep": "07:20", "arr": "13:10",    "duration": "5h 50m",  "classes": ["CC","EC"],            "fare": {"CC": 640,  "EC": 1255}},
    {"train_no": "12014", "name": "Amritsar Shatabdi",        "from": "amritsar",         "to": "delhi",              "dep": "16:40", "arr": "22:45",    "duration": "6h 5m",   "classes": ["CC","EC"],            "fare": {"CC": 640,  "EC": 1255}},
    {"train_no": "12903", "name": "Golden Temple Mail",       "from": "mumbai",           "to": "amritsar",           "dep": "21:35", "arr": "02:10+2",  "duration": "28h 35m", "classes": ["SL","2A","3A","1A"],  "fare": {"SL": 660,  "2A": 2490, "3A": 1725, "1A": 4270}},

    # ── Delhi ↔ Chandigarh ────────────────────────────────────────────────────
    {"train_no": "12011", "name": "Kalka Shatabdi",           "from": "delhi",            "to": "chandigarh",         "dep": "07:40", "arr": "11:20",    "duration": "3h 40m",  "classes": ["CC","EC"],            "fare": {"CC": 420,  "EC": 815}},
    {"train_no": "12012", "name": "Kalka Shatabdi",           "from": "chandigarh",       "to": "delhi",              "dep": "17:30", "arr": "21:15",    "duration": "3h 45m",  "classes": ["CC","EC"],            "fare": {"CC": 420,  "EC": 815}},

    # ── Delhi ↔ Dehradun ──────────────────────────────────────────────────────
    {"train_no": "12017", "name": "Dehradun Shatabdi",        "from": "delhi",            "to": "dehradun",           "dep": "06:50", "arr": "11:55",    "duration": "5h 5m",   "classes": ["CC","EC"],            "fare": {"CC": 575,  "EC": 1125}},
    {"train_no": "12018", "name": "Dehradun Shatabdi",        "from": "dehradun",         "to": "delhi",              "dep": "17:00", "arr": "22:25",    "duration": "5h 25m",  "classes": ["CC","EC"],            "fare": {"CC": 575,  "EC": 1125}},

    # ── Delhi ↔ Varanasi ──────────────────────────────────────────────────────
    {"train_no": "15003", "name": "Chauri Chaura Express",    "from": "delhi",            "to": "varanasi",           "dep": "16:25", "arr": "07:00+1",  "duration": "14h 35m", "classes": ["SL","2A","3A"],       "fare": {"SL": 330,  "2A": 1250, "3A": 865}},
    {"train_no": "22435", "name": "Vande Bharat Express",     "from": "delhi",            "to": "varanasi",           "dep": "06:00", "arr": "14:00",    "duration": "8h 0m",   "classes": ["CC","EC"],            "fare": {"CC": 1180, "EC": 2275}},
    {"train_no": "22436", "name": "Vande Bharat Express",     "from": "varanasi",         "to": "delhi",              "dep": "15:00", "arr": "23:00",    "duration": "8h 0m",   "classes": ["CC","EC"],            "fare": {"CC": 1180, "EC": 2275}},

    # ── Delhi ↔ Agra ──────────────────────────────────────────────────────────
    {"train_no": "12279", "name": "Taj Express",              "from": "delhi",            "to": "agra",               "dep": "07:15", "arr": "10:00",    "duration": "2h 45m",  "classes": ["CC","2S"],            "fare": {"CC": 315,  "2S": 100}},
    {"train_no": "12050", "name": "Gatimaan Express",         "from": "delhi",            "to": "agra",               "dep": "08:10", "arr": "09:50",    "duration": "1h 40m",  "classes": ["CC","EC"],            "fare": {"CC": 755,  "EC": 1505}},
    {"train_no": "12049", "name": "Gatimaan Express",         "from": "agra",             "to": "delhi",              "dep": "17:30", "arr": "19:30",    "duration": "2h 0m",   "classes": ["CC","EC"],            "fare": {"CC": 755,  "EC": 1505}},

    # ── Delhi ↔ Patna ─────────────────────────────────────────────────────────
    {"train_no": "12309", "name": "Rajdhani Express",         "from": "delhi",            "to": "patna",              "dep": "18:25", "arr": "08:00+1",  "duration": "13h 35m", "classes": ["2A","3A","1A"],       "fare": {"2A": 1870, "3A": 1295, "1A": 3190}},
    {"train_no": "12310", "name": "Rajdhani Express",         "from": "patna",            "to": "delhi",              "dep": "19:25", "arr": "08:45+1",  "duration": "13h 20m", "classes": ["2A","3A","1A"],       "fare": {"2A": 1870, "3A": 1295, "1A": 3190}},
    {"train_no": "12391", "name": "Shramjeevi Express",       "from": "patna",            "to": "delhi",              "dep": "20:45", "arr": "12:00+1",  "duration": "15h 15m", "classes": ["SL","2A","3A"],       "fare": {"SL": 415,  "2A": 1565, "3A": 1085}},

    # ── Delhi ↔ Bhopal ────────────────────────────────────────────────────────
    {"train_no": "12001", "name": "Bhopal Shatabdi",          "from": "delhi",            "to": "bhopal",             "dep": "06:00", "arr": "13:55",    "duration": "7h 55m",  "classes": ["CC","EC"],            "fare": {"CC": 895,  "EC": 1760}},
    {"train_no": "12002", "name": "Bhopal Shatabdi",          "from": "bhopal",           "to": "delhi",              "dep": "14:50", "arr": "22:30",    "duration": "7h 40m",  "classes": ["CC","EC"],            "fare": {"CC": 895,  "EC": 1760}},

    # ── Delhi ↔ Indore ────────────────────────────────────────────────────────
    {"train_no": "12919", "name": "Malwa Express",            "from": "delhi",            "to": "indore",             "dep": "22:00", "arr": "14:30+1",  "duration": "16h 30m", "classes": ["SL","2A","3A"],       "fare": {"SL": 390,  "2A": 1475, "3A": 1020}},
    {"train_no": "12920", "name": "Malwa Express",            "from": "indore",           "to": "delhi",              "dep": "08:00", "arr": "06:00+1",  "duration": "22h 0m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 390,  "2A": 1475, "3A": 1020}},

    # ── Mumbai ↔ Pune ─────────────────────────────────────────────────────────
    {"train_no": "12123", "name": "Deccan Queen Express",     "from": "mumbai",           "to": "pune",               "dep": "17:10", "arr": "20:25",    "duration": "3h 15m",  "classes": ["CC","2S"],            "fare": {"CC": 295,  "2S": 100}},
    {"train_no": "12124", "name": "Deccan Queen Express",     "from": "pune",             "to": "mumbai",             "dep": "07:15", "arr": "10:25",    "duration": "3h 10m",  "classes": ["CC","2S"],            "fare": {"CC": 295,  "2S": 100}},
    {"train_no": "12127", "name": "Intercity Express",        "from": "mumbai",           "to": "pune",               "dep": "06:30", "arr": "09:55",    "duration": "3h 25m",  "classes": ["CC","2S"],            "fare": {"CC": 280,  "2S": 95}},
    {"train_no": "12128", "name": "Intercity Express",        "from": "pune",             "to": "mumbai",             "dep": "17:50", "arr": "21:15",    "duration": "3h 25m",  "classes": ["CC","2S"],            "fare": {"CC": 280,  "2S": 95}},

    # ── Mumbai ↔ Goa ──────────────────────────────────────────────────────────
    {"train_no": "10111", "name": "Konkan Kanya Express",     "from": "mumbai",           "to": "goa",                "dep": "23:00", "arr": "10:35+1",  "duration": "11h 35m", "classes": ["SL","2A","3A"],       "fare": {"SL": 295,  "2A": 1115, "3A": 775}},
    {"train_no": "10112", "name": "Konkan Kanya Express",     "from": "goa",              "to": "mumbai",             "dep": "17:00", "arr": "06:20+1",  "duration": "13h 20m", "classes": ["SL","2A","3A"],       "fare": {"SL": 295,  "2A": 1115, "3A": 775}},
    {"train_no": "10103", "name": "Mandovi Express",          "from": "mumbai",           "to": "goa",                "dep": "07:10", "arr": "19:30",    "duration": "12h 20m", "classes": ["SL","2A","3A"],       "fare": {"SL": 295,  "2A": 1115, "3A": 775}},

    # ── Mumbai ↔ Hyderabad ────────────────────────────────────────────────────
    {"train_no": "12701", "name": "Hussainsagar Express",     "from": "mumbai",           "to": "hyderabad",          "dep": "21:45", "arr": "14:30+1",  "duration": "16h 45m", "classes": ["SL","2A","3A"],       "fare": {"SL": 345,  "2A": 1295, "3A": 900}},
    {"train_no": "12702", "name": "Hussainsagar Express",     "from": "hyderabad",        "to": "mumbai",             "dep": "14:45", "arr": "08:00+1",  "duration": "17h 15m", "classes": ["SL","2A","3A"],       "fare": {"SL": 345,  "2A": 1295, "3A": 900}},

    # ── Mumbai ↔ Bangalore ────────────────────────────────────────────────────
    {"train_no": "11301", "name": "Udyan Express",            "from": "mumbai",           "to": "bangalore",          "dep": "08:05", "arr": "08:30+1",  "duration": "24h 25m", "classes": ["SL","2A","3A","1A"],  "fare": {"SL": 440,  "2A": 1665, "3A": 1155, "1A": 2840}},
    {"train_no": "11302", "name": "Udyan Express",            "from": "bangalore",        "to": "mumbai",             "dep": "20:15", "arr": "20:35+1",  "duration": "24h 20m", "classes": ["SL","2A","3A","1A"],  "fare": {"SL": 440,  "2A": 1665, "3A": 1155, "1A": 2840}},

    # ── Mumbai ↔ Nagpur ───────────────────────────────────────────────────────
    {"train_no": "12105", "name": "Vidarbha Express",         "from": "mumbai",           "to": "nagpur",             "dep": "06:20", "arr": "20:05",    "duration": "13h 45m", "classes": ["SL","2A","3A"],       "fare": {"SL": 325,  "2A": 1235, "3A": 855}},
    {"train_no": "12106", "name": "Vidarbha Express",         "from": "nagpur",           "to": "mumbai",             "dep": "05:05", "arr": "21:05",    "duration": "16h 0m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 325,  "2A": 1235, "3A": 855}},

    # ── Mumbai ↔ Kolkata ──────────────────────────────────────────────────────
    {"train_no": "12859", "name": "Gitanjali Express",        "from": "mumbai",           "to": "kolkata",            "dep": "06:10", "arr": "09:30+1",  "duration": "27h 20m", "classes": ["SL","2A","3A","1A"],  "fare": {"SL": 620,  "2A": 2340, "3A": 1620, "1A": 4015}},
    {"train_no": "12860", "name": "Gitanjali Express",        "from": "kolkata",          "to": "mumbai",             "dep": "14:05", "arr": "17:30+1",  "duration": "27h 25m", "classes": ["SL","2A","3A","1A"],  "fare": {"SL": 620,  "2A": 2340, "3A": 1620, "1A": 4015}},

    # ── Mumbai ↔ Surat ────────────────────────────────────────────────────────
    {"train_no": "19001", "name": "Surat Express",            "from": "mumbai",           "to": "surat",              "dep": "06:40", "arr": "10:00",    "duration": "3h 20m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 150,  "2A": 570,  "3A": 395}},
    {"train_no": "19002", "name": "Surat Express",            "from": "surat",            "to": "mumbai",             "dep": "18:30", "arr": "22:05",    "duration": "3h 35m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 150,  "2A": 570,  "3A": 395}},

    # ── Bangalore ↔ Chennai ───────────────────────────────────────────────────
    {"train_no": "12026", "name": "Shatabdi Express",         "from": "chennai",          "to": "bangalore",          "dep": "06:00", "arr": "10:30",    "duration": "4h 30m",  "classes": ["CC","EC"],            "fare": {"CC": 690,  "EC": 1360}},
    {"train_no": "12027", "name": "Shatabdi Express",         "from": "bangalore",        "to": "chennai",            "dep": "15:00", "arr": "19:30",    "duration": "4h 30m",  "classes": ["CC","EC"],            "fare": {"CC": 690,  "EC": 1360}},
    {"train_no": "12607", "name": "Lalbagh Express",          "from": "bangalore",        "to": "chennai",            "dep": "06:30", "arr": "11:30",    "duration": "5h 0m",   "classes": ["SL","CC","2S"],       "fare": {"SL": 215,  "CC": 545,  "2S": 155}},
    {"train_no": "12608", "name": "Lalbagh Express",          "from": "chennai",          "to": "bangalore",          "dep": "15:00", "arr": "20:15",    "duration": "5h 15m",  "classes": ["SL","CC","2S"],       "fare": {"SL": 215,  "CC": 545,  "2S": 155}},

    # ── Bangalore ↔ Mysore ────────────────────────────────────────────────────
    {"train_no": "12007", "name": "Shatabdi Express",         "from": "bangalore",        "to": "mysore",             "dep": "11:00", "arr": "12:55",    "duration": "1h 55m",  "classes": ["CC","EC"],            "fare": {"CC": 250,  "EC": 490}},
    {"train_no": "12008", "name": "Shatabdi Express",         "from": "mysore",           "to": "bangalore",          "dep": "18:25", "arr": "20:15",    "duration": "1h 50m",  "classes": ["CC","EC"],            "fare": {"CC": 250,  "EC": 490}},
    {"train_no": "16215", "name": "Mysore Express",           "from": "chennai",          "to": "mysore",             "dep": "21:50", "arr": "07:55+1",  "duration": "10h 5m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 255,  "2A": 970,  "3A": 670}},
    {"train_no": "16216", "name": "Mysore Express",           "from": "mysore",           "to": "chennai",            "dep": "17:55", "arr": "04:00+1",  "duration": "10h 5m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 255,  "2A": 970,  "3A": 670}},

    # ── Bangalore ↔ Hyderabad ─────────────────────────────────────────────────
    {"train_no": "12785", "name": "Kacheguda Express",        "from": "bangalore",        "to": "hyderabad",          "dep": "22:45", "arr": "09:45+1",  "duration": "11h 0m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 280,  "2A": 1060, "3A": 735}},
    {"train_no": "12786", "name": "Kacheguda Express",        "from": "hyderabad",        "to": "bangalore",          "dep": "18:30", "arr": "06:00+1",  "duration": "11h 30m", "classes": ["SL","2A","3A"],       "fare": {"SL": 280,  "2A": 1060, "3A": 735}},

    # ── Bangalore ↔ Goa ───────────────────────────────────────────────────────
    {"train_no": "16523", "name": "Karwar Express",           "from": "bangalore",        "to": "goa",                "dep": "20:15", "arr": "08:30+1",  "duration": "12h 15m", "classes": ["SL","2A","3A"],       "fare": {"SL": 285,  "2A": 1075, "3A": 745}},
    {"train_no": "16524", "name": "Karwar Express",           "from": "goa",              "to": "bangalore",          "dep": "17:30", "arr": "06:30+1",  "duration": "13h 0m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 285,  "2A": 1075, "3A": 745}},

    # ── Bangalore ↔ Coimbatore ────────────────────────────────────────────────
    {"train_no": "12677", "name": "Ernakulam Express",        "from": "bangalore",        "to": "coimbatore",         "dep": "22:00", "arr": "05:45+1",  "duration": "7h 45m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 230,  "2A": 870,  "3A": 605}},
    {"train_no": "12678", "name": "Ernakulam Express",        "from": "coimbatore",       "to": "bangalore",          "dep": "05:30", "arr": "13:15",    "duration": "7h 45m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 230,  "2A": 870,  "3A": 605}},

    # ── Bangalore ↔ Mangalore ─────────────────────────────────────────────────
    {"train_no": "16517", "name": "Karwar Express",           "from": "bangalore",        "to": "mangalore",          "dep": "21:35", "arr": "06:50+1",  "duration": "9h 15m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 260,  "2A": 985,  "3A": 685}},
    {"train_no": "16518", "name": "Karwar Express",           "from": "mangalore",        "to": "bangalore",          "dep": "20:55", "arr": "06:15+1",  "duration": "9h 20m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 260,  "2A": 985,  "3A": 685}},

    # ── Chennai ↔ Hyderabad ───────────────────────────────────────────────────
    {"train_no": "12759", "name": "Charminar Express",        "from": "chennai",          "to": "hyderabad",          "dep": "18:45", "arr": "07:10+1",  "duration": "12h 25m", "classes": ["SL","2A","3A"],       "fare": {"SL": 295,  "2A": 1115, "3A": 775}},
    {"train_no": "12760", "name": "Charminar Express",        "from": "hyderabad",        "to": "chennai",            "dep": "17:30", "arr": "06:10+1",  "duration": "12h 40m", "classes": ["SL","2A","3A"],       "fare": {"SL": 295,  "2A": 1115, "3A": 775}},

    # ── Chennai ↔ Kochi ───────────────────────────────────────────────────────
    {"train_no": "12601", "name": "Chennai Mail",             "from": "chennai",          "to": "kochi",              "dep": "21:30", "arr": "10:30+1",  "duration": "13h 0m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 310,  "2A": 1175, "3A": 815}},
    {"train_no": "12602", "name": "Chennai Mail",             "from": "kochi",            "to": "chennai",            "dep": "18:00", "arr": "07:30+1",  "duration": "13h 30m", "classes": ["SL","2A","3A"],       "fare": {"SL": 310,  "2A": 1175, "3A": 815}},

    # ── Chennai ↔ Thiruvananthapuram ──────────────────────────────────────────
    {"train_no": "12695", "name": "Trivandrum Mail",          "from": "chennai",          "to": "thiruvananthapuram", "dep": "19:15", "arr": "11:30+1",  "duration": "16h 15m", "classes": ["SL","2A","3A","1A"],  "fare": {"SL": 395,  "2A": 1490, "3A": 1035, "1A": 2565}},
    {"train_no": "12696", "name": "Trivandrum Mail",          "from": "thiruvananthapuram","to": "chennai",           "dep": "17:00", "arr": "09:10+1",  "duration": "16h 10m", "classes": ["SL","2A","3A","1A"],  "fare": {"SL": 395,  "2A": 1490, "3A": 1035, "1A": 2565}},

    # ── Chennai ↔ Visakhapatnam ───────────────────────────────────────────────
    {"train_no": "12841", "name": "Coromandel Express",       "from": "chennai",          "to": "kolkata",            "dep": "08:45", "arr": "13:20+1",  "duration": "28h 35m", "classes": ["SL","2A","3A","1A"],  "fare": {"SL": 565,  "2A": 2135, "3A": 1480, "1A": 3660}},
    {"train_no": "12842", "name": "Coromandel Express",       "from": "kolkata",          "to": "chennai",            "dep": "14:35", "arr": "18:50+1",  "duration": "28h 15m", "classes": ["SL","2A","3A","1A"],  "fare": {"SL": 565,  "2A": 2135, "3A": 1480, "1A": 3660}},
    {"train_no": "12805", "name": "Janmabhoomi Express",      "from": "visakhapatnam",    "to": "chennai",            "dep": "05:00", "arr": "14:20",    "duration": "9h 20m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 285,  "2A": 1075, "3A": 745}},
    {"train_no": "12806", "name": "Janmabhoomi Express",      "from": "chennai",          "to": "visakhapatnam",      "dep": "17:20", "arr": "03:30+1",  "duration": "10h 10m", "classes": ["SL","2A","3A"],       "fare": {"SL": 285,  "2A": 1075, "3A": 745}},

    # ── Kolkata ↔ Guwahati ────────────────────────────────────────────────────
    {"train_no": "12345", "name": "Saraighat Express",        "from": "kolkata",          "to": "guwahati",           "dep": "15:55", "arr": "09:30+1",  "duration": "17h 35m", "classes": ["SL","2A","3A","1A"],  "fare": {"SL": 380,  "2A": 1440, "3A": 995, "1A": 2465}},
    {"train_no": "12346", "name": "Saraighat Express",        "from": "guwahati",         "to": "kolkata",            "dep": "13:05", "arr": "06:30+1",  "duration": "17h 25m", "classes": ["SL","2A","3A","1A"],  "fare": {"SL": 380,  "2A": 1440, "3A": 995, "1A": 2465}},

    # ── Kolkata ↔ Patna ───────────────────────────────────────────────────────
    {"train_no": "12381", "name": "Poorva Express",           "from": "kolkata",          "to": "patna",              "dep": "05:00", "arr": "13:00",    "duration": "8h 0m",   "classes": ["SL","2A","3A"],       "fare": {"SL": 245,  "2A": 930,  "3A": 645}},
    {"train_no": "12382", "name": "Poorva Express",           "from": "patna",            "to": "kolkata",            "dep": "16:00", "arr": "23:40",    "duration": "7h 40m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 245,  "2A": 930,  "3A": 645}},

    # ── Kolkata ↔ Bhubaneswar ─────────────────────────────────────────────────
    {"train_no": "12821", "name": "Dhauli Express",           "from": "bhubaneswar",      "to": "kolkata",            "dep": "06:00", "arr": "12:40",    "duration": "6h 40m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 225,  "2A": 855,  "3A": 595}},
    {"train_no": "12822", "name": "Dhauli Express",           "from": "kolkata",          "to": "bhubaneswar",        "dep": "18:35", "arr": "00:55+1",  "duration": "6h 20m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 225,  "2A": 855,  "3A": 595}},

    # ── Hyderabad ↔ Vijayawada ────────────────────────────────────────────────
    {"train_no": "12739", "name": "Garib Rath Express",       "from": "hyderabad",        "to": "visakhapatnam",      "dep": "16:40", "arr": "07:20+1",  "duration": "14h 40m", "classes": ["3A","CC"],            "fare": {"3A": 680,  "CC": 545}},
    {"train_no": "12740", "name": "Garib Rath Express",       "from": "visakhapatnam",    "to": "hyderabad",          "dep": "17:45", "arr": "08:30+1",  "duration": "14h 45m", "classes": ["3A","CC"],            "fare": {"3A": 680,  "CC": 545}},
    {"train_no": "17202", "name": "Golconda Express",         "from": "hyderabad",        "to": "vijayawada",         "dep": "06:30", "arr": "11:00",    "duration": "4h 30m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 165,  "2A": 625,  "3A": 435}},
    {"train_no": "17201", "name": "Golconda Express",         "from": "vijayawada",       "to": "hyderabad",          "dep": "20:10", "arr": "00:40+1",  "duration": "4h 30m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 165,  "2A": 625,  "3A": 435}},

    # ── Kochi ↔ Bangalore ─────────────────────────────────────────────────────
    {"train_no": "16315", "name": "Kochuveli Express",        "from": "kochi",            "to": "bangalore",          "dep": "19:45", "arr": "06:30+1",  "duration": "10h 45m", "classes": ["SL","2A","3A"],       "fare": {"SL": 270,  "2A": 1020, "3A": 710}},
    {"train_no": "16316", "name": "Kochuveli Express",        "from": "bangalore",        "to": "kochi",              "dep": "19:30", "arr": "07:30+1",  "duration": "12h 0m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 270,  "2A": 1020, "3A": 710}},

    # ── Thiruvananthapuram ↔ Mumbai ───────────────────────────────────────────
    {"train_no": "16345", "name": "Netravati Express",        "from": "thiruvananthapuram","to": "mumbai",            "dep": "11:00", "arr": "01:00+2",  "duration": "38h 0m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 620,  "2A": 2345, "3A": 1625}},
    {"train_no": "16346", "name": "Netravati Express",        "from": "mumbai",           "to": "thiruvananthapuram", "dep": "11:40", "arr": "02:30+2",  "duration": "38h 50m", "classes": ["SL","2A","3A"],       "fare": {"SL": 620,  "2A": 2345, "3A": 1625}},

    # ── Coimbatore ↔ Chennai ─────────────────────────────────────────────────
    {"train_no": "12671", "name": "Nilgiris Express",         "from": "coimbatore",       "to": "chennai",            "dep": "06:20", "arr": "12:00",    "duration": "5h 40m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 245,  "2A": 910,  "3A": 635}},
    {"train_no": "12672", "name": "Nilgiris Express",         "from": "chennai",          "to": "coimbatore",         "dep": "15:10", "arr": "21:00",    "duration": "5h 50m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 245,  "2A": 910,  "3A": 635}},
    {"train_no": "22625", "name": "Double Decker Express",    "from": "coimbatore",       "to": "chennai",            "dep": "13:30", "arr": "19:10",    "duration": "5h 40m",  "classes": ["CC","2S"],            "fare": {"CC": 455,  "2S": 160}},
    {"train_no": "12673", "name": "Cheran Express",           "from": "coimbatore",       "to": "chennai",            "dep": "22:30", "arr": "05:30+1",  "duration": "7h 0m",   "classes": ["SL","2A","3A"],       "fare": {"SL": 245,  "2A": 910,  "3A": 635}},
    {"train_no": "12674", "name": "Cheran Express",           "from": "chennai",          "to": "coimbatore",         "dep": "22:00", "arr": "05:00+1",  "duration": "7h 0m",   "classes": ["SL","2A","3A"],       "fare": {"SL": 245,  "2A": 910,  "3A": 635}},
    {"train_no": "11013", "name": "Mumbai Express",           "from": "coimbatore",       "to": "mumbai",             "dep": "07:00", "arr": "09:30+1",  "duration": "26h 30m", "classes": ["SL","2A","3A"],       "fare": {"SL": 485,  "2A": 1850, "3A": 1270}},

    # ── Madurai ↔ Chennai ─────────────────────────────────────────────────────
    {"train_no": "12637", "name": "Pandian Express",          "from": "madurai",          "to": "chennai",            "dep": "21:45", "arr": "06:00+1",  "duration": "8h 15m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 260,  "2A": 955,  "3A": 665}},
    {"train_no": "12638", "name": "Pandian Express",          "from": "chennai",          "to": "madurai",            "dep": "21:30", "arr": "06:00+1",  "duration": "8h 30m",  "classes": ["SL","2A","3A"],       "fare": {"SL": 260,  "2A": 955,  "3A": 665}},
    {"train_no": "12661", "name": "Pothigai Express",         "from": "madurai",          "to": "delhi",              "dep": "13:55", "arr": "17:30+2",  "duration": "51h 35m", "classes": ["SL","2A","3A"],       "fare": {"SL": 790,  "2A": 2990, "3A": 2075}},

    # ── Nagpur ↔ Delhi ────────────────────────────────────────────────────────
    {"train_no": "12419", "name": "Gondwana Express",         "from": "nagpur",           "to": "delhi",              "dep": "20:30", "arr": "15:05+1",  "duration": "18h 35m", "classes": ["SL","2A","3A"],       "fare": {"SL": 430,  "2A": 1625, "3A": 1125}},
    {"train_no": "12420", "name": "Gondwana Express",         "from": "delhi",            "to": "nagpur",             "dep": "22:50", "arr": "17:35+1",  "duration": "18h 45m", "classes": ["SL","2A","3A"],       "fare": {"SL": 430,  "2A": 1625, "3A": 1125}},

    # ── Ahmedabad ↔ Kolkata ───────────────────────────────────────────────────
    {"train_no": "19165", "name": "Sabarmati Express",        "from": "ahmedabad",        "to": "kolkata",            "dep": "22:05", "arr": "08:30+2",  "duration": "34h 25m", "classes": ["SL","2A","3A"],       "fare": {"SL": 620,  "2A": 2345, "3A": 1625}},

    # ── Jaipur ↔ Mumbai ───────────────────────────────────────────────────────
    {"train_no": "12955", "name": "Jaipur–Mumbai Express",    "from": "jaipur",           "to": "mumbai",             "dep": "23:15", "arr": "20:05+1",  "duration": "20h 50m", "classes": ["SL","2A","3A"],       "fare": {"SL": 465,  "2A": 1760, "3A": 1220}},
    {"train_no": "12956", "name": "Jaipur–Mumbai Express",    "from": "mumbai",           "to": "jaipur",             "dep": "22:00", "arr": "17:45+1",  "duration": "19h 45m", "classes": ["SL","2A","3A"],       "fare": {"SL": 465,  "2A": 1760, "3A": 1220}},

    # ── Varanasi ↔ Kolkata ────────────────────────────────────────────────────
    {"train_no": "13006", "name": "ASR HWH Express",          "from": "varanasi",         "to": "kolkata",            "dep": "00:30", "arr": "09:30",    "duration": "9h 0m",   "classes": ["SL","2A","3A"],       "fare": {"SL": 265,  "2A": 1000, "3A": 695}},

    # ── Guwahati ↔ Delhi ──────────────────────────────────────────────────────
    {"train_no": "12423", "name": "Dibrugarh Rajdhani",       "from": "guwahati",         "to": "delhi",              "dep": "12:35", "arr": "10:00+1",  "duration": "21h 25m", "classes": ["2A","3A","1A"],       "fare": {"2A": 2380, "3A": 1640, "1A": 4060}},
    {"train_no": "12424", "name": "Dibrugarh Rajdhani",       "from": "delhi",            "to": "guwahati",           "dep": "21:30", "arr": "19:55+1",  "duration": "22h 25m", "classes": ["2A","3A","1A"],       "fare": {"2A": 2380, "3A": 1640, "1A": 4060}},

    # ── Bhubaneswar ↔ Delhi ───────────────────────────────────────────────────
    {"train_no": "12801", "name": "Purushottam Express",      "from": "bhubaneswar",      "to": "delhi",              "dep": "20:45", "arr": "22:20+1",  "duration": "25h 35m", "classes": ["SL","2A","3A","1A"],  "fare": {"SL": 545,  "2A": 2060, "3A": 1425, "1A": 3530}},
    {"train_no": "12802", "name": "Purushottam Express",      "from": "delhi",            "to": "bhubaneswar",        "dep": "22:05", "arr": "01:30+2",  "duration": "27h 25m", "classes": ["SL","2A","3A","1A"],  "fare": {"SL": 545,  "2A": 2060, "3A": 1425, "1A": 3530}},
]

CITY_ALIASES = {
    # Short codes
    "cbe": "coimbatore", "mas": "chennai",  "bom": "mumbai",   "del": "delhi",
    "blr": "bangalore",  "hyd": "hyderabad","amd": "ahmedabad","pnq": "pune",
    "jp":  "jaipur",     "lko": "lucknow",  "asr": "amritsar", "cdg": "chandigarh",
    "ddn": "dehradun",   "bsb": "varanasi", "agc": "agra",     "pnc": "patna",
    "bpl": "bhopal",     "indb": "indore",  "nag": "nagpur",   "st":  "surat",
    "ers": "kochi",      "tvc": "thiruvananthapuram", "vsk": "visakhapatnam",
    "bbs": "bhubaneswar","gwl": "guwahati", "maq": "mangalore","mys": "mysore",
    "vja": "vijayawada", "maq": "mangalore",
    # Alternate city names
    "bengaluru":         "bangalore",
    "calcutta":          "kolkata",
    "howrah":            "kolkata",
    "bombay":            "mumbai",
    "madras":            "chennai",
    "trivandrum":        "thiruvananthapuram",
    "vizag":             "visakhapatnam",
    "ernakulam":         "kochi",
    "baroda":            "vadodara",
    "vadodara":          "vadodara",
    "new delhi":         "delhi",
    "secunderabad":      "hyderabad",
    "mysuru":            "mysore",
}


class TrainAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Train Ticket Agent",
            description="Search train schedules, check fares and create journey itinerary"
        )

    def get_capabilities(self) -> List[str]:
        return [
            "Search trains between two cities",
            "Show available classes and fares",
            "Generate journey itinerary",
            "Mock IRCTC-style booking summary",
            "Support for SL, 2A, 3A, CC, EC classes",
        ]

    def execute(self, task: str, **kwargs) -> AgentResult:
        self._start_execution(task)
        try:
            origin = self._normalize(kwargs.get("origin") or self._extract_city("from", task))
            destination = self._normalize(kwargs.get("destination") or self._extract_city("to", task))
            date = kwargs.get("date") or self._extract_date(task)
            travel_class = kwargs.get("travel_class")

            if not origin or not destination:
                result = self._create_result(False,
                    "Please specify source and destination. Example: 'Book train from Coimbatore to Chennai'",
                    error="Missing origin or destination")
                self._end_execution(result)
                return result

            trains = self._search(origin, destination)
            if not trains:
                result = self._create_result(False,
                    f"No trains found from {origin.title()} to {destination.title()}.",
                    data={"origin": origin, "destination": destination})
                self._end_execution(result)
                return result

            itinerary = self._make_itinerary(trains, origin, destination, date, travel_class)
            message = (
                f"Found {len(trains)} train(s) from {origin.title()} to {destination.title()}"
                + (f" on {date}" if date else "")
            )
            result = self._create_result(True, message, data={
                "origin": origin.title(),
                "destination": destination.title(),
                "date": date or "Date not specified",
                "trains": trains,
                "itinerary": itinerary,
                "count": len(trains),
            })

        except Exception as e:
            result = self._create_result(False, f"Train agent error: {str(e)}", error=str(e))

        self._end_execution(result)
        return result

    # ── search & format ───────────────────────────────────────────────────────

    def _search(self, origin: str, destination: str) -> List[Dict]:
        return [t for t in MOCK_TRAINS
                if t["from"] == origin and t["to"] == destination]

    def _make_itinerary(self, trains: List[Dict], origin: str, dest: str,
                        date: Optional[str], preferred_class: Optional[str]) -> str:
        date_str = date or datetime.now().strftime("%d %b %Y")
        lines = [
            f"TRAIN JOURNEY ITINERARY",
            f"Route  : {origin.title()} -> {dest.title()}",
            f"Date   : {date_str}",
            f"{'─'*50}",
        ]
        for t in trains:
            classes = ", ".join(t["classes"])
            fares = " | ".join(f"{k}: Rs.{v}" for k, v in t["fare"].items())
            lines += [
                f"Train  : {t['train_no']} - {t['name']}",
                f"Departs: {t['dep']}  Arrives: {t['arr']}  ({t['duration']})",
                f"Classes: {classes}",
                f"Fares  : {fares}",
                f"{'─'*50}",
            ]
        lines.append("Note: To book, visit https://www.irctc.co.in")
        return "\n".join(lines)

    # ── parsing ───────────────────────────────────────────────────────────────

    def _normalize(self, city: str) -> str:
        if not city:
            return ""
        key = city.lower().strip()
        return CITY_ALIASES.get(key, key)

    def _extract_city(self, direction: str, text: str) -> str:
        lower = text.lower()
        if direction == "from":
            m = re.search(r'from\s+([a-z\s]+?)(?:\s+to\s|\s+on\s|\s+tomorrow|$)', lower)
        else:
            m = re.search(r'to\s+([a-z\s]+?)(?:\s+on\s|\s+tomorrow|\s+next|\?|$)', lower)
        if m:
            return m.group(1).strip().rstrip("?.,")
        return ""

    def _extract_date(self, text: str) -> Optional[str]:
        lower = text.lower()
        if "tomorrow" in lower:
            return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        if "today" in lower:
            return datetime.now().strftime("%Y-%m-%d")
        m = re.search(r'\d{4}-\d{2}-\d{2}', text)
        if m:
            return m.group(0)
        m = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', text)
        if m:
            d, mo, y = m.groups()
            return f"{y}-{int(mo):02d}-{int(d):02d}"
        return None
