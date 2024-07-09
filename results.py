import asyncio
from pyppeteer import launch
import csv

# URL de base du site eresultats.bj
BASE_URL = "https://www.eresultats.bj/consulter/bepc-session-normal-2024"

# Liste des numéros de table à envoyer
table_numbers = ['24K06120', '24K19963']

async def fetch_results(table_number):
    browser = await launch(headless=True)
    page = await browser.newPage()
    await page.goto(BASE_URL)
    print(f"Navigué vers {BASE_URL}")
    
    # Attendre que le champ de saisie soit disponible
    await page.waitForSelector('#exampleInputEmail1', timeout=60000)
    print("Champ de saisie trouvé")
    
    # Remplir le formulaire et soumettre
    await page.type('#exampleInputEmail1', table_number)
    print(f"Numéro de table {table_number} saisi")
    await page.click('#content > div > div > div:nth-child(1) > div > div > form > button')
    print("Formulaire soumis")
    
    # Attendre un court instant pour permettre au formulaire de se soumettre
    await asyncio.sleep(5)  # Attendre 5 secondes
    
    # Imprimer le HTML pour vérifier l'état après la soumission du formulaire
    # content = await page.content()
    # print("Contenu HTML après soumission du formulaire:")
    # print(content)  # Afficher le contenu HTML pour vérifier l'état
    
    # Vérifier la présence d'un message d'erreur
    error_message = await page.evaluate('''() => {
        const errorElement = document.querySelector('#content .alert.alert-danger');
        return errorElement ? errorElement.innerText.trim() : null;
    }''')
    
    if error_message:
        print(f"Message d'erreur détecté : {error_message}")
        return None
    
    # Augmenter le temps d'attente pour les résultats
    await page.waitForSelector('#content > div > div > div:nth-child(2) > div', timeout=60000)
    print("Résultats chargés")
    
    # Imprimer le HTML des résultats pour vérification

    # Extraire les résultats
    results = await page.evaluate('''() => {
        return Array.from(document.querySelectorAll('#content > div > div > div:nth-child(2) > div > div > div > table > tbody > tr:nth-child(9) > td > h4 > span')).map(element => element.textContent.trim());
    }''')
    print(f"Résultats extraits : {results}")
    
    await browser.close()
    return results

def store_results_in_csv(results, filename="results.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Écrire les en-têtes des colonnes
        writer.writerow(["Numéro de table", "Résultats"])
        
        # Écrire les résultats
        for table_number, result_list in results.items():
            writer.writerow([table_number, ", ".join(result_list)])
    print(f"Résultats sauvegardés dans {filename}")

def main():
    all_results = {}
    
    for number in table_numbers:
        results = asyncio.get_event_loop().run_until_complete(fetch_results(number))
        if results:
            all_results[number] = results
        else:
            print(f"Aucun résultat trouvé pour le numéro de table {number}")
    
    store_results_in_csv(all_results)

if __name__ == "__main__":
    main()
