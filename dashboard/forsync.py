import os
import django
import pandas as pd
from mydash.models import ResearchArea, ResearchCenter, Continent, Region

# Set up the Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')  # Correct the settings module
django.setup()  # Initialize the Django environment

# Now you can interact with Django models
file_path = 'مراكز الأبحاث v2.1.xlsx'  # The path to your Excel file

# Load the Excel file into a pandas DataFrame
df = pd.read_excel(file_path)

# Process each row and create the ResearchCenter
for index, row in df.iterrows():
    try:
        # Get the related continent and region from the database
        continent = Continent.objects.get(name=row['القارة'])
        region = Region.objects.get(name=row['المنطقة'])
        
        # Handle 'مجال البحث' column and split it by comma if multiple areas exist
        research_areas = row['مجال البحث'].split(',') if isinstance(row['مجال البحث'], str) else []

        # Create or get the ResearchCenter object
        research_center = ResearchCenter.objects.create(
            name_in_arabic=row['اسم المركز (العربي)'],
            website=row['الموقع الإلكتروني'],
            continent=continent,
            region=region,
        )

        # Add research areas to the research center
        for area in research_areas:
            area = area.strip()
            if area:
                # Ensure the ResearchArea exists or create it
                research_area, created = ResearchArea.objects.get_or_create(name=area)
                research_center.research_areas.add(research_area)

        print(f"Research center '{research_center.name_in_arabic}' added successfully.")

    except Exception as e:
        print(f"Error processing row {index}: {e}")

print("Data inserted successfully.")
