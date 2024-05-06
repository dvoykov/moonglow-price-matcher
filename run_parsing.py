import sys
from parsers.mg_parser import MoonGlowParser
from parsers.ms_parser import MySkinParser
from loguru import logger


if __name__ == "__main__":
    if len(sys.argv) > 1:
        parser_type = sys.argv[1]
    else:
        logger.error('Parser type is not specified')
        exit(1)

    parser = None

    ### moonglow
    if parser_type.lower() == 'moonglow':
        prod_urls = ['https://www.moonglow.md/ru/catalog/page/{page}?loop={loop}&woo_ajax=1']
        parser = MoonGlowParser(parser_type='moonglow', prod_urls=prod_urls)

    ### myskin
    if parser_type.lower() == 'myskin':
        prod_urls = [
            'https://myskin.md/osnovnoj-uhod',
            'https://myskin.md/specialinyj-uhod',
            'https://myskin.md/ru/dlya-doma',
            'https://myskin.md/osnovnoj-uhod'
        ]
        parser = MySkinParser(parser_type='myskin', prod_urls=prod_urls)

    if parser is None:
        logger.error(f'No parser found for the specified parser type: `{parser_type}`')
        exit(2)

    ### parse catalog
    logger.info(f'Product catalog [{parser_type}] parsing started ...')
    status_code, status_message = parser.parse_catalog()

    if status_code != 0:
        logger.error(f'Product catalog parsing finished with error: {status_message}')
        exit(3)

    logger.info(f'Product catalog parsing finished, total products: {len(parser.products)}')

    ### parse products
    logger.info('Products parsing started ...')
    success_qty, err_qty = parser.parse_products()

    if success_qty != 0:
        logger.info(f'Products parsing finished successfully for {success_qty} products.')

    if err_qty != 0:
        logger.warning(f'Products parsing finished with errors for {err_qty} products.')

    ### generate embeddings
    logger.info('Generating embeddings for products started ...')
    success_qty, err_qty = parser.gen_embeddings()
    if success_qty != 0:
        logger.info(f'Generating embeddings finished successfully for {success_qty} products.')

    if err_qty != 0:
        logger.warning(f'Generating embeddings finished with errors for {err_qty} products.')

    ### save products
    logger.info('Products saving started ...')
    success_qty, err_qty = parser.save_products()

    if success_qty != 0:
        logger.info(f'Successfully saved {success_qty} products.')

    if err_qty != 0:
        logger.warning(f'{err_qty} errors while saving products.')

    logger.info('Finish.')
