def format_history_entry_to_string(entry: dict) -> str:
    parts = [f"Pada {entry.get('timestamp')}:"]

    if meal := entry.get("meal_description"):
        parts.append(f"Makan '{meal}'.")
    if glucose := entry.get("blood_glucose_mg_dl"):
        parts.append(f"Gula darah {glucose} mg/dl.")
    if insulin_units := entry.get("insulin_units"):
        parts.append(f"Suntik {insulin_units} unit insulin.")
    if insulin_brand := entry.get("insulin_units"):
        parts.append(f"Suntik menggunakan insulin dengan merk {insulin_brand}.")
    if condition := entry.get("condition_description"):
        parts.append(f"Kondisi: '{condition}'.")
    if activity := entry.get("activity"):
        parts.append(f"Aktivitas: '{activity}'.")
    if medicines := entry.get("medicine_taken"):
        if isinstance(medicines, list):
            joined_meds = ", ".join(medicines)
            parts.append(f"Obat yang diminum: {joined_meds}.")
        else:
            parts.append(f"Obat yang diminum: {medicines}.")

    return " ".join(parts).strip()
