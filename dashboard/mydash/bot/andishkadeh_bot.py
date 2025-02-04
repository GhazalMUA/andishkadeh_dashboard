import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from .config import XPATHS, CONTENT_CATEGORIES, COUNTRY_LIST, MY_IGNORED_LIST
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime, timedelta
import re
from selenium.webdriver.chrome.options import Options
import pandas as pd
from urllib.parse import urlparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.conf import settings

logging.basicConfig(filename="bot_output.log", level=logging.INFO, format="%(asctime)s - %(message)s")
class LogRedirector:
    def __init__(self, log_file):
        self.log_file = log_file
        self.terminal = sys.stdout

    def write(self, message):
        with open(self.log_file, "a") as f:
            f.write(message)  # Write to log file
        self.terminal.write(message)  # Also print to terminal

    def flush(self):
        self.terminal.flush()

    def isatty(self):
        # Return False to indicate this is not a terminal
        return False

# Redirecting stdout and stderr
sys.stdout = LogRedirector("bot_output.log")
sys.stderr = LogRedirector("bot_output.log")
# Redirecting stdout and stderr
sys.stdout = LogRedirector("bot_output.log")
sys.stderr = LogRedirector("bot_output.log")

class andishkadeh_bot:
    
    @staticmethod
    def generate_excel_filename(order_id):
        """
        Generate a dynamic Excel file name based on the order ID and current timestamp.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        return os.path.join('results', f"order_{order_id}_{timestamp}.xlsx")

    
    @staticmethod
    def configure_chrome_options():
        options = Options()
        options.add_argument("--lang=en-US")  # Force Chrome to use English
        options.add_argument("--disable-extensions")  # Disable unnecessary extensions
        options.add_argument("--no-sandbox")  # Necessary for certain environments like Docker or CI/CD
        options.add_argument("--disable-dev-shm-usage")  # Avoid issues in resource-limited environments
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36")
        return options
    
    @staticmethod
    def handle_popup(driver):
        try:
            # Wait for the "Accept all" or "Reject all" button to be clickable
            accept_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, XPATHS["accept_cookies"]))
            )
            # Click the "Accept all" button
            accept_button.click()
            print("❌ Accepted all cookies.")
        except Exception as e:
            print(f"❌ No popup found or error occurred: {e}")

    @staticmethod
    def convert_relative_date(relative_date):
        try:
            if 'hour' in relative_date or 'minute' in relative_date:  # Handle 'X hours ago'
                return datetime.now().strftime('%Y-%m-%d')  # Return today's date
            
            if 'day' in relative_date:  # Handle 'X days ago'
                days_ago = int(re.search(r'(\d+)', relative_date).group(1))
                date_in_past = datetime.now() - timedelta(days=days_ago)
                return date_in_past.strftime('%Y-%m-%d')

            return relative_date  # If it's not a relative date, return it as is
        except Exception as e:
            return None  # In case of error, return None to skip the entry
    
    @staticmethod
    def calculate_similarity(previews):
        """
        Given a list of previews, compute cosine similarity between them and filter out nearly duplicate previews.
        This function keeps the first occurrence of each preview and deletes all duplicates.
        """
        def remove_dates(preview):
            # Remove dates in the format '27 Jan 2025' or '3 days ago'
            return re.sub(r'\d{1,2} \w{3} \d{4}', '', preview)  # This removes dates like '27 Jan 2025'
        
        # Step 1: Preprocess the previews (convert to lower case, strip extra spaces, and remove dates)
        cleaned_previews = [remove_dates(preview.lower().strip()) for preview in previews]

        vectorizer = TfidfVectorizer().fit_transform(cleaned_previews)

        # Step 3: Calculate cosine similarity between the previews
        cosine_sim_matrix = cosine_similarity(vectorizer)

        # Step 4: Identify duplicates based on a similarity threshold
        threshold = 0.70
        to_remove = set()  # To store indices of previews to remove
        seen_previews = {}  # To track the first occurrence of a preview

        # Loop through each pair of previews and calculate similarity
        for i in range(len(cosine_sim_matrix)):
            for j in range(i+1, len(cosine_sim_matrix)):  # Start from the next preview
                similarity_score = cosine_sim_matrix[i, j]
                
                # If the similarity score is greater than the threshold, we consider it a duplicate
                if similarity_score > threshold:
                    # Check if we've already seen this preview
                    if cleaned_previews[i] not in seen_previews:
                        seen_previews[cleaned_previews[i]] = i  # Keep track of the first occurrence of preview i
                    if cleaned_previews[j] not in seen_previews:
                        seen_previews[cleaned_previews[j]] = j  # Keep track of the first occurrence of preview j
                    
                    # Mark all but the first occurrence of the duplicate preview for removal
                    if seen_previews[cleaned_previews[i]] != i:  # If we have already seen this preview, remove it
                        to_remove.add(i)
                    if seen_previews[cleaned_previews[j]] != j:  # If we have already seen this preview, remove it
                        to_remove.add(j)

                    # print(f"Preview {i} and {j} are similar:")
                    # print(f"Preview 1: {cleaned_previews[i]}")
                    # print(f"Preview 2: {cleaned_previews[j]}")
                    # print(f"Similarity Score: {similarity_score}")

        return to_remove

    @staticmethod
    def filter_links(links, previews, ignore_list, country_list):
        filtered_links = []  # List to store the filtered links
        filtered_previews = []  # List to store the corresponding filtered previews
        seen_links = []  # List to track seen links (duplicates will be avoided)
        to_remove = set()  # List of indexes to remove (due to country name or similarity)

        # Step 1: Apply the original URL filtering (including country and ignored list)
        for i, link in enumerate(links):
            # Normalize the link (ensure it ends with a slash)
            if not link.endswith('/'):
                link = link + '/'  # Add a slash if it doesn't already end with one

            # Parse the URL to get the path and domain
            parsed_url = urlparse(link)
            path = parsed_url.path

            # Ignore links with '?' (query parameters) 
            if '?' in link:
                print(f"❌ Ignoring: {link} because it contains a query parameter.")
                continue
            
            # Ignore file extensions
            if link.endswith(('.pdf', '.doc', '.docx')):    
                print(f"❌ Ignoring: {link} because it contains a file extension.")
                continue

            # Ignore links that contain any word from the ignore list in the path
            path_segments = path.strip('/').split('/')
            if len(path_segments) >= 2:
                if any(word in path_segments[0] for word in ignore_list) or any(word in path_segments[1] for word in ignore_list):
                    print(f"❌ Ignoring: {link} because it contains ignored keywords in the URL")
                    continue
            if any(word in link for word in ignore_list):
                print(f"❌ Ignoring: {link} because it contains an ignored keyword in the URL")
                continue
            
            country_list = [country.lower() for country in country_list]
            
            # Step 2: Ignore country names appearing at the end of the URL (between two slashes)
            # Normalize link (remove query parameters, fragments, and trailing slashes)
            normalized_link = urlparse(link).path.rstrip('/')  
            # Extract last segment, even if there is nothing after the final slash
            path_segments = normalized_link.split('/')

            # Handle the case where the last segment is empty (when there is a trailing slash)
            if len(path_segments) > 1:
                last_segment = path_segments[-1].lower()
            else:
                last_segment = path_segments[-2].lower() if len(path_segments) > 1 else ''

            # Check if the last segment matches any country name
            if last_segment in country_list:
                print(f"✅ Ignoring: {link} because it matched {last_segment} in country_list")
                to_remove.add(i)
                continue  # Skip appending this link and its preview

            # Step 3: Remove empty or invalid previews
            valid_previews = [preview for preview in previews if preview.strip() and len(preview.split()) > 3]  # Filter out short previews
            print(f"Filtered Previews: {valid_previews}")

            # If there are no valid previews, skip the filtering
            if not valid_previews:
                print(f"❌ No valid previews for {link}, skipping filtering.")
                continue

            # Step 4: Apply preview similarity filtering
            to_remove.update(andishkadeh_bot.calculate_similarity(valid_previews))  # Add preview similarities to remove list

            for j in to_remove:
                print(f"❌ Ignoring: {links[j]} because it is similar to another preview")
            
            # Step 5: Ignore pagination links (e.g., page=2, p=3)
            if 'page' in link or 'p=' in link:
                print(f"❌ Ignoring: {link} because it is a pagination link")
                to_remove.add(i)
                continue

            # Step 6: Ignore any links that contain question mark (query parameter)
            if '?' in link:
                print(f"❌ Ignoring: {link} because it contains a question mark (query parameter)")
                to_remove.add(i)
                continue

            # Ignore duplicates
            if link in seen_links:
                print(f"❌ Ignoring: {link} because it's a duplicate")
                continue
            seen_links.append(link)

            filtered_links.append(link)
            filtered_previews.append(previews[i])

        # Step 7: Apply preview similarity filtering
        to_remove.update(andishkadeh_bot.calculate_similarity(filtered_previews))  # Add preview similarities to remove list

        # Step 8: Filter out the links marked for removal
        final_links = [link for i, link in enumerate(filtered_links) if i not in to_remove]
        final_previews = [preview for i, preview in enumerate(filtered_previews) if i not in to_remove]

        return final_links, final_previews, to_remove

    @staticmethod
    def perform_search_and_save_links(query, ignore_list, time_option=None, start_date=None, end_date=None, country_list=None, order_id=None):
        output_excel = andishkadeh_bot.generate_excel_filename(order_id)
        # Ensure the results directory exists
        results_dir = os.path.join(settings.MEDIA_ROOT, 'results')
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)

            
        # Initialize Chrome WebDriver
        service = Service(XPATHS["chromedriver_path"])
        options = andishkadeh_bot.configure_chrome_options()
        driver = webdriver.Chrome(service=service, options=options)

        search_results = []

        try:
            # Open Google Search
            driver.get("https://www.google.com")
            andishkadeh_bot.handle_popup(driver)
            try:
                search_box = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.NAME, XPATHS["search_box"]))
                )
                print('❌ I found search box')
            except:
                print('❌ I couldnt find search box')    
            search_box.send_keys(query)
            print('❌ I typed the query')
            search_box.send_keys("\n")
            print('❌ Query entered and search initiated.')
            time.sleep(4)

            try:
                tools_button = WebDriverWait(driver, 10).until(
                    # EC.element_to_be_clickable((By.XPATH, "//div[@aria-controls='hdtbMenus' and @role='button']"))
                    EC.element_to_be_clickable((By.XPATH, XPATHS["tools_button"]))

                )
                tools_button.click()
                print("❌ Tools button clicked")
            except Exception as e:
                print(f"❌ Error interacting with Tools button: {e}")

            # Wait for the "Time" dropdown to be clickable
            try:
                time_dropdown_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, XPATHS["time_dropdown"]))
                )
                time_dropdown_button.click()
                print("❌ Time dropdown clicked.")
            except Exception as e:
                print(f"❌ Error interacting with Time dropdown: {e}")

            if start_date and end_date:
                # Click the "Custom range" option
                custom_range_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, XPATHS["custom_range"]))
                )
                custom_range_button.click()

                # Input the start and end dates in the respective fields
                from_date_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, XPATHS["from_date"]))
                )
                to_date_input = driver.find_element(By.ID, XPATHS["to_date"])

                # Set the custom date range
                from_date_input.send_keys(start_date)
                to_date_input.send_keys(end_date)

                # Submit the form to apply the date range
                submit_button = driver.find_element(By.CSS_SELECTOR, XPATHS["submit_button"])
                submit_button.click()

                print(f"❌ Custom date range set: {start_date} to {end_date}")
                time.sleep(2)  # Wait for the search results to refresh

            else:
                time_option_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//a[@role='menuitemradio' and text()='{time_option}']"))
                )
                time_option_element.click()
                print(f"❌ time range set to {time_option}")
            # Wait briefly to ensure results are updated
            time.sleep(2)

            # Pagination: Loop through all pages and collect data
            while True:
                results = driver.find_elements(By.CSS_SELECTOR,XPATHS["result_container"])  # Each search result container

                for result in results:
                    try:
                        link_element = result.find_element(By.CSS_SELECTOR, XPATHS["result_link"])
                        link = link_element.get_attribute("href")

                        title_element = result.find_element(By.CSS_SELECTOR,XPATHS["result_title"])
                        title = title_element.text

                        preview_element = result.find_element(By.CSS_SELECTOR, XPATHS["result_preview"])
                        preview = preview_element.text

                        datetime_element = result.find_element(By.CSS_SELECTOR, XPATHS["result_datetime"])
                        datetime = datetime_element.text

                        # Convert relative date or Persian date to AD format
                        datetime = andishkadeh_bot.convert_relative_date(datetime) if 'hour' in datetime or 'minute' in datetime or 'day' in datetime else datetime

                        resource = link_element.get_attribute("href").split("//")[-1].split("/")[0].split(".")[-2]  # Extract main domain name

                        # Extract type/category from the URL path
                        category = None
                        url_segments = link.split("/")
                        for segment in url_segments:
                            if segment in CONTENT_CATEGORIES:
                                category = segment
                                break

                        search_results.append({
                            "Title": title,
                            "Link": link,
                            "Preview": preview,
                            "Datetime": datetime,
                            "Resource": resource,
                            "Type": category
                        })
                        
                    except Exception as e:
                        print(f"Error processing a result: {e}")

                print(f"❌ Collected {len(search_results)} results so far.")

                # Check if the "Next" button exists and is clickable
                try:
                    next_button = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.LINK_TEXT, "Next"))
                    )
                    next_button.click()
                    time.sleep(2)  # Allow time for the next page to load
                except Exception as e:
                    print("❌ No more pages or error occurred:", e)
                    break
                
            # Filter the links using the combined filter function
            links = [result['Link'] for result in search_results]
            previews = [result['Preview'] for result in search_results]
            print(f"❌ raftam soraghe filter kardane linkha. tedade linkhayi ke ta hala gerftam: {len(link)}")
            # print("Previews before filtering:", previews)

            # Apply both URL filtering and preview similarity filtering
            filtered_links, filtered_previews, to_remove = andishkadeh_bot.filter_links(links, previews, MY_IGNORED_LIST, COUNTRY_LIST)
            
            # Now filter the search results based on the filtered links
            search_results = [result for i, result in enumerate(search_results) if i not in to_remove]
            
            if not search_results:
                raise ValueError("❌ Bot did not return a valid result")
            # Save the filtered results to Excel
            results_df = pd.DataFrame(search_results)
            
            excel_path = os.path.join(results_dir, output_excel)  # Complete path in media/results directory
            results_df.to_excel(excel_path, index=True)
            print(f"❌ Results saved to {output_excel}")
            
            return output_excel  # Returning the path or file content

        except Exception as e:
            print(f"❌ An error occurred: {e}")
        finally:
            driver.quit()



# Example usage:
# andishkadeh_bot.perform_search_and_save_links(
#         query='allintext:  "iraq" site:https://www.intellinews.com/',
#         ignore_list= MY_IGNORED_LIST,
#         start_date="01/14/2025",
#         end_date="01/25/2025",
#         country_list=COUNTRY_LIST
# )