"""Minimal dict-based i18n. No framework, just a lookup table."""

LANGUAGES = {"en": "English", "pl": "Polski", "no": "Norsk"}

NAV_ITEMS = ["today", "overview", "time", "clients", "receivables", "liquidity", "balance", "profitability", "operations"]

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
    "profit": {"en": "EBIT", "pl": "EBIT", "no": "EBIT"},
    "margin_pct": {"en": "EBIT margin %", "pl": "Marża EBIT %", "no": "EBIT-margin %"},
    "net_result": {"en": "Net result", "pl": "Wynik netto", "no": "Nettoresultat"},
    "net_margin_pct": {"en": "Net margin %", "pl": "Marża netto %", "no": "Netto margin %"},
    "ebitda": {"en": "EBITDA", "pl": "EBITDA", "no": "EBITDA"},
    "depreciation": {"en": "Depreciation", "pl": "Amortyzacja", "no": "Avskrivninger"},
    "financial_result": {"en": "Financial result", "pl": "Wynik finansowy", "no": "Finansresultat"},
    "tax": {"en": "Income tax", "pl": "Podatek dochodowy", "no": "Skattekostnad"},
    "extra_series": {"en": "Add to the chart", "pl": "Dodaj do wykresu", "no": "Legg til i diagrammet"},
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
    "nav_receivables": {"en": "Receivables", "pl": "Należności", "no": "Fordringer"},
    "nav_liquidity": {"en": "Liquidity", "pl": "Płynność", "no": "Likviditet"},
    "nav_balance": {"en": "Balance", "pl": "Bilans", "no": "Balanse"},
    "nav_profitability": {"en": "Profitability", "pl": "Rentowność", "no": "Lønnsomhet"},
    "bs_total_assets": {
        "en": 'Total assets',
        "pl": 'Suma aktywów',
        "no": 'Sum eiendeler',
    },
    "bs_total_equity": {
        "en": 'Total equity',
        "pl": 'Kapitał własny',
        "no": 'Sum egenkapital',
    },
    "bs_equity_ratio": {
        "en": 'Equity ratio',
        "pl": 'Wskaźnik kapitału własnego',
        "no": 'Egenkapitalandel',
    },
    "bs_net_debt": {
        "en": 'Net debt',
        "pl": 'Dług netto',
        "no": 'Netto gjeld',
    },
    "bs_net_debt_note": {
        "en": 'Owner loan minus cash; negative = more cash than debt',
        "pl": 'Pożyczka właściciela minus gotówka; wartość ujemna = więcej gotówki niż długu',
        "no": 'Eierlån minus kontanter; negativ = mer kontanter enn gjeld',
    },
    "bs_as_of": {
        "en": 'Balance at the end of {month} (latest full month)',
        "pl": 'Stan na koniec {month} (ostatni pełny miesiąc)',
        "no": 'Balanse ved utgangen av {month} (siste hele måned)',
    },
    "bs_assets_chart": {
        "en": 'Assets by type',
        "pl": 'Aktywa według rodzaju',
        "no": 'Eiendeler etter type',
    },
    "bs_liab_equity_chart": {
        "en": 'Liabilities and equity',
        "pl": 'Zobowiązania i kapitał własny',
        "no": 'Gjeld og egenkapital',
    },
    "bs_fixed_assets_chart": {
        "en": 'Fixed assets: cost and accumulated depreciation',
        "pl": 'Środki trwałe: wartość początkowa i umorzenie',
        "no": 'Anleggsmidler: kostpris og akkumulerte avskrivninger',
    },
    "bs_fixed_cost": {
        "en": 'Cost (1200)',
        "pl": 'Wartość początkowa (1200)',
        "no": 'Kostpris (1200)',
    },
    "bs_fixed_acc_dep": {
        "en": 'Accumulated depreciation (1209)',
        "pl": 'Umorzenie (1209)',
        "no": 'Akkumulerte avskrivninger (1209)',
    },
    "bs_fixed_net": {
        "en": 'Net book value',
        "pl": 'Wartość netto',
        "no": 'Bokført verdi',
    },
    "bs_fixed_assets_net": {
        "en": 'Fixed assets (net)',
        "pl": 'Środki trwałe (netto)',
        "no": 'Anleggsmidler (netto)',
    },
    "bs_receivables": {
        "en": 'Receivables',
        "pl": 'Należności',
        "no": 'Kundefordringer',
    },
    "bs_cash": {
        "en": 'Cash',
        "pl": 'Gotówka',
        "no": 'Kontanter',
    },
    "bs_other_assets": {
        "en": 'Other assets',
        "pl": 'Pozostałe aktywa',
        "no": 'Andre eiendeler',
    },
    "bs_long_term_debt": {
        "en": 'Owner loan',
        "pl": 'Pożyczka właściciela',
        "no": 'Eierlån',
    },
    "bs_trade_payables": {
        "en": 'Trade payables',
        "pl": 'Zobowiązania handlowe',
        "no": 'Leverandørgjeld',
    },
    "bs_tax_payable": {
        "en": 'Income tax payable',
        "pl": 'Podatek dochodowy do zapłaty',
        "no": 'Betalbar skatt',
    },
    "bs_vat_net": {
        "en": 'VAT (net)',
        "pl": 'VAT (netto)',
        "no": 'MVA (netto)',
    },
    "bs_payroll_and_pension": {
        "en": 'Payroll and pension',
        "pl": 'Wynagrodzenia i emerytury',
        "no": 'Lønn og pensjon',
    },
    "bs_other_liabilities": {
        "en": 'Other liabilities',
        "pl": 'Pozostałe zobowiązania',
        "no": 'Annen gjeld',
    },
    "bs_share_capital": {
        "en": 'Share capital',
        "pl": 'Kapitał zakładowy',
        "no": 'Aksjekapital',
    },
    "bs_retained_earnings": {
        "en": 'Retained earnings',
        "pl": 'Zyski zatrzymane',
        "no": 'Opptjent egenkapital',
    },
    "bs_result_ytd": {
        "en": 'Result year to date',
        "pl": 'Wynik od początku roku',
        "no": 'Resultat hittil i år',
    },
    "bs_check_ok": {
        "en": 'Balance check: max |assets − liabilities − equity| = {value} kr over {n} months — balanced.',
        "pl": 'Kontrola bilansu: maks. |aktywa − zobowiązania − kapitał| = {value} kr w {n} miesiącach — bilans zgodny.',
        "no": 'Balansekontroll: maks. |eiendeler − gjeld − egenkapital| = {value} kr over {n} måneder — i balanse.',
    },
    "bs_check_bad": {
        "en": 'Balance check FAILED: max |assets − liabilities − equity| = {value} kr over {n} months.',
        "pl": 'Kontrola bilansu NIEUDANA: maks. |aktywa − zobowiązania − kapitał| = {value} kr w {n} miesiącach.',
        "no": 'Balansekontroll FEILET: maks. |eiendeler − gjeld − egenkapital| = {value} kr over {n} måneder.',
    },
    "bs_open_note": {
        "en": 'The month in progress is shaded: its payroll and COGS are booked at month end, so its equity and cash are not final.',
        "pl": 'Miesiąc w toku jest zacieniony: wynagrodzenia i COGS są księgowane na koniec miesiąca, więc jego kapitał i gotówka nie są ostateczne.',
        "no": 'Måneden som pågår er skravert: lønn og COGS bokføres ved månedsslutt, så egenkapital og kontanter er ikke endelige.',
    },
    "bs_footnote": {
        "en": 'Equity is negative at the start because of the start-up loss, financed by the owner loan. Retained earnings are the results of earlier calendar years (the ledger is not closed); the current year sits in “Result year to date”. Balances are cumulative since the first voucher; the year selector only slices the view.',
        "pl": 'Kapitał własny jest ujemny na początku z powodu straty z okresu rozruchu, sfinansowanej pożyczką właściciela. Zyski zatrzymane to wyniki poprzednich lat kalendarzowych (księgi nie są zamykane); bieżący rok jest w pozycji „Wynik od początku roku”. Salda są narastające od pierwszego dokumentu; wybór roku tylko zawęża widok.',
        "no": 'Egenkapitalen er negativ i starten på grunn av oppstartstapet, finansiert av eierlånet. Opptjent egenkapital er resultatene fra tidligere kalenderår (regnskapet er ikke avsluttet); inneværende år ligger i «Resultat hittil i år». Saldoene er kumulative fra første bilag; årsvelgeren avgrenser bare visningen.',
    },
    "bs_no_full_month": {
        "en": 'No full month in the selected year yet.',
        "pl": 'W wybranym roku nie ma jeszcze pełnego miesiąca.',
        "no": 'Ingen hel måned i valgt år ennå.',
    },
    # Profitability page
    "prf_customers": {"en": "Customer profitability", "pl": "Rentowność klientów", "no": "Kundelønnsomhet"},
    "prf_method_note": {
        "en": "Contribution = revenue − pass-through COGS (4291/4292, allocated pro rata to revenue) − direct labor "
              "(billable hours × loaded hourly cost, tied to ledger labor). Cost postings carry no customer, so this is "
              "a model. Not included: equipment (4290), operating costs, internal hours. Full months only.",
        "pl": "Wkład = przychód − COGS przelotowy (4291/4292, rozdzielony proporcjonalnie do przychodu) − bezpośrednia "
              "praca (godziny fakturowalne × pełny koszt godziny, zgodny z księgą). Księgowania kosztów nie mają klienta, "
              "więc to model. Nie uwzględnia: sprzętu (4290), kosztów operacyjnych, godzin wewnętrznych. Tylko pełne miesiące.",
        "no": "Bidrag = inntekt − gjennomstrømmings-COGS (4291/4292, fordelt forholdsmessig etter inntekt) − direkte arbeid "
              "(fakturerbare timer × fullt timekostnad, avstemt mot hovedbok). Kostnadsposteringer har ingen kunde, så dette "
              "er en modell. Ikke med: utstyr (4290), driftskostnader, interne timer. Kun hele måneder.",
    },
    "prf_cogs_alloc": {"en": "COGS (allocated)", "pl": "COGS (rozdzielony)", "no": "COGS (fordelt)"},
    "prf_labor": {"en": "Direct labor", "pl": "Praca bezpośrednia", "no": "Direkte arbeid"},
    "prf_contribution": {"en": "Contribution", "pl": "Wkład", "no": "Bidrag"},
    "prf_contribution_pct": {"en": "Contribution %", "pl": "Wkład %", "no": "Bidrag %"},
    "prf_billable_hours": {"en": "Billable hours", "pl": "Godziny fakturowalne", "no": "Fakturerbare timer"},
    "prf_internal_hours": {"en": "Internal hours", "pl": "Godziny wewnętrzne", "no": "Interne timer"},
    "prf_revenue_per_hour": {"en": "Revenue / billable hour", "pl": "Przychód / godz. fakturowalna", "no": "Inntekt / fakturerbar time"},
    "prf_top_contribution": {"en": "Top 15 customers by contribution", "pl": "Top 15 klientów wg wkładu", "no": "Topp 15 kunder etter bidrag"},
    "prf_utilization": {"en": "Utilization per employee", "pl": "Wykorzystanie czasu per pracownik", "no": "Utnyttelse per ansatt"},
    "prf_utilization_pct": {"en": "Utilization %", "pl": "Wykorzystanie %", "no": "Utnyttelse %"},
    "prf_utilization_note": {
        "en": "Utilization = billable ÷ (billable + internal) hours. Invoices are fixed monthly lines, not hours, so there is no billed-hours figure per employee to compare against.",
        "pl": "Wykorzystanie = godziny fakturowalne ÷ (fakturowalne + wewnętrzne). Faktury to stałe miesięczne pozycje, nie godziny, więc nie ma fakturowanych godzin per pracownik do porównania.",
        "no": "Utnyttelse = fakturerbare ÷ (fakturerbare + interne) timer. Fakturaer er faste månedslinjer, ikke timer, så det finnes ingen fakturerte timer per ansatt å sammenligne med.",
    },
    "prf_cost_by_category": {"en": "Cost by category per month", "pl": "Koszty wg kategorii miesięcznie", "no": "Kostnad per kategori per måned"},
    "prf_cat_cogs": {"en": "Pass-through COGS (4291/4292)", "pl": "COGS przelotowy (4291/4292)", "no": "Gjennomstrømmings-COGS (4291/4292)"},
    "prf_cat_equipment": {"en": "Equipment, cash purchases (4290)", "pl": "Sprzęt, zakupy gotówkowe (4290)", "no": "Utstyr, kontantkjøp (4290)"},
    "prf_cat_labor": {"en": "Labor (5xxx)", "pl": "Wynagrodzenia (5xxx)", "no": "Lønn (5xxx)"},
    "prf_cat_operating": {"en": "Operating cost (6000–7999)", "pl": "Koszty operacyjne (6000–7999)", "no": "Driftskostnader (6000–7999)"},
    "prf_cost_note": {
        "en": "Payroll and COGS are booked at month end, so the month in progress shows only part of its costs.",
        "pl": "Wynagrodzenia i COGS są księgowane na koniec miesiąca, więc miesiąc w toku pokazuje tylko część kosztów.",
        "no": "Lønn og COGS bokføres ved månedsslutt, så måneden som pågår viser bare deler av kostnadene.",
    },
    # Liquidity & financing page
    "liq_bank_balance": {"en": "Bank balance", "pl": "Saldo bankowe", "no": "Banksaldo"},
    "liq_as_of": {"en": "as of {date}", "pl": "stan na {date}", "no": "per {date}"},
    "liq_bank_open_note": {
        "en": "payroll and COGS for the current month are not booked yet",
        "pl": "wynagrodzenia i COGS za bieżący miesiąc nie są jeszcze zaksięgowane",
        "no": "lønn og COGS for inneværende måned er ikke bokført ennå",
    },
    "liq_bank_hidden_note": {
        "en": "{month} (month in progress) is not plotted: payroll and COGS are booked at month end, so its balance is not comparable. The tile shows the current balance.",
        "pl": "{month} (miesiąc w toku) nie jest na wykresie: wynagrodzenia i COGS są księgowane na koniec miesiąca, więc jego saldo nie jest porównywalne. Kafelek pokazuje aktualne saldo.",
        "no": "{month} (måned pågår) er ikke tegnet: lønn og COGS bokføres ved månedsslutt, så saldoen er ikke sammenlignbar. Flisen viser gjeldende saldo.",
    },
    "liq_min_balance": {"en": "Lowest balance", "pl": "Najniższe saldo", "no": "Laveste saldo"},
    "liq_on": {"en": "on", "pl": "w dniu", "no": "den"},
    "liq_bank_title": {"en": "Bank balance (month end)", "pl": "Saldo bankowe (koniec miesiąca)", "no": "Banksaldo (månedsslutt)"},
    "liq_min_marker": {"en": "Lowest day", "pl": "Najniższy dzień", "no": "Laveste dag"},
    "liq_loan_outstanding": {"en": "Owner loan outstanding", "pl": "Pożyczka od właściciela — saldo", "no": "Eierlån — utestående"},
    "liq_loan_section": {"en": "Owner loan", "pl": "Pożyczka od właściciela", "no": "Eierlån"},
    "liq_repaid": {"en": "Repaid", "pl": "Spłacona", "no": "Nedbetalt"},
    "liq_last_instalment": {
        "en": "last instalment {month}", "pl": "ostatnia rata {month}", "no": "siste avdrag {month}",
    },
    "liq_principal_repaid": {"en": "Principal repaid", "pl": "Spłacony kapitał", "no": "Betalt avdrag"},
    "liq_interest": {"en": "Interest", "pl": "Odsetki", "no": "Renter"},
    "liq_principal_vs_interest": {"en": "Principal vs interest per month", "pl": "Kapitał vs odsetki miesięcznie", "no": "Avdrag og renter per måned"},
    "liq_financing_structure": {"en": "Financing structure at start", "pl": "Struktura finansowania na starcie", "no": "Finansieringsstruktur ved oppstart"},
    "liq_share_capital": {"en": "Share capital", "pl": "Kapitał zakładowy", "no": "Aksjekapital"},
    "liq_owner_loan": {"en": "Owner loan", "pl": "Pożyczka od właściciela", "no": "Eierlån"},
    "liq_loan_share": {"en": "Loan share of financing", "pl": "Udział pożyczki w finansowaniu", "no": "Lånets andel av finansiering"},
    "liq_loan_repaid_note": {
        "en": "The owner loan is fully repaid (60 instalments, last in 2025-12).",
        "pl": "Pożyczka od właściciela jest w całości spłacona (60 rat, ostatnia w 2025-12).",
        "no": "Eierlånet er fullt tilbakebetalt (60 avdrag, siste 2025-12).",
    },
    "liq_vat_section": {"en": "VAT", "pl": "VAT", "no": "MVA"},
    "liq_output_vat": {"en": "Output VAT (2700)", "pl": "VAT należny (2700)", "no": "Utgående MVA (2700)"},
    "liq_input_vat": {"en": "Input VAT (2710)", "pl": "VAT naliczony (2710)", "no": "Inngående MVA (2710)"},
    "liq_vat_to_pay": {"en": "VAT to pay", "pl": "VAT do zapłaty", "no": "MVA til betaling"},
    "liq_due": {"en": "due", "pl": "termin", "no": "forfall"},
    "liq_vat_accruing": {"en": "VAT accruing, term in progress", "pl": "VAT narastający, termin w toku", "no": "MVA påløpt, termin pågår"},
    "liq_vat_accruing_note": {
        "en": "Estimate: input VAT on COGS is booked at month end, so the final amount will be lower.",
        "pl": "Szacunek: VAT naliczony od COGS jest księgowany na koniec miesiąca, więc kwota końcowa będzie niższa.",
        "no": "Estimat: inngående MVA på COGS bokføres ved månedsslutt, så endelig beløp blir lavere.",
    },
    "liq_vat_settlements": {"en": "VAT settlements", "pl": "Rozliczenia VAT", "no": "MVA-oppgjør"},
    "liq_vat_partial_note": {
        "en": "Month in progress: input VAT on COGS is booked at month end, so the last month's input VAT is incomplete.",
        "pl": "Miesiąc w toku: VAT naliczony od COGS jest księgowany na koniec miesiąca, więc VAT naliczony za ostatni miesiąc jest niepełny.",
        "no": "Måned pågår: inngående MVA på COGS bokføres ved månedsslutt, så siste måneds inngående MVA er ufullstendig.",
    },
    "liq_term": {"en": "Term", "pl": "Termin", "no": "Termin"},
    "liq_period": {"en": "Period", "pl": "Okres", "no": "Periode"},
    "liq_balance": {"en": "To pay / refund", "pl": "Do zapłaty / zwrot", "no": "Å betale / refusjon"},
    "liq_payment_date": {"en": "Payment date", "pl": "Data płatności", "no": "Betalingsdato"},
    "liq_cogs_section": {"en": "COGS payables", "pl": "Zobowiązania COGS", "no": "COGS-forpliktelser"},
    "liq_cogs_unpaid": {"en": "Unpaid COGS payables", "pl": "Niezapłacone zobowiązania COGS", "no": "Ubetalte COGS-forpliktelser"},
    "liq_accrual_date": {"en": "Accrued", "pl": "Zaksięgowano", "no": "Påløpt"},
    "liq_due_date": {"en": "Due date", "pl": "Termin płatności", "no": "Forfallsdato"},
    "liq_paid_date": {"en": "Paid on", "pl": "Zapłacono", "no": "Betalt"},
    "liq_description": {"en": "Description", "pl": "Opis", "no": "Beskrivelse"},
    "liq_net": {"en": "Net", "pl": "Netto", "no": "Netto"},
    "liq_vat": {"en": "VAT", "pl": "VAT", "no": "MVA"},
    "liq_gross": {"en": "Gross", "pl": "Brutto", "no": "Brutto"},
    # Receivables page
    "rcv_outstanding": {"en": "Outstanding", "pl": "Do zapłaty", "no": "Utestående"},
    "rcv_overdue_amount": {"en": "Overdue", "pl": "Po terminie", "no": "Forfalt"},
    "rcv_written_off_net": {"en": "Written off (net)", "pl": "Spisane (netto)", "no": "Tapsført (netto)"},
    "rcv_written_off_gross": {"en": "Written off (gross)", "pl": "Spisane (brutto)", "no": "Tapsført (brutto)"},
    "rcv_paid_late_count": {"en": "Paid late", "pl": "Zapłacone z opóźnieniem", "no": "Betalt for sent"},
    "rcv_status_split": {"en": "Invoices by status", "pl": "Faktury wg statusu", "no": "Fakturaer etter status"},
    "rcv_invoices": {"en": "invoices", "pl": "faktur", "no": "fakturaer"},
    "rcv_ageing": {"en": "Ageing of unpaid invoices", "pl": "Wiekowanie niezapłaconych faktur", "no": "Aldersfordeling av ubetalte fakturaer"},
    "rcv_not_due": {"en": "Not yet due", "pl": "Przed terminem", "no": "Ikke forfalt"},
    "rcv_days_past_due": {"en": "Days past due", "pl": "Dni po terminie", "no": "Dager over forfall"},
    "rcv_top_late": {"en": "Top customers by late payments", "pl": "Klienci wg opóźnionych płatności", "no": "Kunder etter sene betalinger"},
    "rcv_top_outstanding": {"en": "Top customers by outstanding amount", "pl": "Klienci wg kwoty do zapłaty", "no": "Kunder etter utestående beløp"},
    "rcv_late_payments": {"en": "Late payments", "pl": "Opóźnione płatności", "no": "Sene betalinger"},
    "rcv_paid_invoices": {"en": "Paid invoices", "pl": "Zapłacone faktury", "no": "Betalte fakturaer"},
    "rcv_unpaid_invoices": {"en": "Unpaid invoices", "pl": "Niezapłacone faktury", "no": "Ubetalte fakturaer"},
    "rcv_write_offs": {"en": "Write-offs per month", "pl": "Odpisy na straty w miesiącach", "no": "Tapsføringer per måned"},
    "rcv_monthly": {"en": "Per month", "pl": "W miesiącu", "no": "Per måned"},
    "rcv_running_total": {"en": "Running total", "pl": "Narastająco", "no": "Akkumulert"},
    "rcv_no_write_offs": {"en": "No write-offs in this period.", "pl": "Brak odpisów w tym okresie.", "no": "Ingen tapsføringer i denne perioden."},
    "rcv_pending_note": {
        "en": "Overdue includes {n} invoice(s) ({amount}) already flagged as bad debt: they stay Overdue until the write-off is booked, planned {date}.",
        "pl": "Po terminie obejmuje {n} fakt. ({amount}) już uznanych za nieściągalne: pozostają „po terminie” do zaksięgowania odpisu, planowanego na {date}.",
        "no": "Forfalt inkluderer {n} faktura(er) ({amount}) som allerede er vurdert som tap: de forblir Forfalt til tapsføringen er bokført, planlagt {date}.",
    },
    "rcv_pending_title": {"en": "Pending write-offs", "pl": "Odpisy oczekujące", "no": "Ventende tapsføringer"},
    "rcv_pending_amount": {"en": "Amount (gross)", "pl": "Kwota (brutto)", "no": "Beløp (brutto)"},
    "rcv_planned_writeoff": {"en": "Planned write-off", "pl": "Planowany odpis", "no": "Planlagt tapsføring"},
    "rcv_reconciled": {
        "en": "Reconciled: net of the Written-off invoices = ledger account 7830 = {amount}.",
        "pl": "Zgodne: netto spisanych faktur = konto 7830 w księdze = {amount}.",
        "no": "Avstemt: netto for tapsførte fakturaer = hovedbokkonto 7830 = {amount}.",
    },
    "rcv_not_reconciled": {
        "en": "Written-off invoices (net {inv}) do not match ledger account 7830 ({gl}); difference {diff}.",
        "pl": "Spisane faktury (netto {inv}) nie zgadzają się z kontem 7830 w księdze ({gl}); różnica {diff}.",
        "no": "Tapsførte fakturaer (netto {inv}) stemmer ikke med hovedbokkonto 7830 ({gl}); differanse {diff}.",
    },
    "rcv_gross_note": {
        "en": "Outstanding, Overdue and the status chart include VAT. Written off (net) is account 7830 in the ledger and equals the end of the chart below; Written off (gross) adds the VAT reversed with it. Only booked write-offs count.",
        "pl": "Do zapłaty, Po terminie i wykres statusów zawierają VAT. Spisane (netto) to konto 7830 w księdze i równa się końcowi wykresu poniżej; Spisane (brutto) dodaje korygowany z nim VAT. Liczą się tylko zaksięgowane odpisy.",
        "no": "Utestående, Forfalt og statusdiagrammet inkluderer MVA. Tapsført (netto) er konto 7830 i hovedboken og tilsvarer slutten av diagrammet under; Tapsført (brutto) legger til MVA som reverseres. Kun bokførte tapsføringer teller.",
    },
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
    "size_band": {"en": "Size (by revenue)", "pl": "Wielkość (wg przychodu)", "no": "Størrelse (etter inntekt)"},
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
    "invoice_status": {"en": "Invoice status", "pl": "Status faktury", "no": "Fakturastatus"},
    "inv_paid": {"en": "Paid", "pl": "Zapłacona", "no": "Betalt"},
    "inv_open": {"en": "Open", "pl": "Otwarta", "no": "Åpen"},
    "inv_overdue": {"en": "Overdue", "pl": "Po terminie", "no": "Forfalt"},
    "inv_written_off": {"en": "Written off", "pl": "Spisana w straty", "no": "Tapsført"},
    "inv_not_invoiced": {"en": "Not invoiced yet", "pl": "Jeszcze nie zafakturowana", "no": "Ikke fakturert ennå"},
    "partial_month_label": {"en": "month in progress", "pl": "miesiąc w toku", "no": "måned pågår"},
    "partial_month_note": {
        "en": "{month}: month in progress, costs booked at month end — profit and margin for it are not final.",
        "pl": "{month}: miesiąc w toku, koszty księgowane na koniec miesiąca — zysk i marża za ten miesiąc nie są ostateczne.",
        "no": "{month}: måneden pågår, kostnader bokføres ved månedsslutt — resultat og margin for den er ikke endelige.",
    },
    "cash_ledger_note": {
        "en": "From the ledger (bank account 1910): includes income tax, pension and owner-loan payments, and the 2019 capital and loan injection. Inflow minus outflow adds up to the bank balance on the Liquidity page.",
        "pl": "Z księgi głównej (konto bankowe 1910): obejmuje płatności podatku dochodowego, emerytur i rat pożyczki właściciela oraz wpłatę kapitału i pożyczki z 2019 r. Wpływy minus wydatki dają saldo banku ze strony Płynność.",
        "no": "Fra hovedboken (bankkonto 1910): inkluderer betaling av skatt, pensjon og avdrag på eierlånet, samt kapital- og lånetilførselen i 2019. Innbetalinger minus utbetalinger summerer til banksaldoen på Likviditet-siden.",
    },
    "cash_partial_note": {
        "en": "{month}: month in progress, not final — payroll, supplier and VAT payments are booked later in the month.",
        "pl": "{month}: miesiąc w toku, dane nie są ostateczne — wynagrodzenia, płatności dla dostawców i VAT są księgowane później w miesiącu.",
        "no": "{month}: måneden pågår, ikke endelig — lønn, leverandør- og MVA-betalinger bokføres senere i måneden.",
    },
    "partial_month_not_plotted": {
        "en": "{month} (month in progress) is not plotted for cost, profit and margin: payroll and COGS are booked at month end.",
        "pl": "{month} (miesiąc w toku) nie jest na wykresach kosztu, zysku i marży: wynagrodzenia i COGS są księgowane na koniec miesiąca.",
        "no": "{month} (måned pågår) er ikke tegnet for kostnad, resultat og margin: lønn og COGS bokføres ved månedsslutt.",
    },
    "june_holiday_pay_note": {
        "en": "June has a seasonal holiday-pay (feriepenger) artefact: payroll cost drops to ~0.16M because holiday pay is paid out of the accrual, so operating profit in June is higher than in other months.",
        "pl": "Czerwiec ma sezonowy artefakt feriepenger: koszt płac spada do ok. 0,16 mln, bo feriepenger są wypłacane z rezerwy, więc zysk operacyjny w czerwcu jest wyższy niż w innych miesiącach.",
        "no": "Juni har en sesongeffekt fra feriepenger: lønnskostnaden faller til ca. 0,16 mill. fordi feriepenger utbetales fra avsetningen, så driftsresultatet i juni er høyere enn i andre måneder.",
    },
    "range_aligned": {
        "en": "Range aligned to full months: {start} … {end}.",
        "pl": "Zakres dopasowany do pełnych miesięcy: {start} … {end}.",
        "no": "Perioden er justert til hele måneder: {start} … {end}.",
    },
    "range_unaligned_warning": {
        "en": "The custom range does not start on the 1st or end on a month end: profit and margin for partial months are not meaningful. Revenue and orders use your exact dates; cost, profit and margin use {start} … {end}.",
        "pl": "Własny zakres nie zaczyna się 1. dnia ani nie kończy z końcem miesiąca: zysk i marża dla niepełnych miesięcy nie mają sensu. Przychód i zamówienia używają Twoich dokładnych dat; koszt, zysk i marża — {start} … {end}.",
        "no": "Egendefinert periode starter ikke den 1. eller slutter ikke ved månedsslutt: resultat og margin for delvise måneder er ikke meningsfulle. Inntekt og ordrer bruker eksakte datoer; kostnad, resultat og margin bruker {start} … {end}.",
    },
    "no_full_month": {
        "en": "The selected range contains no full month yet, so cost, profit and margin are not available.",
        "pl": "Wybrany zakres nie zawiera jeszcze pełnego miesiąca, więc koszt, zysk i margines są niedostępne.",
        "no": "Valgt periode inneholder ingen hel måned ennå, så kostnad, resultat og margin er utilgjengelig.",
    },
    "fin_items_note": {
        "en": "Between EBIT and the net result: financial result {fin} (interest on the owner loan, accounts 8xxx) and income tax {tax}.",
        "pl": "Między EBIT a wynikiem netto: wynik finansowy {fin} (odsetki od pożyczki właściciela, konta 8xxx) i podatek dochodowy {tax}.",
        "no": "Mellom EBIT og nettoresultat: finansresultat {fin} (renter på eierlånet, konto 8xxx) og skattekostnad {tax}.",
    },
    "profit_definition": {
        "en": "EBIT = operating result: revenue − COGS − payroll − operating costs including depreciation (accounts 4000–7999), before financial items and tax. Net result = EBIT + financial result − income tax.",
        "pl": "EBIT = wynik operacyjny: przychód − COGS − wynagrodzenia − koszty operacyjne łącznie z amortyzacją (konta 4000–7999), przed pozycjami finansowymi i podatkiem. Wynik netto = EBIT + wynik finansowy − podatek dochodowy.",
        "no": "EBIT = driftsresultat: inntekt − COGS − lønn − driftskostnader inkl. avskrivninger (konto 4000–7999), før finansposter og skatt. Nettoresultat = EBIT + finansresultat − skattekostnad.",
    },
    "tax_pending_note": {
        "en": "Income tax is booked on 31 December, so the net result for {year} is still before tax.",
        "pl": "Podatek dochodowy księgowany jest 31 grudnia, więc wynik netto za {year} jest na razie przed podatkiem.",
        "no": "Skattekostnaden bokføres 31. desember, så nettoresultatet for {year} er foreløpig før skatt.",
    },
    "partial_month_excluded": {
        "en": "Totals and margin cover full months only (up to {month}); the open month is excluded.",
        "pl": "Sumy i marża obejmują tylko pełne miesiące (do {month}); miesiąc w toku jest pominięty.",
        "no": "Summer og margin dekker kun hele måneder (til og med {month}); den pågående måneden er utelatt.",
    },
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
    "child_care_leave": {"en": "Child-care leave", "pl": "Opieka nad dzieckiem", "no": "Omsorgspermisjon"},
    "flex_leave": {"en": "Flex leave", "pl": "Odbiór czasu (flex)", "no": "Avspasering"},
    "invoice_count": {"en": "Invoices", "pl": "Faktury", "no": "Fakturaer"},
    "suppliers_note": {
        "en": "Spend and Unpaid are net of VAT and include the pass-through COGS payables as well as purchase invoices.",
        "pl": "Wydatki i Niezapłacone są netto (bez VAT) i obejmują zarówno faktury zakupu, jak i przelotowe zobowiązania COGS.",
        "no": "Utgifter og Ubetalt er eksklusive MVA og omfatter både innkjøpsfakturaer og gjennomstrømmings-COGS.",
    },
    "cogs_by_supplier": {
        "en": "COGS by supplier (share of net COGS)", "pl": "COGS wg dostawcy (udział w COGS netto)",
        "no": "COGS per leverandør (andel av netto COGS)",
    },
    "all_suppliers": {"en": "All suppliers", "pl": "Wszyscy dostawcy", "no": "Alle leverandører"},
    "cogs_filter_label": {"en": "Filter by supplier", "pl": "Filtruj wg dostawcy", "no": "Filtrer på leverandør"},
    "payroll_net": {"en": "Net pay disbursed", "pl": "Wypłacone wynagrodzenia netto", "no": "Utbetalt nettolønn"},
    "payroll_net_note": {
        "en": "Net pay actually paid out (after tax withholding), from payslips. The gross and employer-cost figures below come from the salary specifications and tie to ledger labor cost.",
        "pl": "Wynagrodzenia netto faktycznie wypłacone (po potrąceniu podatku), z list płac. Kwoty brutto i koszt pracodawcy poniżej pochodzą ze specyfikacji płac i zgadzają się z kosztem pracy w księdze.",
        "no": "Nettolønn som faktisk er utbetalt (etter skattetrekk), fra lønnsslipper. Brutto og arbeidsgiverkostnad nedenfor kommer fra lønnsspesifikasjonene og stemmer med lønnskostnaden i hovedboken.",
    },
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
    "Tap på krav": {"en": "Write-offs of receivables", "pl": "Odpisy należności", "no": "Tap på krav"},
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
