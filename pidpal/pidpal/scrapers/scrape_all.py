from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Import the new template-method scrapers:
# (Adjust the import paths as needed, depending on your project layout)
from pidpal.scrapers.counties import *
from county_data.patriot_urls import PATRIOT_URL_MAPPING
from county_data.cpt_urls import CPT_URL_MAPPING


def scrape_all_counties(data_list, screenshot_dir="Screenshots"):
    """
    Creates ONE driver, uses the new template-method scrapers for each county,
    and returns all combined DataObjects.
    """

    # 1) Map (County, State) to "key" (e.g. "HennepinMN") 
    county_mapping = {
        ("Hennepin", "MN"): "HennepinMN",
        ("Lake", "MN"): "LakeMN",
        ("Pierce", "WI"): "PierceWI",
        ("Falmouth", "MA"): "FalmouthMA",
        ("Dover", "MA"): "DoverMA",
        ("Acushnet", "MA"): "AcushnetMA",
        ("Agawam", "MA"): "AgawamMA",
        ("Andover", "MA"): "AndoverMA",
        ("Arlington", "MA"): "ArlingtonMA",
        ("Ashfield", "MA"): "AshfieldMA",
        ("Auburn", "ME"): "AuburnME",
        ("Barnard", "VT"): "BarnardVT",
        ("Barton", "VT"): "BartonVT",
        ("Bedford", "MA"): "BedfordMA",
        ("Belchertown", "MA"): "BelchertownMA",
        ("Bellingham", "MA"): "BellinghamMA",
        ("Beverly", "MA"): "BeverlyMA",
        ("Billerica", "MA"): "BillericaMA",
        ("Blandford", "MA"): "BlandfordMA",
        ("Braintree", "MA"): "BraintreeMA",
        ("Brentwood", "NH"): "BrentwoodNH",
        ("Brimfield", "MA"): "BrimfieldMA",
        ("Burlington", "MA"): "BurlingtonMA",
        ("Carlisle", "MA"): "CarlisleMA",
        ("Castleton", "VT"): "CastletonVT",
        ("Charlton", "MA"): "CharltonMA",
        ("Clarksburg", "MA"): "ClarksburgMA",
        ("Cohasset", "MA"): "CohassetMA",
        ("Coventry", "VT"): "CoventryVT",
        ("Cummington", "MA"): "CummingtonMA",
        ("Dalton", "MA"): "DaltonMA",
        ("Danvers", "MA"): "DanversMA",
        ("Deerfield", "MA"): "DeerfieldMA",
        ("Derby", "VT"): "DerbyVT",
        ("Douglas", "MA"): "DouglasMA",
        ("Dunstable", "MA"): "DunstableMA",
        ("Essex", "MA"): "EssexMA",
        ("Everett", "MA"): "EverettMA",
        ("Fairhaven", "MA"): "FairhavenMA",
        ("Fall River", "MA"): "Fall RiverMA",
        ("Framingham", "MA"): "FraminghamMA",
        ("Franklin", "MA"): "FranklinMA",
        ("Great Barrington", "MA"): "Great BarringtonMA",
        ("Groveland", "MA"): "GrovelandMA",
        ("Hamilton", "MA"): "HamiltonMA",
        ("Hardwick", "MA"): "HardwickMA",
        ("Hatfield", "MA"): "HatfieldMA",
        ("Haverhill", "MA"): "HaverhillMA",
        ("Holbrook", "MA"): "HolbrookMA",
        ("Holyoke", "MA"): "HolyokeMA",
        ("Hopedale", "MA"): "HopedaleMA",
        ("Hopkinton", "MA"): "HopkintonMA",
        ("Hull", "MA"): "HullMA",
        ("Ipswich", "MA"): "IpswichMA",
        ("Jamaica", "VT"): "JamaicaVT",
        ("Jay", "VT"): "JayVT",
        ("Lancaster County", "SC"): "Lancaster CountySC",
        ("Leicester", "MA"): "LeicesterMA",
        ("Littleton", "MA"): "LittletonMA",
        ("Lynn", "MA"): "LynnMA",
        ("Lynnfield", "MA"): "LynnfieldMA",
        ("Malden", "MA"): "MaldenMA",
        ("Manchester-by-the-Sea", "MA"): "Manchester-by-the-SeaMA",
        ("Marblehead", "MA"): "MarbleheadMA",
        ("Marshfield", "MA"): "MarshfieldMA",
        ("Marshfield", "VT"): "MarshfieldVT",
        ("Maynard", "MA"): "MaynardMA",
        ("Medway", "MA"): "MedwayMA",
        ("Melrose", "MA"): "MelroseMA",
        ("Merrimac", "MA"): "MerrimacMA",
        ("Methuen", "MA"): "MethuenMA",
        ("Middleton", "MA"): "MiddletonMA",
        ("Milford", "MA"): "MilfordMA",
        ("Millville", "MA"): "MillvilleMA",
        ("Milton", "MA"): "MiltonMA",
        ("Montague", "MA"): "MontagueMA",
        ("Montgomery", "MA"): "MontgomeryMA",
        ("Montpelier", "VT"): "MontpelierVT",
        ("Nahant", "MA"): "NahantMA",
        ("New Ashford", "MA"): "New AshfordMA",
        ("Newbury", "MA"): "NewburyMA",
        ("North Adams", "MA"): "North AdamsMA",
        ("North Andover", "MA"): "North AndoverMA",
        ("Northborough", "MA"): "NorthboroughMA",
        ("Northfield", "MA"): "NorthfieldMA",
        ("Norwich", "VT"): "NorwichVT",
        ("Orange", "MA"): "OrangeMA",
        ("Pembroke", "MA"): "PembrokeMA",
        ("Pepperell", "MA"): "PepperellMA",
        ("Peru", "MA"): "PeruMA",
        ("Plainville", "MA"): "PlainvilleMA",
        ("Plymouth", "MA"): "PlymouthMA",
        ("Raynham", "MA"): "RaynhamMA",
        ("Reading", "MA"): "ReadingMA",
        ("Revere", "MA"): "RevereMA",
        ("Rochester", "NH"): "RochesterNH",
        ("Salem", "MA"): "SalemMA",
        ("Salisbury", "MA"): "SalisburyMA",
        ("Saugus", "MA"): "SaugusMA",
        ("Shelburne", "MA"): "ShelburneMA",
        ("Sherborn", "MA"): "SherbornMA",
        ("Shirley", "MA"): "ShirleyMA",
        ("Somersworth", "NH"): "SomersworthNH",
        ("Southborough", "MA"): "SouthboroughMA",
        ("Springfield", "VT"): "SpringfieldVT",
        ("Stoneham", "MA"): "StonehamMA",
        ("Stoughton", "MA"): "StoughtonMA",
        ("Swampscott", "MA"): "SwampscottMA",
        ("Tolland", "MA"): "TollandMA",
        ("Topsfield", "MA"): "TopsfieldMA",
        ("Townsend", "MA"): "TownsendMA",
        ("Tyngsborough", "MA"): "TyngsboroughMA",
        ("Upton", "MA"): "UptonMA",
        ("Uxbridge", "MA"): "UxbridgeMA",
        ("Wakefield", "MA"): "WakefieldMA",
        ("Waltham", "MA"): "WalthamMA",
        ("Warwick", "MA"): "WarwickMA",
        ("Watertown", "MA"): "WatertownMA",
        ("Wendell", "MA"): "WendellMA",
        ("Wenham", "MA"): "WenhamMA",
        ("West Bridgewater", "MA"): "West BridgewaterMA",
        ("West Newbury", "MA"): "West NewburyMA",
        ("West Tisbury", "MA"): "West TisburyMA",
        ("Westborough", "MA"): "WestboroughMA",
        ("Westford", "MA"): "WestfordMA",
        ("Whitman", "MA"): "WhitmanMA",
        ("Williamsburg", "MA"): "WilliamsburgMA",
        ("Williamstown", "MA"): "WilliamstownMA",
        ("Winchester", "MA"): "WinchesterMA",
        ("Worthington", "MA"): "WorthingtonMA",
        ("Douglas", "MN"): "DouglasMN",
        ("Grant", "MN"): "GrantMN",
        ("Kandiyohi", "MN"): "KandiyohiMN",
        ("Lincoln", "MN"): "LincolnMN",
        ("Meeker", "MN"): "MeekerMN",
        ("Mille Lacs", "MN"): "Mille LacsMN",
        ("Pope ", "MN"): "Pope MN",
        ("Renville", "MN"): "RenvilleMN",
        ("Sibley", "MN"): "SibleyMN",
        ("Yellow Medicine", "MN"): "Yellow MedicineMN",
        ("Spokane", "WA"): "SpokaneWA",
        ("Douglas", "WI"): "DouglasWI"
    }

    # 2) Group parcel IDs by the "key"
    cnum = {}
    for item in data_list:
        parcel_id = item["ParcelID"].strip()
        state = item["State"].strip().upper()
        county = item["County"].strip().title()
        key = county_mapping.get((county, state))
        if key:
            cnum.setdefault(key, []).append(parcel_id)

    all_data = []

    # 3) Initialize ONE Selenium driver
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")  # optional if you want headless
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        # --------------------------------------------------------------------
        # 4) Template-based scrapers for your known counties
        # --------------------------------------------------------------------

        # Hennepin, MN
        if "HennepinMN" in cnum:
            scraper = HennepinMNScraper(driver, screenshot_dir)
            results = scraper.scrape_county(cnum["HennepinMN"])
            all_data.extend(results)

        # Lake, MN
        if "LakeMN" in cnum:
            scraper = LakeMNScraper(driver, screenshot_dir)
            results = scraper.scrape_county(cnum["LakeMN"])
            all_data.extend(results)

        # Pierce, WI
        if "PierceWI" in cnum:
            scraper = PierceWIScraper(driver, screenshot_dir)
            results = scraper.scrape_county(cnum["PierceWI"])
            all_data.extend(results)
        
        # Spokane, WA
        if "SpokaneWA" in cnum:
            scraper = SpokaneWAScraper(driver, screenshot_dir)
            results = scraper.scrape_county(cnum["SpokaneWA"])
            all_data.extend(results)
        
        # Douglas, WI
        if "DouglasWI" in cnum:
            scraper = DouglasWIScraper(driver, screenshot_dir)
            results = scraper.scrape_county(cnum["DouglasWI"])
            all_data.extend(results)

        # --------------------------------------------------------------------
        # 5) Patriot counties
        #    For each key found in cnum that also matches your PATRIOT_URL_MAPPING,
        #    create a PatriotScraper and call `scrape_county`.
        # --------------------------------------------------------------------
        for county_key, base_url in PATRIOT_URL_MAPPING.items():
            if county_key in cnum and cnum[county_key]:
                patriot_scraper = PatriotScraper(driver, screenshot_dir, base_url)
                result = patriot_scraper.scrape_county(cnum[county_key])
                all_data.extend(result)

        # --------------------------------------------------------------------
        # 6) CPT counties
        #    Same pattern, using the CPTScraper.
        # --------------------------------------------------------------------
        for county_key, base_url in CPT_URL_MAPPING.items():
            if county_key in cnum and cnum[county_key]:
                cpt_scraper = CPTScraper(driver, screenshot_dir, base_url)
                result = cpt_scraper.scrape_county(cnum[county_key])
                all_data.extend(result)

    finally:
        # 7) Quit driver once at the end
        driver.quit()

    return all_data
