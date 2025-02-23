import pdfplumber
import csv
import re

# Datei Pfad anpassen
pdf_path = "Data/Dummys/grades.pdf"
csv_output_path = "grades.csv"

def extract_grades_from_pdf(pdf_path):
    extracted_data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split('\n')
            
            for line in lines:
                match = re.match(r"(\d+)\s+([\w\s/,-]+)\s+(SS|WS)\s+(\d{4})\s+([\d,.-]+)\s+(\w+)\s+([\d.]+)", line)
                if match:
                    prnr = match.group(1)
                    pruefungstext = match.group(2).strip()
                    semester = f"{match.group(3)} {match.group(4)}"
                    note = match.group(5).replace(',', '.')  # Deutsche Kommas in Punkte umwandeln
                    status = match.group(6)
                    credits = match.group(7)
                    
                    extracted_data.append([prnr, pruefungstext, semester, note, status, credits])
    return extracted_data

def save_to_csv(data, output_path):
    with open(output_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["PrNr", "Prüfungstext", "Semester", "Note", "Status", "Credits"])
        writer.writerows(data)

def calculate_sums(input_path):
    total_sum = 0
    graded_credits = 0
    total_credits = 0
    passed_courses = 0
    failed_courses = 0
    
    with open(input_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            status = row[4]
            credits = float(row[5])
            try:
                name = row[1]
                note = float(row[3])
                total_sum += note * credits
                graded_credits += credits
            except ValueError:
                print(f"Keine Note für: {name}")
            if status == "BE":
                passed_courses += 1
            elif status == "NB":
                failed_courses += 1
            total_credits += credits
    
    return total_sum, int(total_credits), int(graded_credits), passed_courses, failed_courses

if __name__ == "__main__":
    data = extract_grades_from_pdf(pdf_path)
    
    if data:
        save_to_csv(data, csv_output_path)
        print(f"\nExtraktion abgeschlossen. Daten gespeichert unter: {csv_output_path}\n")
        
        total_sum, total_credits, graded_credits, passed_courses, failed_courses = calculate_sums(csv_output_path)
        average_rounded = round(total_sum / graded_credits, 2)
        
        print(f"Summe der benoteten Credits: {graded_credits}, insgesamt {total_credits}")
        print(f"Durchschnittsnote: {average_rounded}")
        print(f"Bestandene Prüfungen: {passed_courses}, nicht bestandene Prüfungen: {failed_courses}\n")
    else:
        print("Keine gültigen Daten extrahiert.")