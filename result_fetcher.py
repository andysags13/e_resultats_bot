import asyncio
from pyppeteer import launch

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

def get_exam_results(table_number):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(fetch_results(table_number))
    loop.close()
    return results
