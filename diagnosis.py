#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rogonirnoy — Rule-Based Symptom Checker (English CLI)
----------------------------------------------------
A simple, pure‑Python, rule-based symptom checker with English prompts.

⚠️ Disclaimer: Educational/demo tool only. Not medical advice.

Features
- English CLI
- 30+ symptom questions
- ~15 common conditions with weighted rule scoring
- Top 3 possible conditions with confidence scores
- Red-flag detection and urgent advice
- Option to save a report as .txt

Run
- Python 3.8+
- `python diagnosis.py`
"""

from datetime import datetime
from textwrap import dedent

# ------------------------------
# Utilities
# ------------------------------
YES_WORDS = {"yes", "y", "1", "true"}
NO_WORDS = {"no", "n", "0", "false"}


def yn_prompt(q: str) -> bool:
    """Yes/no prompt with validation."""
    while True:
        ans = input(f"{q} (yes/no): ").strip().lower()
        if ans in YES_WORDS:
            return True
        if ans in NO_WORDS:
            return False
        print("⚠️ Please answer 'yes' or 'no'.")


def read_int(prompt: str, default: int | None = None, mn: int | None = None, mx: int | None = None) -> int:
    while True:
        raw = input(prompt).strip()
        if not raw and default is not None:
            return default
        try:
            val = int(raw)
            if mn is not None and val < mn:
                print(f"⚠️ Minimum is {mn}")
                continue
            if mx is not None and val > mx:
                print(f"⚠️ Maximum is {mx}")
                continue
            return val
        except ValueError:
            print("⚠️ Please enter an integer (e.g. 0, 1, 2 ...)")


# ------------------------------
# Knowledge Base
# ------------------------------

def master_symptoms():
    return {
        "fever": "Do you have a fever?",
        "high_fever": "Is the temperature very high (>=38.5°C / 101.3°F)?",
        "chills": "Are you experiencing chills?",
        "cough": "Do you have a cough?",
        "dry_cough": "Is the cough dry?",
        "sore_throat": "Do you have a sore or scratchy throat?",
        "runny_nose": "Do you have a runny nose?",
        "sneezing": "Are you sneezing?",
        "headache": "Do you have a headache?",
        "migraine_aura": "Do you experience visual sensitivity or aura with headache?",
        "body_ache": "Do you have body aches or muscle pain?",
        "fatigue": "Are you unusually tired or fatigued?",
        "short_breath": "Are you experiencing shortness of breath?",
        "chest_pain": "Do you have chest pain?",
        "wheezing": "Do you hear wheezing sounds when breathing?",
        "diarrhea": "Are you having diarrhea?",
        "vomiting": "Are you vomiting?",
        "nausea": "Do you feel nauseous?",
        "abdominal_pain": "Do you have abdominal pain?",
        "loss_smell": "Has your sense of smell or taste decreased?",
        "rash": "Do you have a skin rash or hives?",
        "eye_pain": "Are you experiencing eye pain or blurred vision?",
        "joint_pain": "Do you have joint pain?",
        "dehydration_signs": "Do you have dry mouth or reduced urination (signs of dehydration)?",
        "urinate_often": "Are you urinating more frequently?",
        "excess_thirst": "Do you feel excessive thirst?",
        "weight_loss": "Have you experienced unexplained weight loss?",
        "blood_in_stool": "Is there blood or dark color in stool?",
        "recent_travel": "Have you recently traveled to an area with outbreaks?",
        "mosquito_bite": "Have you had many mosquito bites recently?",
        "neck_stiff": "Is your neck stiff?",
        "photophobia": "Are you sensitive to bright light?",
        "age_over_60": "Are you over 60 years old?",
        "chronic_condition": "Do you have chronic conditions (diabetes/heart/kidney/asthma)?",
    }


def conditions_kb():
    return {
        "Common Cold": {
            "weights": {
                "runny_nose": 2,
                "sneezing": 2,
                "sore_throat": 1.5,
                "cough": 1.5,
                "fever": 0.5,
                "headache": 0.5,
                "body_ache": 0.5,
            },
            "advice": "Rest, warm fluids, saltwater gargles. See a doctor if not improving in 3–5 days.",
            "severity": "low",
        },
        "Influenza (Flu)": {
            "weights": {
                "fever": 2.5,
                "high_fever": 2,
                "chills": 1.5,
                "dry_cough": 2,
                "body_ache": 1.5,
                "fatigue": 1.5,
                "headache": 1.0,
            },
            "advice": "Rest and fluids. Seek care for high fever or breathing difficulty.",
            "severity": "medium",
        },
        "Migraine": {
            "weights": {
                "headache": 3,
                "migraine_aura": 2,
                "photophobia": 1.5,
                "nausea": 1.0,
            },
            "advice": "Rest in a quiet/dark room and hydrate. See specialist if recurrent.",
            "severity": "low",
        },
        "Suspected Dengue": {
            "weights": {
                "fever": 2.5,
                "high_fever": 2,
                "rash": 1.5,
                "eye_pain": 1.5,
                "joint_pain": 1.5,
                "body_ache": 1.0,
                "recent_travel": 0.5,
                "mosquito_bite": 1.5,
            },
            "advice": "Get tested for dengue. Stay hydrated; avoid NSAIDs (use paracetamol).",
            "severity": "high",
        },
        "Typhoid (Suspected)": {
            "weights": {
                "fever": 2,
                "high_fever": 1.5,
                "abdominal_pain": 1.5,
                "diarrhea": 1.0,
                "headache": 1.0,
                "fatigue": 1.0,
                "recent_travel": 0.5,
            },
            "advice": "Persistent fever warrants medical testing. Drink clean water and eat light food.",
            "severity": "medium",
        },
        "COVID-19-like": {
            "weights": {
                "fever": 2,
                "dry_cough": 2,
                "loss_smell": 2,
                "short_breath": 2,
                "fatigue": 1,
                "sore_throat": 1,
                "headache": 0.5,
            },
            "advice": "Consider isolation and wearing a mask. Seek care for breathing difficulty.",
            "severity": "high",
        },
        "Asthma Exacerbation": {
            "weights": {
                "short_breath": 3,
                "wheezing": 2,
                "cough": 1.5,
                "chest_pain": 1.0,
            },
            "advice": "Use inhaler as prescribed. Seek emergency care if breathing worsens.",
            "severity": "high",
        },
        "Gastroenteritis": {
            "weights": {
                "diarrhea": 2.5,
                "vomiting": 2,
                "nausea": 1.5,
                "abdominal_pain": 1.5,
                "dehydration_signs": 2,
            },
            "advice": "ORS/fluids and light food. Seek care for dehydration.",
            "severity": "medium",
        },
        "Dehydration": {
            "weights": {
                "dehydration_signs": 3,
                "diarrhea": 1.0,
                "vomiting": 1.0,
                "fever": 0.5,
            },
            "advice": "Drink ORS/fluids. Emergency care if very dizzy or urine is minimal.",
            "severity": "medium",
        },
        "Food Poisoning": {
            "weights": {
                "vomiting": 2.5,
                "nausea": 2,
                "diarrhea": 1.5,
                "abdominal_pain": 1.5,
                "fever": 0.5,
            },
            "advice": "Hydrate and rest. Seek help for severe symptoms or blood in stool.",
            "severity": "medium",
        },
        "Possible Uncontrolled Diabetes": {
            "weights": {
                "excess_thirst": 2.5,
                "urinate_often": 2,
                "fatigue": 1.5,
                "weight_loss": 1.5,
                "dehydration_signs": 1.0,
            },
            "advice": "Check blood sugar and consult a doctor.",
            "severity": "medium",
        },
        "IBS/IBD-like": {
            "weights": {
                "abdominal_pain": 2,
                "diarrhea": 1.5,
                "blood_in_stool": 2.5,
                "weight_loss": 1.0,
                "fatigue": 1.0,
            },
            "advice": "See a gastroenterologist if blood in stool or weight loss.",
            "severity": "high",
        },
        "Sinusitis": {
            "weights": {
                "headache": 1.5,
                "runny_nose": 1.5,
                "sore_throat": 0.5,
                "fever": 0.5,
                "sneezing": 0.5,
            },
            "advice": "Steam inhalation, saline nasal spray; see ENT if persistent.",
            "severity": "low",
        },
        "Meningitis (Red Flag)": {
            "weights": {
                "high_fever": 2.5,
                "neck_stiff": 3,
                "photophobia": 2,
                "headache": 2,
                "vomiting": 1.0,
            },
            "advice": "Neck stiffness with high fever and light sensitivity → go to ER immediately.",
            "severity": "critical",
        },
        "Cardiac-related (Chest Pain)": {
            "weights": {
                "chest_pain": 3,
                "short_breath": 2.5,
                "age_over_60": 1.0,
                "fatigue": 0.5,
            },
            "advice": "Chest pain or severe shortness of breath → seek emergency care immediately.",
            "severity": "critical",
        },
    }


RED_FLAGS = {
    "severe_combo": [
        {"high_fever", "short_breath"},
        {"chest_pain", "short_breath"},
        {"neck_stiff", "high_fever"},
        {"dehydration_signs", "vomiting", "diarrhea"},
    ]
}


# ------------------------------
# Engine
# ------------------------------

def ask_all_symptoms():
    qs = master_symptoms()
    answers: dict[str, bool] = {}
    print("\n🧭 You will be asked about symptoms. Answer 'yes' if applicable.\n")
    order = list(qs.keys())
    for sid in order:
        answers[sid] = yn_prompt(qs[sid])
    return answers


def score_conditions(sym_answers: dict[str, bool]):
    kb = conditions_kb()
    scores = {}
    max_possible = {}
    for name, d in kb.items():
        weights = d["weights"]
        s = 0.0
        m = 0.0
        for sid, w in weights.items():
            m += max(w, 0)
            if sym_answers.get(sid):
                s += w
        scores[name] = s
        max_possible[name] = m if m > 0 else 1.0
    perc = {k: (scores[k] / max_possible[k]) * 100 for k in scores}
    return perc


def detect_red_flags(sym_answers: dict[str, bool]):
    triggers = []
    for combo in RED_FLAGS["severe_combo"]:
        if all(sym_answers.get(c, False) for c in combo):
            triggers.append(combo)
    return triggers


def explain_top(perc_scores: dict[str, float], top_n: int = 3):
    kb = conditions_kb()
    ranked = sorted(perc_scores.items(), key=lambda kv: kv[1], reverse=True)
    ranked = ranked[:top_n]
    blocks = []
    for name, pct in ranked:
        advice = kb[name]["advice"]
        severity = kb[name]["severity"]
        blocks.append((name, pct, severity, advice))
    return blocks


# ------------------------------
# Reporting
# ------------------------------

def format_report(user_answers: dict[str, bool], results, red_flags):
    qs = master_symptoms()
    dt = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "Rogonirnoy — Symptom Checker Results",
        f"Time: {dt}",
        "",
        "Answers:",
    ]
    for k, v in user_answers.items():
        lines.append(f"- {qs[k]}: {'Yes' if v else 'No'}")
    lines.append("")
    lines.append("Top possible findings:")
    for name, pct, severity, advice in results:
        lines.append(f"• {name}: approx. {pct:.1f}% (severity: {severity})")
        lines.append(f"  Advice: {advice}")
    if red_flags:
        lines.append("")
        lines.append("⚠️ Red flag detected: consider urgent medical attention.")
    lines.append("")
    lines.append("Disclaimer: This is not medical advice. See a doctor for concerning symptoms.")
    return "\n".join(lines)


def save_report(text: str, filename: str = "diagnosis_report.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    return filename


# ------------------------------
# CLI Menu
# ------------------------------

def main():
    print(dedent(
        """
        ==========================================
             Rogonirnoy — English Symptom Checker (CLI)
        ==========================================
        ⚠️ Educational/demo tool only — not a substitute for medical care.
        """
    ))

    while True:
        print("Menu:\n  1) Start new check\n  2) About this program\n  3) Exit")
        choice = read_int("Your choice (1-3): ", mn=1, mx=3)
        if choice == 1:
            answers = ask_all_symptoms()
            scores = score_conditions(answers)
            red = detect_red_flags(answers)
            results = explain_top(scores, top_n=3)

            print("\n===== Results =====")
            for name, pct, severity, advice in results:
                print(f"• {name}: approx. {pct:.1f}% (severity: {severity})")
                print(f"  Advice: {advice}")
            if red:
                print("\n⚠️ Red flag detected: the following symptom combinations are present → consider urgent care.")
                for combo in red:
                    print("   - "+", ".join(combo))

            if yn_prompt("Save a .txt report?"):
                text = format_report(answers, results, red)
                filename = save_report(text)
                print(f"✅ Report saved: {filename}")
            print()
        elif choice == 2:
            print(dedent(
                """
                This tool uses rule-based scoring. It matches your reported symptoms
                against weighted condition profiles and shows the top matches.

                • Red-flag combos will prompt urgent advice.
                • All processing is local, no internet required.
                • Educational purposes only.
                """
            ))
        else:
            print("Thank you. Stay healthy! ✨")
            break


if __name__ == "__main__":
    main()
