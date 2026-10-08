import os
import json
import time
import argparse
from google import genai
from google.genai import types

def carica_file_testo(filepath: str) -> str:
    """Utility per il caricamento sicuro dei file di testo."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File non trovato: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def esegui_batch_grading(
    api_key: str,
    path_gt: str,
    path_prompt: str,
    dir_studenti: str,
    output_file: str,
    model_name: str = "gemini-3.1-flash-lite"
):
    """Pipeline di valutazione batch parametrizzata e indipendente dal dominio."""
    print("[INFO] Caricamento risorse di configurazione e Ground Truth...")
    testo_ground_truth = carica_file_testo(path_gt)
    prompt_fisso = carica_file_testo(path_prompt)

    print("[INFO] Inizializzazione client GenAI...")
    client = genai.Client(api_key=api_key)

    configurazione = types.GenerateContentConfig(
        system_instruction=prompt_fisso,
        temperature=0.1,  
        response_mime_type="application/json"
    )

    if not os.path.exists(dir_studenti):
        print(f"[ERRORE] La cartella '{dir_studenti}' non esiste!")
        return

    file_puml = [f for f in os.listdir(dir_studenti) if f.endswith(".puml")]
    
    # Logic per il RESUME: Carica eventuali valutazioni pregresse
    report_aggregato = {}
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            try:
                report_aggregato = json.load(f)
                print(f"[INFO] Recuperati {len(report_aggregato)} compiti gia' valutati dal disco.")
            except json.JSONDecodeError:
                pass

    for nome_file in file_puml:
        matricola = os.path.splitext(nome_file)[0]
        
        if matricola in report_aggregato:
            print(f"[SKIP] '{matricola}' gia' elaborato. Passo al successivo...")
            continue
            
        path_file = os.path.join(dir_studenti, nome_file)
        print(f"[PROCESSING] Analisi elaborato matricola: {matricola}...")
        codice_studente = carica_file_testo(path_file)

        payload_dinamico = f"""
        [GROUND TRUTH]:
        {testo_ground_truth}

        [DIAGRAMMA STUDENTE]:
        {codice_studente}
        """

        try:
            risposta = client.models.generate_content(
                model=model_name,
                contents=payload_dinamico,
                config=configurazione
            )
            
            dati_valutazione = json.loads(risposta.text)
            report_aggregato[matricola] = dati_valutazione
            print(f"  -> [OK] Valutazione salvata per matricola {matricola}.")
            
            with open(output_file, "w", encoding="utf-8") as out:
                json.dump(report_aggregato, out, indent=4, ensure_ascii=False)
                
            time.sleep(5)
            
        except Exception as e:
            print(f"  -> [ERRORE] Fallita elaborazione per {matricola}. Dettaglio: {e}")
            print("  -> [PAUSA FORZATA] Attesa di 65 secondi per svincolare rate limits API...")
            time.sleep(65)
            continue 

    print(f"\n[SUCCESS] Sperimentazione conclusa. Output salvato in '{output_file}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pipeline modulare di Autograding basata su LLM per diagrammi PlantUML."
    )
    
    parser.add_argument(
        "--api-key", 
        type=str, 
        default=os.getenv("GEMINI_API_KEY"),
        help="Chiave API Google GenAI (default: legge variabile d'ambiente GEMINI_API_KEY)"
    )
    parser.add_argument(
        "--gt", 
        type=str, 
        default="ground_truth.puml",
        help="Path al file PlantUML contenente la Soluzione di Riferimento (Ground Truth)"
    )
    parser.add_argument(
        "--prompt", 
        type=str, 
        default="system_prompt.txt",
        help="Path al file di testo contenente il System Prompt e le regole della Tassonomia"
    )
    parser.add_argument(
        "--dir", 
        type=str, 
        default="studenti",
        help="Directory contenente gli elaborati PlantUML degli studenti (.puml)"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="risultati_eval.json",
        help="Path del file JSON in cui salvare i report aggregati della valutazione"
    )
    parser.add_argument(
        "--model", 
        type=str, 
        default="gemini-3.1-flash-lite",
        help="Modello Generativo da invocare via API"
    )

    args = parser.parse_args()

    if not args.api_key:
        print("[CRITICAL] API Key non trovata! Passarla tramite --api-key o definire GEMINI_API_KEY.")
        exit(1)

    esegui_batch_grading(
        api_key=args.api_key,
        path_gt=args.gt,
        path_prompt=args.prompt,
        dir_studenti=args.dir,
        output_file=args.output,
        model_name=args.model
    )