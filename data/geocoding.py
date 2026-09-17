"""Static city -> coordinates lookup for Norwegian cities.

The source database has no lat/lon columns; customer location is only
city + postal_code. Since the set of cities is small and fixed (Norwegian
municipalities), a static lookup avoids any external geocoding API call.
"""

import pandas as pd

CITY_COORDINATES = {
    "Oslo": (59.9139, 10.7522),
    "Bergen": (60.3913, 5.3221),
    "Trondheim": (63.4305, 10.3951),
    "Stavanger": (58.9700, 5.7331),
    "Bærum": (59.8938, 10.5453),
    "Kristiansand": (58.1467, 7.9956),
    "Fredrikstad": (59.2181, 10.9298),
    "Sandnes": (58.8516, 5.7357),
    "Tromsø": (69.6492, 18.9553),
    "Sarpsborg": (59.2839, 11.1096),
    "Skien": (59.2096, 9.6085),
    "Ålesund": (62.4722, 6.1495),
    "Sandefjord": (59.1289, 10.2166),
    "Haugesund": (59.4138, 5.2680),
    "Tønsberg": (59.2674, 10.4076),
    "Moss": (59.4342, 10.6577),
    "Porsgrunn": (59.1406, 9.6560),
    "Bodø": (67.2804, 14.4049),
    "Arendal": (58.4610, 8.7723),
    "Hamar": (60.7945, 11.0680),
    "Larvik": (59.0537, 10.0355),
    "Halden": (59.1330, 11.3874),
    "Lillehammer": (61.1153, 10.4662),
    "Molde": (62.7372, 7.1607),
    "Harstad": (68.7986, 16.5417),
    "Kongsberg": (59.6689, 9.6503),
    "Gjøvik": (60.7957, 10.6915),
    "Drammen": (59.7440, 10.2045),
    "Steinkjer": (64.0149, 11.4956),
    "Narvik": (68.4385, 17.4272),
    "Kongsvinger": (60.1938, 12.0021),
    "Askøy": (60.4581, 5.1666),
    "Levanger": (63.7462, 11.2985),
    "Mo i Rana": (66.3128, 14.1428),
    "Notodden": (59.5595, 9.2585),
    "Lillestrøm": (59.9556, 11.0489),
    "Jessheim": (60.1432, 11.1740),
    "Kristiansund": (63.1105, 7.7278),
    "Hønefoss": (60.1690, 10.2570),
    "Stjørdal": (63.4714, 10.9169),
    "Elverum": (60.8811, 11.5623),
}


def geocode_customers(customers_df: pd.DataFrame) -> pd.DataFrame:
    """Attach lat/lon columns to a customers DataFrame based on the city column."""
    df = customers_df.copy()
    df["lat"] = df["city"].map(lambda c: CITY_COORDINATES.get(c, (None, None))[0])
    df["lon"] = df["city"].map(lambda c: CITY_COORDINATES.get(c, (None, None))[1])
    return df
