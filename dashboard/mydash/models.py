from django.db import models
from django.contrib.auth.models import User
# In this step I used default django user model kimia jan but we can change it in future.

# Model for Continent (No relationship with other models)
class Continent(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Model for Region (No relationship with other models)
class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Model to store the status of the order/result
class Status(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True,null=True)

    def __str__(self):
        return self.name

# Model to store Research Areas
class ResearchArea(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
# Model to store Numbering (0-10)
class Numbering(models.Model):
    name = models.CharField(max_length=100) # These names should be numbers but in string type.
    description = models.CharField(max_length=1000)
    
    def __str__(self):
        return self.name
    
# Model to store Research Centers (Websites)
class ResearchCenter(models.Model):
    name_in_arabic = models.CharField(max_length=255)
    website = models.URLField()
    research_areas = models.ManyToManyField(ResearchArea)
    continent = models.ForeignKey(Continent, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    numbering = models.ForeignKey(Numbering, on_delete=models.CASCADE, blank=True,null=True)
    
    def __str__(self):
        return self.name_in_arabic

# Model to store predefined time ranges
class TimeRange(models.Model):
    name = models.CharField(max_length=100)  # E.g., "Past week", "Any time", etc.
    description = models.TextField(null=True, blank=True)  # Optional, to describe the time range

    def __str__(self):
        return self.name

# Model to store the Order (user search details)
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    keyword = models.CharField(max_length=255)
    time_range = models.ForeignKey(TimeRange, on_delete=models.SET_NULL, null=True, blank=True)

    time_range = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    final_status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Order of {self.user.username} for {self.keyword}"

# Model to store details about the order, including the research center and region/continent info
class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    research_center = models.ForeignKey(ResearchCenter, on_delete=models.CASCADE)  # Link to Research Center
    query = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Detail of order {self.order.id} - Query: {self.query}"

# Model to store the result of each order (Bot result file or other)
class OrderResult(models.Model):
    order_detail = models.ForeignKey(OrderDetail, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    result_file = models.FileField(upload_to='result_files/', null=True, blank=True)
    raw_data = models.JSONField(null=True, blank=True)  # Store raw data from the website 
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return f"Result for OrderDetail {self.order_detail.id} - Status: {self.status.name}"
    
