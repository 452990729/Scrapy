# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class OmimcrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    snomedct_ids = scrapy.Field()
    orpha_ids = scrapy.Field()
    do_ids = scrapy.Field()
    omim_url = scrapy.Field()
    omim_id = scrapy.Field()
    omim_name = scrapy.Field()
    location = scrapy.Field()
    phenotype = scrapy.Field()
    phenotype_mim_number = scrapy.Field()
    inheritance = scrapy.Field()
    phenotype_mapping_key = scrapy.Field()
    gene_locus = scrapy.Field()
    gene_locus_mim_number = scrapy.Field()
    pass
