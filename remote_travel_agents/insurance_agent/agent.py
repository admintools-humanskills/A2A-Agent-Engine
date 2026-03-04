from google import genai
from google.genai import types
import uuid
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

SYSTEM_INSTRUCTION = """
# INSTRUCTIONS

Vous etes un conseiller en assurance BNP Paribas Cardif, specialise dans les produits d'assurance pour les particuliers.
Votre role est d'aider les clients a trouver la bonne couverture, generer des devis et prendre rendez-vous avec un conseiller specialise.
Si le client pose une question hors du domaine de l'assurance, indiquez poliment que vous ne pouvez l'aider que sur les sujets d'assurance Cardif.

You understand requests in both French and English and always respond in the language used by the client.

# CATALOGUE DE PRODUITS

## 1. Assurance Pret Immobilier

| Formule | Couverture | Tarif indicatif |
|---------|-----------|-----------------|
| Essentielle | Deces + PTIA | 0.10% du capital emprunte/an |
| Confort | Deces + PTIA + ITT + IPT | 0.22% du capital emprunte/an |
| Serenite | Deces + PTIA + ITT + IPT + Perte d'emploi | 0.34% du capital emprunte/an |

- PTIA = Perte Totale et Irreversible d'Autonomie
- ITT = Incapacite Temporaire Totale de travail
- IPT = Invalidite Permanente Totale
- Quotite : part du capital assure (de 50% a 100%, defaut 100%)
- Tarif varie selon l'age de l'emprunteur (majoration de +0.02% par tranche de 10 ans au-dela de 30 ans)

## 2. Assurance Habitation

| Formule | Type de bien | Tarif mensuel |
|---------|-------------|---------------|
| Locataire Essentiel | Appartement <= 50m2 | 9 EUR/mois |
| Locataire Confort | Appartement <= 100m2 | 16 EUR/mois |
| Proprietaire Essentiel | Appartement/Maison <= 80m2 | 18 EUR/mois |
| Proprietaire Confort | Appartement/Maison <= 150m2 | 28 EUR/mois |
| Proprietaire Premium | Maison > 150m2 | 42 EUR/mois |

Garanties incluses : Responsabilite civile, Degats des eaux, Incendie, Vol, Bris de glace, Catastrophes naturelles.
Formules Confort et Premium ajoutent : Protection juridique, Assistance 24h/24, Remplacement a neuf.

## 3. Prevoyance

| Formule | Couverture | Tarif mensuel indicatif |
|---------|-----------|------------------------|
| Capital Deces Essentiel | 50 000 EUR capital deces | 12 EUR/mois |
| Capital Deces Confort | 150 000 EUR capital deces + rente education | 29 EUR/mois |
| Prevoyance Complete | Deces 200 000 EUR + Invalidite (rente 1 500 EUR/mois) + Incapacite | 55 EUR/mois |

- Tarif indicatif pour un adulte de 30-40 ans, non-fumeur
- Majoration selon l'age, la situation de sante et la profession

## 4. Epargne Retraite (PER Cardif)

| Profil de gestion | Allocation | Frais de gestion |
|-------------------|-----------|------------------|
| Prudent | 70% fonds euro / 30% UC | 0.75%/an |
| Equilibre | 40% fonds euro / 60% UC | 0.85%/an |
| Dynamique | 10% fonds euro / 90% UC | 0.95%/an |

- Versement minimum : 50 EUR/mois ou 500 EUR en ponctuel
- Rendement fonds euro 2024 : 3.2% net de frais de gestion
- UC = Unites de Compte (supports en actions, obligations, immobilier)
- Avantage fiscal : versements deductibles du revenu imposable (dans la limite du plafond)

# REGLES

- Quand TOUTES les informations necessaires sont fournies, generez le devis directement avec la fonction get_insurance_quote SANS demander confirmation.
- Si des informations manquent, demandez UNIQUEMENT les informations manquantes.
- Toujours presenter les garanties de maniere claire et structuree.
- Mentionner que les tarifs sont indicatifs et qu'un conseiller peut affiner le devis personnalise.
- Pour les demandes de rendez-vous, utiliser la fonction book_advisor_appointment.
- Ne PAS inventer de produits ou tarifs qui ne figurent pas dans le catalogue ci-dessus.
"""

RATE_MAP = {
    "essentielle": 0.0010,
    "confort": 0.0022,
    "serenite": 0.0034,
}

HABITATION_MAP = {
    "locataire_essentiel": {"label": "Locataire Essentiel", "tarif": 9, "surface_max": 50, "statut": "locataire"},
    "locataire_confort": {"label": "Locataire Confort", "tarif": 16, "surface_max": 100, "statut": "locataire"},
    "proprietaire_essentiel": {"label": "Proprietaire Essentiel", "tarif": 18, "surface_max": 80, "statut": "proprietaire"},
    "proprietaire_confort": {"label": "Proprietaire Confort", "tarif": 28, "surface_max": 150, "statut": "proprietaire"},
    "proprietaire_premium": {"label": "Proprietaire Premium", "tarif": 42, "surface_max": 9999, "statut": "proprietaire"},
}

PREVOYANCE_MAP = {
    "capital_deces_essentiel": {"label": "Capital Deces Essentiel", "capital": 50000, "tarif_base": 12},
    "capital_deces_confort": {"label": "Capital Deces Confort", "capital": 150000, "tarif_base": 29},
    "prevoyance_complete": {"label": "Prevoyance Complete", "capital": 200000, "tarif_base": 55},
}

PER_MAP = {
    "prudent": {"fonds_euro": 70, "uc": 30, "frais": 0.75},
    "equilibre": {"fonds_euro": 40, "uc": 60, "frais": 0.85},
    "dynamique": {"fonds_euro": 10, "uc": 90, "frais": 0.95},
}


def get_insurance_quote(
    product_type: str,
    formule: str,
    # Pret immobilier
    montant_pret: float = 0,
    duree_pret_annees: int = 0,
    age_emprunteur: int = 0,
    quotite: int = 100,
    # Habitation
    type_bien: str = "",
    surface_m2: int = 0,
    ville: str = "",
    statut: str = "",
    # Prevoyance
    age: int = 0,
    situation_familiale: str = "",
    revenus_annuels: float = 0,
    # Epargne retraite
    versement_mensuel: float = 0,
    profil_risque: str = "",
) -> dict:
    """Generates a simulated insurance quote.

    Args:
        product_type: Type of insurance product (pret_immobilier, habitation, prevoyance, epargne_retraite).
        formule: Formula/plan name.
        montant_pret: Loan amount in EUR (for pret_immobilier).
        duree_pret_annees: Loan duration in years (for pret_immobilier).
        age_emprunteur: Borrower age (for pret_immobilier).
        quotite: Coverage share percentage, default 100% (for pret_immobilier).
        type_bien: Property type - appartement or maison (for habitation).
        surface_m2: Property surface in m2 (for habitation).
        ville: City (for habitation).
        statut: locataire or proprietaire (for habitation).
        age: Client age (for prevoyance and epargne_retraite).
        situation_familiale: Family situation (for prevoyance).
        revenus_annuels: Annual income in EUR (for prevoyance).
        versement_mensuel: Monthly contribution in EUR (for epargne_retraite).
        profil_risque: Risk profile - prudent, equilibre, dynamique (for epargne_retraite).

    Returns:
        dict: Quote details with reference number, coverage, pricing and validity.
    """
    quote_id = f"CDF-{uuid.uuid4().hex[:8].upper()}"
    validity_date = (datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y")
    product = product_type.lower().replace(" ", "_").replace("é", "e").replace("ê", "e")
    formula_key = formule.lower().replace(" ", "_").replace("é", "e").replace("ê", "e")

    if "pret" in product or "mortgage" in product or "immobilier" in product:
        rate = RATE_MAP.get(formula_key, 0.0022)
        # Age adjustment: +0.02% per decade above 30
        age_val = age_emprunteur or age or 35
        if age_val > 30:
            rate += ((age_val - 30) // 10) * 0.0002
        capital_assure = montant_pret * (quotite / 100)
        cout_annuel = capital_assure * rate
        cout_mensuel = round(cout_annuel / 12, 2)
        cout_total = round(cout_annuel * duree_pret_annees, 2)

        guarantees = {
            "essentielle": "Deces + PTIA",
            "confort": "Deces + PTIA + ITT + IPT",
            "serenite": "Deces + PTIA + ITT + IPT + Perte d'emploi",
        }

        return {
            "quote_id": quote_id,
            "product": "Assurance Pret Immobilier",
            "formule": formule.capitalize(),
            "montant_pret": f"{montant_pret:,.0f} EUR",
            "duree": f"{duree_pret_annees} ans",
            "age_emprunteur": age_val,
            "quotite": f"{quotite}%",
            "capital_assure": f"{capital_assure:,.0f} EUR",
            "garanties": guarantees.get(formula_key, "Deces + PTIA + ITT + IPT"),
            "taux_annuel": f"{rate*100:.2f}% du capital/an",
            "cout_mensuel": f"{cout_mensuel} EUR/mois",
            "cout_total_estime": f"{cout_total} EUR sur {duree_pret_annees} ans",
            "validite_devis": validity_date,
            "note": "Tarif indicatif - un conseiller Cardif peut affiner ce devis selon votre profil complet.",
        }

    elif "habitation" in product or "home" in product:
        matched = None
        for key, info in HABITATION_MAP.items():
            if formula_key and formula_key in key:
                matched = info
                break
        if not matched:
            # Auto-select based on statut and surface
            stat = statut.lower() if statut else "locataire"
            for key, info in HABITATION_MAP.items():
                if stat in info["statut"] and surface_m2 <= info["surface_max"]:
                    matched = info
                    break
            if not matched:
                matched = {"label": "Proprietaire Premium", "tarif": 42, "surface_max": 9999, "statut": "proprietaire"}

        tarif = matched["tarif"]
        return {
            "quote_id": quote_id,
            "product": "Assurance Habitation",
            "formule": matched["label"],
            "type_bien": type_bien or "Non precise",
            "surface": f"{surface_m2} m2",
            "ville": ville or "Non precisee",
            "statut": statut or "Non precise",
            "garanties": "Responsabilite civile, Degats des eaux, Incendie, Vol, Bris de glace, Catastrophes naturelles"
            + (", Protection juridique, Assistance 24h/24, Remplacement a neuf" if tarif >= 16 else ""),
            "tarif_mensuel": f"{tarif} EUR/mois",
            "tarif_annuel": f"{tarif * 12} EUR/an",
            "validite_devis": validity_date,
            "note": "Tarif indicatif - un conseiller Cardif peut affiner ce devis selon votre profil complet.",
        }

    elif "prevoyance" in product or "life" in product or "disability" in product or "deces" in product:
        matched = None
        for key, info in PREVOYANCE_MAP.items():
            if formula_key and formula_key in key:
                matched = info
                break
        if not matched:
            matched = PREVOYANCE_MAP["capital_deces_essentiel"]

        tarif = matched["tarif_base"]
        age_val = age or 35
        # Age adjustment
        if age_val > 40:
            tarif = round(tarif * (1 + (age_val - 40) * 0.02), 2)

        details = {
            "capital_deces_essentiel": f"Capital deces : 50 000 EUR",
            "capital_deces_confort": f"Capital deces : 150 000 EUR + Rente education pour enfants a charge",
            "prevoyance_complete": f"Capital deces : 200 000 EUR + Rente invalidite : 1 500 EUR/mois + Indemnites incapacite",
        }

        return {
            "quote_id": quote_id,
            "product": "Prevoyance",
            "formule": matched["label"],
            "age": age_val,
            "situation_familiale": situation_familiale or "Non precisee",
            "revenus_annuels": f"{revenus_annuels:,.0f} EUR" if revenus_annuels else "Non precises",
            "garanties": details.get(formula_key, details["capital_deces_essentiel"]),
            "tarif_mensuel": f"{tarif} EUR/mois",
            "tarif_annuel": f"{round(tarif * 12, 2)} EUR/an",
            "validite_devis": validity_date,
            "note": "Tarif indicatif pour non-fumeur - un conseiller Cardif peut affiner ce devis selon votre profil de sante.",
        }

    elif "epargne" in product or "retraite" in product or "per" in product or "retirement" in product:
        profil_key = (profil_risque or formula_key or "equilibre").lower()
        per_info = PER_MAP.get(profil_key, PER_MAP["equilibre"])
        age_val = age or 35
        versement = versement_mensuel or 50
        annees_jusqua_retraite = max(62 - age_val, 1)
        total_versements = versement * 12 * annees_jusqua_retraite
        # Simplified projection: fonds euro part at 3.2%, UC part at 5% average
        rendement_estime = (per_info["fonds_euro"] / 100 * 0.032 + per_info["uc"] / 100 * 0.05)
        # Rough compound projection
        capital_estime = 0
        for year in range(annees_jusqua_retraite):
            capital_estime = (capital_estime + versement * 12) * (1 + rendement_estime)
        capital_estime = round(capital_estime, 2)

        return {
            "quote_id": quote_id,
            "product": "PER Cardif - Epargne Retraite",
            "profil_gestion": profil_key.capitalize(),
            "allocation": f"{per_info['fonds_euro']}% fonds euro / {per_info['uc']}% UC",
            "frais_gestion": f"{per_info['frais']}%/an",
            "versement_mensuel": f"{versement} EUR/mois",
            "age": age_val,
            "depart_retraite_estime": f"{62} ans (dans {annees_jusqua_retraite} ans)",
            "total_versements_estimes": f"{total_versements:,.0f} EUR",
            "capital_estime_retraite": f"{capital_estime:,.0f} EUR (projection non garantie)",
            "rendement_fonds_euro_2024": "3.2% net",
            "avantage_fiscal": "Versements deductibles du revenu imposable",
            "validite_devis": validity_date,
            "note": "Projection indicative non contractuelle. Les UC presentent un risque de perte en capital. Un conseiller Cardif peut etablir une simulation personnalisee.",
        }

    return {
        "quote_id": quote_id,
        "error": "Type de produit non reconnu. Produits disponibles : pret_immobilier, habitation, prevoyance, epargne_retraite.",
    }


def book_advisor_appointment(
    client_name: str,
    phone: str,
    product_interest: str,
    preferred_date: str = "",
    preferred_time: str = "",
) -> dict:
    """Books an appointment with a Cardif insurance advisor.

    Args:
        client_name: Full name of the client.
        phone: Client phone number.
        product_interest: Insurance product of interest.
        preferred_date: Preferred date (YYYY-MM-DD). If empty, next business day is used.
        preferred_time: Preferred time (HH:MM). If empty, available slots are proposed.

    Returns:
        dict: Appointment confirmation with date, time and advisor details.
    """
    appointment_id = f"RDV-{uuid.uuid4().hex[:6].upper()}"

    # Use next business day if no date provided
    if preferred_date:
        try:
            appt_date = datetime.strptime(preferred_date, "%Y-%m-%d")
        except ValueError:
            appt_date = datetime.now() + timedelta(days=1)
    else:
        appt_date = datetime.now() + timedelta(days=1)
    # Skip weekends
    while appt_date.weekday() >= 5:
        appt_date += timedelta(days=1)

    date_str = appt_date.strftime("%d/%m/%Y")
    available_slots = ["10:00", "14:00", "16:30"]

    if preferred_time and preferred_time in available_slots:
        confirmed_time = preferred_time
    elif preferred_time:
        confirmed_time = preferred_time
    else:
        confirmed_time = available_slots[0]

    product_labels = {
        "pret_immobilier": "Assurance Pret Immobilier",
        "habitation": "Assurance Habitation",
        "prevoyance": "Prevoyance",
        "epargne_retraite": "Epargne Retraite (PER)",
        "mortgage": "Assurance Pret Immobilier",
        "home": "Assurance Habitation",
        "life": "Prevoyance",
        "retirement": "Epargne Retraite (PER)",
    }
    product_label = product_labels.get(
        product_interest.lower().replace(" ", "_"),
        product_interest,
    )

    return {
        "appointment_id": appointment_id,
        "client_name": client_name,
        "phone": phone,
        "product": product_label,
        "date": date_str,
        "time": confirmed_time,
        "available_slots": [f"{date_str} a {s}" for s in available_slots],
        "advisor": "Sophie Martin, Conseillere Cardif",
        "location": "Agence BNP Paribas - ou visioconference selon votre preference",
        "status": "confirmed",
        "note": "Un SMS de confirmation vous sera envoye. Pensez a vous munir de vos documents d'identite et justificatifs.",
    }


# Gemini function declarations
get_insurance_quote_tool = types.FunctionDeclaration(
    name="get_insurance_quote",
    description="Generates a simulated insurance quote for a Cardif product (mortgage insurance, home insurance, life insurance, or retirement savings).",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "product_type": types.Schema(type=types.Type.STRING, description="Type of insurance: pret_immobilier, habitation, prevoyance, or epargne_retraite."),
            "formule": types.Schema(type=types.Type.STRING, description="Plan/formula name (e.g. essentielle, confort, serenite, prudent, equilibre, dynamique)."),
            "montant_pret": types.Schema(type=types.Type.NUMBER, description="Loan amount in EUR (for pret_immobilier)."),
            "duree_pret_annees": types.Schema(type=types.Type.INTEGER, description="Loan duration in years (for pret_immobilier)."),
            "age_emprunteur": types.Schema(type=types.Type.INTEGER, description="Borrower age (for pret_immobilier)."),
            "quotite": types.Schema(type=types.Type.INTEGER, description="Coverage share %, default 100 (for pret_immobilier)."),
            "type_bien": types.Schema(type=types.Type.STRING, description="Property type: appartement or maison (for habitation)."),
            "surface_m2": types.Schema(type=types.Type.INTEGER, description="Property surface in m2 (for habitation)."),
            "ville": types.Schema(type=types.Type.STRING, description="City (for habitation)."),
            "statut": types.Schema(type=types.Type.STRING, description="locataire or proprietaire (for habitation)."),
            "age": types.Schema(type=types.Type.INTEGER, description="Client age (for prevoyance and epargne_retraite)."),
            "situation_familiale": types.Schema(type=types.Type.STRING, description="Family situation (for prevoyance)."),
            "revenus_annuels": types.Schema(type=types.Type.NUMBER, description="Annual income in EUR (for prevoyance)."),
            "versement_mensuel": types.Schema(type=types.Type.NUMBER, description="Monthly contribution in EUR (for epargne_retraite)."),
            "profil_risque": types.Schema(type=types.Type.STRING, description="Risk profile: prudent, equilibre, dynamique (for epargne_retraite)."),
        },
        required=["product_type", "formule"],
    ),
)

book_advisor_appointment_tool = types.FunctionDeclaration(
    name="book_advisor_appointment",
    description="Books an appointment with a BNP Paribas Cardif insurance advisor for a personalized consultation.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "client_name": types.Schema(type=types.Type.STRING, description="Full name of the client."),
            "phone": types.Schema(type=types.Type.STRING, description="Client phone number."),
            "product_interest": types.Schema(type=types.Type.STRING, description="Insurance product of interest (pret_immobilier, habitation, prevoyance, epargne_retraite)."),
            "preferred_date": types.Schema(type=types.Type.STRING, description="Preferred appointment date (YYYY-MM-DD)."),
            "preferred_time": types.Schema(type=types.Type.STRING, description="Preferred time (HH:MM). Available slots: 10:00, 14:00, 16:30."),
        },
        required=["client_name", "phone", "product_interest"],
    ),
)

insurance_tools = types.Tool(function_declarations=[get_insurance_quote_tool, book_advisor_appointment_tool])

FUNCTION_MAP = {
    "get_insurance_quote": get_insurance_quote,
    "book_advisor_appointment": book_advisor_appointment,
}


class InsuranceAgent:
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        self.client = genai.Client(vertexai=True)
        self.model_id = "gemini-2.5-flash-lite"
        self.sessions: dict[str, list] = {}

    def invoke(self, query, sessionId) -> str:
        history = self.sessions.get(sessionId, [])
        history.append(types.Content(role="user", parts=[types.Part.from_text(text=query)]))

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[insurance_tools],
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=history,
                config=config,
            )
        except Exception as e:
            print(f"Error calling GenAI: {e}")
            return f"Sorry, I encountered an error processing your request: {e}"

        max_iterations = 5
        for _ in range(max_iterations):
            if not response.candidates or not response.candidates[0].content or not response.candidates[0].content.parts:
                break

            function_call_part = None
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    function_call_part = part
                    break

            if not function_call_part:
                break

            # Add assistant response to history
            history.append(response.candidates[0].content)

            fn_call = function_call_part.function_call
            fn_args = dict(fn_call.args) if fn_call.args else {}

            fn_to_call = FUNCTION_MAP.get(fn_call.name)
            if fn_to_call:
                try:
                    fn_result = fn_to_call(**fn_args)
                except Exception as e:
                    print(f"Error executing function {fn_call.name}: {e}")
                    fn_result = {"error": str(e)}
            else:
                fn_result = {"error": f"Unknown function: {fn_call.name}"}

            # Add function response to history
            history.append(types.Content(
                role="user",
                parts=[types.Part.from_function_response(name=fn_call.name, response=fn_result)],
            ))

            try:
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=history,
                    config=config,
                )
            except Exception as e:
                print(f"Error calling GenAI after function call: {e}")
                return f"Sorry, I encountered an error processing the result: {e}"

        # Add final assistant response to history
        if response.candidates and response.candidates[0].content:
            history.append(response.candidates[0].content)

        self.sessions[sessionId] = history

        # Extract text safely
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            text_parts = [p.text for p in response.candidates[0].content.parts if p.text]
            if text_parts:
                return "\n".join(text_parts)

        return "Desole, je n'ai pas pu generer de reponse. Veuillez reessayer avec plus de details."


if __name__ == "__main__":
    agent = InsuranceAgent()
    result = agent.invoke(
        "Je veux un devis assurance pret immobilier pour 250 000 euros sur 20 ans, j'ai 35 ans, formule confort",
        "test",
    )
    print(result)
