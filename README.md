# 🎓 LLM-Based UML Autograder

Repository ufficiale del progetto di tesi triennale: **"[Sperimentazione di tecniche
LLM-based per supportare l’assessment
automatico di Class Diagram UML
realizzati a scopo didattico]"**  
*Università degli Studi di Napoli Federico II*

Questo repository contiene un framework software sviluppato per automatizzare la valutazione di modelli concettuali UML (Class Diagram) codificati in PlantUML. Il sistema sfrutta le capacità di inferenza dei Large Language Models (LLM) — nello specifico l'API di Google Gemini — applicando un approccio **Zero-Shot Transfer** basato sui rigorosi criteri formali della *Tassonomia UNINA*.

## ✨ Caratteristiche Principali
- **Zero-Shot Evaluation:** Il sistema non necessita di addestramento o fine-tuning sul dominio specifico. Utilizza un *System Prompt* ingegnerizzato per astrarre le regole della modellazione Object-Oriented.
- **Valutazione Multi-Categoria (Tassonomia UNINA):** Classificazione degli errori su 7 categorie architetturali (Classi, Associazioni, Generalizzazioni, Cardinalità, Attributi, Metodi, Ruoli).
- **Resilienza e Scalabilità:** Lo script di inferenza gestisce automaticamente i *Rate Limit* delle API (con pause forzate) e integra una logica di *resume* per riprendere l'esecuzione senza perdere i dati già processati in caso di interruzione.
- **Pipeline Analitica:** Generazione automatica di metriche aggregate (Accuracy, Precision, Recall, F1-Score, Exact Match) con esportazione in formato Excel e codice LaTeX pronto per l'inclusione nel manoscritto di tesi.

## 🗂 Struttura del Repository

    uml-llm-autograder/
    ├── dataset/
    │   ├── album_fotografico/      # Diagrammi PlantUML anonimizzati (S01.txt, S02.txt...)
    │   ├── posta_elettronica/       # Dataset per validazione Cross-Domain
    │   └── ground_truth/              # Soluzioni di riferimento del docente
    ├── prompts/
    │   └── system_prompt.txt       # Prompt definitivo con le regole valutative
    ├── src/
    │   ├── valutatore.py              # Script di inferenza LLM batch
    │   └── esporta_dataset_tesi.py    # Script per calcolo metriche e matrici di confusione
    ├── results/                       # Output JSON, Excel e LaTeX generati
    ├── config_esperimento.json        # Configurazione per il calcolo delle metriche
    ├── requirements.txt               # Dipendenze del progetto
    └── README.md

*Nota: A tutela della privacy, tutti gli elaborati studenteschi sono stati rigorosamente anonimizzati (identificativi S01, S02, ..., S35).*

## ⚙️ Istruzioni per la Replicazione (Riproducibilità)

### 1. Prerequisiti e Installazione
Assicurati di avere Python 3.8+ installato sul sistema.
Clona il repository e installa le librerie necessarie:

    git clone https://github.com/[TUO-USERNAME]/uml-llm-autograder.git
    cd uml-llm-autograder
    pip install -r requirements.txt

### 2. Configurazione API
Il sistema richiede una chiave API valida per i modelli Google Gemini. Puoi impostarla come variabile d'ambiente:
- **Windows:** `set GEMINI_API_KEY=la_tua_chiave`
- **Mac/Linux:** `export GEMINI_API_KEY="la_tua_chiave"`

### 3. Fase di Inferenza (Autograding)
Per replicare l'estrazione delle valutazioni da parte dell'LLM, esegui lo script `valutatore.py` specificando i percorsi di input e output. Esempio di esecuzione sul dataset "Album Fotografico":

    python src/valutatore.py \
      --dir dataset/album_fotografico \
      --gt dataset/ground_truth/ground_truth_foto.txt \
      --prompt prompts/system_prompt.txt \
      --output results/output_album.json

### 4. Calcolo delle Metriche
Una volta estratti i JSON ed eventualmente convertiti in formato tabellare (CSV), è possibile generare l'analisi statistica. Configura i percorsi nel file `config_esperimento.json` e lancia:

    python src/esporta_dataset_tesi.py --config config_esperimento.json

I risultati verranno salvati nella cartella `results/` sia in formato foglio di calcolo (`.xlsx`) sia come tabelle LaTeX pronte per la pubblicazione (`.tex`).

## 🔄 Estensione a Nuovi Domini (Cross-Domain)
Da un punto di vista operativo, lo sforzo richiesto per replicare o estendere la sperimentazione a nuovi compiti d'esame è minimo. L'approccio Zero-Shot non richiede la riscrittura del codice o del System Prompt. Lo sperimentatore deve esclusivamente:
1. Fornire la nuova *Ground Truth* del docente in formato testo/PlantUML.
2. Trascrivere i diagrammi degli studenti nel medesimo formato, posizionandoli in una nuova cartella nel `dataset/`.
3. Lanciare la pipeline tramite riga di comando.

## 👤 Autore
- **[Davide Gatta]** - *Studente Triennale, Università degli Studi di Napoli Federico II*