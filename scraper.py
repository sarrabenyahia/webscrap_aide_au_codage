import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import json
from datetime import datetime

class CIMScraper:
    def __init__(self, csv_file, output_file="synonymes_cim.xlsx", checkpoint_file="checkpoint.json", delay=1):
        self.csv_file = csv_file
        self.output_file = output_file
        self.checkpoint_file = checkpoint_file
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def load_codes(self):
        """Charge les codes depuis le fichier CSV"""
        try:
            df = pd.read_csv(self.csv_file, sep=';', header=None)
            # Colonne 9 (index 8) contient les codes
            codes = df.iloc[:, 8].dropna().unique().tolist()
            print(f"Chargé {len(codes)} codes uniques")
            return codes
        except Exception as e:
            print(f"Erreur lors du chargement du CSV: {e}")
            return []
    
    def clean_code(self, code):
        """Nettoie le code en supprimant les points"""
        return str(code).replace('.', '').replace('-', '')
    
    def load_checkpoint(self):
        """Charge le point de sauvegarde s'il existe"""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint = json.load(f)
                print(f"Checkpoint trouvé: {checkpoint['processed']}/{checkpoint['total']} codes traités")
                return checkpoint
            except Exception as e:
                print(f"Erreur lors du chargement du checkpoint: {e}")
        return None
    
    def save_checkpoint(self, processed_codes, total_codes, results):
        """Sauvegarde le point de contrôle"""
        checkpoint = {
            'processed': len(processed_codes),
            'total': total_codes,
            'processed_codes': list(processed_codes),
            'timestamp': datetime.now().isoformat(),
            'results_count': len(results)
        }
        try:
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du checkpoint: {e}")
    
    def scrape_synonymes(self, code):
        """Scrape les synonymes pour un code donné"""
        clean_code = self.clean_code(code)
        url = f"https://www.aideaucodage.fr/cim-{clean_code.lower()}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Trouve tous les éléments <li class="synonyme">
            synonymes_elements = soup.find_all('li', class_='synonyme')
            
            synonymes = []
            for element in synonymes_elements:
                synonyme_text = element.get_text(strip=True)
                if synonyme_text:
                    synonymes.append(synonyme_text)
            
            return synonymes
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur réseau pour le code {code}: {e}")
            return []
        except Exception as e:
            print(f"Erreur lors du scraping du code {code}: {e}")
            return []
    
    def save_results(self, results):
        """Sauvegarde les résultats dans un fichier Excel"""
        if not results:
            print("Aucun résultat à sauvegarder")
            return
        
        try:
            df = pd.DataFrame(results, columns=['Code', 'Synonyme'])
            df.to_excel(self.output_file, index=False, engine='openpyxl')
            print(f"Résultats sauvegardés dans {self.output_file}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
    
    def run(self):
        """Lance le scraping complet"""
        print("Démarrage du scraping CIM...")
        
        # Charge les codes
        codes = self.load_codes()
        if not codes:
            print("Aucun code à traiter")
            return
        
        # Charge le checkpoint
        checkpoint = self.load_checkpoint()
        processed_codes = set()
        results = []
        
        if checkpoint:
            processed_codes = set(checkpoint.get('processed_codes', []))
            print(f"Reprise depuis le checkpoint: {len(processed_codes)} codes déjà traités")
        
        # Filtre les codes déjà traités
        remaining_codes = [code for code in codes if code not in processed_codes]
        total_codes = len(codes)
        
        print(f"Codes à traiter: {len(remaining_codes)}/{total_codes}")
        
        try:
            for i, code in enumerate(remaining_codes):
                print(f"Traitement du code {code} ({len(processed_codes)+1}/{total_codes})")
                
                synonymes = self.scrape_synonymes(code)
                
                if synonymes:
                    for synonyme in synonymes:
                        results.append([code, synonyme])
                    print(f"  → {len(synonymes)} synonymes trouvés")
                else:
                    print(f"  → Aucun synonyme trouvé")
                
                processed_codes.add(code)
                
                # Sauvegarde intermédiaire tous les 50 codes
                if (len(processed_codes)) % 50 == 0:
                    print(f"Sauvegarde intermédiaire ({len(processed_codes)} codes traités)")
                    self.save_results(results)
                    self.save_checkpoint(processed_codes, total_codes, results)
                
                # Délai entre les requêtes
                if i < len(remaining_codes) - 1:  # Pas de délai pour la dernière requête
                    time.sleep(self.delay)
        
        except KeyboardInterrupt:
            print("\nInterruption détectée. Sauvegarde des résultats...")
        except Exception as e:
            print(f"Erreur inattendue: {e}")
        finally:
            # Sauvegarde finale
            self.save_results(results)
            self.save_checkpoint(processed_codes, total_codes, results)
            print(f"\nScraping terminé: {len(processed_codes)}/{total_codes} codes traités")
            print(f"Total de synonymes collectés: {len(results)}")
            
            # Nettoie le checkpoint si terminé
            if len(processed_codes) == total_codes:
                try:
                    os.remove(self.checkpoint_file)
                    print("Checkpoint supprimé (scraping complet)")
                except:
                    pass


if __name__ == "__main__":
    # Configuration
    CSV_FILE = "./CIM10GM2024_CSV_S_FR_versionmétadonnée_codes_20241031_new_col.csv"  
    OUTPUT_FILE = "synonymes_cim.xlsx"
    DELAY = 3  # Délai en secondes entre chaque requête
    
    # Création et lancement du scraper
    scraper = CIMScraper(
        csv_file=CSV_FILE,
        output_file=OUTPUT_FILE,
        delay=DELAY
    )
    
    scraper.run()