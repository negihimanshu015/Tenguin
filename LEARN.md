## DAY 1

# DOCKER
  - Docker uses root ownership which can cause security issues during production so we change owenership.
  - We do it twice, first one to resolve problems with  pip installation and second one to change the ownership of the files inside the workdir (COPY command is run as root so the files created will have root ownership.)
  - Volume in web is for hot reload and volume in db is for data persistence.  