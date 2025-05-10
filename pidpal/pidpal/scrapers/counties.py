import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from pidpal.func import take_screenshot, DataObject


class BaseCountyScraper:
    """
    Base / abstract class for all county scrapers.
    Defines a template method pattern for scraping parcels.
    """

    def __init__(self, driver, screenshot_dir):
        self.driver = driver
        self.screenshot_dir = screenshot_dir

    def scrape_county(self, parcel_ids):
        """
        The 'template method': Orchestrates the entire scraping workflow.
        1) Go to the county's main page
        2) Handle disclaimers
        3) Scrape all parcels
        4) Return the resulting data (list of DataObject)
        """
        self.go_to_main_page()
        self.handle_disclaimers()
        return self.scrape_parcels(parcel_ids)

    def go_to_main_page(self):
        """
        (Abstract) Navigate to the county's landing page or initial URL.
        Subclasses must override.
        """
        raise NotImplementedError("Subclasses must implement go_to_main_page()")

    def handle_disclaimers(self):
        """
        (Hook) If the county site has disclaimers or popups to click away,
        subclasses can override. Default does nothing.
        """
        pass

    def scrape_parcels(self, parcel_ids):
        """
        (Abstract) The main loop for each parcel:
            - potentially call search_for_parcel(...)
            - parse and collect data
            - screenshots, if needed
            - return a list of DataObject
        """
        raise NotImplementedError("Subclasses must implement scrape_parcels()")


# ----------------------------------------------------------------------------
# 1) Pierce County, WI
# ----------------------------------------------------------------------------
class PierceWIScraper(BaseCountyScraper):
    """
    Scraper for Pierce County, WI.
    """

    def __init__(self, driver, screenshot_dir):
        super().__init__(driver, screenshot_dir)
        self.base_url = 'https://internal.co.pierce.wi.us/gcswebportal/'

    def go_to_main_page(self):
        """
        Navigate to the main page and accept disclaimers ONCE.
        """
        self.driver.get(self.base_url)
        self.driver.implicitly_wait(10)

        # Accept disclaimers
        disclaimer_button_xpath = '//*[@id="ctl00_cphMainApp_btnEntryPageAccept"]'
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, disclaimer_button_xpath))
        ).click()


    def scrape_county(self, parcel_ids):
        """
        The 'template method' that orchestrates the entire scraping flow:
        1) Go to the county's main page, accept disclaimers ONCE
        2) Then scrape all parcels in a loop
        """
        # 1) Go to main page, accept disclaimers once
        self.go_to_main_page()

        # 2) Now do the per-parcel logic in scrape_parcels
        return self.scrape_parcels(parcel_ids)

    def scrape_parcels(self, parcel_ids):
        """
        Scrape parcel data for all parcels, reusing the session
        without re-invoking disclaimers each time.
        """
        all_data = []

        for parcel_id in parcel_ids:
            parcel_data = None
            try:
                print("\nDEBUG: Processing parcel:", parcel_id)

                # 1) Search for the parcel
                search_box_xpath = '//*[@id="mtxtParcelNumber"]'
                search_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, search_box_xpath))
                )

                # Clear + set value by JS to handle any masked input
                self.driver.execute_script(
                    "arguments[0].value = arguments[1];", search_box, parcel_id
                )
                time.sleep(1)

                # Some sites require a button click instead of ENTER, but let's try ENTER first
                search_box.send_keys(Keys.ENTER)
    

                # 2) Navigate to the assessment page
                assessment_page_link_xpath = '//*[@id="LinkButtonAssessments"]'
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, assessment_page_link_xpath))
                ).click()

                # 3) Check if current year is assessed, if not, select previous year
                not_assessed_xpath = '//*[@id="LabelViewValuationsNotAllowed"]'
                year_dropdown_xpath = '//*[@id="ddlTaxYear"]'

                if self.driver.find_elements(By.XPATH, not_assessed_xpath):
                    year_dropdown = Select(
                        self.driver.find_element(By.XPATH, year_dropdown_xpath)
                    )
                    year_dropdown.select_by_index(1)

                # 4) Extract values
                land_value_xpath = '//*[@id="lblLand"]'
                building_value_xpath  = '//*[@id="lblImprovements"]'
                total_value_xpath = '//*[@id="lblTotal"]'
                assyear_value_xpath = '//*[@id="LabelCurrentYearValuationsRE"]'

                assyear = self.driver.find_element(By.XPATH, assyear_value_xpath).text
                assyear_value = assyear.split()[0]
                land_value = self.driver.find_element(By.XPATH, land_value_xpath).text
                building_value = self.driver.find_element(By.XPATH, building_value_xpath).text
                total_value = self.driver.find_element(By.XPATH, total_value_xpath).text

                # 4.5) Take screenshot
                screenshot_path = take_screenshot(self.driver, self.screenshot_dir, f"{parcel_id}.png")

                # 5) Create DataObject
                parcel_data = DataObject(
                    ParcelID=parcel_id,
                    LandValue=land_value,
                    BuildingValue=building_value,
                    TotalValue=total_value,
                    AssessmentYear=assyear_value,  # Extract if available
                    ScreenshotPath=screenshot_path
                )

                

                all_data.append(parcel_data)

            except Exception as e:
                print(f"PierceWI: Error processing parcel ID {parcel_id}: {e}")
                # Optionally do an error screenshot
                error_shot = os.path.join(self.screenshot_dir, f"error_{parcel_id}.png")
                self.driver.save_screenshot(error_shot)

        return all_data


# ----------------------------------------------------------------------------
# 2) Hennepin County, MN
# ----------------------------------------------------------------------------
class HennepinMNScraper(BaseCountyScraper):
    """
    Scraper for Hennepin County, MN.
    """

    def go_to_main_page(self):
        """
        In Hennepin's case, we directly navigate in scrape_parcels below,
        so you can leave this blank or implement the main landing page.
        """
        pass

    def scrape_parcels(self, parcel_ids):
        """
        Implementation of the Hennepin County logic from your original 'HennepinMN' method.
        """
        all_data = []
        for parcel_id in parcel_ids:
            try:
                # 1) Go to the Hennepin site
                self.driver.get('https://www16.co.hennepin.mn.us/pins/?articleId=by_pid#by_pid')

                # 2) Wait for input to be clickable, then type parcel ID
                WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.ID, "pid"))
                ).click()
                pid_text = self.driver.find_element(By.ID, "pid")
                pid_text.send_keys(parcel_id, Keys.ENTER)

                # 3) Gather fields
                land_val = self.driver.find_element(
                    By.XPATH, "/html/body/div[3]/section/div/div[2]/article[4]/div[2]/div[3]/div[2]"
                ).text
                bldg_val = self.driver.find_element(
                    By.XPATH, "/html/body/div[3]/section/div/div[2]/article[4]/div[2]/div[4]/div[2]"
                ).text
                total_val = self.driver.find_element(
                    By.XPATH, "/html/body/div[3]/section/div/div[2]/article[4]/div[2]/div[6]/div[2]"
                ).text

                # 4) Assessment year
                select_element = self.driver.find_element(By.ID, 'year')
                select = Select(select_element)
                assessment_year = select.first_selected_option.text

                # 5) Create DataObject
                parcel_data = DataObject(
                    ParcelID=parcel_id,
                    LandValue=land_val,
                    BuildingValue=bldg_val,
                    TotalValue=total_val,
                    AssessmentYear=assessment_year,
                    ScreenshotPath=""
                )

                # 6) Take screenshot
                screenshot_path = take_screenshot(self.driver, self.screenshot_dir, f"{parcel_id}.png")
                parcel_data.ScreenshotPath = screenshot_path

                print(
                    f"HennepinMN -> {parcel_id}: Land={land_val}, Building={bldg_val}, "
                    f"Total={total_val}, Year={assessment_year}"
                )
                all_data.append(parcel_data)

            except Exception as e:
                print(f"HennepinMN: Error processing parcel ID {parcel_id}: {e}")
                # Optionally do an error screenshot
                error_shot = os.path.join(self.screenshot_dir, f"error_{parcel_id}.png")
                self.driver.save_screenshot(error_shot)

        return all_data


# ----------------------------------------------------------------------------
# 3) Lake County, MN
# ----------------------------------------------------------------------------
class LakeMNScraper(BaseCountyScraper):
    """
    Scraper for Lake County, MN, based on your 'scrape_lake_mn' method.
    """

    def __init__(self, driver, screenshot_dir):
        super().__init__(driver, screenshot_dir)
        # Hardcoded or optional config:
        self.initial_url = 'https:parcelinfo.com/'
        self.lake_county_link = "//a[@href='processlogin.php?county=Lake']"
        self.parcel_info_link = "//a[@href='http://parcelinfo.com/parcels/']"

    def go_to_main_page(self):
        """
        1) Go to the initial Lake County page
        2) Click the "Lake County Users Click Here" link
        3) Click the "Parcel Info" link
        """
        self.driver.get(self.initial_url)
        self.driver.implicitly_wait(10)

        # "Lake County Users Click Here" link
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, self.lake_county_link))
        ).click()

        # Now to the parcel search page
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, self.parcel_info_link))
        ).click()

    def scrape_parcels(self, parcel_ids):
        """
        Reuse self.driver, do not quit. Each parcel is processed in a loop.
        """
        all_data = []

        for parcel_id in parcel_ids:
            try:
                # 1) We are already on the search page after go_to_main_page,
                #    but if you need to "reset" each time, you could call go_to_main_page() again.
                #    For now, let's assume we stay on the search page.

                # same logic as your existing code
                search_box_xpath = "//form[@action='parcelresults1.php']//input[@name='searchvalue' and @type='text']"
                search_button_xpath = "//form[@action='parcelresults1.php']//button[@type='submit']"
                result_table_xpath = "//table[@summary='search results']/tbody/tr[@class='results']"
                additional_info_link = "/html/body/div[3]/table/tbody/tr[4]/td[1]/a"
                return_to_searchpage_path = "/html/body/div[1]/table[2]/tbody/tr/td[1]/a"

                # 2) Search
                search_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, search_box_xpath))
                )
                search_box.clear()
                search_box.send_keys(parcel_id)

                # hidden value for search type
                search_field = self.driver.find_element(By.XPATH, "//input[@name='searchfield' and @type='hidden']")
                self.driver.execute_script(
                    "arguments[0].setAttribute('value','parcelnumber')", search_field
                )

                # Click search
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, search_button_xpath))
                ).click()

                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                # 3) Extract table rows
                rows = self.driver.find_elements(By.XPATH, result_table_xpath)

                for row in rows:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    # Build a DataObject
                    parcel_data = DataObject(
                        ParcelID=parcel_id,
                        LandValue=cols[7].text,
                        BuildingValue=cols[8].text,
                        TotalValue=cols[9].text,
                    )

                    # Additional info link -> assessment year
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, additional_info_link))
                    ).click()

                    # Scrape assessment year
                    assessed_year_element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/h2"))
                    )
                    assessed_text = assessed_year_element.text.strip()
                    assessed_year = assessed_text.split(" ")[0]  # e.g. "2023 Assessment..."
                    parcel_data.AssessmentYear = assessed_year

                    # Screenshot
                    screenshot_path = take_screenshot(self.driver, self.screenshot_dir, f"{parcel_id}.png")
                    parcel_data.ScreenshotPath = screenshot_path

                    print(
                        f"LakeMN -> {parcel_id}: Land={parcel_data.LandValue}, "
                        f"Bldg={parcel_data.BuildingValue}, Total={parcel_data.TotalValue}, "
                        f"Year={assessed_year}"
                    )
                    all_data.append(parcel_data)

                    # Return to search page
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, return_to_searchpage_path))
                    ).click()

            except Exception as e:
                print(f"LakeMN: Error processing parcel ID {parcel_id}: {e}")
                error_shot = os.path.join(self.screenshot_dir, f"error_{parcel_id}.png")
                self.driver.save_screenshot(error_shot)

        return all_data


# ----------------------------------------------------------------------------
# 4) Patriot Properties Counties (Generic)
# ----------------------------------------------------------------------------
class PatriotScraper(BaseCountyScraper):
    """
    Generic Patriot approach. Each county using Patriot can be handled by
    instantiating this scraper with its unique 'base_url' if needed.
    """

    def __init__(self, driver, screenshot_dir, base_url):
        super().__init__(driver, screenshot_dir)
        self.base_url = base_url

    def go_to_main_page(self):
        # If the Patriot site is always the same, or if each county has a different URL:
        self.driver.get(self.base_url)

    def scrape_parcels(self, parcel_ids):
        """
        Re-implements your 'scrape_patriot_properties' logic.
        """
        all_data = []
        for parcel_id in parcel_ids:
            try:
                # 1) Go to the base URL
                self.go_to_main_page()

                parcel_data = DataObject(ParcelID=parcel_id)

                # 2) Switch frames, search for parcel
                WebDriverWait(self.driver, 10).until(
                    EC.frame_to_be_available_and_switch_to_it((By.NAME, 'middle'))
                )
                search_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, 'SearchParcel'))
                )
                search_box.clear()
                search_box.send_keys(parcel_id)
                search_box.send_keys(Keys.RETURN)

                # 3) Switch to bottom frame
                self.driver.switch_to.default_content()
                WebDriverWait(self.driver, 10).until(
                    EC.frame_to_be_available_and_switch_to_it((By.NAME, 'bottom'))
                )

                # 4) Parcel detail link
                parcel_link = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'Summary.asp?AccountNumber')]"))
                )
                parcel_link.click()

                # 5) Switch again
                self.driver.switch_to.default_content()
                WebDriverWait(self.driver, 10).until(
                    EC.frame_to_be_available_and_switch_to_it((By.NAME, 'bottom'))
                )

                # 6) Extract fields
                try:
                    land = self.driver.find_element(
                        By.XPATH, "//td[normalize-space()='Land Value']/following-sibling::td/font"
                    ).text
                    parcel_data.LandValue = land
                except:
                    parcel_data.LandValue = ""

                try:
                    bldg = self.driver.find_element(
                        By.XPATH, "//td[normalize-space()='Building Value']/following-sibling::td/font"
                    ).text
                    parcel_data.BuildingValue = bldg
                except:
                    parcel_data.BuildingValue = ""

                try:
                    total = self.driver.find_element(
                        By.XPATH, "//td[normalize-space()='Total Value']/following-sibling::td/font/b"
                    ).text
                    parcel_data.TotalValue = total
                except:
                    parcel_data.TotalValue = ""

                try:
                    assessed_year = self.driver.find_element(
                        By.XPATH, "//td[normalize-space()='Year']/following-sibling::td/font/b"
                    ).text
                    parcel_data.AssessmentYear = assessed_year
                except:
                    parcel_data.AssessmentYear = ""

                # 7) Screenshot
                screenshot_path = take_screenshot(self.driver, self.screenshot_dir, f"{parcel_id}.png")
                parcel_data.ScreenshotPath = screenshot_path

                print(f"Patriot -> {parcel_id}: {parcel_data.LandValue}, {parcel_data.BuildingValue}, {parcel_data.TotalValue}")
                all_data.append(parcel_data)

                # short pause
                time.sleep(2)

                # Switch back if needed:
                self.driver.switch_to.default_content()

            except Exception as e:
                print(f"Patriot error with {parcel_id}: {e}")
                error_shot = os.path.join(self.screenshot_dir, f"error_{parcel_id}.png")
                self.driver.save_screenshot(error_shot)

                # Optionally continue or break depending on your preference.

        return all_data


# ----------------------------------------------------------------------------
# 5) CPT Counties (Generic)
# ----------------------------------------------------------------------------
class CPTScraper(BaseCountyScraper):
    """
    Generic CPT approach. Reuse self.driver, parameterized by base_url if different counties
    share this same approach but have distinct starting URLs.
    """

    def __init__(self, driver, screenshot_dir, base_url):
        super().__init__(driver, screenshot_dir)
        self.base_url = base_url

    def go_to_main_page(self):
        self.driver.get(self.base_url)

    def scrape_parcels(self, parcel_ids):
        """
        Re-implements your 'scrape_cpt_counties' logic.
        """
        all_data = []
        for parcel_id in parcel_ids:
            try:
                # 1) Go to the base URL
                self.go_to_main_page()
                wait = WebDriverWait(self.driver, 10)

                # 2) Affirm/Continue disclaimers
                try:
                    affirm_button = wait.until(EC.presence_of_element_located((By.ID, "affirm")))
                    affirm_button.click()
                except:
                    pass

                try:
                    continue_button = wait.until(EC.presence_of_element_located((By.ID, "continueButton")))
                    continue_button.click()
                except:
                    pass

                # 3) Search for parcel
                parcel_input = wait.until(EC.presence_of_element_located((By.ID, "parcelBox")))
                parcel_input.clear()
                parcel_input.send_keys(parcel_id)

                search_button = wait.until(EC.element_to_be_clickable((By.ID, "parcelButton")))
                search_button.click()

                # 4) Click matching row
                parcelNum_xpath = f'//div[@col-id="parcelNum" and normalize-space()="{parcel_id}"]'
                parcel_cell = wait.until(EC.element_to_be_clickable((By.XPATH, parcelNum_xpath)))
                parcel_cell.click()

                # 5) Appraisal summary tab
                appraisal_tab = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@role='tab' and contains(., 'Appraisal Summary')]"))
                )
                appraisal_tab.click()
                time.sleep(1)  # let it load

                # 6) Screenshot
                screenshot_path = take_screenshot(self.driver, self.screenshot_dir, f"{parcel_id}.png")

                # 7) Land / building / total / year
                try:
                    land_val = wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//mat-cell[contains(@class, 'mat-column-landValue')]")
                        )
                    ).text.strip()
                except:
                    land_val = ""

                try:
                    build_val = wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//mat-cell[contains(@class, 'mat-column-buildValue')]")
                        )
                    ).text.strip()
                except:
                    build_val = ""

                try:
                    total_val = wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//mat-cell[contains(@class, 'mat-column-totalValue')]")
                        )
                    ).text.strip()
                except:
                    total_val = ""

                try:
                    assessment_elem = wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//mat-card-title/span[contains(@class, 'darkBlueText')]")
                        )
                    )
                    assessment_year = assessment_elem.text.split("/")[0].strip()  # e.g. "2023/2024"
                except:
                    assessment_year = ""

                parcel_data = DataObject(
                    ParcelID=parcel_id,
                    LandValue=land_val,
                    BuildingValue=build_val,
                    TotalValue=total_val,
                    AssessmentYear=assessment_year,
                    ScreenshotPath=screenshot_path
                )
                all_data.append(parcel_data)

            except Exception as e:
                print(f"CPT error with {parcel_id}: {e}")
                error_shot = os.path.join(self.screenshot_dir, f"error_{parcel_id}.png")
                self.driver.save_screenshot(error_shot)

        return all_data
    

# ----------------------------------------------------------------------------
# 6) Spokane WA 
# ----------------------------------------------------------------------------
class SpokaneWAScraper(BaseCountyScraper):
    """
    Scraper for Spokane County, WA.
    """

    def __init__(self, driver, screenshot_dir):
        super().__init__(driver, screenshot_dir)
        self.base_url = 'https://cp.spokanecounty.org/scout/propertyinformation/'

    def go_to_main_page(self):
        """
        Navigate to the main page of Spokane County property information.
        """
        self.driver.get(self.base_url)

    def scrape_parcels(self, parcel_ids):
        """
        Implementation of the Spokane County logic.
        """
        all_data = []
        for parcel_id in parcel_ids:
            try:
                # 1) Go to the Spokane site
                self.go_to_main_page()

                # 2) Wait for input to be clickable, then type parcel ID
                search_box = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="txtSearch"]'))
                )
                search_box.clear()
                search_box.send_keys(parcel_id)

                # Click search button
                search_button = self.driver.find_element(By.XPATH, '//*[@id="MainContent_btnSearch"]')
                search_button.click()

                # 3) Gather fields
                assessment_year = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="MainContent_AssessedValue_GridView4"]/tbody/tr[1]/td[1]'))
                ).text

                land_value = self.driver.find_element(
                    By.XPATH, '//*[@id="MainContent_AssessedValue_GridView4"]/tbody/tr[1]/td[4]'
                ).text

                # Expand building value dropdown
                expand_button = self.driver.find_element(
                    By.XPATH, '//*[@id="MainContent_AssessedValue_GridView4"]/tbody/tr[1]/td[1]/span'
                )
                expand_button.click()

                building_value = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="MainContent_AssessedValue_GridView4"]/tbody/tr[2]/td/div/div[1]/div[2]'))
                ).text

                total_value = self.driver.find_element(
                    By.XPATH, '//*[@id="MainContent_AssessedValue_GridView4"]/tbody/tr[1]/td[3]'
                ).text

                # 4) Create DataObject
                parcel_data = DataObject(
                    ParcelID=parcel_id,
                    LandValue=land_value,
                    BuildingValue=building_value,
                    TotalValue=total_value,
                    AssessmentYear=assessment_year,
                    ScreenshotPath=""
                )

                # 5) Take screenshot
                screenshot_path = take_screenshot(self.driver, self.screenshot_dir, f"{parcel_id}.png")
                parcel_data.ScreenshotPath = screenshot_path

                print(
                    f"SpokaneWA -> {parcel_id}: Land={land_value}, Building={building_value}, "
                    f"Total={total_value}, Year={assessment_year}"
                )
                all_data.append(parcel_data)

            except Exception as e:
                print(f"SpokaneWA: Error processing parcel ID {parcel_id}: {e}")
                # Optionally do an error screenshot
                error_shot = os.path.join(self.screenshot_dir, f"error_{parcel_id}.png")
                self.driver.save_screenshot(error_shot)

        return all_data
    
# ----------------------------------------------------------------------------
# 7) WI (MAYBE OTHER) COUNTIES
# ----------------------------------------------------------------------------

class WIScraper(BaseCountyScraper):
    """
    Generic WI approach. Each county using WI can be handled by
    instantiating this scraper with its unique 'base_url'.
    """

    def __init__(self, driver, screenshot_dir, base_url):
        super().__init__(driver, screenshot_dir)
        self.base_url = base_url


    def go_to_main_page(self):
        # If the WI site is always the same, or if each county has a different URL:
        self.driver.get(self.base_url)
        self.driver.implicitly_wait(10)

        # Accept disclaimers
        disclaimer_button_xpath = '//*[@id="ctl00_cphMainApp_btnEntryPageAccept"]'
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, disclaimer_button_xpath))
        ).click()


    def scrape_county(self, parcel_ids):
        """
        The 'template method' that orchestrates the entire scraping flow:
        1) Go to the county's main page, accept disclaimers ONCE
        2) Then scrape all parcels in a loop
        """
        # 1) Go to main page, accept disclaimers once
        self.go_to_main_page()

        # 2) Now do the per-parcel logic in scrape_parcels
        return self.scrape_parcels(parcel_ids)
    

    def scrape_parcels(self, parcel_ids):
        """
        Scrape parcel data for all parcels, reusing the session
        without re-invoking disclaimers each time.
        """
        all_data = []

        for parcel_id in parcel_ids:
            parcel_data = None
            try:
                print("\nDEBUG: Processing parcel:", parcel_id)

                # 1) Search for the parcel
                search_box_xpath = '//*[@id="mtxtParcelNumber"]'
                search_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, search_box_xpath))
                )

                # Clear + set value by JS to handle any masked input
                self.driver.execute_script(
                    "arguments[0].value = arguments[1];", search_box, parcel_id
                )
                time.sleep(1)

                # Some sites require a button click instead of ENTER, but let's try ENTER first
                search_box.send_keys(Keys.ENTER)
    

                # 2) Navigate to the assessment page
                assessment_page_link_xpath = '//*[@id="LinkButtonAssessments"]'
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, assessment_page_link_xpath))
                ).click()

                # 3) Check if current year is assessed, if not, select previous year
                not_assessed_xpath = '//*[@id="LabelViewValuationsNotAllowed"]'
                year_dropdown_xpath = '//*[@id="ddlTaxYear"]'

                if self.driver.find_elements(By.XPATH, not_assessed_xpath):
                    year_dropdown = Select(
                        self.driver.find_element(By.XPATH, year_dropdown_xpath)
                    )
                    year_dropdown.select_by_index(1)

                # 4) Extract values
                land_value_xpath = '//*[@id="lblLand"]'
                building_value_xpath  = '//*[@id="lblImprovements"]'
                total_value_xpath = '//*[@id="lblTotal"]'
                assyear_value_xpath = '//*[@id="LabelCurrentYearValuationsRE"]'

                assyear = self.driver.find_element(By.XPATH, assyear_value_xpath).text
                assyear_value = assyear.split()[0]
                land_value = self.driver.find_element(By.XPATH, land_value_xpath).text
                building_value = self.driver.find_element(By.XPATH, building_value_xpath).text
                total_value = self.driver.find_element(By.XPATH, total_value_xpath).text

                # 4.5) Take screenshot
                screenshot_path = take_screenshot(self.driver, self.screenshot_dir, f"{parcel_id}.png")

                # 5) Create DataObject
                parcel_data = DataObject(
                    ParcelID=parcel_id,
                    LandValue=land_value,
                    BuildingValue=building_value,
                    TotalValue=total_value,
                    AssessmentYear=assyear_value,  # Extract if available
                    ScreenshotPath=screenshot_path
                )

                

                all_data.append(parcel_data)

            except Exception as e:
                print(f"PierceWI: Error processing parcel ID {parcel_id}: {e}")
                # Optionally do an error screenshot
                error_shot = os.path.join(self.screenshot_dir, f"error_{parcel_id}.png")
                self.driver.save_screenshot(error_shot)

        return all_data