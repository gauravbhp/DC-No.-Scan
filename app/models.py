# from django.db import models

# class Data(models.Model):  # Note: Changed to PascalCase which is Django convention
#     PROVISIONAL_CODE = models.CharField(max_length=100, primary_key=True)
#     DELIVERYPOINTUNIQUE = models.IntegerField()
#     vehicle_no = models.CharField(max_length=20)  
#     destination = models.CharField(max_length=50)

#     class Meta:
#         db_table = 'DB2INST1.DATA'  # Explicitly specify the schema and table name

#     def __str__(self):
#         return self.name