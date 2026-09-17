"""Minimal dict-based i18n. No framework, just a lookup table."""

LANGUAGES = {"en": "English", "pl": "Polski", "no": "Norsk"}

TRANSLATIONS = {
    "app_title": {
        "en": "NORFINGEN ANALYTICS",
        "pl": "NORFINGEN ANALYTICS",
        "no": "NORFINGEN ANALYTICS",
    },
    "measures": {"en": "Measures", "pl": "Miary", "no": "Målinger"},
    "group_by": {"en": "Group by", "pl": "Grupuj wg", "no": "Grupper etter"},
    "granularity": {"en": "Granularity", "pl": "Ziarnistość", "no": "Granularitet"},
    "date_range": {"en": "Date range", "pl": "Zakres dat", "no": "Datoperiode"},
    "filters": {"en": "Filters", "pl": "Filtry", "no": "Filtre"},
    "company": {"en": "Company", "pl": "Firma", "no": "Selskap"},
    "location": {"en": "Location", "pl": "Lokalizacja", "no": "Sted"},
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
    "nav_overview": {"en": "Overview", "pl": "Przegląd", "no": "Oversikt"},
    "nav_time": {"en": "Time Analysis", "pl": "Analiza czasowa", "no": "Tidsanalyse"},
    "nav_clients": {"en": "Clients", "pl": "Klienci", "no": "Kunder"},
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
}


def t(key: str, lang: str) -> str:
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(lang, entry.get("en", key))
