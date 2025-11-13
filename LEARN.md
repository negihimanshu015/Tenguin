# DAY 1

# DOCKER
  - Docker uses root ownership which can cause security issues during production so we change ownership.
  - We do it twice, first one to resolve problems with  pip installation and second one to change the ownership of the files inside the workdir (COPY command is run as root so the files created will have root ownership.)
  - Volume in web is for hot reload and volume in db is for data persistence.  

# DAY 2

# DJANGO
  - Django paths and URL confs
  - Django models
  - makemigrations and migrations

  - get_object_or_404 , render
  - templates

# DAY 3
  - never hardcode URL
  - generic view is the goat
  - Test driven development is the best approach as it allows critical thinking and unbiased testing

  