import logging

from release_helper import process_potential_release


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting the release process.")
    process_potential_release()
