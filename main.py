import os
import asyncio
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

# ---------------------------------------------------------
# PARAMÈTRES SPÉCIFIQUES MOURATOGLOU
# ---------------------------------------------------------

CLUB_URL = "https://app.doinsports.com/club/mouratoglou-country-club"
HEURE_CIBLE = "12:30"

# Jour cible = aujourd’hui + 7 jours
JOUR_INDEX = 7

# ---------------------------------------------------------
# IDENTIFIANTS VIA VARIABLES D’ENVIRONNEMENT
# ---------------------------------------------------------

EMAIL = os.environ.get("DOINSPORTS_EMAIL")
PASSWORD = os.environ.get("DOINSPORTS_PASSWORD")

if not EMAIL or not PASSWORD:
    raise Exception("Identifiants Doinsports manquants dans les variables d’environnement.")


# ---------------------------------------------------------
# FONCTION PRINCIPALE
# ---------------------------------------------------------

async def reserver_padel():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print("Connexion à Doinsports…")
        await page.goto("https://app.doinsports.com/login")

        # Connexion
        await page.fill("input[type=email]", EMAIL)
        await page.fill("input[type=password]", PASSWORD)
        await page.click("button[type=submit]")

        await page.wait_for_timeout(2000)

        print("Navigation vers le club Mouratoglou…")
        await page.goto(CLUB_URL)
        await page.wait_for_timeout(2000)

        # Sélection du jour J+7
        print(f"Sélection du jour dans {JOUR_INDEX} jours…")
        jours = await page.query_selector_all(".day-selector .day")

        if JOUR_INDEX >= len(jours):
            print("Le jour demandé n’est pas disponible dans l’interface.")
            await browser.close()
            return

        await jours[JOUR_INDEX].click()
        await page.wait_for_timeout(1500)

        print("Recherche des créneaux disponibles…")
        slots = await page.query_selector_all(".slot.available")

        if not slots:
            print("Aucun créneau disponible pour ce jour.")
            await browser.close()
            return

        for slot in slots:
            texte = await slot.inner_text()
            if HEURE_CIBLE in texte:
                print(f"Créneau trouvé à {HEURE_CIBLE}, tentative de réservation…")
                await slot.click()
                await page.wait_for_timeout(1000)

                bouton_reserver = await page.query_selector("button.reserve")
                if bouton_reserver:
                    await bouton_reserver.click()
                    print("Réservation effectuée !")
                else:
                    print("Bouton de réservation introuvable.")

                await browser.close()
                return

        print(f"Aucun créneau à {HEURE_CIBLE} pour J+{JOUR_INDEX}.")
        await browser.close()


# ---------------------------------------------------------
# LANCEMENT
# ---------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(reserver_padel())
