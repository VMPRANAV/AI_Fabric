import os
# Extend package path to include the actual application package located in the sibling 'backend/app' directory.
__path__.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'app')))
