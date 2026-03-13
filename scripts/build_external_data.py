#!/usr/bin/env python3
"""Process external CSVs into dashboard-ready JSON files.

Uses only stdlib (csv, json, os) so it runs without installing any packages.
Reads from data/raw/external/ and writes to dashboard/data/.
"""

import csv
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT = os.path.join(BASE, "data", "raw", "external")
DASH = os.path.join(BASE, "dashboard", "data")

WHO = os.path.join(EXT, "who_ghe")
WB = os.path.join(EXT, "worldbank_wdi")
UNDP = os.path.join(EXT, "undp_hdi")
GEO = os.path.join(EXT, "geo")

# World Bank aggregate codes to skip
WB_AGGREGATES = {
    "ZH", "ZI", "ZJ", "ZQ", "ZG", "ZF", "Z4", "Z7", "ZT",
    "1A", "1W", "4E", "7E", "8S", "B8", "EU", "F1", "OE",
    "S1", "S2", "S3", "S4", "V1", "V2", "V3", "V4", "XC",
    "XD", "XE", "XF", "XG", "XH", "XI", "XJ", "XL", "XM",
    "XN", "XO", "XP", "XQ", "XT", "XU", "XY", "ZB",
    "AFE", "AFW", "ARB", "CEB", "CSS", "EAP", "EAR", "EAS",
    "ECA", "ECS", "EMU", "FCS", "HIC", "HPC", "IBD", "IBT",
    "IDA", "IDB", "IDX", "INX", "LAC", "LCN", "LDC", "LIC",
    "LMC", "LMY", "LTE", "MEA", "MIC", "MNA", "NAC", "OED",
    "OSS", "PRE", "PSS", "PST", "SAS", "SSA", "SSF", "SST",
    "TEA", "TEC", "TLA", "TMN", "TSA", "TSS", "UMC", "WLD",
}


def safe_float(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def read_who_csv(filepath, sex_filter="SEX_BTSX", dim1_type="SEX"):
    """Parse WHO GHO CSV. Returns {(iso3, year): value}."""
    result = {}
    if not os.path.exists(filepath):
        return result
    with open(filepath, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("SpatialDimType") != "COUNTRY":
                continue
            # Filter by Dim1 if the file uses it
            if dim1_type and row.get("Dim1Type") == dim1_type:
                if row.get("Dim1") != sex_filter:
                    continue
            iso3 = row.get("SpatialDim", "").strip()
            year = safe_float(row.get("TimeDim"))
            value = safe_float(row.get("NumericValue"))
            if iso3 and year is not None and value is not None:
                yr = int(year)
                key = (iso3, yr)
                # Keep most recent entry per country-year
                if key not in result or yr >= result[key][1]:
                    result[key] = (value, yr)
    return {k: v[0] for k, v in result.items()}


def build_iso2_to_iso3():
    """Build ISO2 → ISO3 mapping from country_meta.csv."""
    filepath = os.path.join(GEO, "country_meta.csv")
    mapping = {}
    if not os.path.exists(filepath):
        return mapping
    with open(filepath, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            iso2 = row.get("iso2", "").strip()
            iso3 = row.get("iso3", "").strip()
            if iso2 and iso3:
                mapping[iso2] = iso3
    return mapping


# WB 2-letter aggregate codes to skip
WB_AGGREGATE_2 = {
    "ZH", "ZI", "ZJ", "ZQ", "ZG", "ZF", "Z4", "Z7", "ZT", "ZB",
    "1A", "1W", "4E", "7E", "8S", "B8", "EU", "F1", "OE",
    "S1", "S2", "S3", "S4", "V1", "V2", "V3", "V4", "XC",
    "XD", "XE", "XF", "XG", "XH", "XI", "XJ", "XL", "XM",
    "XN", "XO", "XP", "XQ", "XT", "XU", "XY",
}


def read_wb_csv(filepath, iso2_to_iso3=None):
    """Parse World Bank API CSV. Returns {(iso3, year): value}.
    WB files use 2-letter country codes, so we convert via iso2_to_iso3 mapping.
    """
    result = {}
    if not os.path.exists(filepath):
        return result
    if iso2_to_iso3 is None:
        iso2_to_iso3 = build_iso2_to_iso3()
    with open(filepath, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cc = row.get("country_code", "").strip()
            if cc in WB_AGGREGATE_2 or cc in WB_AGGREGATES:
                continue
            iso3 = iso2_to_iso3.get(cc)
            if not iso3:
                continue
            year = safe_float(row.get("year"))
            value = safe_float(row.get("value"))
            if year is not None and value is not None:
                result[(iso3, int(year))] = value
    return result


def read_undp_hdi():
    """Parse UNDP HDI wide-format file. Returns {iso3: {year: {hdi, le, gnipc, ...}}}."""
    filepath = os.path.join(UNDP, "hdi_composite_indices.csv")
    result = {}
    if not os.path.exists(filepath):
        return result
    with open(filepath, encoding="latin-1") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        for row in reader:
            iso3 = row.get("iso3", "").strip()
            if not iso3 or len(iso3) != 3:
                continue
            country_data = {"country": row.get("country", ""), "region": row.get("region", "")}
            yearly = {}
            for yr in range(1990, 2024):
                entry = {}
                for prefix in ("hdi", "le", "gnipc", "eys", "mys"):
                    col = f"{prefix}_{yr}"
                    if col in headers:
                        entry[prefix] = safe_float(row.get(col))
                if any(v is not None for v in entry.values()):
                    yearly[yr] = entry
            country_data["yearly"] = yearly
            result[iso3] = country_data
    return result


def read_geo():
    """Parse country_meta.csv. Returns {iso3: {region, subregion, lat, lng, population}}."""
    filepath = os.path.join(GEO, "country_meta.csv")
    result = {}
    if not os.path.exists(filepath):
        return result
    with open(filepath, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            iso3 = row.get("iso3", "").strip()
            if not iso3:
                continue
            result[iso3] = {
                "region": row.get("region", ""),
                "subregion": row.get("subregion", ""),
                "lat": safe_float(row.get("latitude")),
                "lng": safe_float(row.get("longitude")),
            }
    return result


def latest_value(data_dict, iso3, max_year=2023, min_year=2000):
    """Get most recent value for an iso3 from a {(iso3, year): value} dict."""
    for yr in range(max_year, min_year - 1, -1):
        val = data_dict.get((iso3, yr))
        if val is not None:
            return val, yr
    return None, None


def build_all():
    print("Loading external data sources...")

    # WHO data
    hale = read_who_csv(os.path.join(WHO, "hale_at_birth.csv"))
    le = read_who_csv(os.path.join(WHO, "life_expectancy_at_birth.csv"))
    uhc = read_who_csv(os.path.join(WHO, "uhc_service_coverage.csv"), sex_filter=None, dim1_type=None)
    pm25 = read_who_csv(os.path.join(WHO, "pm25_exposure.csv"), sex_filter=None, dim1_type=None)
    doctors = read_who_csv(os.path.join(WHO, "medical_doctors_per_10k.csv"), sex_filter=None, dim1_type=None)
    nurses = read_who_csv(os.path.join(WHO, "nursing_midwifery_per_10k.csv"), sex_filter=None, dim1_type=None)
    beds = read_who_csv(os.path.join(WHO, "hospital_beds_per_10k.csv"), sex_filter=None, dim1_type=None)
    che = read_who_csv(os.path.join(WHO, "che_per_capita_usd.csv"), sex_filter=None, dim1_type=None)
    oop = read_who_csv(os.path.join(WHO, "oop_pct_che.csv"), sex_filter=None, dim1_type=None)
    smoking = read_who_csv(os.path.join(WHO, "smoking_prevalence.csv"))
    obesity = read_who_csv(os.path.join(WHO, "obesity_prevalence.csv"))
    alcohol = read_who_csv(os.path.join(WHO, "alcohol_consumption_per_capita.csv"))
    maternal = read_who_csv(os.path.join(WHO, "maternal_mortality_ratio.csv"), sex_filter=None, dim1_type=None)
    suicide = read_who_csv(os.path.join(WHO, "suicide_rate.csv"))
    infant_mort = read_who_csv(os.path.join(WHO, "infant_mortality_rate.csv"))

    print(f"  WHO: hale={len(hale)}, le={len(le)}, uhc={len(uhc)}, pm25={len(pm25)}, "
          f"doctors={len(doctors)}, smoking={len(smoking)}, obesity={len(obesity)}")

    # World Bank data
    iso2_to_iso3 = build_iso2_to_iso3()
    gdp_pc = read_wb_csv(os.path.join(WB, "NY.GDP.PCAP.CD.csv"), iso2_to_iso3)
    pop = read_wb_csv(os.path.join(WB, "SP.POP.TOTL.csv"), iso2_to_iso3)
    urban = read_wb_csv(os.path.join(WB, "SP.URB.TOTL.IN.ZS.csv"), iso2_to_iso3)
    gini = read_wb_csv(os.path.join(WB, "SI.POV.GINI.csv"), iso2_to_iso3)
    literacy = read_wb_csv(os.path.join(WB, "SE.ADT.LITR.ZS.csv"), iso2_to_iso3)
    unemployment = read_wb_csv(os.path.join(WB, "SL.UEM.TOTL.ZS.csv"), iso2_to_iso3)

    print(f"  WB: gdp={len(gdp_pc)}, pop={len(pop)}, urban={len(urban)}")

    # UNDP HDI
    undp = read_undp_hdi()
    print(f"  UNDP: {len(undp)} countries")

    # Geo metadata
    geo = read_geo()
    print(f"  Geo: {len(geo)} countries")

    # Collect all unique ISO3 codes
    all_iso3 = set()
    for d in [hale, le, uhc, pm25, doctors, che, gdp_pc, pop]:
        all_iso3.update(k[0] for k in d.keys())
    all_iso3.update(undp.keys())
    all_iso3 = sorted(c for c in all_iso3 if len(c) == 3)

    print(f"  Total unique countries: {len(all_iso3)}")

    # --- Build panorama.json ---
    print("Building panorama.json...")
    panorama_countries = []
    for iso3 in all_iso3:
        hale_val, _ = latest_value(hale, iso3)
        hdi_val = None
        if iso3 in undp:
            for yr in range(2023, 1999, -1):
                ydata = undp[iso3].get("yearly", {}).get(yr, {})
                if ydata.get("hdi") is not None:
                    hdi_val = ydata["hdi"]
                    break
        uhc_val, _ = latest_value(uhc, iso3)
        pm25_val, _ = latest_value(pm25, iso3)
        doc_val, _ = latest_value(doctors, iso3)
        che_val, _ = latest_value(che, iso3)
        smoking_val, _ = latest_value(smoking, iso3)
        obesity_val, _ = latest_value(obesity, iso3)
        le_val, _ = latest_value(le, iso3)
        pop_val, _ = latest_value(pop, iso3)
        nurse_val, _ = latest_value(nurses, iso3)
        bed_val, _ = latest_value(beds, iso3)

        geo_info = geo.get(iso3, {})

        # At least 3 indicators must be present
        vals = [hale_val, hdi_val, uhc_val, pm25_val, doc_val, che_val]
        if sum(1 for v in vals if v is not None) < 2:
            continue

        entry = {
            "iso3": iso3,
            "hale": round(hale_val, 1) if hale_val else None,
            "hdi": round(hdi_val, 3) if hdi_val else None,
            "uhc_index": round(uhc_val, 1) if uhc_val else None,
            "pm25": round(pm25_val, 1) if pm25_val else None,
            "doctor_density": round(doc_val, 2) if doc_val else None,
            "nurse_density": round(nurse_val, 2) if nurse_val else None,
            "bed_density": round(bed_val, 2) if bed_val else None,
            "che_per_capita": round(che_val, 1) if che_val else None,
            "smoking_rate": round(smoking_val, 1) if smoking_val else None,
            "obesity_rate": round(obesity_val, 1) if obesity_val else None,
            "life_expectancy": round(le_val, 1) if le_val else None,
            "population": int(pop_val) if pop_val else None,
            "region": geo_info.get("region", ""),
            "subregion": geo_info.get("subregion", ""),
        }
        panorama_countries.append(entry)

    panorama = {"generated": "build_external_data.py", "countries": panorama_countries}
    write_json(os.path.join(DASH, "panorama.json"), panorama)
    print(f"  panorama.json: {len(panorama_countries)} countries")

    # --- Build bubble_timeseries.json ---
    print("Building bubble_timeseries.json...")
    bubble_data = {}
    # Pre-compute latest LE per country for carry-forward
    latest_le_by_iso3 = {}
    for (iso3_code, yr), val in le.items():
        if iso3_code not in latest_le_by_iso3 or yr > latest_le_by_iso3[iso3_code][1]:
            latest_le_by_iso3[iso3_code] = (val, yr)
    for yr in range(2000, 2024):
        year_records = []
        for iso3 in all_iso3:
            gdp_val = gdp_pc.get((iso3, yr))
            le_val_ts = le.get((iso3, yr))
            # Carry forward LE for recent years if missing
            if le_val_ts is None and yr >= 2020:
                best = latest_le_by_iso3.get(iso3)
                if best and best[1] >= 2018:
                    le_val_ts = best[0]
            pop_val_ts = pop.get((iso3, yr))

            if gdp_val is None or le_val_ts is None or pop_val_ts is None:
                continue

            geo_info = geo.get(iso3, {})
            year_records.append({
                "iso3": iso3,
                "gdp_pc": round(gdp_val, 1),
                "life_expectancy": round(le_val_ts, 2),
                "population": int(pop_val_ts),
                "region": geo_info.get("region", ""),
            })
        bubble_data[str(yr)] = year_records

    bubble_out = {"years": list(range(2000, 2024)), "by_year": bubble_data}
    write_json(os.path.join(DASH, "bubble_timeseries.json"), bubble_out)
    total_records = sum(len(v) for v in bubble_data.values())
    print(f"  bubble_timeseries.json: {total_records} total records across {len(bubble_data)} years")

    # --- Build risk_indicators.json ---
    print("Building risk_indicators.json...")
    risk_countries = []
    for iso3 in all_iso3:
        pm25_val, _ = latest_value(pm25, iso3)
        smoking_val, _ = latest_value(smoking, iso3)
        obesity_val, _ = latest_value(obesity, iso3)
        alcohol_val, _ = latest_value(alcohol, iso3)

        if all(v is None for v in [pm25_val, smoking_val, obesity_val, alcohol_val]):
            continue

        risk_countries.append({
            "iso3": iso3,
            "pm25": round(pm25_val, 1) if pm25_val else None,
            "smoking_rate": round(smoking_val, 1) if smoking_val else None,
            "obesity_rate": round(obesity_val, 1) if obesity_val else None,
            "alcohol_consumption": round(alcohol_val, 2) if alcohol_val else None,
        })

    risk_out = {"generated": "build_external_data.py", "countries": risk_countries}
    write_json(os.path.join(DASH, "risk_indicators.json"), risk_out)
    print(f"  risk_indicators.json: {len(risk_countries)} countries")

    # --- Enhance country_profiles.json ---
    print("Enhancing country_profiles.json...")
    profiles_path = os.path.join(DASH, "country_profiles.json")
    if os.path.exists(profiles_path):
        with open(profiles_path, encoding="utf-8") as f:
            profiles = json.load(f)

        enhanced = 0
        for iso3, profile in profiles.items():
            latest = profile.get("latest", {})

            hale_val, _ = latest_value(hale, iso3)
            hdi_val = None
            if iso3 in undp:
                for yr in range(2023, 1999, -1):
                    ydata = undp[iso3].get("yearly", {}).get(yr, {})
                    if ydata.get("hdi") is not None:
                        hdi_val = ydata["hdi"]
                        break
            uhc_val, _ = latest_value(uhc, iso3)
            pm25_val, _ = latest_value(pm25, iso3)
            doc_val, _ = latest_value(doctors, iso3)
            nurse_val, _ = latest_value(nurses, iso3)
            bed_val, _ = latest_value(beds, iso3)
            che_val, _ = latest_value(che, iso3)
            oop_val, _ = latest_value(oop, iso3)
            smoking_val, _ = latest_value(smoking, iso3)
            obesity_val, _ = latest_value(obesity, iso3)
            maternal_val, _ = latest_value(maternal, iso3)
            suicide_val, _ = latest_value(suicide, iso3)
            alcohol_val, _ = latest_value(alcohol, iso3)

            new_fields = {
                "hale": round(hale_val, 1) if hale_val else None,
                "hdi": round(hdi_val, 3) if hdi_val else None,
                "uhc_index": round(uhc_val, 1) if uhc_val else None,
                "pm25": round(pm25_val, 1) if pm25_val else None,
                "doctor_density": round(doc_val, 2) if doc_val else None,
                "nurse_density": round(nurse_val, 2) if nurse_val else None,
                "bed_density": round(bed_val, 2) if bed_val else None,
                "che_per_capita": round(che_val, 1) if che_val else None,
                "oop_pct": round(oop_val, 1) if oop_val else None,
                "smoking_rate": round(smoking_val, 1) if smoking_val else None,
                "obesity_rate": round(obesity_val, 1) if obesity_val else None,
                "maternal_mortality": round(maternal_val, 1) if maternal_val else None,
                "suicide_rate": round(suicide_val, 1) if suicide_val else None,
                "alcohol_consumption": round(alcohol_val, 2) if alcohol_val else None,
            }

            added = False
            for k, v in new_fields.items():
                if v is not None:
                    latest[k] = v
                    added = True
            if added:
                enhanced += 1

        write_json(profiles_path, profiles)
        print(f"  country_profiles.json: enhanced {enhanced} country profiles")
    else:
        print("  country_profiles.json not found, skipping enhancement")

    print("Done!")


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__":
    build_all()
