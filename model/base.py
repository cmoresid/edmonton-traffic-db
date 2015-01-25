from sqlalchemy.ext.declarative import declarative_base

# Create a base instance to share between
# the different database model classes. This instance 
# is required in order to split the database model classes 
# into different physical files.
Base = declarative_base()