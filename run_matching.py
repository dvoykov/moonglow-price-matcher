import sys
from loguru import logger
from db.controller import ProductController
from models.matcher import Matcher

if __name__ == "__main__":
    if len(sys.argv) == 3:
        source1 = sys.argv[1]
        source2 = sys.argv[2]
    else:
        logger.error('Parser type is not specified')
        exit(1)

    result, msg, mg_products = ProductController.get_products(source1)
    if result != 0:
        logger.error(f'Error while loading products for source "{source1}"')
        exit(2)

    if not mg_products:
        logger.error(f'No products for source "{source1}"')
        exit(2)

    result, msg, ms_products = ProductController.get_products(source2)
    if result != 0:
        logger.error(f'Error while loading products for source "{source2}"')
        exit(3)

    if not ms_products:
        logger.error(f'No products for source "{source1}"')
        exit(3)

    logger.info('Product matching started ...')

    matcher = Matcher(mg_products, ms_products)
    matcher.find_best_matches()

    logger.info(f'Product matching finished: {len(matcher.matches)} matches found.')

    print('First 8 matches:')
    for prod1, prod2, similarity in matcher.matches[:8]:
        print(f'<<{source1}>>:')
        print(prod1)
        print(f'<<{source2}>>:')
        print(prod2)
        print(f'similarity: {similarity}')
        print('--')
