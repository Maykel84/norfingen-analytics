"""Minimal dict-based i18n. No framework, just a lookup table."""

LANGUAGES = {"en": "English", "pl": "Polski", "no": "Norsk"}

NAV_ITEMS = ["today", "overview", "time", "clients", "operations"]

TRANSLATIONS = {
    "app_title": {
        "en": "Norfingen Analytics",
        "pl": "Norfingen Analytics",
        "no": "Norfingen Analytics",
    },
    "measures": {"en": "Measures", "pl": "Miary", "no": "Målinger"},
    "measure_label": {"en": "Measure", "pl": "Miara", "no": "Mål"},
    "group_by": {"en": "Group by", "pl": "Grupuj wg", "no": "Grupper etter"},
    "granularity": {"en": "Granularity", "pl": "Ziarnistość", "no": "Granularitet"},
    "date_range": {"en": "Date range", "pl": "Zakres dat", "no": "Datoperiode"},
    "filters": {"en": "Filters", "pl": "Filtry", "no": "Filtre"},
    "company": {"en": "Company", "pl": "Firma", "no": "Selskap"},
    "location": {"en": "Location", "pl": "Lokalizacja", "no": "Sted"},
    "city": {"en": "City", "pl": "Miasto", "no": "By"},
    "segment": {"en": "Segment", "pl": "Segment", "no": "Segment"},
    "nace_name": {"en": "Industry", "pl": "Branża", "no": "Bransje"},
    "cost_bucket": {"en": "Cost type", "pl": "Typ kosztu", "no": "Kostnadstype"},
    "revenue": {"en": "Revenue", "pl": "Przychód", "no": "Inntekt"},
    "cost": {"en": "Cost", "pl": "Koszt", "no": "Kostnad"},
    "profit": {"en": "Profit", "pl": "Zysk", "no": "Fortjeneste"},
    "margin_pct": {"en": "Margin %", "pl": "Marża %", "no": "Margin %"},
    "order_count": {"en": "Orders", "pl": "Zamówienia", "no": "Ordrer"},
    "day": {"en": "Day", "pl": "Dzień", "no": "Dag"},
    "week": {"en": "Week", "pl": "Tydzień", "no": "Uke"},
    "month": {"en": "Month", "pl": "Miesiąc", "no": "Måned"},
    "quarter": {"en": "Quarter", "pl": "Kwartał", "no": "Kvartal"},
    "year": {"en": "Year", "pl": "Rok", "no": "År"},
    "map_view": {"en": "Map", "pl": "Mapa", "no": "Kart"},
    "breakdown": {"en": "Breakdown", "pl": "Podział", "no": "Fordeling"},
    "comparison": {"en": "Comparison", "pl": "Porównanie", "no": "Sammenligning"},
    "period_a": {"en": "Period A", "pl": "Okres A", "no": "Periode A"},
    "period_b": {"en": "Period B", "pl": "Okres B", "no": "Periode B"},
    "delta": {"en": "Delta", "pl": "Różnica", "no": "Endring"},
    "last_updated": {"en": "Last updated", "pl": "Ostatnia aktualizacja", "no": "Sist oppdatert"},
    "theme": {"en": "Theme", "pl": "Motyw", "no": "Tema"},
    "language": {"en": "Language", "pl": "Język", "no": "Språk"},
    "select_measure": {"en": "Select a measure", "pl": "Wybierz miarę", "no": "Velg en måling"},
    "top_companies": {"en": "Top companies", "pl": "Najlepsze firmy", "no": "Toppselskaper"},
    "over_time": {"en": "Over time", "pl": "W czasie", "no": "Over tid"},
    "partial_data": {"en": "partial", "pl": "częściowe", "no": "delvis"},
    # Nav
    "nav_today": {"en": "Today", "pl": "Dzisiaj", "no": "I dag"},
    "nav_overview": {"en": "Overview", "pl": "Przegląd", "no": "Oversikt"},
    "nav_time": {"en": "Time Analysis", "pl": "Analiza czasowa", "no": "Tidsanalyse"},
    "nav_clients": {"en": "Clients", "pl": "Klienci", "no": "Kunder"},
    "nav_operations": {"en": "Operations", "pl": "Operacje", "no": "Drift"},
    # Overview
    "all_years": {"en": "All years", "pl": "Wszystkie lata", "no": "Alle år"},
    "client_count": {"en": "Clients", "pl": "Klienci", "no": "Kunder"},
    "history": {"en": "History", "pl": "Historia", "no": "Historikk"},
    "coverage": {"en": "Coverage", "pl": "Zasięg", "no": "Dekning"},
    "by_revenue": {"en": "By revenue", "pl": "Wg przychodu", "no": "Etter inntekt"},
    "by_profit": {"en": "By profit", "pl": "Wg zysku", "no": "Etter fortjeneste"},
    "by_orders": {"en": "By orders", "pl": "Wg zamówień", "no": "Etter ordrer"},
    "client_map": {"en": "Client map", "pl": "Mapa klientów", "no": "Kundekart"},
    # Time analysis
    "period_type": {"en": "Period type", "pl": "Typ okresu", "no": "Periodetype"},
    "custom": {"en": "Custom", "pl": "Niestandardowy", "no": "Egendefinert"},
    "compare_periods": {"en": "Compare periods", "pl": "Porównaj okresy", "no": "Sammenlign perioder"},
    # Clients
    "search_clients": {"en": "Search clients", "pl": "Szukaj klientów", "no": "Søk kunder"},
    "sector": {"en": "Sector", "pl": "Sektor", "no": "Sektor"},
    "size_band": {"en": "Size", "pl": "Wielkość", "no": "Størrelse"},
    "add_to_compare": {"en": "Compare", "pl": "Porównaj", "no": "Sammenlign"},
    "compare_selected": {"en": "Compare selected", "pl": "Porównaj wybrane", "no": "Sammenlign valgte"},
    "compare_limit": {
        "en": "Up to 3 clients", "pl": "Maksymalnie 3 klientów", "no": "Opptil 3 kunder",
    },
    "client_profile": {"en": "Client profile", "pl": "Profil klienta", "no": "Kundeprofil"},
    "back_to_list": {"en": "Back", "pl": "Wróć", "no": "Tilbake"},
    "lifetime_revenue": {"en": "Lifetime revenue", "pl": "Przychód całkowity", "no": "Total inntekt"},
    "clear_compare": {"en": "Clear", "pl": "Wyczyść", "no": "Tøm"},
    "no_cost_note": {
        "en": "Cost data in this system isn't recorded per client — only company-wide totals are available (see Overview).",
        "pl": "Dane o kosztach w tym systemie nie są rejestrowane per klient — dostępne są tylko sumy dla całej firmy (patrz Przegląd).",
        "no": "Kostnadsdata i dette systemet registreres ikke per klient — kun selskapsomfattende totaler er tilgjengelig (se Oversikt).",
    },
    "cost_by_dimension_note": {
        "en": "Cost/Profit/Margin aren't available broken down by company, location, segment, or industry — cost isn't tracked at that level.",
        "pl": "Koszt/Zysk/Marża nie są dostępne w podziale na firmę, lokalizację, segment lub branżę — koszty nie są śledzone na tym poziomie.",
        "no": "Kostnad/Fortjeneste/Margin er ikke tilgjengelig fordelt på selskap, sted, segment eller bransje — kostnad spores ikke på det nivået.",
    },
    "projects": {"en": "Projects", "pl": "Projekty", "no": "Prosjekter"},
    "project_number": {"en": "Project #", "pl": "Nr projektu", "no": "Prosjektnr"},
    "project_name": {"en": "Name", "pl": "Nazwa", "no": "Navn"},
    "status": {"en": "Status", "pl": "Status", "no": "Status"},
    "start_date": {"en": "Start date", "pl": "Data rozpoczęcia", "no": "Startdato"},
    "end_date": {"en": "End date", "pl": "Data zakończenia", "no": "Sluttdato"},
    "lifecycle_events": {"en": "Client lifecycle", "pl": "Cykl życia klienta", "no": "Kundens livssyklus"},
    "onboarded": {"en": "Acquired", "pl": "Pozyskany", "no": "Anskaffet"},
    "active_status": {"en": "Active", "pl": "Aktywny", "no": "Aktiv"},
    "churned": {"en": "Churned", "pl": "Utracony", "no": "Churnet"},
    "status_label": {"en": "Status", "pl": "Status", "no": "Status"},
    "event_date": {"en": "Date", "pl": "Data", "no": "Dato"},
    "event_type": {"en": "Event", "pl": "Zdarzenie", "no": "Hendelse"},
    # Today page
    "today_title": {"en": "Today", "pl": "Dzisiaj", "no": "I dag"},
    "most_recent_day": {
        "en": "No activity today yet — showing the most recent day with data:",
        "pl": "Brak aktywności dzisiaj — pokazuję najnowszy dzień z danymi:",
        "no": "Ingen aktivitet i dag ennå — viser siste dag med data:",
    },
    "todays_revenue": {"en": "Today's revenue", "pl": "Dzisiejszy przychód", "no": "Dagens inntekt"},
    "todays_orders": {"en": "Today's orders", "pl": "Dzisiejsze zamówienia", "no": "Dagens ordrer"},
    "active_clients_today": {"en": "Active clients", "pl": "Aktywni klienci", "no": "Aktive kunder"},
    "todays_activity": {"en": "Today's orders", "pl": "Dzisiejsze zamówienia", "no": "Dagens ordrer"},
    "no_activity": {"en": "No orders on this day.", "pl": "Brak zamówień tego dnia.", "no": "Ingen ordrer denne dagen."},
    "loading_data": {"en": "Loading…", "pl": "Wczytywanie…", "no": "Laster…"},
    "app_starting": {
        "en": "Starting up — first load after inactivity can take up to a minute…",
        "pl": "Uruchamianie — pierwsze wczytanie po okresie nieaktywności może potrwać do minuty…",
        "no": "Starter opp — første innlasting etter inaktivitet kan ta opptil et minutt…",
    },
    "recent_activity": {"en": "Recent activity", "pl": "Ostatnia aktywność", "no": "Nylig aktivitet"},
    "last_n_days": {"en": "Last {n} days", "pl": "Ostatnie {n} dni", "no": "Siste {n} dager"},
    "invoice_payment_status": {
        "en": "Invoice & payment status", "pl": "Status faktury i płatności", "no": "Faktura- og betalingsstatus",
    },
    "invoiced": {"en": "Invoiced", "pl": "Zafakturowane", "no": "Fakturert"},
    "paid": {"en": "Paid", "pl": "Zapłacone", "no": "Betalt"},
    "yes": {"en": "Yes", "pl": "Tak", "no": "Ja"},
    "no": {"en": "No", "pl": "Nie", "no": "Nei"},
    # Operations page
    "products_services": {"en": "Products & services", "pl": "Produkty i usługi", "no": "Produkter og tjenester"},
    "suppliers": {"en": "Suppliers", "pl": "Dostawcy", "no": "Leverandører"},
    "staffing": {"en": "Staffing", "pl": "Kadra", "no": "Bemanning"},
    "utilization": {"en": "Utilization", "pl": "Wykorzystanie czasu", "no": "Utnyttelse"},
    "cost_by_account": {"en": "Cost by account", "pl": "Koszty wg konta", "no": "Kostnad per konto"},
    "payroll": {"en": "Payroll", "pl": "Wynagrodzenia", "no": "Lønn"},
    "cash_flow": {"en": "Cash flow", "pl": "Przepływy pieniężne", "no": "Kontantstrøm"},
    "product": {"en": "Product", "pl": "Produkt", "no": "Produkt"},
    "service": {"en": "Service", "pl": "Usługa", "no": "Tjeneste"},
    "supplier": {"en": "Supplier", "pl": "Dostawca", "no": "Leverandør"},
    "spend": {"en": "Spend", "pl": "Wydatki", "no": "Utgifter"},
    "unpaid": {"en": "Unpaid", "pl": "Niezapłacone", "no": "Ubetalt"},
    "department": {"en": "Department", "pl": "Dział", "no": "Avdeling"},
    "headcount": {"en": "Headcount", "pl": "Liczba pracowników", "no": "Antall ansatte"},
    "employment_type": {"en": "Employment type", "pl": "Typ zatrudnienia", "no": "Ansettelsestype"},
    "activity_type": {"en": "Activity type", "pl": "Typ aktywności", "no": "Aktivitetstype"},
    "billable": {"en": "Billable", "pl": "Fakturowalne", "no": "Fakturerbart"},
    "internal": {"en": "Internal", "pl": "Wewnętrzne", "no": "Internt"},
    "sick": {"en": "Sick", "pl": "Chorobowe", "no": "Sykt"},
    "vacation": {"en": "Vacation", "pl": "Urlop", "no": "Ferie"},
    "parental_leave": {"en": "Parental leave", "pl": "Urlop rodzicielski", "no": "Foreldrepermisjon"},
    "welfare_leave": {"en": "Other leave", "pl": "Inne nieobecności", "no": "Annen permisjon"},
    "absences": {"en": "Absences", "pl": "Nieobecności", "no": "Fravær"},
    "absences_by_department": {
        "en": "Absences by department", "pl": "Nieobecności wg działu", "no": "Fravær per avdeling",
    },
    "payroll_by_employee": {
        "en": "Payroll by employee", "pl": "Wynagrodzenia wg pracownika", "no": "Lønn per ansatt",
    },
    "employee": {"en": "Employee", "pl": "Pracownik", "no": "Ansatt"},
    "gross_annual": {"en": "Gross annual", "pl": "Brutto rocznie", "no": "Brutto årlig"},
    "yoy_growth": {"en": "YoY growth", "pl": "Wzrost r/r", "no": "Vekst å/å"},
    "employer_cost": {"en": "Employer cost", "pl": "Koszt pracodawcy", "no": "Arbeidsgiverkostnad"},
    "employer_cost_note": {
        "en": "Employer cost = gross × 1.141 (14.1% employer's National Insurance contribution, Zone 1).",
        "pl": "Koszt pracodawcy = brutto × 1,141 (14,1% składki pracodawcy, strefa 1 wg danych z bazy).",
        "no": "Arbeidsgiverkostnad = brutto × 1,141 (14,1% arbeidsgiveravgift, sone 1).",
    },
    "payroll_year_label": {"en": "Year", "pl": "Rok", "no": "År"},
    "select_employee": {"en": "Select employee", "pl": "Wybierz pracownika", "no": "Velg ansatt"},
    "amount_type": {"en": "Amount type", "pl": "Rodzaj kwoty", "no": "Beløpstype"},
    "amount": {"en": "Amount", "pl": "Kwota", "no": "Beløp"},
    "partial_year_note": {
        "en": "year in progress, not fully paid out yet",
        "pl": "rok w trakcie, jeszcze niekompletny",
        "no": "året pågår, ikke fullt utbetalt ennå",
    },
    "days": {"en": "Days", "pl": "Dni", "no": "Dager"},
    "hours": {"en": "Hours", "pl": "Godziny", "no": "Timer"},
    "account": {"en": "Account", "pl": "Konto", "no": "Konto"},
    "flow_type": {"en": "Flow", "pl": "Kierunek", "no": "Retning"},
    "incoming": {"en": "Incoming", "pl": "Wpływy", "no": "Inngående"},
    "outgoing": {"en": "Outgoing", "pl": "Wypływy", "no": "Utgående"},
    "net": {"en": "Net", "pl": "Netto", "no": "Netto"},
}


# customers.nace_name is stored in Norwegian (the source data's own
# language) regardless of UI language — every distinct value present in the
# DB (confirmed via `SELECT DISTINCT nace_name FROM customers`, 18 values,
# not guessed at). NO keeps the original text since it's already Norwegian.
SECTOR_TRANSLATIONS = {
    "Andre helsetjenester": {
        "en": "Other health services", "pl": "Inne usługi zdrowotne", "no": "Andre helsetjenester",
    },
    "Andre tjenester tilknyttet informasjonsteknologi": {
        "en": "Other information technology services",
        "pl": "Inne usługi związane z technologią informacyjną",
        "no": "Andre tjenester tilknyttet informasjonsteknologi",
    },
    "Annen butikkhandel med bredt vareutvalg": {
        "en": "Other retail sale in non-specialized stores",
        "pl": "Pozostała sprzedaż detaliczna w sklepach niewyspecjalizowanych",
        "no": "Annen butikkhandel med bredt vareutvalg",
    },
    "Bankvirksomhet ellers": {
        "en": "Other banking activities", "pl": "Pozostała działalność bankowa", "no": "Bankvirksomhet ellers",
    },
    "Bearbeiding og konservering av fisk, skalldyr og bløtdyr": {
        "en": "Processing and preserving of fish, crustaceans and molluscs",
        "pl": "Przetwarzanie i konserwowanie ryb, skorupiaków i mięczaków",
        "no": "Bearbeiding og konservering av fisk, skalldyr og bløtdyr",
    },
    "Bedriftsrådgivning og annen administrativ rådgivning": {
        "en": "Business and other management consultancy",
        "pl": "Doradztwo biznesowe i pozostałe doradztwo administracyjne",
        "no": "Bedriftsrådgivning og annen administrativ rådgivning",
    },
    "Elektrisk installasjonsarbeid": {
        "en": "Electrical installation work",
        "pl": "Roboty związane z wykonywaniem instalacji elektrycznych",
        "no": "Elektrisk installasjonsarbeid",
    },
    "Godstransport på vei": {
        "en": "Freight transport by road", "pl": "Transport drogowy towarów", "no": "Godstransport på vei",
    },
    "Handel med elektrisitet": {
        "en": "Trade of electricity", "pl": "Handel energią elektryczną", "no": "Handel med elektrisitet",
    },
    "Havbruk av fisk i sjøvann": {
        "en": "Marine fish farming", "pl": "Hodowla ryb morskich", "no": "Havbruk av fisk i sjøvann",
    },
    "Hovedkontortjenester": {
        "en": "Head office activities", "pl": "Działalność centrali firm", "no": "Hovedkontortjenester",
    },
    "Juridisk tjenesteyting": {
        "en": "Legal services", "pl": "Usługi prawne", "no": "Juridisk tjenesteyting",
    },
    "Kjøp og salg av egen fast eiendom": {
        "en": "Buying and selling of own real estate",
        "pl": "Kupno i sprzedaż nieruchomości na własny rachunek",
        "no": "Kjøp og salg av egen fast eiendom",
    },
    "Oppføring av bygninger": {
        "en": "Construction of buildings", "pl": "Wznoszenie budynków", "no": "Oppføring av bygninger",
    },
    "Produksjon av metallkonstruksjoner": {
        "en": "Manufacture of structural metal products",
        "pl": "Produkcja konstrukcji metalowych",
        "no": "Produksjon av metallkonstruksjoner",
    },
    "Sjøtransport med gods": {
        "en": "Sea freight transport", "pl": "Transport morski towarów", "no": "Sjøtransport med gods",
    },
    "Spesialisert designvirksomhet": {
        "en": "Specialized design activities",
        "pl": "Działalność w zakresie specjalistycznego projektowania",
        "no": "Spesialisert designvirksomhet",
    },
    "Vedlikehold og reparasjon av motorvogner": {
        "en": "Maintenance and repair of motor vehicles",
        "pl": "Konserwacja i naprawa pojazdów samochodowych",
        "no": "Vedlikehold og reparasjon av motorvogner",
    },
}


# departments.name — 4 distinct values in the DB (confirmed via
# `SELECT DISTINCT name FROM departments`), each a Norwegian business-
# function name, not a proper noun (unlike company names), so translating
# them is meaningful. NO keeps the original since it's already Norwegian.
DEPARTMENT_TRANSLATIONS = {
    "Leveranse": {"en": "Delivery", "pl": "Realizacja", "no": "Leveranse"},
    "Økonomi": {"en": "Finance", "pl": "Finanse", "no": "Økonomi"},
    "Salg": {"en": "Sales", "pl": "Sprzedaż", "no": "Salg"},
    "Teknologi": {"en": "Technology", "pl": "Technologia", "no": "Teknologi"},
}

# accounts.name for every account in the cost range (4000-7999) actually
# posted to (confirmed via a live DISTINCT query against postings JOIN
# accounts, not guessed at) — 17 values, Norwegian GL account names.
ACCOUNT_TRANSLATIONS = {
    "Annen driftskostnad": {
        "en": "Other operating expense", "pl": "Inne koszty operacyjne", "no": "Annen driftskostnad",
    },
    "Arbeidsgiveravgift": {
        "en": "Employer's National Insurance contribution",
        "pl": "Składka na ubezpieczenie społeczne pracodawcy",
        "no": "Arbeidsgiveravgift",
    },
    "Avsetning feriepenger": {
        "en": "Holiday pay accrual", "pl": "Rezerwa na wynagrodzenie urlopowe", "no": "Avsetning feriepenger",
    },
    "Driftskostnad Managed IT Support (RMM/EDR/verktøy)": {
        "en": "Managed IT Support operating cost (RMM/EDR/tools)",
        "pl": "Koszt operacyjny Managed IT Support (RMM/EDR/narzędzia)",
        "no": "Driftskostnad Managed IT Support (RMM/EDR/verktøy)",
    },
    "Driftsmateriell for kundeleveranse": {
        "en": "Operating supplies for client delivery",
        "pl": "Materiały eksploatacyjne do realizacji usług dla klientów",
        "no": "Driftsmateriell for kundeleveranse",
    },
    "Forsikringspremier": {
        "en": "Insurance premiums", "pl": "Składki ubezpieczeniowe", "no": "Forsikringspremier",
    },
    "Fremmed tjeneste": {
        "en": "Purchased services", "pl": "Usługi obce", "no": "Fremmed tjeneste",
    },
    "Husleie og leie av lokaler": {
        "en": "Rent and premises lease", "pl": "Czynsz i wynajem lokali", "no": "Husleie og leie av lokaler",
    },
    "Inventar og utstyr": {
        "en": "Furniture and equipment", "pl": "Wyposażenie i sprzęt", "no": "Inventar og utstyr",
    },
    "Kantinetilskudd": {
        "en": "Canteen subsidy", "pl": "Dofinansowanie stołówki", "no": "Kantinetilskudd",
    },
    "Kontorkostnader": {
        "en": "Office expenses", "pl": "Koszty biurowe", "no": "Kontorkostnader",
    },
    "Lisenser og programvare": {
        "en": "Licenses and software", "pl": "Licencje i oprogramowanie", "no": "Lisenser og programvare",
    },
    "Lønn, fast": {
        "en": "Fixed salary", "pl": "Wynagrodzenie stałe", "no": "Lønn, fast",
    },
    "Reisekostnader": {
        "en": "Travel expenses", "pl": "Koszty podróży", "no": "Reisekostnader",
    },
    "Representasjon": {
        "en": "Business entertainment", "pl": "Reprezentacja", "no": "Representasjon",
    },
    "Telefon og internett": {
        "en": "Telephone and internet", "pl": "Telefon i internet", "no": "Telefon og internett",
    },
    "Videresalgskostnad Microsoft/Azure": {
        "en": "Microsoft/Azure resale cost", "pl": "Koszt odsprzedaży Microsoft/Azure",
        "no": "Videresalgskostnad Microsoft/Azure",
    },
}

# employments.employment_type — only one distinct value in the DB
# ("ORDINARY", confirmed via a live query), but it's a raw enum, not a
# label, so it was rendering untranslated in every language.
EMPLOYMENT_TYPE_TRANSLATIONS = {
    "ORDINARY": {"en": "Ordinary", "pl": "Standardowe", "no": "Ordinær"},
}


def t(key: str, lang: str) -> str:
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(lang, entry.get("en", key))


def _translate_via(table: dict, value: str | None, lang: str) -> str | None:
    if not value:
        return value
    entry = table.get(value)
    if not entry:
        return value
    return entry.get(lang, value)


def t_sector(nace_name: str | None, lang: str) -> str:
    """Translates a customers.nace_name value (stored in Norwegian) for
    display. Falls back to the raw value for anything not in
    SECTOR_TRANSLATIONS (e.g. null/unexpected data) rather than hiding it."""
    return _translate_via(SECTOR_TRANSLATIONS, nace_name, lang)


def t_department(name: str | None, lang: str) -> str:
    """Translates a departments.name value. Falls back to the raw value for
    anything not in DEPARTMENT_TRANSLATIONS."""
    return _translate_via(DEPARTMENT_TRANSLATIONS, name, lang)


def t_account(name: str | None, lang: str) -> str:
    """Translates an accounts.name (GL account) value. Falls back to the
    raw value for anything not in ACCOUNT_TRANSLATIONS."""
    return _translate_via(ACCOUNT_TRANSLATIONS, name, lang)


def t_employment_type(value: str | None, lang: str) -> str:
    """Translates an employments.employment_type raw enum value. Falls back
    to the raw value for anything not in EMPLOYMENT_TYPE_TRANSLATIONS."""
    return _translate_via(EMPLOYMENT_TYPE_TRANSLATIONS, value, lang)
