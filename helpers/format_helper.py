def format_history_entry_to_string(entry: dict) -> str:
    parts = [f"Pada {entry.get('timestamp')}:"]

    if meal := entry.get("meal_description"):
        parts.append(f"Makan '{meal}'.")
    if glucose := entry.get("blood_glucose_mg_dl"):
        parts.append(f"Gula darah {glucose} mg/dl.")
    if insulin := entry.get("insulin_units"):
        parts.append(f"Suntik {insulin} unit insulin.")
    if condition := entry.get("condition_description"):
        parts.append(f"Kondisi: '{condition}'.")
    if activity := entry.get("activity"):
        parts.append(f"Aktivitas: '{activity}'.")
    if medicine := entry.get("medicine_taken"):
        parts.append(f"Obat: '{medicine}'.")

    return " ".join(parts).strip()
