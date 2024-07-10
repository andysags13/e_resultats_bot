import asyncio
from pyppeteer import launch
import telebot

API_TOKEN = '6334936391:AAEnDDqeuP8zt-fm1RrlD3DtGQLlAMHCocI'
bot = telebot.TeleBot(API_TOKEN)

BASE_URL = "https://www.eresultats.bj/consulter/bepc-session-normal-2024"

async def fetch_results(table_number):
    browser = await launch(headless=True)
    page = await browser.newPage()
    await page.goto(BASE_URL)
    
    await page.waitForSelector('#exampleInputEmail1', timeout=60000)
    await page.type('#exampleInputEmail1', table_number)
    await page.click('#content > div > div > div:nth-child(1) > div > div > form > button')
    await asyncio.sleep(5)
    
    error_message = await page.evaluate('''() => {
        const errorElement = document.querySelector('#content .alert.alert-danger');
        return errorElement ? errorElement.innerText.trim() : null;
    }''')
    
    if error_message:
        await browser.close()
        return f"Erreur: {error_message}"
    
    await page.waitForSelector('#content > div > div > div:nth-child(2) > div', timeout=60000)
    
    results = await page.evaluate('''() => {
        return Array.from(document.querySelectorAll('#content > div > div > div:nth-child(2) > div > div > div > table > tbody > tr:nth-child(9) > td > h4 > span')).map(element => element.textContent.trim());
    }''')
    
    await browser.close()
    return results

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, (
        "Bienvenue sur le bot de consultation des résultats du BEPC 2024!\n\n"
        "Utilisez la commande /result suivie de votre numéro de table pour obtenir vos résultats.\n"
        "Par exemple: /result 24K06120"
    ))

@bot.message_handler(commands=['result'])
def handle_results(message):
    try:
        table_number = message.text.split()[1]
        results = asyncio.run(fetch_results(table_number))
        if results:
            bot.reply_to(message, f"Résultats pour {table_number}: {', '.join(results)}")
        else:
            bot.reply_to(message, f"Aucun résultat trouvé pour le numéro de table {table_number}")
    except IndexError:
        bot.reply_to(message, "Veuillez fournir un numéro de table.")
    except Exception as e:
        bot.reply_to(message, f"Erreur : {str(e)}")

if __name__ == '__main__':
    print("Le bot est en cours d'exécution...")
    bot.polling()
